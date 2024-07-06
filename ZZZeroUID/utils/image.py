from pathlib import Path

from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.image_tools import (
    crop_center_img,
    get_avatar_with_ring,
)

from .zzzero_api import zzz_api
from .fonts.zzz_fonts import zzz_font_28, zzz_font_30, zzz_font_38

TEXT_PATH = Path(__file__).parent / 'texture2d'
GREY = (216, 216, 216)
BLACK_G = (40, 40, 40)
YELLOW = (255, 200, 1)
BLUE = (1, 183, 255)


def count_characters(s: str) -> float:
    count = 0
    for char in s:
        if '\u4e00' <= char <= '\u9fff':
            count += 1
        else:
            count += 0.5
    return count


async def get_player_card_min(uid: str, ev: Event, world: str = ''):
    data = await zzz_api.get_zzz_user_info(uid)
    if isinstance(data, int):
        return data

    user_name = data['nickname']
    world_level = data['level']
    if world:
        region_name = world
    else:
        region_name = data['region_name']
    name_len = count_characters(user_name) * 45

    player_card = Image.open(TEXT_PATH / 'player_card_min.png')
    card_draw = ImageDraw.Draw(player_card)

    avatar = await get_avatar_with_ring(ev, 129, is_ring=False)
    player_card.paste(avatar, (105, 30), avatar)

    card_draw.text((426, 120), f'UID {uid}', GREY, zzz_font_30, 'mm')
    card_draw.text((290, 64), user_name, 'white', zzz_font_38, 'lm')

    xs, ys = 290 + name_len + 20, 45
    xt, yt = xs + 90 + 12, 45
    card_draw.rounded_rectangle((xs, ys, xs + 90, ys + 35), 10, YELLOW)
    card_draw.rounded_rectangle((xt, yt, xt + 144, yt + 35), 10, BLUE)

    card_draw.text(
        (xs + 45, ys + 17),
        f'Lv{world_level}',
        BLACK_G,
        zzz_font_28,
        'mm',
    )
    card_draw.text(
        (xt + 72, yt + 17),
        region_name,
        BLACK_G,
        zzz_font_28,
        'mm',
    )
    return player_card


def get_zzz_bg(w: int, h: int) -> Image.Image:
    bg = Image.open(TEXT_PATH / 'bg.jpg').convert('RGBA')
    return crop_center_img(bg, w, h)


def add_footer(img: Image.Image) -> Image.Image:
    footer = Image.open(TEXT_PATH / 'footer.png')
    w = img.size[0]
    if w != footer.size[0]:
        footer = footer.resize(
            (w, int(footer.size[1] * w / footer.size[0])),
        )
    x, y = (
        int((img.size[0] - footer.size[0]) / 2),
        img.size[1] - footer.size[1] - 20,
    )
    img.paste(footer, (x, y), footer)
    return img
