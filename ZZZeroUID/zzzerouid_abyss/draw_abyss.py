from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.hint import error_reply
from ..utils.zzzero_api import zzz_api
from ..utils.api.models import ChallengeNode
from ..zzzerouid_roleinfo.draw_role_info import draw_avatar, draw_bangboo
from ..utils.fonts.zzz_fonts import (
    zzz_font_20,
    zzz_font_30,
    zzz_font_32,
    zzz_font_40,
    zzz_font_60,
)
from ..utils.image import (
    GREY,
    add_footer,
    get_zzz_bg,
    get_rank_img,
    get_element_img,
    get_player_card_min,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'
ERROR_HINT = '''❌[绝区零] 你还没有解锁/挑战过【‌式舆防卫战】的记录噢！
如果你已挑战过, 请稍等片刻, 等待数据同步后查询！'''
RANK_COLOR = {'B': (39, 193, 255), 'A': (206, 34, 247), 'S': (255, 135, 0)}


def format_timestamp(timestamp: int):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%m/%d")


def format_seconds(seconds: float):
    hours = seconds // 3600
    minute = (seconds % 3600) // 60
    second = seconds % 60
    return f"{hours}小时{minute}分钟{second}秒"


async def draw_team(
    node: ChallengeNode,
    time: str,
    floor_img: Image.Image,
    pos_y: int = 114,
):
    team_bar = Image.open(TEXT_PATH / 'team_bar.png')
    team_draw = ImageDraw.Draw(team_bar)
    node_element = node['element_type_list']
    team_draw.text(
        (690, 35),
        time,
        GREY,
        zzz_font_20,
        'rm',
    )
    team_draw.text(
        (135, 38),
        '队伍1',
        'white',
        zzz_font_30,
        'lm',
    )
    for eindex, element in enumerate(node_element):
        element_img = get_element_img(element, 32, 32)
        team_bar.paste(
            element_img,
            (767 + eindex * 32, 21),
            element_img,
        )
    floor_img.paste(team_bar, (0, pos_y), team_bar)

    for aindex, agent in enumerate(node['avatars']):
        avatar_img = await draw_avatar(agent)
        floor_img.paste(
            avatar_img,
            (99 + aindex * 190, pos_y + 55),
            avatar_img,
        )

    if 'buddy' in node:
        bangboo_img = await draw_bangboo(node['buddy'])
        bangboo_img = bangboo_img.resize((152, 176))
        floor_img.paste(
            bangboo_img,
            (681, pos_y + 91),
            bangboo_img,
        )
    return floor_img


async def draw_abyss_img(
    uid: str,
    ev: Event,
    schedule_type: int = 1,
    is_full: bool = False,
):
    data = await zzz_api.get_zzz_challenge_info(
        uid,
        schedule_type,
    )
    if isinstance(data, int):
        return error_reply(data)

    if 'has_data' not in data or not data['has_data']:
        return ERROR_HINT

    player_card = await get_player_card_min(uid, ev)
    if isinstance(player_card, int):
        return error_reply(player_card)

    w, h = 950, 710 + 700 * len(data['all_floor_detail']) + 100

    img = get_zzz_bg(w, h, 'bg2')
    title = Image.open(TEXT_PATH / 'title.png')
    banner = Image.open(TEXT_PATH / 'banner.png')
    title_draw = ImageDraw.Draw(title)

    fast_layer_time = data['fast_layer_time']
    layer_time = format_seconds(fast_layer_time)
    max_layer = data['max_layer']
    begin = format_timestamp(int(data['begin_time']))
    end = format_timestamp(int(data['end_time']))

    s_num, a_num, b_num = 0, 0, 0
    for i in data['rating_list']:
        if i['rating'] == 'B':
            b_num += i['times']
        elif i['rating'] == 'A':
            a_num += i['times']
        else:
            s_num += i['times']

    for index, num in enumerate([s_num, a_num, b_num]):
        title_draw.text(
            (402 + 109 * index, 285),
            f'{num}',
            'white',
            zzz_font_30,
            'mm',
        )

    title_draw.text(
        (302, 367),
        layer_time,
        'white',
        zzz_font_32,
        'lm',
    )
    title_draw.text(
        (723, 367),
        f'第{max_layer}防线',
        'white',
        zzz_font_32,
        'lm',
    )
    title_draw.text(
        (224, 256),
        begin,
        (81, 81, 81),
        zzz_font_60,
        'mm',
    )
    title_draw.text(
        (733, 256),
        end,
        (81, 81, 81),
        zzz_font_60,
        'mm',
    )

    img.paste(player_card, (0, 70), player_card)
    img.paste(title, (0, 190), title)
    img.paste(banner, (0, 610), banner)

    if is_full:
        abyss_data = data['all_floor_detail']
    else:
        abyss_data = data['all_floor_detail'][:3]

    for floor_num, floor_data in enumerate(abyss_data):
        floor_img = Image.open(TEXT_PATH / 'floor.png')
        floor_draw = ImageDraw.Draw(floor_img)
        rating = floor_data['rating']
        zone_name = floor_data['zone_name']
        color = RANK_COLOR.get(rating, 'white')
        times = floor_data['floor_challenge_time']
        time1 = f'{times["year"]}.{times["month"]}.{times["day"]}'
        time2 = f'{times["hour"]}:{times["minute"]}:{times["second"]}'
        time = f'{time1} {time2}'

        rank_img = get_rank_img(rating, 51, 51)
        floor_img.paste(rank_img, (76, 57), rank_img)
        floor_draw.text(
            (138, 83),
            zone_name,
            'black',
            zzz_font_40,
            'lm',
            stroke_width=5,
            stroke_fill='black',
        )
        floor_draw.text(
            (138, 83),
            zone_name,
            color,
            zzz_font_40,
            'lm',
        )

        await draw_team(
            floor_data['node_1'],
            time,
            floor_img,
            115,
        )
        await draw_team(
            floor_data['node_2'],
            time,
            floor_img,
            385,
        )
        img.paste(floor_img, (0, 720 + floor_num * 700), floor_img)

    img = add_footer(img)
    res = await convert_img(img)
    return res
