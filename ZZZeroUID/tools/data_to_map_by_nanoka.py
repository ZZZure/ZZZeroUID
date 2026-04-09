import re
import sys
import json
import asyncio
from pathlib import Path

MAP_PATH = Path(__file__).parents[1] / "utils" / "map"

sys.path.append(str(Path(__file__).parents[5]))
sys.path.append(str(Path(__file__).parents[2]))
__package__ = "ZZZeroUID.tools"

from ZZZeroUID.tools.data_to_map import (  # noqa: E402
    EquipId2DataFile,
    WeaponId2DataFile,
    PartnerId2DataFile,
    PartnerId2SkillParamFile,
)
from ZZZeroUID.utils.hakush_api.request import (  # noqa: E402
    get_hakush_char_data,
    get_hakush_weapon_data,
    get_hakush_all_char_data,
    get_hakush_all_equipment,
    get_hakush_all_weapon_data,
)

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
            for _ in range(5):
                try:
                    char_data = await get_hakush_char_data(char)
                    break
                except Exception as e:
                    print(e)
                    await asyncio.sleep(30)
                    continue
            if char_data:
                skill_data[char] = {}

                if "partner_info" in char_data and "full_name" in char_data["partner_info"]:
                    full_name = char_data["partner_info"]["full_name"]
                else:
                    full_name = char_data["name"]
                partner_data[char] = {
                    "sprite_id": char_data["icon"].replace("IconRole", ""),
                    "name": char_data["name"],
                    "full_name": full_name,
                    "en_name": char_data["code_name"],
                }

                for skill in char_data["skill"]:
                    for k in char_data["skill"][skill]["description"]:
                        if "param" in k:
                            skill_name = k["name"]
                            if "招架支援" in skill_name:
                                continue

                            skill_data[char][skill_name] = {}

                            for param in k["param"]:
                                if "param" not in param:
                                    continue

                                skill_sub = param["name"]
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
            for _ in range(5):
                try:
                    weapon_data = await get_hakush_weapon_data(weapon)
                    break
                except Exception as e:
                    print(e)
                    await asyncio.sleep(30)
                    continue
            if weapon_data:
                weapon_result[weapon] = {
                    "code_name": weapon_data["code_name"],
                    "name": weapon_data["name"],
                    "talents": weapon_data["talents"],
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
    await get_new_char()
    # await get_new_weapon()
    # await get_new_equipment()


asyncio.run(get_new())
