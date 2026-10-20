import re
import sys
import json
import shutil
import asyncio
from pathlib import Path

import httpx

MAP_PATH = Path(__file__).parents[1] / "utils" / "map"

sys.path.append(str(Path(__file__).parents[5]))
sys.path.append(str(Path(__file__).parents[2]))
__package__ = "ZZZeroUID.tools"

from ZZZeroUID.version import ZZZero_version  # noqa: E402
from gsuid_core.data_store import data_cache_path  # noqa: E402
from ZZZeroUID.tools.data_to_map import (  # noqa: E402
    EquipId2DataFile,
    WeaponId2DataFile,
    PartnerId2DataFile,
    PartnerId2SkillParamFile,
)
from ZZZeroUID.utils.hakush_api.api import ZZZ_WEAPON, ZZZ_CHARACTER  # noqa: E402
from ZZZeroUID.utils.hakush_api.request import (  # noqa: E402
    get_hakush_all_char_data,
    get_hakush_all_equipment,
    get_hakush_all_weapon_data,
)

_HEADER = {"User-Agent": f"ZZZeroUID/{ZZZero_version}"}

# gsuid_core 的 cache_data 缓存目录（只按 id 落盘，无 TTL / 无数据版本键）
STALE_CACHE_DIRS = ("get_hakush_char_data", "get_hakush_weapon_data")

# nanoka 现网数据里这几个新角色的 partner_info.full_name 还是占位符 "..."，
# 角色面板卡会直接显示 full_name，用官方全名补上。
FULL_NAME_OVERRIDE = {
    "1631": "赛维里安·洛威尔",
    "1641": "菲欧妮·蕾法爱菈",
}

# 上线前的测试快照里，名字带 (Test1) 这类占位前缀，正式数据不会有。
TEST_PREFIX_RE = re.compile(r"^\(Test[^)]*\)\s*")

# map 文件名里的版本后缀，如 PartnerId2Data_3.4.json
VERSION_SUFFIX_RE = re.compile(r"_(\d+\.\d+\.\d+)\.json$")


def clear_stale_cache() -> None:
    """清掉 gsuid_core 里 nanoka 详情接口的磁盘缓存。

    cache_data 只按 id 落盘，没有 TTL、没有数据版本键，磁盘里可能还留着角色
    上线前的测试快照（名字带 (Test1) 前缀、数值是 beta 值）。不清掉的话，
    运行时的伤害计算（utils/data.py -> get_hakush_char -> get_hakush_char_data）
    也会读到旧快照，算出来的伤害是 beta 数值。
    """
    root = Path(data_cache_path)
    for name in STALE_CACHE_DIRS:
        cache_dir = root / name
        if not cache_dir.exists():
            continue
        count = len(list(cache_dir.glob("*.json")))
        shutil.rmtree(cache_dir, ignore_errors=True)
        left = len(list(cache_dir.glob("*.json"))) if cache_dir.exists() else 0
        if left:
            print(f"警告：缓存目录 {cache_dir} 仍有 {left}/{count} 个文件未清掉（可能正被占用）")
        else:
            print(f"已清理缓存 {cache_dir}（{count} 个文件）")


def remove_old_map_files() -> None:
    """只保留当前版本的 map json，旧版本删掉。

    `utils/zzz_map.py` / `utils/name_convert.py` 只按 `ZZZero_version` 读一个后缀，
    留着旧版本既占仓库体积，又会让人误以为插件还在用旧数据。
    """
    for f in sorted(MAP_PATH.glob("*.json")):
        m = VERSION_SUFFIX_RE.search(f.name)
        if not m or m.group(1) == ZZZero_version:
            continue
        f.unlink()
        print(f"已删除旧版本 map {f.name}")


def strip_test_prefix(text: str) -> str:
    """去掉名字里的 (TestN) 占位前缀。"""
    return TEST_PREFIX_RE.sub("", text).strip()


def strip_test_prefix_deep(data):
    """递归去掉所有字符串里的 (TestN) 占位前缀。"""
    if isinstance(data, str):
        return strip_test_prefix(data)
    if isinstance(data, dict):
        return {k: strip_test_prefix_deep(v) for k, v in data.items()}
    if isinstance(data, list):
        return [strip_test_prefix_deep(v) for v in data]
    return data


async def fetch_detail(url: str) -> dict | None:
    """直连 CDN 取详情，绕开 gsuid_core 的 cache_data 磁盘缓存。

    cache_data 只按 id 落盘，没有 TTL、没有数据版本键，磁盘里可能还留着角色
    上线前的测试快照（名字带 (Test1) 前缀、数值是 beta 值）。用它生成的 map
    会把测试期数据当成正式数据发布。
    """
    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(5):
            try:
                resp = await client.get(url, headers=_HEADER)
                if resp.status_code == 200:
                    return resp.json()
                print(f"{url} -> HTTP {resp.status_code}")
            except Exception as e:
                print(e)
            if attempt < 4:
                await asyncio.sleep(10)
    return None


