import math
from typing import Dict, List, Union
from datetime import datetime

from gsuid_core.logger import logger

from .zzz_map import equip_effect
from .name_convert import equip_data, weapon_data, partener_data
from ..utils.api.models import ZZZAvatarInfo

ID_TO_PROP_NAME = {
    "11101": "生命值",
    "11103": "生命值",
    "11102": "生命值",
    "12101": "攻击力",
    "12103": "攻击力",
    "12102": "攻击力",
    "13101": "防御力",
    "13103": "防御力",
    "13102": "防御力",
    "12202": "冲击力",
    "12201": "冲击力",
    "12203": "冲击力",
    "20103": "暴击率",
    "21103": "暴击伤害",
    "31401": "异常掌控",
    "31402": "异常掌控",
    "31403": "异常掌控",
    "31201": "异常精通",
    "31202": "异常精通",
    "31203": "异常精通",
    "23103": "穿透率",
    "23203": "穿透值",
    "30501": "能量自动回复",
    "30503": "能量自动回复",
    "30502": "能量回复百分比",
    "315": "伤害加成",
    "31503": "物理伤害加成",
    "31603": "火属性伤害加成",
    "31703": "冰属性伤害加成",
    "31803": "雷属性伤害加成",
    "31903": "以太属性伤害加成",
}

ID_TO_EN = {
    "11101": "HpMax",
    "11103": "HpBase",
    "11102": "HpAdd",
    "12101": "Attack",
    "12103": "AttackBase",
    "12102": "AttackAdd",
    "13101": "Defence",
    "13103": "DefenceBase",
    "13102": "DefenceAdd",
    "12202": "BreakStunAdd",
    "12201": "BreakStunBase",
    "12203": "BreakStunAdd",
    "20103": "Crit",
    "21103": "CritDmg",
    "31401": "ElementAbnormalPowerBase",
    "31402": "ElementAbnormalPowerAdd",
    "31403": "ElementAbnormalPower",
    "31201": "ElementMysteryBase",
    "31202": "ElementMysteryAdd",
    "31203": "ElementMystery",
    "23103": "PenRate",
    "23203": "PenDelta",
    "30501": "SpRecoverBase",
    "30503": "SpRecover",
    "30502": "SpRecoverAdd",
    "31503": "PhysDmgBonus",
    "31603": "FireDmgBonus",
    "31703": "IceDmgBonus",
    "31803": "ThunderDmgBonus",
    "31903": "EtherDmgBonus",
}
ELEMENT_TO_EN = {
    "203": "Thunder",
    "205": "Ether",
    "202": "Ice",
    "200": "Phys",
    "201": "Fire",
}
EN_TO_ZH = {ID_TO_EN[k]: ID_TO_PROP_NAME[k] for k in ID_TO_EN}
EN_TO_ID = {ID_TO_EN[k]: k for k in ID_TO_EN}
PERCENT_ID = [
    "11102",
    "12102",
    "13102",
    "12202",
    "20103",
    "21103",
    "23103",
    "31603",
    "12203",
    "31703",
    "31803",
    "31903",
]

PERCENT_NAME = [
    "Crit",
    "CritDmg",
    "PenRate",
    "PhysDmgBonus",
    "FireDmgBonus",
    "IceDmgBonus",
    "ThunderDmgBonus",
    "EtherDmgBonus",
    "SpRecover",
]
MAIN_PROP_VALUE = {
    "11101": 330,
    "11103": 330,
    "11102": 330,
    "12101": 47.4,
    "12103": 47.4,
    "12102": 450,
    "12202": 270,
    "13101": 27.6,
    "13103": 27.6,
    "13102": 720,
    "12203": 270,
    "20103": 360,
    "21103": 720,
    "31402": 450,
    "31403": 450,
    "31202": 13,
    "31203": 13,
    "23103": 360,
    "23203": 36,
    "30503": 900,
    "30502": 900,
    "315": 450,
    "31503": 450,
    "31603": 450,
    "31703": 450,
    "31803": 450,
    "31903": 450,
}

MYS_NAME_TO_ID = {
    "生命值": "1",
    "攻击力": "2",
    "防御力": "3",
    "冲击力": "4",
    "暴击率": "5",
    "暴击伤害": "6",
    "异常掌控": "7",
    "异常精通": "8",
    "穿透率": "9",
    "穿透值": "10",
    "能量自动回复": "11",
    "能量回复百分比": "12",
    "贯穿力": "19",
    "闪能自动累积": "20",
    "以太伤害加成": "319",
    "雷属性伤害加成": "318",
    "冰属性伤害加成": "317",
    "火属性伤害加成": "316",
    "物理伤害加成": "315",
}

