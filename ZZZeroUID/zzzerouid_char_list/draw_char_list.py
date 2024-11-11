import json
from pathlib import Path
from typing import Dict, List, Tuple, Union

import aiofiles
from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.utils.image.convert import convert_img

from ..utils.hint import error_reply
from ..utils.resource.download_file import get_weapon
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..zzzerouid_char_detail.utils import get_skill_dict
from ..zzzerouid_char_detail.refresh_char_detail import refresh_char
from ..utils.fonts.zzz_fonts import (
    zzz_font_18,
    zzz_font_20,
    zzz_font_24,
    zzz_font_32,
)
from ..utils.image import (
    add_footer,
    get_zzz_bg,
    get_rarity_img,
    get_element_img,
    get_player_card_min,
    get_general_role_img,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'
prefix = get_plugin_available_prefix("ZZZeroUID")
ERROR = (
    f' ❌【绝区零】你还未刷新角色面板, 请使用{prefix}刷新面板进行刷新后使用...'
)
COLOR_MAP = {
    'S': (255, 188, 0),
    'A': (208, 0, 255),
}
RANK1, RANK2, RANK3, RANK4, RANK5, RANK6 = (
    (189, 33, 33),
    (189, 89, 33),
    (134, 33, 189),
    (33, 69, 189),
    (39, 127, 47),
    (39, 106, 74),
)
shape = Image.open(TEXT_PATH / 'shape.png')
banner = Image.open(TEXT_PATH / 'banner.png')


def get_color(value: int, value_ramp: Dict[int, Tuple[int, int, int]]):
    for i in value_ramp:
        if value >= i:
            return Image.new('RGBA', (90, 30), value_ramp[i])
    else:
        return Image.new('RGBA', (90, 30), (58, 58, 58))


def get_shape(value: str, color: Image.Image):
    img = Image.new('RGBA', shape.size)
    img.paste(color, (0, 0), shape)
    img_draw = ImageDraw.Draw(img)
    img_draw.text((45, 15), value, 'white', zzz_font_24, 'mm')
    return img


async def draw_char_list_img(uid: str, ev: Event) -> Union[str, bytes]:
    await refresh_char(uid, ev, True)

    path = PLAYER_PATH / uid
    if not path.exists():
        return ERROR

    char_paths = list(path.rglob('[0-9][0-9][0-9][0-9].json'))
    if not char_paths:
        return ERROR

    player_card = await get_player_card_min(uid, ev)
    if isinstance(player_card, int):
        return error_reply(player_card)

    char_num = len(char_paths)

    w, h = 1000, 600 + char_num * 92 + 90
    img = get_zzz_bg(w, h, 'bg')
    title = Image.open(TEXT_PATH / 'title.png')
    title_draw = ImageDraw.Draw(title)
    img.paste(player_card, (25, 70), player_card)
    img.paste(banner, (25, 487), banner)

    SRANK_WEAPON = 0
    HIGH_AVATAR = 0
    HIGH_SHADOW = 0
    SRANK_AVATAR = 0
    frame = Image.open(TEXT_PATH / 'frame.png')
    weapon_mask = Image.open(TEXT_PATH / 'weapon_mask.png')

    datas: List[Dict] = []
    for index, i in enumerate(char_paths):
        async with aiofiles.open(i, mode='r', encoding='UTF8') as f:
            data: Dict = json.loads(await f.read())

        base_score = 250 if data['rarity'] == 'S' else 50
        score = (data['rank'] + 1) * base_score
        score += data['level']
        for skill in data['skills']:
            skill_level = skill['level']
            score += skill_level * 10

        if data['weapon']:
            score += 210 if data['weapon']['rarity'] == 'S' else 60
            score += data['weapon']['level']

        data['score'] = score
        datas.append(data)

    datas.sort(key=lambda x: x['score'], reverse=True)

    for index, data in enumerate(datas):
        char_id: int = data['id']
        char_img = get_general_role_img(char_id)
        element_icon = get_element_img(data['element_type'], 30, 30)
        level: int = data['level']
        level_str = f'Lv{level}'
        level_color = get_color(
            level,
            {
                60: RANK1,
                50: RANK2,
                40: RANK3,
                30: RANK4,
                20: RANK5,
                10: RANK6,
            },
        )
        rank: int = data['rank']
        if rank >= 5:
            HIGH_SHADOW += 1
        rank_str = f'{rank}影'
        rank_color = get_color(
            rank,
            {
                6: RANK1,
                5: RANK2,
                4: RANK3,
                3: RANK4,
                2: RANK5,
                1: RANK6,
            },
        )

        rarity: str = data['rarity']
        if rarity == 'S':
            SRANK_AVATAR += 1
        color = COLOR_MAP.get(rarity, (255, 188, 0))

        skill_dict = get_skill_dict(data)
        bar = Image.open(TEXT_PATH / 'bar.png')
        bar_draw = ImageDraw.Draw(bar)

        bar.paste(char_img, (103, 14), char_img)

        skill_bar = Image.open(TEXT_PATH / 'skill_bar.png')
        skill_draw = ImageDraw.Draw(skill_bar)

        skill_all_level = 0
        for skill_pos_num in skill_dict:
            skill_level, skill_color = skill_dict[skill_pos_num]
            skill_all_level += skill_level
            skill_draw.text(
                (int(32 + skill_pos_num * 50.3), 50),
                f'{skill_level}',
                skill_color,
                zzz_font_18,
                'mm',
            )

        if skill_all_level / 6 >= 8:
            HIGH_AVATAR += 1

        if data['weapon']:
            weapon = data['weapon']
            weapon_img = await get_weapon(weapon['id'])
            weapon_img = weapon_img.resize((133, 133))
            weapon_name: str = weapon['name']
            weapon_level: int = weapon['level']
            wlevel_str = f'Lv{weapon_level}'
            wlevel_color = get_color(
                weapon_level,
                {
                    60: RANK1,
                    50: RANK2,
                    40: RANK3,
                    30: RANK4,
                    20: RANK5,
                    10: RANK6,
                },
            )
            weapon_star: int = weapon['star']
            star_str = f'{weapon_star}精'
            star_color = get_color(
                weapon_star,
                {
                    6: RANK1,
                    5: RANK2,
                    4: RANK3,
                    3: RANK4,
                    2: RANK5,
                    1: RANK6,
                },
            )
            weapon_rarity: str = weapon['rarity']
            if weapon_rarity == 'S':
                SRANK_WEAPON += 1
            rarity_icon = get_rarity_img(weapon_rarity, 40, 40)
            bar.paste(weapon_img, (648, -20), weapon_mask)

        bar.paste(element_icon, (287, 16), element_icon)

        color_bar = Image.new('RGBA', bar.size, color)
        bar.paste(color_bar, (0, 0), frame)

        level_tag = get_shape(level_str, level_color)
        rank_tag = get_shape(rank_str, rank_color)
        bar.paste(rank_tag, (75, 14), rank_tag)
        bar.paste(level_tag, (220, 47), level_tag)

        if data['weapon']:
            wlevel_tag = get_shape(wlevel_str, wlevel_color)
            star_tag = get_shape(star_str, star_color)
            bar.paste(rarity_icon, (780, 10), rarity_icon)
            bar.paste(wlevel_tag, (837, 47), wlevel_tag)
            bar.paste(star_tag, (755, 47), star_tag)
            bar_draw.text(
                (820, 30),
                weapon_name[:5],
                'white',
                zzz_font_20,
                'lm',
            )

        bar.paste(skill_bar, (309, 8), skill_bar)
        img.paste(bar, (0, 600 + index * 92), bar)

    SAVATAR_STR = f'{SRANK_AVATAR}/{char_num}'
    HIGHShadow_STR = f'{HIGH_SHADOW}/{char_num}'
    HIGHAVATAR_STR = f'{HIGH_AVATAR}/{char_num}'
    SRANK_WEAPON_RATE = str(round(SRANK_WEAPON / char_num, 2) * 100) + '%'

    for sindex, s in enumerate(
        [SAVATAR_STR, HIGHShadow_STR, HIGHAVATAR_STR, SRANK_WEAPON_RATE]
    ):
        title_draw.text(
            (221 + sindex * 177, 166),
            s,
            (24, 24, 24),
            zzz_font_32,
            'mm',
        )

    img.paste(title, (0, 228), title)
    img = add_footer(img)
    res = await convert_img(img)
    return res
