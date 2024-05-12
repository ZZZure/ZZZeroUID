from pathlib import Path

from PIL import ImageFont

FONT_ORIGIN_PATH = Path(__file__).parent / 'FirstWorld.ttf'


def first_word_origin(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_ORIGIN_PATH), size=size)


fw_font_12 = first_word_origin(12)
fw_font_24 = first_word_origin(24)
fw_font_26 = first_word_origin(26)
fw_font_28 = first_word_origin(28)
fw_font_120 = first_word_origin(34)
