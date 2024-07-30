from pathlib import Path
from typing import List, Union

from gsuid_core.bot import Bot
from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.database.models import GsBind
from gsuid_core.utils.image.convert import convert_img

from ..utils.zzzero_api import zzz_api
from ..utils.hint import BIND_UID_HINT, error_reply
from ..utils.fonts.zzz_fonts import (
    zzz_font_26,
    zzz_font_36,
    zzz_font_40,
    zzz_font_50,
)
from ..utils.image import (
    GREY,
    YELLOW,
    add_footer,
    get_zzz_bg,
    get_player_card_min,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'
YES = Image.open(TEXT_PATH / 'yes.png')
NO = Image.open(TEXT_PATH / 'no.png')


def convert_seconds_to_hm(seconds: int):
    hours = seconds // 3600
    remaining_seconds = seconds % 3600
    minutes = remaining_seconds // 60

    return hours, minutes


async def draw_stamina_img(bot: Bot, ev: Event):
    user_id = ev.at if ev.at else ev.user_id
    uids = await GsBind.get_uid_list_by_game(user_id, ev.bot_id, 'zzz')
    if not uids:
        await bot.send(BIND_UID_HINT)
    else:
        img_list: List[Image.Image] = []
        _list = [await _draw_stamina_img(uid, ev) for uid in uids]
        for i in _list:
            if isinstance(i, str):
                await bot.send(i)
            else:
                img_list.append(i)
        if img_list:
            _x = img_list[0].size[0]
            res = Image.new('RGBA', (_x * len(img_list), img_list[0].size[1]))
            for index, img in enumerate(img_list):
                res.paste(img, (index * _x, 0), img)
            res = await convert_img(res)
            await bot.send(res)
        else:
            await bot.send('你当前绑定的UID存在错误, 请尝试解决...')


async def _draw_stamina_img(uid: str, ev: Event) -> Union[str, Image.Image]:

    data = await zzz_api.get_zzz_note_info(uid)
    player_card = await get_player_card_min(uid, ev)
    if isinstance(data, int):
        return error_reply(data)
    if isinstance(player_card, int):
        return error_reply(player_card)

    energy = data['energy']['progress']['current']
    max_energy = data['energy']['progress']['max']
    radio = energy / max_energy
    max_len = 386
    restore = data['energy']['restore']
    rh, rm = convert_seconds_to_hm(restore)
    restore_str = f'{rh}小时{rm}分钟'

    vitality = data['vitality']['current']
    max_vitality = data['vitality']['max']
    vitality_radio = vitality / max_vitality
    if vitality_radio == 1:
        vitality_icon = YES
    else:
        vitality_icon = NO

    VHSSale = data['vhs_sale']['sale_state']
    if 'Doing' in VHSSale:
        sale_icon = YES
        sale_text = '正在营业'
    else:
        sale_icon = NO
        sale_text = '尚未营业'

    card_sign = data['card_sign']
    if 'Done' in card_sign:
        card_icon = YES
        card_text = '已抽奖'
    else:
        card_icon = NO
        card_text = '未抽奖'

    img = get_zzz_bg(950, 1400)
    bg = Image.open(TEXT_PATH / 'bg.png')
    battery_banner = Image.open(TEXT_PATH / 'battery_banner.png')
    active_banner = Image.open(TEXT_PATH / 'active_banner.png')
    battery_card = Image.open(TEXT_PATH / 'battery_card.png')
    active_bar = Image.open(TEXT_PATH / 'bar.png')
    active_draw = ImageDraw.Draw(active_bar)
    gacha_bar = Image.open(TEXT_PATH / 'bar.png')
    gacha_draw = ImageDraw.Draw(gacha_bar)
    shop_bar = Image.open(TEXT_PATH / 'bar.png')
    shop_draw = ImageDraw.Draw(shop_bar)
    battery_draw = ImageDraw.Draw(battery_card)

    active_draw.text((188, 51), '今日活跃度', GREY, zzz_font_40, 'lm')
    gacha_draw.text((188, 51), '刮刮卡', GREY, zzz_font_40, 'lm')
    shop_draw.text((188, 51), '录像店经营', GREY, zzz_font_40, 'lm')

    active_bar.paste(vitality_icon, (93, 10), vitality_icon)
    gacha_bar.paste(card_icon, (93, 10), card_icon)
    shop_bar.paste(sale_icon, (93, 10), sale_icon)

    active_draw.text((716, 56), f'/{max_vitality}', GREY, zzz_font_40, 'lm')
    active_draw.text((708, 54), f'{vitality}', YELLOW, zzz_font_50, 'rm')

    gacha_draw.text((826, 50), card_text, YELLOW, zzz_font_50, 'rm')
    shop_draw.text((826, 50), sale_text, YELLOW, zzz_font_50, 'rm')

    battery_draw.text(
        (565, 111),
        f'/{max_energy}',
        (165, 165, 165),
        zzz_font_36,
        'lm',
    )
    battery_draw.text(
        (517, 108),
        f'{energy}',
        YELLOW,
        zzz_font_50,
        'mm',
    )
    battery_draw.text(
        (454, 152),
        f'{restore_str}',
        'white',
        zzz_font_26,
        'lm',
    )
    battery_draw.rounded_rectangle(
        (415, 230, int(415 + radio * max_len), 246),
        20,
        YELLOW,
    )

    img.paste(bg, (0, 0), bg)
    img.paste(player_card, (0, 224), player_card)
    img.paste(battery_banner, (0, 402), battery_banner)
    img.paste(active_banner, (0, 849), active_banner)
    img.paste(battery_card, (0, 511), battery_card)
    for index, i in enumerate([active_bar, shop_bar, gacha_bar]):
        img.paste(i, (0, 961 + index * 101), i)

    img = add_footer(img)
    return img
