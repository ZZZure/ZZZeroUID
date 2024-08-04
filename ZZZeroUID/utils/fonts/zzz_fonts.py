from pathlib import Path

from PIL import ImageFont

FONT_ORIGIN_PATH = Path(__file__).parent / 'zzz_fonts.ttf'
FONT_THIN_PATH = Path(__file__).parent / 'zzz_thins.ttf'


def zzz_font_origin(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_ORIGIN_PATH), size=size)


def zzz_font_thin(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_THIN_PATH), size=size)


zzz_font_12 = zzz_font_origin(12)
zzz_font_14 = zzz_font_origin(14)
zzz_font_15 = zzz_font_origin(15)
zzz_font_18 = zzz_font_origin(18)
zzz_font_20 = zzz_font_origin(20)
zzz_font_22 = zzz_font_origin(22)
zzz_font_23 = zzz_font_origin(23)
zzz_font_24 = zzz_font_origin(24)
zzz_font_25 = zzz_font_origin(25)
zzz_font_26 = zzz_font_origin(26)
zzz_font_28 = zzz_font_origin(28)
zzz_font_30 = zzz_font_origin(30)
zzz_font_32 = zzz_font_origin(32)
zzz_font_34 = zzz_font_origin(34)
zzz_font_36 = zzz_font_origin(36)
zzz_font_38 = zzz_font_origin(38)
zzz_font_40 = zzz_font_origin(40)
zzz_font_42 = zzz_font_origin(42)
zzz_font_44 = zzz_font_origin(44)
zzz_font_50 = zzz_font_origin(50)
zzz_font_58 = zzz_font_origin(58)
zzz_font_60 = zzz_font_origin(60)
zzz_font_62 = zzz_font_origin(62)
zzz_font_70 = zzz_font_origin(70)
zzz_font_84 = zzz_font_origin(84)
