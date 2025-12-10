from typing import Union, Sequence
from pathlib import Path

from PIL import Image, ImageDraw

from gsuid_core.models import Event
from gsuid_core.utils.database.models import CoreUser
from gsuid_core.utils.image.image_tools import (
    crop_center_img,
    get_avatar_with_ring,
)

from .zzzero_api import zzz_api
from .name_convert import char_id_to_sprite, equip_id_to_sprite
from .fonts.zzz_fonts import zzz_font_28, zzz_font_30, zzz_font_38
from .resource.RESOURCE_PATH import SUIT_PATH
from ..utils.resource.RESOURCE_PATH import (
    CAMP_PATH,
    MIND_PATH,
    ROLECIRCLE_PATH,
    ROLEGENERAL_PATH,
)

TEXT_PATH = Path(__file__).parent / "texture2d"
GREY = (216, 216, 216)
BLACK_G = (40, 40, 40)
YELLOW = (255, 200, 1)
BLUE = (1, 183, 255)

ELEMENT_TYPE = {
    203: "电属性",
    205: "以太属性",
    202: "冰属性",
    200: "物理属性",
    201: "火属性",
}

prop_id = {
    "111": "IconHpMax",
    "121": "IconAttack",
    "131": "IconDef",
    "122": "IconBreakStun",
    "201": "IconCrit",
    "211": "IconCritDam",
    "314": "IconElementAbnormalPower",
    "312": "IconElementMystery",
    "231": "IconPenRatio",
    "232": "IconPenValue",
    "305": "IconSpRecover",
    "310": "IconSpGetRatio",
    "115": "IconSpMax",
    "315": "IconPhysDmg",
    "316": "IconFire",
    "317": "IconIce",
    "318": "IconThunder",
    "319": "IconDungeonBuffEther",
}

pro_id = {
    "1": "IconAttack",  # 强攻
    "2": "IconStun",  # 击破
    "3": "IconAnomaly",  # 异常
    "4": "IconSupport",  # 支援
    "5": "IconDefense",  # 防御
    "6": "IconRupture",  # 命破
}

camp_map = {
    "白祇重工": "BelobogIndustries",
    "奥波勒斯小队": "Obols",
    "狡兔屋": "GentleHouse",
    "对空洞特别行动部第六课": "H.S.O-S6",
    "卡吕冬之子": "SonsOfCalydon",
    "维多利亚家政": "VictoriaHousekeepingCo.",
    "新艾利都治安局": "N.E.P.S.",
    "刑侦特勤组": "JaneBadge",
    "天琴座": "StarsOfLyra",
    "防卫军·白银小队": "Silvers",
    "防卫军·奥波勒斯小队": "Obols",
    "反舌鸟": "MockingBird",
    "云岿山": "Suibian",
    "怪啖屋": "SpookShack",
    "坎卜斯黑枝": "BlackRoot",
}


def get_camp_img(camp_name: str):
    name = camp_map[camp_name]
    return Image.open(CAMP_PATH / f"IconCamp{name}.png")


def get_mind_role_img(_id: Union[str, int], _type: str = "3"):
    path = MIND_PATH / f"Mindscape_{_id}_{_type}.png"
    if not path.exists():
        path = MIND_PATH / "Mindscape_1291_1.png"
    return Image.open(path)


def get_general_role_img(_id: Union[str, int], w: int = 180, h: int = 64):
    char_id = str(_id)
    sprite_id = char_id_to_sprite(char_id)
    path = ROLEGENERAL_PATH / f"IconRoleGeneral{sprite_id}.png"
    if not path.exists():
        path = ROLEGENERAL_PATH / "IconRoleGeneral03.png"
    return Image.open(path).resize((w, h)).convert("RGBA")


def get_circle_role_img(_id: Union[str, int], w: int = 142, h: int = 142):
    char_id = str(_id)
    sprite_id = char_id_to_sprite(char_id)
    path = ROLECIRCLE_PATH / f"IconRoleCircle{sprite_id}.png"
    if not path.exists():
        path = ROLECIRCLE_PATH / "IconRoleCircle03.png"
    return Image.open(path).resize((w, h)).convert("RGBA")


def get_pro_img(_id: Union[str, int], w: int = 50, h: int = 50):
    img = Image.new("RGBA", (100, 100))
    propid = str(_id)
    prop_icon = pro_id.get(propid)
    if not prop_icon:
        return img.resize((w, h))

    icon = Image.open(TEXT_PATH / "pro" / f"{prop_icon}.png")
    return icon.resize((w, h)).convert("RGBA")


