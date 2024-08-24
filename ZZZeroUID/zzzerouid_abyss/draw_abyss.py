from typing import Any
from pathlib import Path

from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.hint import error_reply
from ..utils.zzzero_api import zzz_api
from ..zzzerouid_stamina.draw_zzz_stamina import draw_bar
from ..utils.image import (
    GREY,
    YELLOW,
    add_footer,
    get_zzz_bg,
    get_player_card_min,
)
from ..utils.fonts.zzz_fonts import (
    zzz_font_30,
    zzz_font_34,
    zzz_font_36,
    zzz_font_40,
    zzz_font_50,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'

COLLECT_MAP = {
    1: '鸣徽图鉴',
    2: '特殊区域记录',
    3: '哨站课题',
    4: '侵蚀研究',
    5: '旧都失物',
}


async def draw_data_bar(
    title: str,
    cur_value: Any,
    max_value: Any,
):
    bar = Image.open(TEXT_PATH / 'data_bar.png')
    bar_draw = ImageDraw.Draw(bar)

    bar_draw.text((151, 49), f'{title}', GREY, zzz_font_36, 'lm')

    bar_draw.text((765, 51), f'/{max_value}', GREY, zzz_font_30, 'lm')
    bar_draw.text((757, 50), f'{cur_value}', YELLOW, zzz_font_40, 'rm')

    return bar


async def draw_stage_bar(
    title: str,
    value: bool,
):
    bar = Image.open(TEXT_PATH / 'stage_bar.png')
    bar_draw = ImageDraw.Draw(bar)

    if value:
        _value = '已完成'
        _color = YELLOW
    else:
        _value = '尚未挑战'
        _color = GREY

    bar_draw.text((151, 49), f'{title}', GREY, zzz_font_36, 'lm')

    bar_draw.text((817, 49), f'{_value}', _color, zzz_font_36, 'rm')

    return bar


async def draw_abyss_img(uid: str, ev: Event):
    data = await zzz_api.get_zzz_abyss_info(uid)
    if isinstance(data, int):
        return error_reply(data)

    player_card = await get_player_card_min(uid, ev)
    if isinstance(player_card, int):
        return error_reply(player_card)

    cur_level = data['abyss_level']['cur_level']
    max_level = data['abyss_level']['max_level']

    cur_talent = data['abyss_talent']['cur_talent']
    max_talent = data['abyss_talent']['max_talent']

    cur_duty = data['abyss_duty']['cur_duty']
    max_duty = data['abyss_duty']['max_duty']

    cur_point = data['abyss_point']['cur_point']
    max_point = data['abyss_point']['max_point']

    duty_bar = await draw_bar('悬赏委托', cur_duty, max_duty)
    point_bar = await draw_bar('调查点数', cur_point, max_point)

    bg = TEXT_PATH / 'bg.jpg'
    data_banner = Image.open(TEXT_PATH / 'data_banner.png')
    stage_banner = Image.open(TEXT_PATH / 'stage_banner.png')
    level_bg = Image.open(TEXT_PATH / 'level_bg.png')
    buff_bg = Image.open(TEXT_PATH / 'buff_bg.png')
    level_draw = ImageDraw.Draw(level_bg)
    buff_draw = ImageDraw.Draw(buff_bg)

    level_draw.text((130, 130), f'/{max_level}', 'white', zzz_font_34, 'lm')
    level_draw.text(
        (123, 126), f'{cur_level}', (255, 200, 1), zzz_font_50, 'rm'
    )

    buff_draw.text((130, 130), f'/{max_talent}', 'white', zzz_font_34, 'lm')
    buff_draw.text(
        (123, 126), f'{cur_talent}', (255, 200, 1), zzz_font_50, 'rm'
    )

    img = get_zzz_bg(950, 1700, bg)

    for index, _d in enumerate(data['abyss_collect']):
        bar = await draw_data_bar(
            COLLECT_MAP.get(_d['type'], '未知数据'),
            _d['cur_collect'],
            _d['max_collect'],
        )
        img.paste(bar, (0, 824 + index * 87), bar)

    bar1 = await draw_stage_bar('枯败花圃', data['abyss_nest']['is_nest'])
    bar2 = await draw_stage_bar('刀耕火焚', data['abyss_throne']['is_throne'])

    for index, _s in enumerate([bar1, bar2]):
        img.paste(_s, (0, 1400 + index * 87), _s)

    img.paste(player_card, (0, 70), player_card)
    img.paste(data_banner, (0, 718), data_banner)
    img.paste(stage_banner, (0, 1278), stage_banner)
    img.paste(level_bg, (68, 289), level_bg)
    img.paste(buff_bg, (474, 289), buff_bg)
    img.paste(duty_bar, (0, 491), duty_bar)
    img.paste(point_bar, (0, 609), point_bar)

    img = add_footer(img)
    res = await convert_img(img)
    return res
