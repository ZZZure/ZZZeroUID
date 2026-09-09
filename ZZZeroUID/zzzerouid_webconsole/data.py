"""扫描 PLAYER_PATH 下的抽卡 JSON / 角色面板 JSON。"""

from __future__ import annotations

import re
import json
from typing import TypedDict
from pathlib import Path

from ..utils.name_convert import char_id_to_char_name, char_id_to_full_name
from ..zzzerouid_gachalog.get_gachalogs import GACHA_NUM_MAP, OPTIONAL_GACHA_NAMES

_UID_RE = re.compile(r"^\d{8,10}$")
_CHAR_FILE_RE = re.compile(r"^\d{4,8}\.json$")
_S_RANK = "4"

POOL_ORDER = [
    "独家频段",
    "独家重映",
    "音擎频段",
    "音擎回响",
    "常驻频段",
    "邦布频段",
]


class PlayerRow(TypedDict):
    uid: str
    has_gacha: bool
    gacha_total: int
    gacha_time: str
    char_count: int


class GachaRecord(TypedDict):
    id: str
    name: str
    item_id: str
    item_type: str
    rank_type: str
    time: str
    gacha_type: str


class GachaPool(TypedDict):
    name: str
    total: int
    s_count: int
    remain: int
    records: list[GachaRecord]


class CharacterRow(TypedDict):
    id: str
    name: str
    full_name: str
    rarity: str
    rank: int
    level: int
    element_type: int
    weapon_name: str
    weapon_rarity: str
    weapon_level: int


def is_zzz_uid(uid: str) -> bool:
    return bool(_UID_RE.match(uid))


def _as_dict(raw: object) -> dict[str, object] | None:
    if not isinstance(raw, dict):
        return None
    out: dict[str, object] = {}
    for key, value in raw.items():
        if isinstance(key, str):
            out[key] = value
    return out


