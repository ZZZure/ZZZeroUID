from typing import Union
from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw

from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.hint import error_reply
from ..utils.image import (
    GREY,
    add_footer,
    get_zzz_bg,
    get_rank_img,
    get_level_img,
    get_player_card_min,
)
from ..utils.api.models import FifthLayerChallengeItem, FourthLayerChallengeItem
from ..utils.zzzero_api import zzz_api
from ..utils.fonts.zzz_fonts import (
    zzz_font_20,
    zzz_font_30,
    zzz_font_32,
    zzz_font_40,
    zzz_font_60,
)
from ..zzzerouid_mem.draw_mem import get_rank_tier
from ..zzzerouid_roleinfo.draw_role_info import draw_avatar, draw_bangboo

TEXT_PATH = Path(__file__).parent / "texture2d"
ERROR_HINT = """❌[绝区零] 你还没有解锁/挑战过【‌式舆防卫战】的记录噢！
如果你已挑战过, 请稍等片刻, 等待数据同步后查询！"""
RANK_COLOR = {"B": (39, 193, 255), "A": (206, 34, 247), "S": (255, 135, 0)}


def format_timestamp(timestamp: int):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%m/%d")


def format_seconds(seconds: float):
    # hours = seconds // 3600
    minute = (seconds % 3600) // 60
    second = seconds % 60
    return f"{minute}分钟{second}秒"


async def draw_team(
    node: Union[FifthLayerChallengeItem, FourthLayerChallengeItem],
    floor_img: Image.Image,
    team_index: int = 0,
    pos_y: int = 114,
):
    if "score" in node:
        rating = node["rating"]
        _p = TEXT_PATH / f"team_bar_{rating.lower()}.png"
        if _p.exists():
            team_bar = Image.open(TEXT_PATH / f"team_bar_{rating.lower()}.png")
        else:
            team_bar = Image.open(TEXT_PATH / "team_bar.png")
    else:
        team_bar = Image.open(TEXT_PATH / "team_bar.png")

    team_draw = ImageDraw.Draw(team_bar)

    # node_element = node["element_type_list"]

    battle_time = node["battle_time"]
    battle_time = format_seconds(battle_time)

    team_draw.text(
        (818, 42),
        battle_time,
        GREY,
        zzz_font_20,
        "rm",
    )
    if "score" in node:
        score = node["score"]
        team_draw.text(
            (184, 38),
            f"{score}分",
            "white",
            zzz_font_30,
            "lm",
        )
        level = get_level_img(node["rating"], 51, 51)
        team_bar.paste(
            level,
            (121, 12),
            level,
        )
    else:
        team_draw.text(
            (135, 38),
            f"队伍{team_index + 1}",
            "white",
            zzz_font_30,
            "lm",
        )
    """
    for eindex, element in enumerate(node_element):
        element_img = get_element_img(element, 32, 32)
        team_bar.paste(
            element_img,
            (767 + eindex * 32, 21),
            element_img,
        )
    """

    floor_img.paste(team_bar, (0, pos_y), team_bar)

    for aindex, agent in enumerate(node["avatar_list"]):
        avatar_img = await draw_avatar(agent)
        floor_img.paste(
            avatar_img,
            (105 + aindex * 190, pos_y + 55),
            avatar_img,
        )

    if "buddy" in node:
        bangboo_img = await draw_bangboo(node["buddy"])
        bangboo_img = bangboo_img.resize((152, 176))
        floor_img.paste(
            bangboo_img,
            (685, pos_y + 91),
            bangboo_img,
        )
    return floor_img


