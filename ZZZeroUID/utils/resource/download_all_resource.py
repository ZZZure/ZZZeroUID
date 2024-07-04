from gsuid_core.utils.download_resource.download_core import download_all_file

from .RESOURCE_PATH import FLOWER_GUIDE_PATH


async def download_all_resource():
    await download_all_file(
        'ZZZeroUID',
        {
            'guide/flower': FLOWER_GUIDE_PATH,
        },
    )
