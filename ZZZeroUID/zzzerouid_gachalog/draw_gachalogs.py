import json
import random
from typing import Dict, List, Tuple, Union
from pathlib import Path
from datetime import datetime

import aiofiles
from PIL import Image, ImageDraw

from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from .up_windows import is_up_item
from ..utils.hint import error_reply
from ..utils.image import (
    get_footer,
    get_zzz_bg,
    get_rank_img,
    get_player_card_min,
)
from .get_gachalogs import OPTIONAL_GACHA_NAMES
from ..utils.fonts.zzz_fonts import zzz_font_18, zzz_font_20, zzz_font_32
from ..utils.resource.download_file import (
    get_weapon,
    get_square_avatar,
    get_square_bangboo,
)
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH

TEXT_PATH = Path(__file__).parent / "texture2d"
EMOJI_PATH = Path(__file__).parent / "texture2d" / "emoji"
CHAR_PATH = Path(__file__).parent / "texture2d" / "char"

first_color = (29, 29, 29)
brown_color = (41, 25, 0)
red_color = (255, 66, 66)
green_color = (74, 189, 119)
white_color = (213, 213, 213)
whole_white_color = (255, 255, 255)

RANK_MAP = {
    "4": "S",
    "3": "A",
    "2": "B",
}
HOMO_TAG = ["非到极致", "运气不好", "平稳保底", "小欧一把", "欧狗在此"]
GACHA_DISPLAY_ORDER = [
    "音擎频段",
    "独家频段",
    "常驻频段",
    "邦布频段",
    "独家重映",
    "音擎回响",
]
WEAPON_PITY_NAMES = {"音擎频段", "邦布频段", "音擎回响"}

CARD_W = 1900
COL_W = 950
TITLE_SIZE = (950, 300)
OSET = 260
BSET = 130
ITEM_COLS = 4
ITEM_W = 186
SIDE_MARGIN = 25
COL_GAP_SHRINK = 50
LEFT_X = SIDE_MARGIN
RIGHT_X = SIDE_MARGIN + COL_W - COL_GAP_SHRINK
POOL_START_Y = 257
ITEM_X_IN_BLOCK = 88
ITEM_Y_IN_BLOCK = 283
EMPTY_Y_IN_BLOCK = 278
HEADER_Y = 80
FOOTER_W = 1200
FOOTER_BOTTOM = 25
CONTENT_FOOTER_GAP = 60


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


def _pool_block_height(s_count: int) -> int:
    return OSET + get_num_h(s_count, ITEM_COLS) * BSET


def _iter_gachalogs(raw_data: Dict) -> Dict:
    src = raw_data.get("data") or {}
    ordered: Dict = {}
    for name in GACHA_DISPLAY_ORDER:
        if name not in src:
            continue
        items = src[name]
        if name in OPTIONAL_GACHA_NAMES and not items:
            continue
        if not (TEXT_PATH / f"{name}.png").exists():
            continue
        ordered[name] = items
    for name, items in src.items():
        if name in ordered:
            continue
        if name in OPTIONAL_GACHA_NAMES and not items:
            continue
        if not (TEXT_PATH / f"{name}.png").exists():
            continue
        ordered[name] = items
    return ordered


def _pack_two_columns(pools: List[str], heights: List[int]) -> Tuple[List[str], List[str]]:
    """把卡池分到两列，使整体接近矩形。

    枚举非空划分：先压画布高度，再压列差，大池靠左，左列更少。
    """
    n = len(pools)
    if n == 0:
        return [], []
    if n == 1:
        return [pools[0]], []

    tallest = max(range(n), key=lambda i: (heights[i], -i))
    best_score = None
    best_left: List[str] = []
    best_right: List[str] = []

    for mask in range(1, (1 << n) - 1):
        left: List[str] = []
        right: List[str] = []
        h_l = 0
        h_r = 0
        n_left = 0
        for i in range(n):
            if mask & (1 << i):
                left.append(pools[i])
                h_l += heights[i]
                n_left += 1
            else:
                right.append(pools[i])
                h_r += heights[i]
        score = (
            max(h_l, h_r),
            abs(h_l - h_r),
            0 if (mask & (1 << tallest)) else 1,
            n_left,
        )
        if best_score is None or score < best_score:
            best_score = score
            best_left = left
            best_right = right

    return best_left, best_right


def _normalize_title(title: Image.Image) -> Image.Image:
    title = title.convert("RGBA")
    if title.size == TITLE_SIZE:
        return title
    canvas = Image.new("RGBA", TITLE_SIZE, (0, 0, 0, 0))
    ox = (TITLE_SIZE[0] - title.size[0]) // 2
    oy = (TITLE_SIZE[1] - title.size[1]) // 2
    canvas.paste(title, (ox, oy), title)
    return canvas


def _gacha_footer_img() -> Image.Image:
    footer = get_footer().convert("RGBA")
    footer_h = int(footer.size[1] * FOOTER_W / footer.size[0])
    return footer.resize((FOOTER_W, footer_h))


