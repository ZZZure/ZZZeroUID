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
)
from ZZZeroUID.utils.hakush_api.request import (  # noqa: E402
    get_hakush_char_data,
    get_hakush_weapon_data,
    get_hakush_all_char_data,
    get_hakush_all_weapon_data,
)


async def get_new():
    all_char_data = await get_hakush_all_char_data()
    all_weapon_data = await get_hakush_all_weapon_data()
    if all_char_data and all_weapon_data:
        partner_data = {}
        for char in all_char_data:
            print(char)
            char_data = await get_hakush_char_data(char)
            if char_data:
                if (
                    'PartnerInfo' in char_data
                    and 'FullName' in char_data['PartnerInfo']
                ):
                    full_name = char_data['PartnerInfo']['FullName']
                else:
                    full_name = char_data['Name']
                partner_data[char] = {
                    "sprite_id": char_data['Icon'].replace('IconRole', ''),
                    "name": char_data['Name'],
                    "full_name": full_name,
                    "en_name": char_data['CodeName'],
                }
        with open(MAP_PATH / PartnerId2DataFile, 'w', encoding='UTF-8') as f:
            json.dump(partner_data, f, indent=4, ensure_ascii=False)

        weapon2sprite_data = {}
        for weapon in all_weapon_data:
            print(weapon)
            weapon_data = await get_hakush_weapon_data(weapon)
            if weapon_data:
                weapon2sprite_data[weapon] = weapon_data['CodeName']
        with open(MAP_PATH / WeaponId2SpriteFile, 'w', encoding='UTF-8') as f:
            json.dump(weapon2sprite_data, f, indent=4, ensure_ascii=False)


asyncio.run(get_new())
