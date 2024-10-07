from pathlib import Path

from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.hint import error_reply
from ..utils.zzzero_api import zzz_api
from ..utils.image import (
    GREY,
    BLACK_G,
    add_footer,
    get_zzz_bg,
    get_player_card_min,
)
from ..utils.fonts.zzz_fonts import (
    zzz_font_24,
    zzz_font_28,
    zzz_font_30,
    zzz_font_42,
    zzz_font_58,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'

ACTION_MAP = {
    'daily_activity_rewards': '日常活跃奖励',
    'mail_rewards': '邮件奖励',
    'growth_rewards': '成长奖励',
    'event_rewards': '活动奖励',
    'hollow_rewards': '零号空洞奖励',
    'shiyu_rewards': '式舆防卫战奖励',
    'other_rewards': '其他奖励',
}

COLOR_MAP = {
    'daily_activity_rewards': (74, 191, 53),
    'mail_rewards': (189, 67, 225),
    'growth_rewards': (190, 225, 67),
    'event_rewards': (67, 108, 225),
    'hollow_rewards': (109, 29, 149),
    'shiyu_rewards': (225, 67, 67),
    'other_rewards': (197, 143, 62),
}


async def draw_month_info(uid: str, ev: Event):
    data = await zzz_api.get_zzz_month_info(uid)
    if isinstance(data, int):
        return error_reply(data)

    data_month = data['data_month'][:4] + '-' + data['data_month'][4:]

    player_card = await get_player_card_min(uid, ev)

    img = get_zzz_bg(950, 1800)
    fg = Image.open(TEXT_PATH / 'fg.png')
    img.paste(player_card, (0, 75), player_card)
    img.paste(fg, (0, 0), fg)
    img_draw = ImageDraw.Draw(img)

    img_draw.text(
        (205, 366),
        '绳网月报',
        'white',
        zzz_font_58,
        'lm',
    )
    img_draw.text(
        (205, 413),
        data_month,
        GREY,
        zzz_font_30,
        'lm',
    )

    for i in data['month_data']['list']:
        _count = i['count']
        # 菲林
        if i['data_type'] == 'PolychromesData':
            pos = (246, 811)
        # 加密母带 & 原装母带
        elif i['data_type'] == 'MatserTapeData':
            pos = (476, 811)
        # 邦布券
        elif i['data_type'] == 'BooponsData':
            pos = (707, 811)
        # 暂时不会存在
        else:
            pos = (0, 0)

        img_draw.text(
            pos,
            str(_count),
            BLACK_G,
            zzz_font_42,
            'mm',
        )

    for index, j in enumerate(data['month_data']['income_components']):
        line = Image.new('RGBA', (950, 82))
        action = ACTION_MAP.get(j['action'], '未知奖励')
        line_draw = ImageDraw.Draw(line)
        line_draw.text(
            (143, 32),
            action,
            GREY,
            zzz_font_28,
            'lm',
        )
        x1, _, x2, _ = zzz_font_28.getbbox(action)
        x = x2 - x1

        line_draw.text(
            (150 + x, 33),
            f"{j['percent']}%",
            GREY,
            zzz_font_24,
            'lm',
        )
        line_draw.text(
            (804, 35),
            f"{j['num']}",
            'white',
            zzz_font_28,
            'rm',
        )

        lenth = 670
        percent_lenth = int(lenth * (j['percent'] / 100))

        line_draw.rounded_rectangle(
            (141, 55, 141 + lenth, 65),
            60,
            (100, 100, 100, 125),
        )

        line_draw.rounded_rectangle(
            (141, 55, 141 + percent_lenth, 65),
            60,
            COLOR_MAP.get(j['action'], (225, 67, 67)),
        )
        img.paste(line, (0, 981 + index * 82), line)

    img_draw.text(
        (475, 1636),
        '*注意，所有数据会有两小时左右的延迟',
        GREY,
        zzz_font_24,
        'mm',
    )
    img = add_footer(img)
    res = await convert_img(img)
    return res
