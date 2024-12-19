from gsuid_core.utils.download_resource.download_core import download_all_file

from .RESOURCE_PATH import (
    CAMP_PATH,
    MIND_PATH,
    ROLE_PATH,
    SUIT_PATH,
    CUSTOM_PATH,
    WEAPON_PATH,
    SUIT_3D_PATH,
    CAT_GUIDE_PATH,
    SQUARE_BANGBOO,
    ROLECIRCLE_PATH,
    ROLEGENERAL_PATH,
    FLOWER_GUIDE_PATH,
)


async def download_all_resource():
    await download_all_file(
        'ZZZeroUID',
        {
            'guide/flower': FLOWER_GUIDE_PATH,
            'guide/cat': CAT_GUIDE_PATH,
            'resource/weapon': WEAPON_PATH,
            'resource/role_circle': ROLECIRCLE_PATH,
            'resource/role_general': ROLEGENERAL_PATH,
            'resource/role': ROLE_PATH,
            'resource/3d_suit': SUIT_3D_PATH,
            'resource/suit': SUIT_PATH,
            'resource/camp': CAMP_PATH,
            'resource/mind': MIND_PATH,
            'resource/square_bangbo': SQUARE_BANGBOO,
            'custom': CUSTOM_PATH,
        },
    )
