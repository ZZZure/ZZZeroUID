from typing import Any, Dict, List, Tuple, Optional

# 雅 & 浅羽版本
CUSTOM_OFFSET = {
    "1091": (-767, -128),
    "1201": (-253, -8),
    "1251": (-791, -126),
    "1241": (-374, -127),
    "1261": (-747, -124),
    "1171": (-390, -125),
    "1161": (-472, -122),
    "1321": (-472, -122),
}

# 雅 & 浅羽版本
CUSTOM_LEFT = [
    "1131",
    "1141",
    "1181",
    "1191",
    "1261",
    "1241",
    "1161",
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
INVALID_GREY = (170, 170, 170)

# 官方 equip_rating -> 面板评级字母
EQUIP_RATING_MAP = {
    "ER_S+": "S+",
    "ER_S_PLUS": "S+",
    "ER_SP": "S+",
    "ER_S": "S",
    "ER_A": "A",
    "ER_B": "B",
    "ER_C": "C",
}


def map_equip_rating(equip_rating: str) -> str:
    """将官方 equip_rating (如 ER_S) 映射为 S/A/B/S+。"""
    if not equip_rating:
        return ""
    raw = str(equip_rating).strip().upper()
    if raw in EQUIP_RATING_MAP:
        return EQUIP_RATING_MAP[raw]
    if raw.startswith("ER_"):
        tail = raw[3:].replace("_PLUS", "+").replace("PLUS", "+")
        if tail in ("S", "A", "B", "C", "S+"):
            return tail
        return tail
    if raw in ("S", "A", "B", "C", "S+"):
        return raw
    return raw


def get_equip_plan_info(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    plan = data.get("equip_plan_info")
    if isinstance(plan, dict) and plan:
        return plan
    return None


def get_effective_display_names(plan: Optional[Dict[str, Any]]) -> List[str]:
    """有效副属性展示名（优先 full_name）。"""
    if not plan:
        return []
    names: List[str] = []
    for item in plan.get("plan_effective_property_list") or []:
        name = item.get("full_name") or item.get("name") or ""
        if name and name not in names:
            names.append(name)
    return names


def calc_equip_valid_hit(equip: Dict[str, Any]) -> int:
    """单盘有效副属性命中次数 = sum(level of valid props)。"""
    total = 0
    for prop in equip.get("properties") or []:
        if prop.get("valid"):
            total += int(prop.get("level") or 0)
    return total


def get_skill_dict(data: Dict):
    skills = data["skills"]
    result: Dict[int, Tuple[int, Tuple[int, int, int]]] = {}

    for skill in skills:
        skill_type = skill["skill_type"]
        skill_pos_num = SKILL_MAP.get(skill_type, 0)
        skill_level = skill["level"]
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