def _add_gacha_footer(img: Image.Image, footer: Image.Image) -> Image.Image:
    x = (img.size[0] - footer.size[0]) // 2
    y = img.size[1] - footer.size[1] - FOOTER_BOTTOM
    img.paste(footer, (x, y), footer)
    return img


async def _make_s_item(
    item: Dict,
    item_mask: Image.Image,
    item_fg: Image.Image,
    up_icon: Image.Image,
) -> Image.Image:
    item_bg = Image.new("RGBA", (ITEM_W, BSET))
    item_bg.paste(item_mask, (0, 0), item_mask)

    item_temp = Image.new("RGBA", (ITEM_W, BSET))
    try:
        if item["item_type"] == "音擎":
            item_icon = await get_weapon(item["item_id"])
            item_icon = item_icon.resize((160, 160)).convert("RGBA")
            item_temp.paste(item_icon, (0, -18), item_icon)
        elif item["item_type"] == "邦布":
            item_icon = await get_square_bangboo(item["item_id"])
            item_icon = item_icon.convert("RGBA")
            item_temp.paste(item_icon, (32, -19), item_icon)
        else:
            item_icon = await get_square_avatar(item["item_id"])
            item_icon = item_icon.resize((175, 214)).convert("RGBA")
            item_temp.paste(item_icon, (10, -24), item_icon)
    except FileNotFoundError:
        logger.error(f"{item['item_type']}id:{item['item_id']}图片缺失")
    else:
        item_bg.paste(item_temp, (0, 0), item_mask)

    item_bg.paste(item_fg, (0, 0), item_fg)
    item_draw = ImageDraw.Draw(item_bg)
    gnum = item["gacha_num"]
    if gnum >= 80:
        gcolor = (255, 20, 20)
    elif gnum <= 60:
        gcolor = (63, 255, 0)
    else:
        gcolor = "white"
    item_draw.text((42, 102), f"{gnum}抽", gcolor, zzz_font_20, "mm")
    rank_str = RANK_MAP[item["rank_type"]]
    rank_icon = get_rank_img(rank_str, 50, 50)
    item_bg.paste(rank_icon, (122, 18), rank_icon)
    if item["is_up"]:
        item_bg.paste(up_icon, (9, 14), up_icon)
    return item_bg


