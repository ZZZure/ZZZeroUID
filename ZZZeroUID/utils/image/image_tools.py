from pathlib import Path
from typing import Union, Optional

from PIL import Image
from gsuid_core.utils.image.image_tools import TEXT_PATH, CustomizeImage

from ..resource.RESOURCE_PATH import CU_BG_PATH
from ...starrailuid_config.sr_config import srconfig

BG_PATH = Path(__file__).parent / 'bg'
NM_BG_PATH = BG_PATH / 'nm_bg'
SP_BG_PATH = BG_PATH / 'sp_bg'

if list(CU_BG_PATH.iterdir()) != []:
    bg_path = CU_BG_PATH
else:
    bg_path = NM_BG_PATH

if list(CU_BG_PATH.iterdir()) != []:
    bg_path = CU_BG_PATH
else:
    bg_path = NM_BG_PATH


async def get_simple_bg(
    based_w: int, based_h: int, image: Union[str, None, Image.Image] = None
) -> Image.Image:
    CIL = CustomizeImage(NM_BG_PATH)
    return CIL.get_image(image, based_w, based_h)


async def get_color_bg(
    based_w: int,
    based_h: int,
    bg: Optional[str] = None,
    without_mask: bool = False,
) -> Image.Image:
    image = ''
    if bg and srconfig.get_config('DefaultBaseBG').data:
        path = SP_BG_PATH / f'{bg}.jpg'
        path2 = CU_BG_PATH / f'{bg}.jpg'
        if path2.exists():
            image = Image.open(path2)
        elif path.exists():
            image = Image.open(path)
    CI_img = CustomizeImage(bg_path)
    img = CI_img.get_image(image, based_w, based_h)
    color = CI_img.get_bg_color(img)
    if not without_mask:
        color_mask = Image.new('RGBA', (based_w, based_h), color)
        enka_mask = Image.open(TEXT_PATH / 'bg_mask.png').resize(
            (based_w, based_h)
        )
        img.paste(color_mask, (0, 0), enka_mask)
    return img