"""
A 普攻
B 特殊
C 强化特殊
X 冲刺攻击
S 闪避反击
W 连携技
Q 终结技
P 快速支援
E 支援突击
"""


def _determine_char_star_tier(level: int):
    if level >= 50:
        return "6"
    elif level >= 40:
        return "5"
    elif level >= 30:
        return "4"
    elif level >= 20:
        return "3"
    elif level >= 10:
        return "2"
    else:
        return "1"


def _determine_weapon_star_tier(level):
    if level >= 50:
        return "5"
    elif level >= 40:
        return "4"
    elif level >= 30:
        return "3"
    elif level >= 20:
        return "2"
    elif level >= 10:
        return "1"
    else:
        return "0"


def render_weapon_detail(weapon: Dict, current_level: int, star_tier: str):
    # 基础属性计算
    base_value = weapon["props_value"]
    base_value = (
        base_value
        + base_value * (weapon["level"][str(current_level)]["Rate"] + weapon["stars"][star_tier]["StarRate"]) / 10000
    )

    # 随机属性计算
    rand_value = weapon["rand_props_value"]
    if rand_value:
        rand_value = rand_value + rand_value * (weapon["stars"][star_tier]["RandRate"] / 10000)

    return int(base_value), int(rand_value) if rand_value else rand_value


def add_buff_props(props: Dict, buff_list: List[str]):
    for buff in buff_list:
        buff = buff.strip()
        if buff:
            buff_name, buff_value = buff.split("+")
            props[buff_name] += float(buff_value)
    return props


def get_normal_equip_buff(equip_suit_list: Dict, _type: str = "normal_effect"):
    buff_list = []
    for equip_suit_id, equip_suit_count in equip_suit_list.items():
        if equip_suit_count >= 2:
            equip_name: str = equip_data[equip_suit_id]["equip_name"]
            buff = equip_effect[equip_name][_type]["desc1"].split(";")
            buff_list.extend(buff)

        if equip_suit_count >= 4:
            equip_name = equip_data[equip_suit_id]["equip_name"]
            buff = equip_effect[equip_name][_type]["desc2"].split(";")
            buff_list.extend(buff)

    return buff_list


def _calculate_base_stat(
    base: float,
    growth: float,
    level_data: Dict,
    extra_level: Dict,
    level: int,
    act: Union[int, str],
    level_key: str,
    extra_key=None,
):
    base_value = base
    if level > 0:
        base_value += (level - 1) * growth / 10000

    act = str(act)

    if act in level_data and level_key in level_data[act]:
        base_value += level_data[act][level_key]

    if level > 10 and extra_key:
        base_value += extra_level[act]["Extra"].get(extra_key, {}).get("Value", 0)

    return math.floor(base_value)


def _get_value_str(value: float, prop_level: int, prop_id: str, is_main_r: bool = False):
    if is_main_r:
        value += MAIN_PROP_VALUE[str(prop_id)] * prop_level
    else:
        value = value * prop_level

    if str(prop_id) in PERCENT_ID:
        value_str = str(value / 100) + "%"
    else:
        value_str = str(value)
    return value_str


