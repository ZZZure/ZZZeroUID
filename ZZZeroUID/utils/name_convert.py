from pathlib import Path
from typing import Dict, List

from msgspec import json as msgjson

ALIAS_LIST = Path(__file__).parent / 'alias'
CHAR_ALIAS = ALIAS_LIST / 'char_alias.json'


with open(CHAR_ALIAS, 'r', encoding='UTF-8') as f:
    char_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])


def alias_to_char_name(char_name: str) -> str:
    for i in char_alias_data:
        if (char_name in i) or (char_name in char_alias_data[i]):
            return i
    return char_name
