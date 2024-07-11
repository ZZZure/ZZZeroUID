from gsuid_core.utils.download_resource.download_core import download_all_file

from .RESOURCE_PATH import (
    ROLE_PATH,
    SUIT_PATH,
    WEAPON_PATH,
    SUIT_3D_PATH,
    ROLECIRCLE_PATH,
    FLOWER_GUIDE_PATH,
)


async def download_all_resource():
    await download_all_file(
        'ZZZeroUID',
        {
            'guide/flower': FLOWER_GUIDE_PATH,
            'resource/weapon': WEAPON_PATH,
            'resource/role_circle': ROLECIRCLE_PATH,
            'resource/role': ROLE_PATH,
            'resource/3d_suit': SUIT_3D_PATH,
            'resource/suit': SUIT_PATH,
        },
    )