PROP_NAME_TO_ID = {
    "基础生命值": "11101",
    "生命值": "11103",
    "生命值百分比": "11102",
    "生命值上限": "11403",
    "基础攻击力": "12101",
    "攻击力": "12103",
    "攻击力百分比": "12102",
    "基础防御力": "13101",
    "防御力": "13103",
    "防御力百分比": "13102",
    "冲击力": "12203",
    "暴击率": "20103",
    "暴击伤害": "21103",
    "异常掌控": "31403",
    "异常精通": "31203",
    "穿透率": "23103",
    "穿透值": "23203",
    "能量自动回复": "30502",
}


def parse_desc(desc: str, skill_data: dict) -> list[int]:
    """
    解析技能描述字符串，根据提供的字典计算 main 和 growth 的最终值。
    """

    # 匹配 {Skill:1031001, Prop:1001} 提取出中间的 ID: 1031001
    # \d+ 匹配数字，[^}]* 匹配直到遇到右括号 } 之前的所有字符
    pattern = r"\{Skill:\s*(\d+)[^\}]*\}"

    # 定义替换 main 值的函数
    def replace_main(match):
        skill_id = match.group(1)
        # 获取对应 ID 的 main 值，如果不存在默认返回 0
        return str(skill_data.get(skill_id, {}).get("main", 0))

    # 定义替换 growth 值的函数
    def replace_growth(match):
        skill_id = match.group(1)
        # 获取对应 ID 的 growth 值，如果不存在默认返回 0
        return str(skill_data.get(skill_id, {}).get("growth", 0))

    # 第一步：把表达式中的 {Skill:xxx, ...} 替换为具体的数字
    desc_main = re.sub(pattern, replace_main, desc)
    desc_growth = re.sub(pattern, replace_growth, desc)

    # 第二步：把剩余的当作数学括号用的 '{' 和 '}' 替换为标准的 '(' 和 ')'
    desc_main = desc_main.replace("{", "(").replace("}", ")")
    desc_growth = desc_growth.replace("{", "(").replace("}", ")")

    # 第三步：使用 eval 计算数学表达式的值，并转换为 int
    # 提示: 如果除法产生浮点精度问题（例如249.999），用 round() 四舍五入后再转 int 会更稳妥
    try:
        main_val = int(round(eval(desc_main)))
        growth_val = int(round(eval(desc_growth)))
        print([main_val, growth_val])
        return [main_val, growth_val]
    except Exception as e:
        print(f"解析计算出错: {e}")
        return [0, 0]


def process_json(json_data: dict):
    result = {}
    for item in json_data:
        name = item["name"]
        param_entries = item["param"]
        processed_params = {}
        for param_entry in param_entries:
            param_name = param_entry["name"]
            desc = param_entry.get("desc", "")
            param_dict = param_entry.get("param", {})
            main_growth = parse_desc(desc, param_dict)
            processed_params[param_name] = main_growth
        result[name] = processed_params
    return result


