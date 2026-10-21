from typing import Dict, List, Tuple, FrozenSet

NORMAL_LIST = [
    "「11号」",
    "猫又",
    "莱卡恩",
    "丽娜",
    "格莉丝",
    "珂蕾妲",
    "拘缚者",
    "燃狱齿轮",
    "嵌合编译器",
    "钢铁肉垫",
    "硫磺石",
    "啜泣摇篮",
]


# (开始, 结束)：必须严格写成补零的 "YYYY-MM-DD HH:MM:SS"（如 09:00:00）
UpWindow = Tuple[str, str]
# 能被歪到的旧 UP：频段 -> 名字 -> 该频段内的各期 UP 时间段（含复刻）
# 上半卡池记录为9点开启避免受提前开服影响
OLD_UP_WINDOWS: Dict[str, Dict[str, List[UpWindow]]] = {
    "独家频段": {
        "朱鸢": [
            ("2024-07-24 12:00:00", "2024-08-13 14:59:59"),
            ("2025-04-02 12:00:00", "2025-04-22 14:59:59"),
        ],
        "凯撒": [
            ("2024-09-25 09:00:00", "2024-10-16 11:59:59"),
            ("2025-06-25 12:00:00", "2025-07-15 14:59:59"),
        ],
        "柳": [
            ("2024-11-06 09:00:00", "2024-11-27 11:59:59"),
            ("2025-08-06 12:00:00", "2025-09-03 14:59:59"),
        ],
    },
    "音擎频段": {
        "防暴者Ⅵ型": [
            ("2024-07-24 12:00:00", "2024-08-13 14:59:59"),
            ("2025-04-02 12:00:00", "2025-04-22 14:59:59"),
        ],
        "奔袭獠牙": [
            ("2024-09-25 09:00:00", "2024-10-16 11:59:59"),
            ("2025-06-25 12:00:00", "2025-07-15 14:59:59"),
        ],
        "时流贤者": [
            ("2024-11-06 09:00:00", "2024-11-27 11:59:59"),
            ("2025-08-06 12:00:00", "2025-09-03 14:59:59"),
        ],
    },
}

OLD_UP_NAMES: FrozenSet[str] = frozenset(name for pool in OLD_UP_WINDOWS.values() for name in pool)


def is_up_item(gacha_name: str, name: str, gacha_time: str) -> bool:
    if name in NORMAL_LIST:
        return False
    if name not in OLD_UP_NAMES:
        return True
    if gacha_name not in OLD_UP_WINDOWS or name not in OLD_UP_WINDOWS[gacha_name]:
        return False
    return any(start <= gacha_time <= end for start, end in OLD_UP_WINDOWS[gacha_name][name])