async def draw_challenge_img(
    uid: str,
    ev: Event,
    schedule_type: int = 1,
    is_full: bool = False,
):
    data_raw = await zzz_api.get_zzz_hadal_info(
        uid,
        schedule_type,
    )
    if isinstance(data_raw, int):
        return error_reply(data_raw)

    data = data_raw["hadal_info_v2"]

    if "fourth_layer_detail" not in data or not data["fourth_layer_detail"]:
        return ERROR_HINT

    player_card = await get_player_card_min(uid, ev)
    if isinstance(player_card, int):
        return error_reply(player_card)

    """
    if is_full:
        abyss_data = data["fitfh_layer_detail"]
    else:
        abyss_data = data["fitfh_layer_detail"][:3]
    """

    abyss_data_5 = []
    abyss_data_4 = []

    if (
        "fitfh_layer_detail" in data
        and data["fitfh_layer_detail"]
        and "layer_challenge_info_list" in data["fitfh_layer_detail"]
        and data["fitfh_layer_detail"]["layer_challenge_info_list"]
    ):
        abyss_data_5 = data["fitfh_layer_detail"]["layer_challenge_info_list"]

    if (
        "fourth_layer_detail" in data
        and data["fourth_layer_detail"]
        and "layer_challenge_info_list" in data["fourth_layer_detail"]
        and data["fourth_layer_detail"]["layer_challenge_info_list"]
    ):
        abyss_data_4 = [data["fourth_layer_detail"]]

    w, h = 950, 710 + 100

    if abyss_data_4:
        h += 700

    if abyss_data_5:
        h += 1000

    img = get_zzz_bg(w, h, "bg2")
    title = Image.open(TEXT_PATH / "title.png")
    banner = Image.open(TEXT_PATH / "banner.png")
    title_draw = ImageDraw.Draw(title)

    fast_layer_time = data["brief"]["battle_time"]
    layer_time = format_seconds(fast_layer_time)
    max_layer = data["brief"]["cur_period_zone_layer_count"]

    layer_name = f"第{max_layer}防线"
    begin = format_timestamp(int(data["begin_time"]))
    end = format_timestamp(int(data["end_time"]))

    s_num, a_num, b_num = 0, 0, 0

    for i in abyss_data_5 + abyss_data_4:
        if i["rating"] == "B":
            b_num += 1
        elif i["rating"] == "A":
            a_num += 1
        else:
            s_num += 1

    for index, num in enumerate([s_num, a_num, b_num]):
        title_draw.text(
            (402 + 109 * index, 285),
            f"{num}",
            "white",
            zzz_font_30,
            "mm",
        )

    title_draw.text(
        (302, 367),
        layer_time,
        "white",
        zzz_font_32,
        "lm",
    )
    title_draw.text(
        (723, 367),
        layer_name,
        "white",
        zzz_font_32,
        "lm",
    )
    title_draw.text(
        (224, 256),
        begin,
        (81, 81, 81),
        zzz_font_60,
        "mm",
    )
    title_draw.text(
        (733, 256),
        end,
        (81, 81, 81),
        zzz_font_60,
        "mm",
    )

    img.paste(player_card, (0, 70), player_card)
    img.paste(title, (0, 190), title)
    img.paste(banner, (0, 610), banner)

    y = 720

    for floor_num, floor_data in enumerate(abyss_data_4):
        floor_img = Image.open(TEXT_PATH / "floor.png")
        floor_draw = ImageDraw.Draw(floor_img)
        rating = floor_data["rating"]
        zone_name = "第四节点"
        color = RANK_COLOR.get(rating, "white")

        rank_img = get_rank_img(rating, 51, 51)
        floor_img.paste(rank_img, (76, 57), rank_img)
        floor_draw.text(
            (138, 83),
            zone_name,
            "black",
            zzz_font_40,
            "lm",
            stroke_width=5,
            stroke_fill="black",
        )
        floor_draw.text(
            (138, 83),
            zone_name,
            color,
            zzz_font_40,
            "lm",
        )

        await draw_team(
            floor_data["layer_challenge_info_list"][0],
            floor_img,
            0,
            115,
        )
        await draw_team(
            floor_data["layer_challenge_info_list"][1],
            floor_img,
            1,
            385,
        )
        img.paste(floor_img, (0, 720 + floor_num * 700), floor_img)
        y += 700

    if abyss_data_5:
        floor_img = Image.open(TEXT_PATH / "floor5.png")
        floor_draw = ImageDraw.Draw(floor_img)
        rating = data["brief"]["rating"]
        score = data["brief"]["score"]
        zone_name = f"{layer_name}"
        color = RANK_COLOR.get(rating, "white")

        rank_percent = data["brief"]["rank_percent"] / 100

        rank_tier = get_rank_tier(rank_percent)
        rank_img = get_rank_img(rating, 64, 64)
        floor_img.paste(rank_img, (70, 50), rank_img)
        floor_img.paste(rank_tier, (618, 33), rank_tier)

        floor_draw.text(
            (645, 84),
            f"{score}分",
            "white",
            zzz_font_40,
            "rm",
        )

        floor_draw.text(
            (138, 83),
            zone_name,
            "black",
            zzz_font_40,
            "lm",
            stroke_width=5,
            stroke_fill="black",
        )
        floor_draw.text(
            (138, 83),
            zone_name,
            color,
            zzz_font_40,
            "lm",
        )

        await draw_team(
            abyss_data_5[0],
            floor_img,
            0,
            138,
        )
        await draw_team(
            abyss_data_5[1],
            floor_img,
            1,
            408,
        )
        await draw_team(
            abyss_data_5[2],
            floor_img,
            2,
            678,
        )
        img.paste(floor_img, (0, y), floor_img)

    img = add_footer(img)
    res = await convert_img(img)
    return res
