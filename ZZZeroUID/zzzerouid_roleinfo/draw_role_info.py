from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.hint import error_reply
from ..utils.zzzero_api import zzz_api
from ..utils.fonts.zzz_fonts import zzz_font_32, zzz_font_44
from ..utils.resource.download_file import (
    get_square_avatar,
    get_square_bangboo,
)
from ..utils.image import (
    GREY,
    add_footer,
    get_zzz_bg,
    get_rank_img,
    get_player_card_min,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'

ELEMENT_TYPE = {
    203: '电属性',
    205: '以太属性',
    202: '冰属性',
    200: '物理属性',
    201: '火属性',
}


async def draw_role_img(uid: str, ev: Event) -> Union[str, bytes]:
    data = await zzz_api.get_zzz_index_info(uid)
    if isinstance(data, int):
        return error_reply(data)

    stats = data['stats']
    player_card = await get_player_card_min(
        uid,
        ev,
        stats['world_level_name'],
    )
    if isinstance(player_card, int):
        return error_reply(player_card)

    base_info = Image.open(TEXT_PATH / 'base_info.png')
    agent_banner = Image.open(TEXT_PATH / 'agent_banner.png')
    bangboo_banner = Image.open(TEXT_PATH / 'bangboo_banner.png')
    char_fg = Image.open(TEXT_PATH / 'char_fg.png')
    bangboo_fg = Image.open(TEXT_PATH / 'bangboo_fg.png')
    base_draw = ImageDraw.Draw(base_info)

    active_days = stats['active_days']
    avatar_num = stats['avatar_num']
    buddy_num = stats['buddy_num']
    zone_layer = stats['cur_period_zone_layer_count']

    base_draw.text((202, 239), f'{active_days}', 'white', zzz_font_44, 'mm')
    base_draw.text((378, 239), f'{avatar_num}', 'white', zzz_font_44, 'mm')
    base_draw.text((556, 239), f'{buddy_num}', 'white', zzz_font_44, 'mm')
    base_draw.text((734, 239), f'{zone_layer}', 'white', zzz_font_44, 'mm')

    agent_num = len(data['avatar_list'])
    bangboo_num = len(data['buddy_list'])
    agent_h = ((agent_num - 1) // 4 + 1) * 220
    w, h = (
        950,
        660 + agent_h + ((bangboo_num - 1) // 4 + 1) * 220 + 100 + 80,
    )
    img = get_zzz_bg(w, h)

    img.paste(player_card, (0, 37), player_card)
    img.paste(base_info, (0, 137), base_info)
    img.paste(agent_banner, (0, 551), agent_banner)
    img.paste(bangboo_banner, (0, 651 + agent_h), bangboo_banner)

    for aindex, agent in enumerate(data['avatar_list']):
        rarity = agent['rarity']
        rank_icon = get_rank_img(rarity)
        element_icon = Image.open(
            TEXT_PATH / f'{ELEMENT_TYPE[agent["element_type"]]}.png'
        )
        rank_bg = Image.open(TEXT_PATH / f'{rarity}RANK_BG.png')
        rank_draw = ImageDraw.Draw(rank_bg)
        agent_icon = await get_square_avatar(agent['id'])
        rank_bg.paste(agent_icon, (19, 17), agent_icon)
        rank_bg.paste(char_fg, (0, 0), char_fg)
        rank_bg.paste(rank_icon, (20, 20), rank_icon)
        rank_bg.paste(element_icon, (130, 21), element_icon)
        rank_draw.text(
            (94, 184),
            f'等级{agent["level"]}',
            GREY,
            zzz_font_32,
            'mm',
        )
        img.paste(
            rank_bg,
            (94 + aindex % 4 * 190, 659 + aindex // 4 * 220),
            rank_bg,
        )

    for bindex, bangboo in enumerate(data['buddy_list']):
        rarity = bangboo['rarity']
        rank_icon = get_rank_img(rarity)
        rank_bg = Image.open(TEXT_PATH / f'{rarity}RANK_BG.png')
        rank_draw = ImageDraw.Draw(rank_bg)
        bangboo_icon = await get_square_bangboo(bangboo['id'])
        rank_bg.paste(bangboo_icon, (19, 17), bangboo_icon)
        rank_bg.paste(bangboo_fg, (0, 0), bangboo_fg)
        rank_bg.paste(rank_icon, (20, 20), rank_icon)
        rank_draw.text(
            (94, 184),
            f'等级{bangboo["level"]}',
            GREY,
            zzz_font_32,
            'mm',
        )
        img.paste(
            rank_bg,
            (94 + bindex % 4 * 190, 659 + bindex // 4 * 220 + agent_h + 100),
            rank_bg,
        )

    img = add_footer(img)
    return await convert_img(img)
