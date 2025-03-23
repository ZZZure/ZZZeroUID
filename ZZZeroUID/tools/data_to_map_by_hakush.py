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
    EquipId2DataFile,
    WeaponId2DataFile,
    PartnerId2DataFile,
    PartnerId2SkillParamFile,
)
from ZZZeroUID.utils.hakush_api.request import (  # noqa: E402
    get_hakush_char_data,
    get_hakush_weapon_data,
    get_hakush_all_char_data,
    get_hakush_all_equipment,
    get_hakush_all_weapon_data,
)

PROP_NAME_TO_ID = {
    '基础生命值': '11101',
    '生命值': '11103',
    '生命值百分比': '11102',
    '生命值上限': '11403',
    '基础攻击力': '12101',
    '攻击力': '12103',
    '攻击力百分比': '12102',
    '基础防御力': '13101',
    '防御力': '13103',
    '防御力百分比': '13102',
    '冲击力': '12203',
    '暴击率': '20103',
    '暴击伤害': '21103',
    '异常掌控': '31403',
    '异常精通': '31203',
    '穿透率': '23103',
    '穿透值': '23203',
    '能量自动回复': '30502',
}


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

                partner_data[char].update(
                    {
                        'WeaponType': '',
                        'ElementType': '',
                        'Camp': '',
                        'HitType': '',
                        'Rarity': '',
                    }
                )

                stats = [
                    'Attack',
                    'AttackGrowth',
                    'BreakStun',
                    'Defence',
                    'DefenceGrowth',
                    'HpMax',
                    'HpGrowth',
                    'Crit',
                    'CritDamage',
                    'ElementAbnormalPower',
                    'ElementMystery',
                    'PenDelta',
                    'PenRate',
                    'SpRecover',
                ]

                partner_data[char].update({k: 0 for k in stats})

                if char not in ['2011', '2021']:
                    partner_data[char].update(
                        {
                            'WeaponType': list(char_data['WeaponType'].keys())[
                                0
                            ],
                            'ElementType': list(
                                char_data['ElementType'].keys()
                            )[0],
                            'Camp': list(char_data['Camp'].values())[0],
                            'HitType': list(char_data['HitType'].values())[0],
                            'Rarity': {4: 'S', 3: 'A'}.get(
                                char_data['Rarity'], 'A'
                            ),
                        }
                    )

                    for k in char_data['Stats']:
                        if k in stats:
                            partner_data[char][k] = char_data['Stats'][k]

                    partner_data[char]['Level'] = char_data['Level']
                    partner_data[char]['ExtraLevel'] = char_data['ExtraLevel']

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
        weapon_result = {}
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
                weapon_result[weapon] = {
                    'code_name': weapon_data['CodeName'],
                    'name': weapon_data['Name'],
                    'talents': weapon_data['Talents'],
                    'rarity': 'S' if weapon_data['Rarity'] == 4 else 'A',
                    'props_name': weapon_data['BaseProperty']['Name'],
                    'props_id': PROP_NAME_TO_ID[
                        weapon_data['BaseProperty']['Name2']
                    ],
                    'props_value': weapon_data['BaseProperty']['Value'],
                    'rand_props_name': weapon_data['RandProperty']['Name'],
                    'rand_props_id': PROP_NAME_TO_ID[
                        weapon_data['RandProperty']['Name2']
                    ],
                    'rand_props_value': weapon_data['RandProperty']['Value'],
                    'level': weapon_data['Level'],
                    'stars': weapon_data['Stars'],
                }
        with open(MAP_PATH / WeaponId2DataFile, 'w', encoding='UTF-8') as f:
            json.dump(weapon_result, f, indent=4, ensure_ascii=False)


async def get_new_equipment():
    all_equipment_data = await get_hakush_all_equipment()
    if all_equipment_data:
        equipment2sprite_data = {}

        for equipment in all_equipment_data:
            print(equipment)
            name = (
                all_equipment_data[equipment]['icon']
                .split('/')[-1]
                .split('.')[0]
            )
            equipment2sprite_data[equipment] = {
                'equip_id_list': [],
                'sprite_file': f'3D{name}',
                'equip_name': all_equipment_data[equipment]['CHS']['name'],
                'desc1': all_equipment_data[equipment]['CHS']['desc2'],
                'desc2': all_equipment_data[equipment]['CHS']['desc4'],
            }
            for i in (
                list(range(21, 27)) + list(range(31, 37)) + list(range(41, 47))
            ):
                equipment2sprite_data[equipment]['equip_id_list'].append(
                    int(equipment[:3] + str(i))
                )
        with open(MAP_PATH / EquipId2DataFile, 'w', encoding='UTF-8') as f:
            json.dump(equipment2sprite_data, f, indent=4, ensure_ascii=False)


async def get_new():
    # await get_new_char()
    await get_new_weapon()
    # await get_new_equipment()


asyncio.run(get_new())
