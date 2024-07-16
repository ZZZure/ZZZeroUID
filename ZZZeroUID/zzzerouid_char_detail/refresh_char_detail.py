import json
from datetime import datetime
from typing import List, Union

from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.hint import error_reply
from ..utils.zzzero_api import zzz_api
from ..utils.api.models import ZZZAvatarInfo
from .draw_char_detail_card import TEXT_PATH
from ..utils.fonts.zzz_fonts import zzz_font_40
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..zzzerouid_config.zzzero_config import ZZZ_CONFIG
from ..utils.image import (
    add_footer,
    get_rank_img,
    get_circle_role_img,
    get_player_card_min,
)

REFRESH_BG_PATH = TEXT_PATH / 'refresh_bg'


async def refresh_char(uid: str, ev: Event) -> Union[str, bytes]:
    raw_data = await zzz_api.get_zzz_avatar_basic_info(uid)
    if isinstance(raw_data, int):
        return error_reply(raw_data)
    id_list = [i['id'] for i in raw_data]
    data = await zzz_api.get_zzz_avatar_info(uid, id_list)
    if isinstance(data, int):
        return error_reply(data)

    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %H:%M:%S')

    path = PLAYER_PATH / str(uid)
    path.mkdir(parents=True, exist_ok=True)
    im = []
    for avatar in data:
        save_data = {}
        save_data.update(avatar)
        _id = avatar['id']
        save_data['uid'] = uid
        save_data['current_time'] = current_time

        with open(path / f'{_id}.json', 'wb') as f:
            d = json.dumps(
                save_data,
                ensure_ascii=False,
                indent=4,
            ).encode('utf-8')
            f.write(d)
        im.append(avatar['name_mi18n'])

    is_pic: bool = ZZZ_CONFIG.get_config('RefreshCardUsePic').data
    if is_pic:
        return await draw_refresh_card(uid, ev, data)

    msg = f'[绝区零] 刷新完成！本次刷新{len(im)}个角色!'
    msg += f'\n刷新角色列表:{",".join(im)}'
    return msg


async def draw_refresh_card(
    uid: str,
    ev: Event,
    data: List[ZZZAvatarInfo],
):
    player_card = await get_player_card_min(uid, ev)
    player_card = player_card.resize((1140, 240))
    refresh_title = Image.open(TEXT_PATH / 'refresh_title.png')
    title_draw = ImageDraw.Draw(refresh_title)
    refresh_title.paste(player_card, (-8, 40), player_card)
    title_draw.text(
        (970, 183),
        f'已成功更新 {len(data)} 个角色！',
        font=zzz_font_40,
        fill=(216, 216, 216),
        anchor='mm',
    )

    _REFRESH_BG: str = ZZZ_CONFIG.get_config('RefreshBG').data
    REFRESH_BG = Image.open(REFRESH_BG_PATH / f'{_REFRESH_BG}.jpg')
    avatar_h = (((len(data) - 1) // 5) + 1) * 400
    w, h = 1800, 300 + 140 + 50 + avatar_h

    img = crop_center_img(REFRESH_BG, w, h)
    img.paste(refresh_title, (0, 0), refresh_title)
    img_draw = ImageDraw.Draw(img, 'RGBA')

    img_draw.rounded_rectangle(
        (100, 300, 1700, 300 + avatar_h + 50),
        25,
        (0, 0, 0, 120),
        (0, 0, 0, 255),
        width=4,
    )

    for index, avatar in enumerate(data):
        char_bg = Image.open(TEXT_PATH / 'refresh_char_bg.png')
        _id = avatar['id']
        _rank = avatar['rarity']
        rank_img = get_rank_img(_rank)
        role_img = get_circle_role_img(_id, 234, 234)
        char_bg.paste(role_img, (33, 26), role_img)
        char_bg.paste(rank_img, (84, 329), rank_img)
        char_draw = ImageDraw.Draw(char_bg)
        name = avatar['name_mi18n']
        name = name.replace('「', '').replace('」', '')
        char_draw.text(
            (133, 350),
            name,
            font=zzz_font_40,
            fill=(255, 255, 255),
            anchor='lm',
        )

        ox = (index % 5) * 300
        oy = (index // 5) * 400
        char_bg = char_bg.resize((270, 360))

        img.paste(char_bg, (160 + ox, 340 + oy), char_bg)

    img = add_footer(img, 1150)
    return await convert_img(img)
