from typing import Dict, Tuple

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