def read_json_file(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _as_dict(raw)


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return default


def _as_str(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def list_player_uids(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    uids: list[str] = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and is_zzz_uid(child.name):
            uids.append(child.name)
    return uids


def count_characters(uid_dir: Path) -> int:
    n = 0
    for child in uid_dir.iterdir():
        if child.is_file() and _CHAR_FILE_RE.match(child.name):
            n += 1
    return n


def gacha_total_from_payload(payload: dict[str, object]) -> int:
    total = 0
    for _name, key in GACHA_NUM_MAP.items():
        if key in payload:
            total += _as_int(payload[key])
    if total > 0:
        return total
    data = payload["data"] if "data" in payload else None
    if not isinstance(data, dict):
        return 0
    for items in data.values():
        if isinstance(items, list):
            total += len(items)
    return total


def summarize_players(root: Path) -> list[PlayerRow]:
    rows: list[PlayerRow] = []
    for uid in list_player_uids(root):
        uid_dir = root / uid
        gacha_path = uid_dir / "gacha_logs.json"
        payload = read_json_file(gacha_path)
        has_gacha = payload is not None
        gacha_total = gacha_total_from_payload(payload) if payload else 0
        gacha_time = _as_str(payload["data_time"]) if payload and "data_time" in payload else ""
        rows.append(
            {
                "uid": uid,
                "has_gacha": has_gacha,
                "gacha_total": gacha_total,
                "gacha_time": gacha_time,
                "char_count": count_characters(uid_dir),
            }
        )
    return rows


def _record_from_item(item: object, pool_name: str) -> GachaRecord | None:
    data = _as_dict(item)
    if data is None:
        return None
    return {
        "id": _as_str(data["id"]) if "id" in data else "",
        "name": _as_str(data["name"]) if "name" in data else "",
        "item_id": _as_str(data["item_id"]) if "item_id" in data else "",
        "item_type": _as_str(data["item_type"]) if "item_type" in data else "",
        "rank_type": _as_str(data["rank_type"]) if "rank_type" in data else "",
        "time": _as_str(data["time"]) if "time" in data else "",
        "gacha_type": _as_str(data["gacha_type"]) if "gacha_type" in data else pool_name,
    }


def _pool_from_items(name: str, items: list[object], limit: int) -> GachaPool:
    records: list[GachaRecord] = []
    s_count = 0
    remain = 0
    seen_s = False
    for item in items:
        rec = _record_from_item(item, name)
        if rec is None:
            continue
        if rec["rank_type"] == _S_RANK:
            s_count += 1
            seen_s = True
        elif not seen_s:
            remain += 1
        if len(records) < limit:
            records.append(rec)
    return {
        "name": name,
        "total": len(items),
        "s_count": s_count,
        "remain": remain,
        "records": records,
    }


def load_gacha(root: Path, uid: str, pool: str | None, limit: int) -> dict[str, object] | None:
    payload = read_json_file(root / uid / "gacha_logs.json")
    if payload is None:
        return None
    raw_data = payload["data"] if "data" in payload else None
    pools: list[GachaPool] = []
    names = list(POOL_ORDER)
    if isinstance(raw_data, dict):
        for extra in raw_data:
            if isinstance(extra, str) and extra not in names:
                names.append(extra)
        for name in names:
            if pool and name != pool:
                continue
            if name not in raw_data:
                continue
            items = raw_data[name]
            if not isinstance(items, list):
                continue
            if name in OPTIONAL_GACHA_NAMES and len(items) == 0:
                continue
            pools.append(_pool_from_items(name, items, limit))
    return {
        "uid": uid,
        "data_time": _as_str(payload["data_time"]) if "data_time" in payload else "",
        "gacha_total": gacha_total_from_payload(payload),
        "pools": pools,
    }


def _weapon_fields(data: dict[str, object]) -> tuple[str, str, int]:
    weapon = data["weapon"] if "weapon" in data else None
    wdict = _as_dict(weapon)
    if wdict is None:
        return "", "", 0
    name = _as_str(wdict["name"]) if "name" in wdict else ""
    rarity = _as_str(wdict["rarity"]) if "rarity" in wdict else ""
    level = _as_int(wdict["level"]) if "level" in wdict else 0
    return name, rarity, level


def character_row_from_file(path: Path) -> CharacterRow | None:
    data = read_json_file(path)
    if data is None:
        return None
    char_id = _as_str(data["id"]) if "id" in data else path.stem
    name = char_id_to_char_name(char_id) or char_id
    full_name = char_id_to_full_name(char_id)
    weapon_name, weapon_rarity, weapon_level = _weapon_fields(data)
    return {
        "id": char_id,
        "name": name,
        "full_name": full_name,
        "rarity": _as_str(data["rarity"]) if "rarity" in data else "",
        "rank": _as_int(data["rank"]) if "rank" in data else 0,
        "level": _as_int(data["level"]) if "level" in data else 0,
        "element_type": _as_int(data["element_type"]) if "element_type" in data else 0,
        "weapon_name": weapon_name,
        "weapon_rarity": weapon_rarity,
        "weapon_level": weapon_level,
    }


def list_characters(root: Path, uid: str) -> list[CharacterRow]:
    uid_dir = root / uid
    if not uid_dir.is_dir():
        return []
    rows: list[CharacterRow] = []
    for child in sorted(uid_dir.iterdir()):
        if not child.is_file() or not _CHAR_FILE_RE.match(child.name):
            continue
        row = character_row_from_file(child)
        if row is not None:
            rows.append(row)
    rows.sort(key=lambda r: (0 if r["rarity"] == "S" else 1, -r["level"], r["name"]))
    return rows


def load_character_raw(root: Path, uid: str, char_id: str) -> dict[str, object] | None:
    path = root / uid / f"{char_id}.json"
    return read_json_file(path)


def delete_gacha(root: Path, uid: str) -> bool:
    path = root / uid / "gacha_logs.json"
    if not path.is_file():
        return False
    path.unlink()
    return True


def delete_character(root: Path, uid: str, char_id: str) -> bool:
    path = root / uid / f"{char_id}.json"
    if not path.is_file():
        return False
    path.unlink()
    return True
