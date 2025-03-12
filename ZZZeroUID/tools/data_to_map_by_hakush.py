import re
import sys
import json
import asyncio
from pathlib import Path

MAP_PATH = Path(__file__).parents[1] / 'utils' / 'map'

sys.path.append(str(Path(__file__).parents[5]))
sys.path.append(str(Path(__file__).parents[2]))
__package__ = 'ZZZeroUID.tools'

from ZZZeroUID.tools.data_to_map import (  # noqa: E402
    PartnerId2DataFile,
    WeaponId2SpriteFile,
    PartnerId2SkillParamFile,
)
from ZZZeroUID.utils.hakush_api.request import (  # noqa: E402
    get_hakush_char_data,
    get_hakush_weapon_data,
    get_hakush_all_char_data,
    get_hakush_all_weapon_data,
)


def parse_desc(desc, param_dict):
    # 替换Skill引用为Main的值并移除所有大括号
    main_expr = re.sub(
        r'\{Skill:(\d+)[^\}]*\}',
        lambda m: str(param_dict.get(m.group(1), {}).get('Main', 0)),
        desc,
    )
    main_expr = re.sub(r'[{}]', '', main_expr)  # 新增行：移除所有大括号

    # 替换Skill引用为Growth的值并移除所有大括号
    growth_expr = re.sub(
        r'\{Skill:(\d+)[^\}]*\}',
        lambda m: str(param_dict.get(m.group(1), {}).get('Growth', 0)),
        desc,
    )
    growth_expr = re.sub(r'[{}]', '', growth_expr)  # 新增行：移除所有大括号

    try:
        main_value = eval(main_expr)
    except:  # noqa: E722
        main_value = 0
    try:
        growth_value = eval(growth_expr)
    except:  # noqa: E722
        growth_value = 0
    return [int(main_value), int(growth_value)]  # 保证输出为整数


def process_json(json_data: dict):
    result = {}
    for item in json_data:
        name = item['Name']
        param_entries = item['Param']
        processed_params = {}
        for param_entry in param_entries:
            param_name = param_entry['Name']
            desc = param_entry.get('Desc', '')
            param_dict = param_entry.get('Param', {})
            main_growth = parse_desc(desc, param_dict)
            processed_params[param_name] = main_growth
        result[name] = processed_params
    return result


async def get_new_char():
    all_char_data = await get_hakush_all_char_data()
    partner_data = {}
    skill_data = {}
    if all_char_data:
        for char in all_char_data:
            print(char)
            for _ in range(5):
                try:
                    char_data = await get_hakush_char_data(char)
                    break
                except Exception as e:
                    print(e)
                    await asyncio.sleep(30)
                    continue
            if char_data:
                skill_data[char] = {}

                if (
                    'PartnerInfo' in char_data
                    and 'FullName' in char_data['PartnerInfo']
                ):
                    full_name = char_data['PartnerInfo']['FullName']
                else:
                    full_name = char_data['Name']
                partner_data[char] = {
                    'sprite_id': char_data['Icon'].replace('IconRole', ''),
                    'name': char_data['Name'],
                    'full_name': full_name,
                    'en_name': char_data['CodeName'],
                }

                for skill in char_data['Skill']:
                    for k in char_data['Skill'][skill]['Description']:
                        if 'Param' in k:
                            skill_name = k['Name']
                            if '招架支援' in skill_name:
                                continue

                            skill_data[char][skill_name] = {}

                            for param in k['Param']:
                                if 'Param' not in param:
                                    continue

                                skill_sub = param['Name']
                                if '失衡' in skill_sub:
                                    continue

                                if 'Prop:1001' not in param['Desc']:
                                    print(char, param['Desc'])

                                klist = list(param['Param'].values())
                                if len(klist) > 1:
                                    print(
                                        '超过1',
                                        char,
                                        skill_name,
                                        param['Desc'],
                                    )

                                skill_data[char][skill_name][skill_sub] = (
                                    parse_desc(
                                        param['Desc'],
                                        param['Param'],
                                    )
                                )

            await asyncio.sleep(3)

        with open(
            MAP_PATH / PartnerId2SkillParamFile,
            'w',
            encoding='UTF-8',
        ) as f:
            json.dump(skill_data, f, indent=4, ensure_ascii=False)

        with open(
            MAP_PATH / PartnerId2DataFile,
            'w',
            encoding='UTF-8',
        ) as f:
            json.dump(partner_data, f, indent=4, ensure_ascii=False)


async def get_new_weapon():
    all_weapon_data = await get_hakush_all_weapon_data()
    if all_weapon_data:
        weapon2sprite_data = {}
        for weapon in all_weapon_data:
            print(weapon)
            for _ in range(5):
                try:
                    weapon_data = await get_hakush_weapon_data(weapon)
                    break
                except Exception as e:
                    print(e)
                    await asyncio.sleep(30)
                    continue
            if weapon_data:
                weapon2sprite_data[weapon] = weapon_data['CodeName']
        with open(MAP_PATH / WeaponId2SpriteFile, 'w', encoding='UTF-8') as f:
            json.dump(weapon2sprite_data, f, indent=4, ensure_ascii=False)


async def get_new():
    await get_new_char()
    await get_new_weapon()


asyncio.run(get_new())