async def _enka_data_to_mys_data(enka_data: Dict) -> List[ZZZAvatarInfo]:
    uid = enka_data["uid"]
    result_list: List[ZZZAvatarInfo] = []
    for char in enka_data["PlayerInfo"]["ShowcaseDetail"]["AvatarList"]:
        result = {}
        char_id = str(char["Id"])
        logger.debug(char_id)
        _partener = partener_data[char_id]
        result["id"] = char["Id"]
        result["level"] = char["Level"]
        result["name_mi18n"] = _partener["name"]
        result["full_name_mi18n"] = _partener["full_name"]

        result["element_type"] = int(_partener["ElementType"])
        result["avatar_profession"] = int(_partener["WeaponType"])
        result["rarity"] = _partener["Rarity"]
        result["camp_name_mi18n"] = _partener["Camp"]

        # 基础属性
        props = {}
        for _prop in ID_TO_EN.values():
            if _prop == "CritDmg":
                props[_prop] = _partener["CritDamage"]
            elif _prop == "BreakStunBase":
                props[_prop] = _partener["BreakStun"]
            elif _prop == "BreakStun" or _prop == "BreakStunAdd":
                props[_prop] = 0
            elif _prop == "ElementAbnormalPowerBase":
                props[_prop] = _partener["ElementAbnormalPower"]
            elif _prop == "SpRecoverBase":
                props[_prop] = _partener["SpRecover"]
            elif _prop not in _partener:
                props[_prop] = 0
            else:
                props[_prop] = _partener[_prop]

            props[_prop] = _calculate_base_stat(
                props[_prop],
                {
                    "HpMax": _partener["HpGrowth"],
                    "Attack": _partener["AttackGrowth"],
                    "Defence": _partener["DefenceGrowth"],
                }.get(_prop, 0),
                _partener["Level"],
                _partener["ExtraLevel"],
                char["Level"],
                char["PromotionLevel"],
                _prop,
                EN_TO_ID.get(_prop, _prop),
            )
        logger.debug(props)
        # 圣遗物
        relics = []
        equip_suit_list = {}

        for relic in char["EquippedList"]:
            properties = []
            main_properties = []
            _equip = relic["Equipment"]
            suit_id = str(_equip["Id"])[:3] + "00"
            equip_meta = equip_data[suit_id]

            if suit_id not in equip_suit_list:
                equip_suit_list[suit_id] = 1
            else:
                equip_suit_list[suit_id] += 1

            equip_suit = {
                "suit_id": suit_id,
                "name": equip_meta["equip_name"],
                "own": "",
                "desc1": equip_meta["desc1"],
                "desc2": equip_meta["desc2"],
            }

            relic_level = _equip["Level"]
            for main_prop in _equip["MainPropertyList"]:
                value = main_prop["PropertyValue"] + MAIN_PROP_VALUE[str(main_prop["PropertyId"])] * (
                    main_prop["PropertyLevel"] * (relic_level // 3)
                )
                value_str = _get_value_str(
                    main_prop["PropertyValue"],
                    main_prop["PropertyLevel"] * (relic_level // 3),
                    main_prop["PropertyId"],
                    True,
                )
                props[ID_TO_EN[str(main_prop["PropertyId"])]] += value
                main_properties.append(
                    {
                        "property_name": ID_TO_PROP_NAME[str(main_prop["PropertyId"])],
                        "property_id": main_prop["PropertyId"],
                        "base": value_str,
                        "level": main_prop["PropertyLevel"],
                        "add": main_prop["PropertyLevel"] - 1,
                        "valid": False,
                        "system_id": 100,
                    }
                )

            for prop in _equip["RandomPropertyList"]:
                value = prop["PropertyValue"] * prop["PropertyLevel"]
                value_str = _get_value_str(
                    prop["PropertyValue"],
                    prop["PropertyLevel"],
                    prop["PropertyId"],
                )

                props[ID_TO_EN[str(prop["PropertyId"])]] += value
                properties.append(
                    {
                        "property_name": ID_TO_PROP_NAME[str(prop["PropertyId"])],
                        "property_id": prop["PropertyId"],
                        "base": value_str,
                        "level": prop["PropertyLevel"],
                        "add": prop["PropertyLevel"] - 1,
                        "valid": False,
                        "system_id": 100,
                    }
                )

            relics.append(
                {
                    "equipment_type": relic["Slot"],
                    "id": _equip["Id"],
                    "level": _equip["Level"],
                    "name": equip_meta["equip_name"] + f"{[relic['Slot']]}",
                    "rarity": "B",
                    "properties": properties,
                    "main_properties": main_properties,
                    "equip_suit": equip_suit,
                }
            )
        result["equip"] = relics
        # logger.debug(relics)

        # 武器
        weapon_id = str(char["Weapon"]["Id"])
        _weapon = weapon_data[weapon_id]

        weapon = {}
        weapon["id"] = char["Weapon"]["Id"]
        weapon["level"] = char["Weapon"]["Level"]
        # level_str = str(weapon['level'])
        weapon["star"] = char["Weapon"]["UpgradeLevel"]
        weapon["name"] = _weapon["name"]
        weapon["icon"] = ""
        weapon["rarity"] = _weapon["rarity"]
        base, rand = render_weapon_detail(
            _weapon,
            char["Weapon"]["Level"],
            str(
                char["Weapon"]["BreakLevel"],
            ),
        )
        if rand:
            weapon["properties"] = [
                {
                    "property_name": _weapon["rand_props_name"],
                    "property_id": _weapon["rand_props_id"],
                    "base": (f"{round(rand) / 100}%" if _weapon["rand_props_id"] in PERCENT_ID else str(rand)),
                }
            ]
        else:
            weapon["properties"] = []

        weapon["main_properties"] = [
            {
                "property_name": _weapon["props_name"],
                "property_id": _weapon["props_id"],
                "base": (f"{round(base) / 100}%" if _weapon["props_id"] in PERCENT_ID else str(base)),
            }
        ]
        weapon["talent_title"] = _weapon["talents"][str(weapon["star"])]["Name"]
        weapon["talent_content"] = _weapon["talents"][str(weapon["star"])]["Desc"]
        props[ID_TO_EN[_weapon["props_id"]]] += base
        props[ID_TO_EN[_weapon["rand_props_id"]]] += rand

        result["weapon"] = weapon

        # 添加驱动盘特效
        buffs = get_normal_equip_buff(equip_suit_list)
        props = add_buff_props(props, buffs)
        logger.debug(props)

        props["HpMax"] += props["HpBase"] + (props["HpAdd"] / 10000) * props["HpMax"]
        props["Attack"] += props["AttackBase"] + (props["AttackAdd"] / 10000) * props["Attack"]
        props["Defence"] += props["DefenceBase"] + (props["DefenceAdd"] / 10000) * props["Defence"]
        props["BreakStun"] = props["BreakStunBase"] + (props["BreakStunAdd"] / 10000 * props["BreakStunBase"])
        props["ElementAbnormalPower"] = props["ElementAbnormalPowerBase"] + (
            props["ElementAbnormalPowerAdd"] / 10000 * props["ElementAbnormalPowerBase"]
        )
        props["ElementMystery"] = (
            props["ElementMysteryBase"]
            + props["ElementMystery"]
            + (props["ElementMysteryAdd"] / 10000 * props["ElementMysteryBase"])
        )
        props["SpRecover"] = props["SpRecoverBase"] + (props["SpRecoverAdd"] / 10000 * props["SpRecoverBase"])

        del props["HpBase"]
        del props["HpAdd"]
        del props["AttackBase"]
        del props["AttackAdd"]
        del props["DefenceBase"]
        del props["DefenceAdd"]
        del props["BreakStunBase"]
        del props["BreakStunAdd"]
        del props["ElementAbnormalPowerBase"]
        del props["ElementAbnormalPowerAdd"]
        del props["ElementMysteryBase"]
        del props["ElementMysteryAdd"]
        del props["SpRecoverBase"]
        del props["SpRecoverAdd"]

        char_element = ELEMENT_TO_EN[_partener["ElementType"]]
        for i in ELEMENT_TO_EN.values():
            if i != char_element:
                del props[f"{i}DmgBonus"]

        logger.debug(props)
        properties = []

        atk = 0
        hp = 0

        for p in props:
            if p == "BreakStun":
                pid = 4
                property_name = "冲击力"
            else:
                pid = int(MYS_NAME_TO_ID.get(EN_TO_ZH[p], 0))
                property_name = EN_TO_ZH[p]

            if pid == 2:
                atk += props[p]
            elif pid == 1:
                hp += props[p]

            properties.append(
                {
                    "property_name": property_name,
                    "property_id": pid,
                    "base": "",
                    "add": "",
                    "final": (f"{props[p] / 100:.1f}%" if str(p) in PERCENT_NAME else f"{props[p]:.1f}"),
                }
            )

        if result["avatar_profession"] == 6:
            final = 0.3 * atk
            if str(result["id"]) == "1371":
                final += 0.1 * hp

            # 保留一位小数并转为str
            final = f"{final:.1f}"

            properties.append(
                {
                    "property_name": "贯穿力",
                    "property_id": 19,
                    "base": "",
                    "add": "",
                    "final": final,
                }
            )

            # 然后删除properties中property_id为9或者10的项
            properties = [p for p in properties if p["property_id"] not in [9, 10]]

        result["properties"] = properties

        # 技能
        skills = []
        for skill in char["SkillLevelList"]:
            skills.append(
                {
                    "level": skill["Level"],
                    "skill_type": skill["Index"],
                    "items": [],
                }
            )
        result["skills"] = skills

        # 命座
        result["rank"] = char["TalentLevel"]

        # 其他信息
        result["uid"] = uid
        timestamp = char["ObtainmentTimestamp"]
        result["current_time"] = datetime.fromtimestamp(timestamp)

        result_list.append(result)  # type: ignore

    return result_list
