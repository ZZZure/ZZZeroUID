import json
from pathlib import Path
from typing import Dict, List

from ..version import ZZZero_version

MAP_PATH = Path(__file__).parent / 'map'

PartnerId2SkillParamFile = f'PartnerId2SkillParam_{ZZZero_version}.json'

with open(MAP_PATH / PartnerId2SkillParamFile, 'r', encoding='utf-8') as f:
    skill_param: Dict[str, Dict[str, Dict[str, List[int]]]] = json.load(f)
