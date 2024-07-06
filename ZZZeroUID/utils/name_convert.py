from pathlib import Path
from typing import Dict, List, Optional

from msgspec import json as msgjson

from ..tools.data_to_map import PartnerId2DataFile, WeaponId2SpriteFile

ALIAS_LIST = Path(__file__).parent / 'alias'
CHAR_ALIAS = ALIAS_LIST / 'char_alias.json'


with open(CHAR_ALIAS, 'r', encoding='UTF-8') as f:
    char_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

with open(PartnerId2DataFile, 'r', encoding='UTF-8') as f:
    partener_data = msgjson.decode(f.read(), type=Dict[str, Dict[str, str]])

with open(WeaponId2SpriteFile, 'r', encoding='UTF-8') as f:
    weapon_data = msgjson.decode(f.read(), type=Dict[str, str])


def alias_to_char_name(char_name: str) -> str:
    for i in char_alias_data:
        if (char_name in i) or (char_name in char_alias_data[i]):
            return i
    return char_name


def char_id_to_char_name(char_id: str) -> Optional[str]:
    if char_id in partener_data:
        return partener_data[char_id]['name']
    else:
        return None


def char_name_to_char_id(char_name: str) -> Optional[str]:
    char_name = alias_to_char_name(char_name)
    for i in partener_data:
        chars = partener_data[i]
        if char_name == chars['name']:
            return i
    else:
        return None