async def _draw_pool_block(
    card_img: Image.Image,
    card_draw: ImageDraw.ImageDraw,
    gacha_name: str,
    gacha_data: Dict,
    base_x: int,
    base_y: int,
    item_mask: Image.Image,
    item_fg: Image.Image,
    up_icon: Image.Image,
):
    title = _normalize_title(Image.open(TEXT_PATH / f"{gacha_name}.png"))
    title_draw = ImageDraw.Draw(title)

    remain_s = f"{gacha_data['remain']}"
    avg_s = f"{gacha_data['avg']}"
    avg_up_s = f"{gacha_data['avg_up']}"
    total = f"{gacha_data['total']}"
    level = gacha_data["level"]

    if gacha_data["time_range"]:
        time_range = gacha_data["time_range"]
    else:
        time_range = "暂未抽过卡!"
    title_draw.text(
        (163, 132),
        time_range,
        (220, 220, 220),
        zzz_font_18,
        "lm",
    )

    level_path = TEXT_PATH / f"{level}"
    level_icon = Image.open(random.choice(list(level_path.iterdir())))
    level_icon = level_icon.resize((140, 140)).convert("RGBA")
    tag = HOMO_TAG[level]

    title_draw.text((253, 182), avg_s, "white", zzz_font_32, "mm")
    title_draw.text((373, 182), avg_up_s, "white", zzz_font_32, "mm")
    title_draw.text((492, 182), total, "white", zzz_font_32, "mm")
    title_draw.text((398, 106), remain_s, (63, 255, 0), zzz_font_20, "mm")

    title.paste(level_icon, (684, 51), level_icon)
    title_draw.text((757, 222), tag, "white", zzz_font_32, "mm")
    card_img.paste(title, (base_x, base_y), title)

    s_list = gacha_data["rank_s_list"]
    for index, item in enumerate(s_list):
        item_bg = await _make_s_item(item, item_mask, item_fg, up_icon)
        _x = base_x + ITEM_X_IN_BLOCK + ITEM_W * (index % ITEM_COLS)
        _y = base_y + ITEM_Y_IN_BLOCK + BSET * (index // ITEM_COLS)
        card_img.paste(item_bg, (_x, _y), item_bg)
    if not s_list:
        card_draw.text(
            (base_x + 475, base_y + EMPTY_Y_IN_BLOCK),
            "当前该卡池暂未有S_Rank数据噢!",
            (157, 157, 157),
            zzz_font_20,
            "mm",
        )


async def draw_card(uid: str, ev: Event) -> Union[str, bytes]:
    # 获取数据
    gacha_log_path = PLAYER_PATH / uid / "gacha_logs.json"
    if not gacha_log_path.exists():
        prefix = get_plugin_available_prefix("ZZZeroUID")
        return f"[绝区零] 你还没有抽卡记录噢!请绑定CK后使用{prefix}刷新抽卡记录重试!"
    async with aiofiles.open(gacha_log_path, "r", encoding="UTF-8") as f:
        raw_data: Dict = json.loads(await f.read())

    player_card = await get_player_card_min(uid, ev)

    if isinstance(player_card, int):
        return error_reply(player_card)

    gachalogs = _iter_gachalogs(raw_data)

    total_data = {}
    for gacha_name in gachalogs:
        total_data[gacha_name] = {
            "total": 0,  # 抽卡总数
            "avg": 0,  # 抽卡平均数
            "avg_up": 0,  # up平均数
            "remain": 0,  # 已xx抽未出金
            "time_range": "",
            "all_time": "",
            "r_num": [],  # 包含首位的抽卡数量
            "up_list": [],  # 抽到的UP列表
            "rank_s_list": [],  # 抽到的五星列表
            "short_gacha_data": {"time": 0, "num": 0},
            "long_gacha_data": {"time": 0, "num": 0},
            "level": 0,  # 抽卡等级
        }

    for gacha_name in gachalogs:
        num = 1
        gacha_data = gachalogs[gacha_name]
        current_data = total_data[gacha_name]
        for index, data in enumerate(gacha_data[::-1]):
            if index == 0:
                current_data["time_range"] = data["time"]
            if index == len(gacha_data) - 1:
                time_1 = datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S")
                time_2 = datetime.strptime(current_data["time_range"], "%Y-%m-%d %H:%M:%S")
                current_data["all_time"] = (time_1 - time_2).total_seconds()

                current_data["time_range"] += "~" + data["time"]

            if data["rank_type"] == "4":
                data["gacha_num"] = num

                data["is_up"] = is_up_item(gacha_name, data["name"], data["time"])

                current_data["r_num"].append(num)
                current_data["rank_s_list"].append(data)
                if data["is_up"]:
                    current_data["up_list"].append(data)

                num = 1
            else:
                num += 1
            current_data["total"] += 1

        current_data["remain"] = num - 1
        if len(current_data["rank_s_list"]) == 0:
            current_data["avg"] = "-"
        else:
            _d = sum(current_data["r_num"]) / len(current_data["r_num"])
            current_data["avg"] = float("{:.2f}".format(_d))
        # 计算平均up数量
        if len(current_data["up_list"]) == 0:
            current_data["avg_up"] = "-"
        else:
            _u = sum(current_data["r_num"]) / len(current_data["up_list"])
            current_data["avg_up"] = float("{:.2f}".format(_u))

        current_data["level"] = 2
        if current_data["avg_up"] == "-" and current_data["avg"] == "-":
            current_data["level"] = 2
        else:
            if gacha_name in WEAPON_PITY_NAMES:
                if current_data["avg_up"] != "-":
                    current_data["level"] = get_level_from_list(current_data["avg_up"], [62, 75, 88, 99, 111])
                elif current_data["avg"] != "-":
                    current_data["level"] = get_level_from_list(current_data["avg"], [51, 55, 61, 68, 70])
            else:
                if current_data["avg_up"] != "-":
                    current_data["level"] = get_level_from_list(current_data["avg_up"], [74, 87, 99, 105, 120])
                elif current_data["avg"] != "-":
                    current_data["level"] = get_level_from_list(current_data["avg"], [53, 60, 68, 73, 75])

    pool_names = list(total_data.keys())
    pool_heights = [_pool_block_height(len(total_data[n]["rank_s_list"])) for n in pool_names]
    height_map: Dict[str, int] = dict(zip(pool_names, pool_heights))
    left_pools, right_pools = _pack_two_columns(pool_names, pool_heights)
    col_h = max(
        sum(height_map[n] for n in left_pools),
        sum(height_map[n] for n in right_pools),
        0,
    )

    footer = _gacha_footer_img()
    footer_pad = CONTENT_FOOTER_GAP + footer.size[1] + FOOTER_BOTTOM
    w, h = CARD_W, POOL_START_Y + col_h + footer_pad

    # 绘制骨架
    card_img = get_zzz_bg(w, h)
    if card_img.size != (w, h):
        canvas = Image.new("RGBA", (w, h))
        tile_h = max(card_img.size[1], 1)
        for tile_y in range(0, h, tile_h):
            canvas.paste(card_img, (0, tile_y))
        card_img = canvas
    card_img.paste(player_card, (LEFT_X, HEADER_Y), player_card)
    card_draw = ImageDraw.Draw(card_img)

    item_fg = Image.open(TEXT_PATH / "char_fg.png")
    up_icon = Image.open(TEXT_PATH / "up.png")
    item_mask = Image.open(TEXT_PATH / "char_bg_and_mask.png")

    columns: List[Tuple[List[str], int]] = [(left_pools, LEFT_X)]
    if right_pools:
        columns.append((right_pools, RIGHT_X))

    for col_pools, col_x in columns:
        cur_y = POOL_START_Y
        for gacha_name in col_pools:
            await _draw_pool_block(
                card_img,
                card_draw,
                gacha_name,
                total_data[gacha_name],
                col_x,
                cur_y,
                item_mask,
                item_fg,
                up_icon,
            )
            cur_y += height_map[gacha_name]

    card_img = _add_gacha_footer(card_img, footer)
    card_img = await convert_img(card_img)
    return card_img
