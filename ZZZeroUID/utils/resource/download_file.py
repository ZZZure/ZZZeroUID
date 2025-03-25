from pathlib import Path
from typing import Union

from PIL import Image, UnidentifiedImageError
from gsuid_core.utils.download_resource.download_file import download

from ..name_convert import weapon_data, char_name_to_char_id
from .RESOURCE_PATH import WEAPON_PATH, SQUARE_AVATAR, SQUARE_BANGBOO
from ..api.api import (
    ZZZ_SQUARE_AVATAR,
    ZZZ_SQUARE_BANGBOO,
    V2_ZZZ_SQUARE_AVATAR,
    V2_ZZZ_SQUARE_BANGBOO,
)


def get_source(img: Union[Image.Image, Path], w: int, h: int):
    if isinstance(img, Path):
        _img = Image.open(img).convert("RGBA")
    else:
        _img = img.convert("RGBA")
    scale = w / _img.size[0]
    img = _img.resize((w, int(_img.size[1] * scale)))
    return img


async def get_square_avatar(
    char_id: Union[str, int] = "",
    char_name: str = "",
) -> Image.Image:
    if not char_id:
        if char_name:
            _char_id = char_name_to_char_id(char_name)
            if _char_id is None:
                raise ValueError("[绝区零] 传入char_id/char_name不正确!")
            else:
                char_id = _char_id
        else:
            raise ValueError("[绝区零] 你必须至少传入一个数值!")

    name = f"role_square_avatar_{char_id}.png"
    url = f"{ZZZ_SQUARE_AVATAR}/{name}"
    new_url = f"{V2_ZZZ_SQUARE_AVATAR}/{name}"

    path = SQUARE_AVATAR / name
    if path.exists():
        try:
            return get_source(path, 152, 186)
        except UnidentifiedImageError:
            pass

    retcode = await download(new_url, SQUARE_AVATAR, name, tag="[绝区零]")
    if retcode != 200:
        retcode = await download(url, SQUARE_AVATAR, name, tag="[绝区零]")

    return get_source(path, 152, 186)


async def get_square_bangboo(bangboo_id: Union[str, int]) -> Image.Image:
    name = f"bangboo_rectangle_avatar_{bangboo_id}.png"
    url = f"{ZZZ_SQUARE_BANGBOO}/{name}"
    new_url = f"{V2_ZZZ_SQUARE_BANGBOO}/{name}"
    path = SQUARE_BANGBOO / name
    if path.exists():
        try:
            return get_source(path, 152, 186)
        except UnidentifiedImageError:
            pass

    retcode = await download(new_url, SQUARE_BANGBOO, name, tag="[绝区零]")
    if retcode != 200:
        retcode = await download(url, SQUARE_BANGBOO, name, tag="[绝区零]")

    return get_source(path, 152, 186)


async def get_weapon(weapon_id: Union[str, int]) -> Image.Image:
    img = Image.new("RGBA", (400, 400))
    if str(weapon_id) in weapon_data:

        weapon_sprite = weapon_data[str(weapon_id)]
        path_1 = WEAPON_PATH / f"{weapon_sprite['code_name']}.png"
        path_2 = WEAPON_PATH / f"{weapon_sprite['code_name']}_High.png"
        if path_2.exists():
            weapon = Image.open(path_2)
        elif path_1.exists():
            weapon = Image.open(path_1)
        else:
            return img
        weapon = weapon.convert("RGBA")
        x, y = weapon.size
        img.paste(weapon, (200 - x // 2, 200 - y // 2), weapon)
    return img
