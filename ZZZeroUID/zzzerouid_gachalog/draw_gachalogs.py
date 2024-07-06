from pathlib import Path

from PIL import Image, ImageDraw
from gsuid_core.utils.image.image_tools import draw_pic_with_ring
from gsuid_core.plugins.ZZZeroUID.ZZZeroUID.utils.fonts.zzz_fonts import (
    zzz_font_26,
    zzz_font_36,
    zzz_font_38,
)

TEXT_PATH = Path(__file__).parent / "texture2d"
EMOJI_PATH = Path(__file__).parent / "texture2d" / "emoji"
CHAR_PATH = Path(__file__).parent / "texture2d" / "char"

first_color = (29, 29, 29)
brown_color = (41, 25, 0)
red_color = (255, 66, 66)
green_color = (74, 189, 119)
white_color = (213, 213, 213)
whole_white_color = (255, 255, 255)

CHANGE_MAP = {
    "始发跃迁": "begin",
    "群星跃迁": "normal",
    "角色跃迁": "char",
    "光锥跃迁": "weapon",
}
HOMO_TAG = ["非到极致", "运气不好", "平稳保底", "小欧一把", "欧狗在此"]
NORMAL_LIST = [
    "彦卿",
    "白露",
    "姬子",
    "瓦尔特",
    "布洛妮娅",
    "克拉拉",
    "杰帕德",
    "银河铁道之夜",
    "以世界之名",
    "但战斗还未结束",
    "制胜的瞬间",
    "无可取代的东西",
    "时节不居",
    "如泥酣眠",
]

UP_LIST = {
    "刻晴": [(2021, 2, 17, 18, 0, 0), (2021, 3, 2, 15, 59, 59)],
    "提纳里": [(2022, 8, 24, 11, 0, 0), (2022, 9, 9, 17, 59, 59)],
    "迪希雅": [(2023, 3, 1, 11, 0, 0), (2023, 3, 21, 17, 59, 59)],
}


async def draw_card():
    # 绘制骨架
    card_img = Image.open(TEXT_PATH / "bg.jpg")
    item_avatar_title = Image.open(TEXT_PATH / "title.png")
    item_sp_title = Image.open(TEXT_PATH / "sp_title.png")
    item_nm_title = Image.open(TEXT_PATH / "nm_title.png")
    item_wp_title = Image.open(TEXT_PATH / "wp_title.png")
    item_footer_title = Image.open(TEXT_PATH / "footer.png")

    card_img_draw = ImageDraw.Draw(card_img)
    card_img.paste(item_avatar_title, (0, 0), item_avatar_title)
    card_img.paste(item_footer_title, (0, 2250), item_footer_title)
    card_img.paste(item_sp_title, (0, 450), item_sp_title)
    card_img.paste(item_wp_title, (0, 1050), item_wp_title)
    card_img.paste(item_nm_title, (0, 1650), item_nm_title)
    # 头像
    item_avatar = Image.open(CHAR_PATH / "NicoleAvailable.png").convert("RGBA")
    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    mask = mask_pic.resize((300, 300))
    char_pic = await draw_pic_with_ring(item_avatar, 300, None, False)
    card_img.paste(char_pic, (330, 65), mask)
    # UID
    uid = "UID 3123123333"
    card_img_draw.text((480, 450), uid, whole_white_color, zzz_font_36, "mm")

    # up数据绘制
    up_gacha_cur = 30
    up_gacha_avg_s = 30
    up_gacha_avg_up = 30
    up_gacha_total = 30
    up_tag = "运气一般"
    # TODO TAG列表绘制
    card_img_draw.text(
        (397, 555),
        str(up_gacha_cur),
        red_color,
        zzz_font_26,
        "mm",
    )
    card_img_draw.text(
        (255, 630),
        str(up_gacha_avg_s),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (370, 630),
        str(up_gacha_avg_up),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (490, 630),
        str(up_gacha_total),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (730, 670),
        up_tag,
        whole_white_color,
        zzz_font_38,
        "mm",
    )

    # 音擎数据绘制
    wp_gacha_cur = 30
    wp_gacha_avg_s = 30
    wp_gacha_avg_up = 30
    wp_gacha_total = 30
    wp_tag = "超级欧皇"

    card_img_draw.text(
        (397, 1155),
        str(wp_gacha_cur),
        red_color,
        zzz_font_26,
        "mm",
    )
    card_img_draw.text(
        (255, 1230),
        str(wp_gacha_avg_s),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (370, 1230),
        str(wp_gacha_avg_up),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (490, 1230),
        str(wp_gacha_total),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (730, 1270),
        wp_tag,
        whole_white_color,
        zzz_font_38,
        "mm",
    )

    # 常驻池绘制
    nm_gacha_cur = 30
    nm_gacha_avg_s = 30
    nm_gacha_avg_up = 30
    nm_gacha_total = 30
    nm_tag = "超级欧皇"

    card_img_draw.text(
        (397, 1155),
        str(nm_gacha_cur),
        red_color,
        zzz_font_26,
        "mm",
    )
    card_img_draw.text(
        (255, 1230),
        str(nm_gacha_avg_s),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (370, 1230),
        str(nm_gacha_avg_up),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (490, 1230),
        str(nm_gacha_total),
        whole_white_color,
        zzz_font_38,
        "mm",
    )
    card_img_draw.text(
        (730, 1270),
        nm_tag,
        whole_white_color,
        zzz_font_38,
        "mm",
    )

    card_img.save("test.png")