def get_prop_img(_id: Union[str, int], w: int = 40, h: int = 40):
    img = Image.new("RGBA", (70, 70))
    propid = str(_id)
    if propid.isdigit():
        propid = propid[:3]
        prop_icon = prop_id.get(propid)
    else:
        prop_icon = propid

    if not prop_icon:
        return img.resize((w, h))

    icon = Image.open(TEXT_PATH / "prop" / f"{prop_icon}.png")
    x, y = icon.size
    img.paste(icon, (35 - x // 2, 35 - y // 2), icon)
    return img.resize((w, h))


def get_element_img(elemet_id: Union[int, str], w: int = 40, h: int = 40):
    elemet_id = int(elemet_id)
    if elemet_id not in ELEMENT_TYPE:
        return Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img = Image.open(TEXT_PATH / f"{ELEMENT_TYPE[elemet_id]}.png")
    return img.resize((w, h)).convert("RGBA")


def get_equip_img(equip_id: str, w: int = 90, h: int = 90):
    sprite_id = equip_id_to_sprite(equip_id)
    if sprite_id:
        sprite_id = sprite_id[2:]
        img = Image.open(SUIT_PATH / f"{sprite_id}.png")
        return img.resize((w, h)).convert("RGBA")
    else:
        return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def get_rarity_img(rank: str, w: int = 80, h: int = 80):
    rank = rank.upper()
    if rank in ["S", "A", "B", "C"]:
        img = Image.open(TEXT_PATH / f"Rarity_{rank}.png")
        return img.resize((w, h)).convert("RGBA")
    else:
        return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def get_rank_img(rank: str, w: int = 40, h: int = 40):
    rank = rank.upper()
    if rank in ["S", "A", "B"]:
        img = Image.open(TEXT_PATH / f"{rank}RANK.png")
        return img.resize((w, h)).convert("RGBA")
    else:
        return Image.new("RGBA", (w, h), (0, 0, 0, 0))


async def get_player_card_min(
    uid: str,
    ev: Event,
    world: str = "",
):
    data = await zzz_api.get_zzz_user_info_g(uid)
    if isinstance(data, int):
        nickname = None
        if ev.at:
            nicknames: Sequence[CoreUser] = await CoreUser.select_rows(user_id=ev.at)
            if nicknames:
                nickname = nicknames[0].user_name
        else:
            nickname = ev.sender["nickname"] if ev.sender and "nickname" in ev.sender else "绳匠"

        if nickname is None:
            nickname = "未知绳匠"

        data = {
            "nickname": nickname,
            "level": "未知",
            "region_name": "新艾丽都",
        }

    user_name = data["nickname"]
    world_level = str(data["level"])
    if world:
        region_name = world
    else:
        region_name = data["region_name"]

    player_card = Image.open(TEXT_PATH / "player_card_min.png")
    card_draw = ImageDraw.Draw(player_card)

    avatar = await get_avatar_with_ring(ev, 129, is_ring=False)
    player_card.paste(avatar, (105, 30), avatar)

    card_draw.text((290, 120), f"UID {uid}", GREY, zzz_font_30, "lm")
    card_draw.text((290, 64), user_name, "white", zzz_font_38, "lm")

    text_lenth = card_draw.textlength(user_name, zzz_font_38)

    xs, ys = 290 + text_lenth + 20, 45
    xt, yt = xs + 90 + 12, 45
    card_draw.rounded_rectangle((xs, ys, xs + 90, ys + 35), 10, YELLOW)
    card_draw.rounded_rectangle((xt, yt, xt + 144, yt + 35), 10, BLUE)

    if world_level != "未知":
        level_str = f"Lv.{world_level}"
    else:
        level_str = "未知"

    card_draw.text(
        (xs + 45, ys + 17),
        level_str,
        BLACK_G,
        zzz_font_28,
        "mm",
    )
    card_draw.text(
        (xt + 72, yt + 17),
        region_name,
        BLACK_G,
        zzz_font_28,
        "mm",
    )
    return player_card


def get_zzz_bg(
    w: int,
    h: int,
    bg: Union[str, Path] = "bg",
) -> Image.Image:
    if isinstance(bg, Path):
        img = Image.open(bg).convert("RGBA")
    else:
        img = Image.open(TEXT_PATH / f"{bg}.jpg").convert("RGBA")
    return crop_center_img(img, w, h)


def get_footer():
    return Image.open(TEXT_PATH / "footer.png")


def add_footer(img: Image.Image, w: int = 0) -> Image.Image:
    footer = get_footer()
    w = img.size[0] if not w else w
    if w != footer.size[0]:
        footer = footer.resize(
            (w, int(footer.size[1] * w / footer.size[0])),
        )
    x, y = (
        int((img.size[0] - footer.size[0]) / 2),
        img.size[1] - footer.size[1] - 10,
    )
    img.paste(footer, (x, y), footer)
    return img
