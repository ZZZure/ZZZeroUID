import json
from pathlib import Path
from typing import Dict, List

from ..version import ZZZero_version

MAP_PATH = Path(__file__).parent / 'map'
EXTEND_PATH = Path(__file__).parent / 'extend_data'

PartnerId2SkillParamFile = f'PartnerId2SkillParam_{ZZZero_version}.json'

with open(MAP_PATH / PartnerId2SkillParamFile, 'r', encoding='utf-8') as f:
    skill_param: Dict[str, Dict[str, Dict[str, List[int]]]] = json.load(f)

with open(EXTEND_PATH / 'equip_effect.json', 'r', encoding='utf-8') as f:
    equip_effect: Dict[str, Dict[str, Dict[str, str]]] = json.load(f)

with open(EXTEND_PATH / 'weapon_effect.json', 'r', encoding='utf-8') as f:
    weapon_effect: Dict[str, Dict[str, Dict[str, str]]] = json.load(f)
