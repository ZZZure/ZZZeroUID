import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Union

import aiofiles
from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.utils.image.convert import convert_img

from ..utils.hint import error_reply
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.fonts.zzz_fonts import zzz_font_18, zzz_font_20, zzz_font_32
from ..utils.image import (
    add_footer,
    get_zzz_bg,
    get_rank_img,
    get_player_card_min,
)
from ..utils.resource.download_file import (
    get_weapon,
    get_square_avatar,
    get_square_bangboo,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'
EMOJI_PATH = Path(__file__).parent / 'texture2d' / 'emoji'
CHAR_PATH = Path(__file__).parent / 'texture2d' / 'char'

first_color = (29, 29, 29)
brown_color = (41, 25, 0)
red_color = (255, 66, 66)
green_color = (74, 189, 119)
white_color = (213, 213, 213)
whole_white_color = (255, 255, 255)

RANK_MAP = {
    '4': 'S',
    '3': 'A',
    '2': 'B',
}
HOMO_TAG = ['非到极致', '运气不好', '平稳保底', '小欧一把', '欧狗在此']
NORMAL_LIST = [
    '「11号」',
    '猫又',
    '莱卡恩',
    '丽娜',
    '格莉丝',
    '珂蕾妲',
    '拘缚者',
    '燃狱齿轮',
    '嵌合编译器',
    '钢铁肉垫',
    '硫磺石',
    '啜泣摇篮',
]


def get_level_from_list(ast: int, lst: List) -> int:
    if ast == 0:
        return 2

    for num_index, num in enumerate(lst):
        if ast <= num:
            level = 4 - num_index
            break
    else:
        level = 0
    return level


def get_num_h(num: int, column: int):
    if num == 0:
        return 0
    row = ((num - 1) // column) + 1
    return row


async def draw_card(uid: str, ev: Event) -> Union[str, bytes]:
    # 获取数据
    gacha_log_path = PLAYER_PATH / uid / 'gacha_logs.json'
    if not gacha_log_path.exists():
        prefix = get_plugin_available_prefix("ZZZeroUID")
        return f'[绝区零] 你还没有抽卡记录噢!请绑定CK后使用{prefix}刷新抽卡记录重试!'
    async with aiofiles.open(gacha_log_path, 'r', encoding='UTF-8') as f:
        raw_data: Dict = json.loads(await f.read())

    player_card = await get_player_card_min(uid, ev)

    if isinstance(player_card, int):
        return error_reply(player_card)

    gachalogs = raw_data['data']
    title_num = len(gachalogs)

    total_data = {}
    for gacha_name in gachalogs:
        total_data[gacha_name] = {
            'total': 0,  # 抽卡总数
            'avg': 0,  # 抽卡平均数
            'avg_up': 0,  # up平均数
            'remain': 0,  # 已xx抽未出金
            'time_range': '',
            'all_time': '',
            'r_num': [],  # 包含首位的抽卡数量
            'up_list': [],  # 抽到的UP列表
            'rank_s_list': [],  # 抽到的五星列表
            'short_gacha_data': {'time': 0, 'num': 0},
            'long_gacha_data': {'time': 0, 'num': 0},
            'level': 0,  # 抽卡等级
        }

    for gacha_name in gachalogs:
        num = 1
        gacha_data = gachalogs[gacha_name]
        current_data = total_data[gacha_name]
        for index, data in enumerate(gacha_data[::-1]):
            if index == 0:
                current_data['time_range'] = data['time']
            if index == len(gacha_data) - 1:
                time_1 = datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S')
                time_2 = datetime.strptime(
                    current_data['time_range'], '%Y-%m-%d %H:%M:%S'
                )
                current_data['all_time'] = (time_1 - time_2).total_seconds()

                current_data['time_range'] += '~' + data['time']

            if data['rank_type'] == '4':
                data['gacha_num'] = num

                # 判断是否是UP
                if data['name'] in NORMAL_LIST:
                    data['is_up'] = False
                else:
                    data['is_up'] = True

                current_data['r_num'].append(num)
                current_data['rank_s_list'].append(data)
                if data['is_up']:
                    current_data['up_list'].append(data)

                num = 1
            else:
                num += 1
            current_data['total'] += 1

        current_data['remain'] = num - 1
        if len(current_data['rank_s_list']) == 0:
            current_data['avg'] = '-'
        else:
            _d = sum(current_data['r_num']) / len(current_data['r_num'])
            current_data['avg'] = float('{:.2f}'.format(_d))
        # 计算平均up数量
        if len(current_data['up_list']) == 0:
            current_data['avg_up'] = '-'
        else:
            _u = sum(current_data['r_num']) / len(current_data['up_list'])
            current_data['avg_up'] = float('{:.2f}'.format(_u))

        current_data['level'] = 2
        if current_data['avg_up'] == '-' and current_data['avg'] == '-':
            current_data['level'] = 2
        else:
            if gacha_name in ['音擎频段', '邦布频段']:
                if current_data['avg_up'] != '-':
                    current_data['level'] = get_level_from_list(
                        current_data['avg_up'], [62, 75, 88, 99, 111]
                    )
                elif current_data['avg'] != '-':
                    current_data['level'] = get_level_from_list(
                        current_data['avg'], [51, 55, 61, 68, 70]
                    )
            else:
                if current_data['avg_up'] != '-':
                    current_data['level'] = get_level_from_list(
                        current_data['avg_up'], [74, 87, 99, 105, 120]
                    )
                elif current_data['avg'] != '-':
                    current_data['level'] = get_level_from_list(
                        current_data['avg'], [53, 60, 68, 73, 75]
                    )

    oset = 260
    bset = 130

    _numlen = 0
    for name in total_data:
        _num = len(total_data[name]['rank_s_list'])
        _numlen += bset * get_num_h(_num, 4)
    w, h = 950, 350 + title_num * oset + _numlen

    # 绘制骨架
    card_img = get_zzz_bg(w, h)
    card_img.paste(player_card, (0, 50), player_card)
    card_draw = ImageDraw.Draw(card_img)

    y = 0
    item_fg = Image.open(TEXT_PATH / 'char_fg.png')
    up_icon = Image.open(TEXT_PATH / 'up.png')
    for gindex, gacha_name in enumerate(total_data):
        gacha_data = total_data[gacha_name]
        title = Image.open(TEXT_PATH / f'{gacha_name}.png')
        title_draw = ImageDraw.Draw(title)

        remain_s = f'{gacha_data["remain"]}'
        avg_s = f'{gacha_data["avg"]}'
        avg_up_s = f'{gacha_data["avg_up"]}'
        total = f'{gacha_data["total"]}'
        level = gacha_data["level"]

        if gacha_data['time_range']:
            time_range = gacha_data['time_range']
        else:
            time_range = '暂未抽过卡!'
        title_draw.text(
            (163, 132),
            time_range,
            (220, 220, 220),
            zzz_font_18,
            'lm',
        )

        level_path = TEXT_PATH / f'{level}'
        level_icon = Image.open(random.choice(list(level_path.iterdir())))
        level_icon = level_icon.resize((140, 140)).convert('RGBA')
        tag = HOMO_TAG[level]

        title_draw.text((253, 182), avg_s, 'white', zzz_font_32, 'mm')
        title_draw.text((373, 182), avg_up_s, 'white', zzz_font_32, 'mm')
        title_draw.text((492, 182), total, 'white', zzz_font_32, 'mm')
        title_draw.text((398, 106), remain_s, (63, 255, 0), zzz_font_20, 'mm')

        title.paste(level_icon, (684, 51), level_icon)
        title_draw.text((757, 222), tag, 'white', zzz_font_32, 'mm')

        card_img.paste(title, (0, 227 + y + gindex * oset), title)
        s_list = gacha_data['rank_s_list']
        for index, item in enumerate(s_list):
            item_bg = Image.new('RGBA', (186, 130))
            item_mask = Image.open(TEXT_PATH / 'char_bg_and_mask.png')
            item_bg.paste(item_mask, (0, 0), item_mask)

            item_temp = Image.new('RGBA', (186, 130))
            try:
                if item['item_type'] == '音擎':
                    item_icon = await get_weapon(item['item_id'])
                    item_icon = item_icon.resize((160, 160)).convert('RGBA')
                    item_temp.paste(item_icon, (0, -18), item_icon)
                elif item['item_type'] == '邦布':
                    item_icon = await get_square_bangboo(item['item_id'])
                    item_icon = item_icon.convert('RGBA')
                    item_temp.paste(item_icon, (32, -19), item_icon)
                else:
                    item_icon = await get_square_avatar(item['item_id'])
                    item_icon.resize((175, 214)).convert('RGBA')
                    item_temp.paste(item_icon, (10, -24), item_icon)
            except FileNotFoundError:
                logger.error(
                    f'{item["item_type"]}id:{item["item_id"]}图片缺失'
                )
            else:
                item_bg.paste(item_temp, (0, 0), item_mask)

            item_bg.paste(item_fg, (0, 0), item_fg)
            item_draw = ImageDraw.Draw(item_bg)
            gnum = item['gacha_num']
            if gnum >= 80:
                gcolor = (255, 20, 20)
            elif gnum <= 60:
                gcolor = (63, 255, 0)
            else:
                gcolor = 'white'
            item_draw.text((42, 102), f'{gnum}抽', gcolor, zzz_font_20, 'mm')
            rank_str = RANK_MAP[item['rank_type']]
            rank_icon = get_rank_img(rank_str, 50, 50)

            item_bg.paste(rank_icon, (122, 18), rank_icon)
            _x = 88 + 186 * (index % 4)
            _y = 510 + bset * (index // 4) + y + gindex * oset

            if item['is_up']:
                item_bg.paste(up_icon, (9, 14), up_icon)
            card_img.paste(
                item_bg,
                (_x, _y),
                item_bg,
            )
        if not s_list:
            card_draw.text(
                (475, 505 + y + gindex * oset),
                '当前该卡池暂未有S_Rank数据噢!',
                (157, 157, 157),
                zzz_font_20,
                'mm',
            )
        y += get_num_h(len(s_list), 4) * 130

    card_img = add_footer(card_img)
    card_img = await convert_img(card_img)
    return card_img
