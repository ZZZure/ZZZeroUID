import sys
import json
from pathlib import Path

MAP_PATH = Path(__file__).parents[1] / "utils" / "map"
EXTEND_PATH = Path(__file__).parents[1] / "utils" / "extend_data"

sys.path.append(str(Path(__file__).parents[5]))
sys.path.append(str(Path(__file__).parents[2]))
__package__ = "ZZZeroUID.tools"

from ..utils.name_convert import equip_data, weapon_data  # noqa: E402

WEAPON_EFFECT = EXTEND_PATH / "weapon_effect.json"
EQUIP_EFFECT = EXTEND_PATH / "equip_effect.json"


def gen_weapon_data():
    result = {}

    for k in weapon_data:
        item = weapon_data[k]
        weapon_name = item["name"]
        result[weapon_name] = {
            "normal_effect": {
                "1": "",
                "2": "",
                "3": "",
                "4": "",
                "5": "",
            },
            "skill_effect": {
                "1": "",
                "2": "",
                "3": "",
                "4": "",
                "5": "",
            },
        }

    with open(WEAPON_EFFECT, "w", encoding="UTF-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


def gen_equip_data():
    result = {}
    for k in equip_data:
        item = equip_data[k]
        equip_name = item["equip_name"]
        result[equip_name] = {
            "normal_effect": {
                "desc1": item["desc1"],
                "desc2": item["desc2"],
            },
            "skill_effect": {
                "desc1": item["desc1"],
                "desc2": item["desc2"],
            },
        }

    with open(EQUIP_EFFECT, "w", encoding="UTF-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # gen_weapon_data()
    gen_equip_data()