async def get_new_char():
    all_char_data = await get_hakush_all_char_data()
    partner_data = {}
    skill_data = {}

    if all_char_data:
        for char in all_char_data:
            print(char)
            char_data = await fetch_detail(ZZZ_CHARACTER.format(char))
            if char_data:
                skill_data[char] = {}

                char_name = strip_test_prefix(str(char_data["name"]))
                if "partner_info" in char_data and "full_name" in char_data["partner_info"]:
                    full_name = str(char_data["partner_info"]["full_name"])
                else:
                    full_name = char_name
                if full_name in ("", "..."):
                    full_name = FULL_NAME_OVERRIDE.get(char, char_name)
                partner_data[char] = {
                    "sprite_id": char_data["icon"].replace("IconRole", ""),
                    "name": char_name,
                    "full_name": full_name,
                    "en_name": strip_test_prefix(str(char_data["code_name"])),
                }

                for skill in char_data["skill"]:
                    for k in char_data["skill"][skill]["description"]:
                        if "param" in k:
                            skill_name = strip_test_prefix(str(k["name"]))
                            if "招架支援" in skill_name:
                                continue

                            skill_data[char][skill_name] = {}

                            for param in k["param"]:
                                if "param" not in param:
                                    continue

                                skill_sub = strip_test_prefix(str(param["name"]))
                                if "失衡" in skill_sub:
                                    continue

                                if "Prop:1001" not in param["desc"]:
                                    print(char, param["desc"])

                                klist = list(param["param"].values())
                                if len(klist) > 1:
                                    print(
                                        "超过1",
                                        char,
                                        skill_name,
                                        param["desc"],
                                    )

                                skill_data[char][skill_name][skill_sub] = parse_desc(
                                    param["desc"],
                                    param["param"],
                                )

                partner_data[char].update(
                    {
                        "weapon_type": "",
                        "element_type": "",
                        "camp": "",
                        "hit_type": "",
                        "rarity": "",
                    }
                )

                stats = [
                    "Attack",
                    "AttackGrowth",
                    "BreakStun",
                    "Defence",
                    "DefenceGrowth",
                    "HpMax",
                    "HpGrowth",
                    "Crit",
                    "CritDamage",
                    "ElementAbnormalPower",
                    "ElementMystery",
                    "PenDelta",
                    "PenRate",
                    "SpRecover",
                ]

                partner_data[char].update({k: 0 for k in stats})

                if char not in ["2011", "2021"]:
                    partner_data[char].update(
                        {
                            "weapon_type": list(char_data["weapon_type"].keys())[0],
                            "element_type": list(char_data["element_type"].keys())[0],
                            "camp": list(char_data["camp"].values())[0],
                            "hit_type": list(char_data["hit_type"].values())[0],
                            "rarity": {4: "S", 3: "A"}.get(char_data["rarity"], "A"),
                        }
                    )

                    for k in char_data["stats"]:
                        if k in stats:
                            partner_data[char][k] = char_data["stats"][k]

                    partner_data[char]["level"] = char_data["level"]
                    partner_data[char]["extra_level"] = char_data["extra_level"]

            await asyncio.sleep(3)

        with open(
            MAP_PATH / PartnerId2SkillParamFile,
            "w",
            encoding="UTF-8",
        ) as f:
            json.dump(skill_data, f, indent=4, ensure_ascii=False)

        with open(
            MAP_PATH / PartnerId2DataFile,
            "w",
            encoding="UTF-8",
        ) as f:
            json.dump(partner_data, f, indent=4, ensure_ascii=False)


async def get_new_weapon():
    all_weapon_data = await get_hakush_all_weapon_data()
    if all_weapon_data:
        weapon_result = {}
        for weapon in all_weapon_data:
            print(weapon)
            weapon_data = await fetch_detail(ZZZ_WEAPON.format(weapon))
            if weapon_data:
                weapon_result[weapon] = {
                    "code_name": strip_test_prefix(str(weapon_data["code_name"])),
                    "name": strip_test_prefix(str(weapon_data["name"])),
                    "talents": strip_test_prefix_deep(weapon_data["talents"]),
                    "rarity": "S" if weapon_data["rarity"] == 4 else "A",
                    "props_name": weapon_data["base_property"]["name"],
                    "props_id": PROP_NAME_TO_ID[weapon_data["base_property"]["name2"]],
                    "props_value": weapon_data["base_property"]["value"],
                    "rand_props_name": weapon_data["rand_property"]["name"],
                    "rand_props_id": PROP_NAME_TO_ID[weapon_data["rand_property"]["name2"]],
                    "rand_props_value": weapon_data["rand_property"]["value"],
                    "level": weapon_data["level"],
                    "stars": weapon_data["stars"],
                }
        with open(MAP_PATH / WeaponId2DataFile, "w", encoding="UTF-8") as f:
            json.dump(weapon_result, f, indent=4, ensure_ascii=False)


async def get_new_equipment():
    all_equipment_data = await get_hakush_all_equipment()
    if all_equipment_data:
        equipment2sprite_data = {}

        for equipment in all_equipment_data:
            print(equipment)
            name = all_equipment_data[equipment]["icon"].split("/")[-1].split(".")[0]
            equipment2sprite_data[equipment] = {
                "equip_id_list": [],
                "sprite_file": f"3D{name}",
                "equip_name": all_equipment_data[equipment]["zh"]["name"],
                "desc1": all_equipment_data[equipment]["zh"]["desc2"],
                "desc2": all_equipment_data[equipment]["zh"]["desc4"],
            }
            for i in list(range(21, 27)) + list(range(31, 37)) + list(range(41, 47)):
                equipment2sprite_data[equipment]["equip_id_list"].append(int(equipment[:3] + str(i)))
        with open(MAP_PATH / EquipId2DataFile, "w", encoding="UTF-8") as f:
            json.dump(equipment2sprite_data, f, indent=4, ensure_ascii=False)


async def get_new():
    # 先清缓存：磁盘里的 nanoka 详情快照可能是角色上线前的 beta 数据
    clear_stale_cache()
    await get_new_char()
    await get_new_weapon()
    await get_new_equipment()
    # 新 map 写成功后再删旧版本
    remove_old_map_files()


asyncio.run(get_new())
