import json
from pathlib import Path
from typing import Dict, Tuple, Union

# 雅 & 浅羽版本
CUSTOM_OFFSET = {
    '1091': (-767, -128),
    '1201': (-253, -8),
    '1251': (-791, -126),
    '1241': (-374, -127),
    '1261': (-747, -124),
    '1171': (-390, -125),
    '1161': (-472, -122),
    '1321': (-472, -122),
}

# 雅 & 浅羽版本
CUSTOM_LEFT = [
    '1131',
    '1141',
    '1181',
    '1191',
    '1261',
    '1241',
    '1161',
]

SKILL_MAP = {
    0: 0,
    2: 1,
    6: 2,
    1: 3,
    3: 4,
    5: 5,
}
WEAPON_EQUIP_POS = {
    1: (69, 34),
    2: (-13, 202),
    3: (65, 362),
    4: (302, 368),
    5: (379, 200),
    6: (296, 34),
}
GREY = (210, 210, 210)
BLUE = (0, 151, 255)
YELLOW = (255, 188, 0)
SCORE_MAP = {
    "11103": 0.043,
    "11102": 1.6,
    "12103": 0.25,
    "12102": 1.6,
    "13103": 0.32,
    "13102": 1,
    "20103": 2,
    "21103": 1,
    "23203": 0.53,  # 穿透值
    "23103": 1.1,  # 穿透率
    "31203": 0.5,  # 异常精通
    "12203": 1,  # 冲击力
    "315": 0,
    "30503": 1.1,  # 能量自动回复
    "31403": 1.1,  # 异常掌控
}
PROP_NAME_TO_ID = {
    '生命值': '11103',
    '生命值百分比': '11102',
    '攻击力': '12103',
    '攻击力百分比': '12102',
    '防御力': '13103',
    '防御力百分比': '13102',
    '冲击力': '12203',
    '暴击率': '20103',
    '暴击伤害': '21103',
    '异常掌控': '31403',
    '异常精通': '31203',
    '穿透率': '23103',
    '穿透值': '23203',
    '能量自动回复': '30503',
}
ID_TO_PROP_NAME = {
    '11103': '生命值',
    '11102': '生命值百分比',
    '12103': '攻击力',
    '12102': '攻击力百分比',
    '13103': '防御力',
    '13102': '防御力百分比',
    '12203': '冲击力',
    '20103': '暴击率',
    '21103': '暴击伤害',
    '31403': '异常掌控',
    '31203': '异常精通',
    '23103': '穿透率',
    '23203': '穿透值',
    '30503': '能量自动回复',
    '315': '伤害加成',
}

PartenrScore_File = (
    Path(__file__).parents[1] / 'utils' / 'map' / 'PartnerScore.json'
)

with open(PartenrScore_File, 'r', encoding='utf-8') as f:
    PartnerScore_Dict: Dict[str, Dict[str, float]] = json.load(f)


def get_ep_value(
    char_id: Union[int, str],
    epid: Union[int, str],
    ep: str,
) -> float:
    partner_data = PartnerScore_Dict.get(str(char_id), {})
    ep_name = ID_TO_PROP_NAME[str(epid)]
    target = partner_data.get(str(ep_name), 0)
    _epid = int(str(epid)[:3])
    if '%' in ep:
        ep = ep[:-1]
    value = float(ep)
    if _epid >= 315:
        target_value = 5.83
    else:
        target_value = SCORE_MAP.get(str(epid), 0) * value
    return target_value * target


def get_skill_dict(data: Dict):
    skills = data['skills']
    result: Dict[int, Tuple[int, Tuple[int, int, int]]] = {}

    for skill in skills:
        skill_type = skill['skill_type']
        skill_pos_num = SKILL_MAP.get(skill_type, 0)
        skill_level = skill['level']
        if skill_level >= 11:
            skill_color = YELLOW
        elif skill_level >= 6:
            skill_color = BLUE
        elif skill_level >= 3:
            skill_color = (255, 255, 255)
        else:
            skill_color = GREY

        result[skill_pos_num] = skill_level, skill_color

    return result
