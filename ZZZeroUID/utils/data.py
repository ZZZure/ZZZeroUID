import json
from typing import Union

import aiofiles

from .hakush_api.request import get_hakush_char_data
from ..utils.resource.RESOURCE_PATH import CHAR_DATA_PATH
from ..zzzerouid_char_detail.mono.Character import Character
from .hakush_api.models import (
    SkillParam,
    SkillValue,
    SkillDetail,
    CharacterData,
    SkillParamDesc,
)


async def get_hakush_char(_id: Union[str, int]):
    path = CHAR_DATA_PATH / f'{_id}.json'
    if not path.exists():
        raw_data = await get_hakush_char_data(_id)
        if raw_data:
            async with aiofiles.open(CHAR_DATA_PATH / f'{_id}.json', 'w') as f:
                await f.write(
                    json.dumps(
                        raw_data,
                        ensure_ascii=False,
                        indent=4,
                    )
                )
            return raw_data
    else:
        async with aiofiles.open(f'/{_id}.json', 'r') as f:
            data: CharacterData = json.loads(await f.read())
        return data


def get_skill_power(char_data: CharacterData, char: Character):
    result = {}
    skills = char_data['Skill']
    for skill_type in skills:
        skill: SkillDetail = skills[skill_type]
        skill_level = 8  # 暂定
        descs = skill['Description']
        for desc in descs:
            desc_name = desc['Name']
            if desc_name not in result:
                result[desc_name] = {}

            if 'Param' in desc:
                for sub in desc['Param']:
                    subParam: SkillParam = desc['Param'][sub]
                    param_name = subParam['Name']
                    param_desc: SkillParamDesc = json.loads(subParam['Desc'])
                    skill_param_id = str(param_desc['Skill'])
                    param: SkillValue = subParam['Param'][skill_param_id]
                    value = (
                        param['Main'] + param['Growth'] * skill_level
                    ) / 10000

                    result[desc_name][param_name] = value

    return result
