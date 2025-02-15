import sys
import json
import asyncio
from pathlib import Path

import httpx

sys.path.append(str(Path(__file__).parents[5]))
sys.path.append(str(Path(__file__).parents[2]))

__package__ = 'ZZZeroUID.tools'

from ..version import ZZZero_version  # noqa: E402

R_PATH = Path(__file__).parents[0]
ZZZ_DATA = R_PATH / 'zzz_data'
MAP_PATH = Path(__file__).parents[1] / 'utils' / 'map'
ALIAS = Path(__file__).parents[1] / 'utils' / 'alias' / 'char_alias.json'

if not ZZZ_DATA.exists():
    ZZZ_DATA.mkdir()

version = ZZZero_version
raw_data = {}
weapon_data = {}
partner_data = {}
gacha_data = {}
avatar_data = {}
equip_data = {}

partner_id_to_data = {}


WeaponId2SpriteFile = f'WeaponId2Sprite_{version}.json'
PartnerId2DataFile = f'PartnerId2Data_{version}.json'
EquipId2DataFile = f'EquipId2Data_{version}.json'
PartnerId2SkillParamFile = f'PartnerId2SkillParam_{version}.json'
# GachaId2SpriteIdFile = f'GachaId2SpriteId_{version}.json'

A = 'LFPICNCBMIF'
ID = 'CMDJPOHGGBI'

PARTENER_NAME = 'JOMJELIIAGO'
PARTENER_ID = 'FJKECLFEHOA'
ICONROLE_ID = 'DKHLDPFGBLC'
SPRITE_FILE = 'MMGLIMPGGHL'

SUIT_ID = 'EJBDEINOKEM'
SUIT_SPRITE_FILE = 'LEIAGCBOCGD'


def gen_equip_id_to_data():
    print('[正在执行] gen_equip_id_to_data')
    equip_id_to_data = {}
    for item in equip_data[A]:
        suit_id = item[SUIT_ID]
        if suit_id not in equip_id_to_data:
            equip_id_to_data[suit_id] = {
                'equip_id_list': [],
                'sprite_file': '',
            }
        equip_id = item[ID]
        equip_id_to_data[suit_id]['equip_id_list'].append(equip_id)
        name = '3D' + item[SUIT_SPRITE_FILE].split('/')[-1]
        name = name.split('.')[0]

        equip_id_to_data[suit_id]['sprite_file'] = name
    with open(MAP_PATH / EquipId2DataFile, 'w', encoding='UTF-8') as f:
        json.dump(equip_id_to_data, f, indent=4, ensure_ascii=False)
    print('[执行完成] gen_equip_id_to_data')


def gen_weapon_id_to_sprite():
    print('[正在执行] gen_weapon_id_to_sprite')
    weapon_id_to_sprite = {}
    for item in weapon_data[A]:
        weapon_id = item[ID]
        sprite_file = item[SPRITE_FILE]
        weapon_id_to_sprite[weapon_id] = sprite_file
    with open(MAP_PATH / WeaponId2SpriteFile, 'w', encoding='UTF-8') as f:
        json.dump(weapon_id_to_sprite, f, indent=4, ensure_ascii=False)
    print('[执行完成] gen_weapon_id_to_sprite')


'''
def gen_gacha_id_to_sprite():
    print('[正在执行] gen_gacha_id_to_sprite')
    gacha_id_to_sprite = {}
    for item in gacha_data['GMNCBMLIHPE']:
        gacha_id = item['NOJCFGOCGBI']
        sprite_file = item['FAIIOENDLMC'].split('/')[-1]
        gacha_id_to_sprite[gacha_id] = sprite_file
    with open(MAP_PATH / GachaId2SpriteIdFile, 'w', encoding='UTF-8') as f:
        json.dump(gacha_id_to_sprite, f, indent=4, ensure_ascii=False)
    print('[执行完成] gen_gacha_id_to_sprite')
'''


def gen_partner_id_to_data():
    print('[正在执行] gen_partner_id_to_data')
    global partner_id_to_data
    for item in avatar_data[A]:
        partner_id = item[PARTENER_ID]
        name = item[PARTENER_NAME]
        partner_name = raw_data[name]
        full_name = raw_data[f'{name}_FullName']
        en_name = raw_data[f'{name}_En']
        for i in gacha_data[A]:
            if i[ID] == partner_id:
                sprite_id = i[ICONROLE_ID].replace('IconRole', '')

        if partner_id not in partner_id_to_data:
            partner_id_to_data[partner_id] = {}

        partner_id_to_data[partner_id]['sprite_id'] = sprite_id
        partner_id_to_data[partner_id]['name'] = partner_name
        partner_id_to_data[partner_id]['full_name'] = full_name
        partner_id_to_data[partner_id]['en_name'] = en_name

    with open(MAP_PATH / PartnerId2DataFile, 'w', encoding='UTF-8') as f:
        json.dump(partner_id_to_data, f, indent=4, ensure_ascii=False)
    print('[执行完成] gen_partner_id_to_data')


async def download_new_file():
    print('[正在执行] download_new_file')
    URL = 'https://git.mero.moe/dimbreath/ZenlessData/raw/branch/master'
    url_list = [
        f'{URL}/FileCfg/WeaponTemplateTb.json',
        f'{URL}/FileCfg/PartnerConfigTemplateTb.json',
        f'{URL}/FileCfg/GachaItemResourceTemplateTb.json',
        f'{URL}/FileCfg/AvatarBaseTemplateTb.json',
        f'{URL}/TextMap/TextMapTemplateTb.json',
        f'{URL}/FileCfg/EquipmentTemplateTb.json',
    ]

    async with httpx.AsyncClient() as client:
        for url in url_list:
            file_name = url.split('/')[-1]
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                with open(ZZZ_DATA / file_name, 'w', encoding='UTF-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(
                    f'[执行完成] 文件已成功下载并保存为{ZZZ_DATA / file_name}'
                )
            else:
                print(f'下载失败，状态码为{response.status_code}')


def get_alias():
    with open(ALIAS, 'r', encoding='UTF-8') as f:
        alias = json.load(f)
    for _id in partner_id_to_data:
        partner = partner_id_to_data[_id]
        if partner['name'] not in alias:
            full_name = partner['full_name'].replace(' ', '')
            en_name = partner['en_name'].replace(' ', '')
            alias[partner['name']] = [full_name, en_name]

    with open(ALIAS, 'w', encoding='UTF-8') as f:
        json.dump(alias, f, indent=4, ensure_ascii=False)

    return alias


async def main():
    # await download_new_file()
    global raw_data
    global weapon_data
    global partner_data
    global gacha_data
    global equip_data
    MAP = {
        'TextMapTemplateTb.json': raw_data,
        'WeaponTemplateTb.json': weapon_data,
        'PartnerConfigTemplateTb.json': partner_data,
        'GachaItemResourceTemplateTb.json': gacha_data,
        'AvatarBaseTemplateTb.json': avatar_data,
        'EquipmentTemplateTb.json': equip_data,
    }
    try:
        for k in MAP:
            with open(ZZZ_DATA / k, 'r', encoding='UTF-8') as f:
                MAP[k].update(json.load(f))

        # gen_weapon_id_to_sprite()
        # gen_partner_id_to_data()
        gen_equip_id_to_data()
        get_alias()
        # gen_gacha_id_to_sprite()

    except FileNotFoundError:
        print('未找到TextMapCHS.json文件，停止转换！')


if __name__ == '__main__':
    asyncio.run(main())
