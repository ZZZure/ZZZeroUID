from ...version import NANOKA_DATA_VERSION

HAKUSH_BASE = f"https://static.nanoka.cc/zzz/{NANOKA_DATA_VERSION}"
HAKUSH_API = f"{HAKUSH_BASE}/zh"

ZZZ_CHARACTER = HAKUSH_API + "/character/{}.json"
ZZZ_WEAPON = HAKUSH_API + "/weapon/{}.json"

ZZZ_NEW = f"{HAKUSH_BASE}/new.json"
ZZZ_ALL_CHAR = f"{HAKUSH_BASE}/character.json"
ZZZ_ALL_WEAPON = f"{HAKUSH_BASE}/weapon.json"
ZZZ_ALL_EQUIP = f"{HAKUSH_BASE}/equipment.json"
