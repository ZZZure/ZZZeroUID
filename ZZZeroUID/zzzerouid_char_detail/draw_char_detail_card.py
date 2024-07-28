import json
from pathlib import Path
from typing import Dict, Tuple, Union

import aiofiles
from PIL import Image, ImageDraw
from gsuid_core.utils.image.convert import convert_img

from ..utils.zzzero_prefix import PREFIX
from .data.char_offset import char_offset
from ..utils.resource.download_file import get_weapon
from ..utils.resource.RESOURCE_PATH import ROLE_PATH, PLAYER_PATH
from ..utils.name_convert import (
    char_id_to_sprite,
    char_id_to_full_name,
    char_name_to_char_id,
)
from ..utils.fonts.zzz_fonts import (
    zzz_font_20,
    zzz_font_24,
    zzz_font_28,
    zzz_font_30,
    zzz_font_34,
    zzz_font_50,
)
from ..utils.image import (
    add_footer,
    get_zzz_bg,
    get_prop_img,
    get_rank_img,
    get_equip_img,
    get_rarity_img,
    get_element_img,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'
STAR_PATH = TEXT_PATH / 'star'

PROP_POS_MAP = {
    '生命值': (554, 140),
    '攻击力': (554, 199),
    '防御力': (554, 258),
    '冲击力': (554, 317),
    '暴击率': (554, 376),
    '暴击伤害': (554, 433),
    '异常掌控': (554, 491),
    '异常精通': (554, 550),
    '穿透率': (554, 609),
    '能量自动回复': (554, 667),
}
PROFESSION_MAP = {}
SKILL_MAP = {
    0: 0,
    2: 1,
    6: 2,
    1: 3,
    3: 4,
    5: 5,
}
GREY = (210, 210, 210)
BLUE = (0, 151, 255)
YELLOW = (255, 188, 0)


def get_skill_dict(data: Dict):
    skills = data['skills']
    result: Dict[int, Tuple[int, Tuple[int, int, int]]] = {}

    for skill in skills:
        skill_type = skill['skill_type']
        skill_pos_num = SKILL_MAP.get(skill_type, 0)
        skill_level = skill['level']
        if skill_level >= 11:
            skill_color = YELLOW
        elif skill_level >= 6:
            skill_color = BLUE
        elif skill_level >= 3:
            skill_color = (255, 255, 255)
        else:
            skill_color = GREY

        result[skill_pos_num] = skill_level, skill_color

    return result


async def draw_char_detail_img(uid: str, char: str) -> Union[str, bytes]:
    char_id = char_name_to_char_id(char)
    if not char_id:
        return f'[绝区零] 角色名{char}无法找到, 可能暂未适配, 请先检查输入是否正确！'

    path = PLAYER_PATH / str(uid) / f'{char_id}.json'
    if not path.exists():
        return (
            f'[绝区零] 未找到该角色信息, 请先使用[{PREFIX}刷新面板]进行刷新!'
        )

    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        data = json.loads(await f.read())  # noqa: F841

    img = get_zzz_bg(950, 2100)

    # 角色部分
    char_bg = Image.new('RGBA', (2000, 2100))
    offset = char_offset[char_id]
    char_sprite = char_id_to_sprite(char_id)
    char_img = Image.open(ROLE_PATH / f'IconRole{char_sprite}.png')
    char_img = char_img.convert('RGBA')
    char_bg.paste(char_img, offset, char_img)
    img.paste(char_bg, (-525, 0), char_bg)

    # 属性部分
    props = data['properties']
    property_bg = Image.open(TEXT_PATH / 'property_bg.png')
    property_draw = ImageDraw.Draw(property_bg)
    for prop in props:
        if prop['property_name'] in PROP_POS_MAP:
            x, y = PROP_POS_MAP[prop['property_name']]
            property_draw.text(
                (x, y),
                f'{prop["final"]}',
                'white',
                zzz_font_30,
                'rm',
            )
    img.paste(property_bg, (361, 136), property_bg)

    # 信息部分
    full_name = char_id_to_full_name(char_id)
    level = data['level']
    profession = data['avatar_profession']
    rank = data['rank']
    char_star = Image.open(STAR_PATH / f'{profession}.png')
    element_icon = get_element_img(data['element_type'], 70, 70)
    rarity_icon = get_rank_img(data['rarity'], 70, 70)

    if len(full_name) > 10:
        full_name = full_name.split('·')[0]
    info_bg = Image.open(TEXT_PATH / 'info_bg.png')
    info_draw = ImageDraw.Draw(info_bg)
    info_draw.text((213, 65), full_name, 'white', zzz_font_50, 'lm')
    info_draw.text((171, 121), f'Lv.{level}', 'white', zzz_font_30, 'mm')
    info_bg.paste(char_star, (223, 101), char_star)
    for r in range(rank + 1):
        if r == 0:
            continue
        rank_icon = Image.open(TEXT_PATH / 'ranks' / f'{r}.png')
        rank_icon = rank_icon.resize((31, 31)).convert('RGBA')
        info_bg.paste(rank_icon, (394 + 34 * (r - 1), 105), rank_icon)
    info_bg.paste(element_icon, (142, 35), element_icon)
    info_bg.paste(rarity_icon, (75, 35), rarity_icon)
    img.paste(info_bg, (340, 17), info_bg)

    # 技能部分
    skill_dict = get_skill_dict(data)
    skill_bg = Image.open(TEXT_PATH / 'skill_bg.png')
    skill_draw = ImageDraw.Draw(skill_bg)
    for skill_pos_num in skill_dict:
        skill_level, skill_color = skill_dict[skill_pos_num]
        skill_draw.text(
            (62 + skill_pos_num * 80, 73),
            f'{skill_level}',
            skill_color,
            zzz_font_30,
            'mm',
        )
    img.paste(skill_bg, (-33, 996), skill_bg)

    # 武器部分
    weapon = data['weapon']
    weapon_name = weapon['name']
    weapon_level = weapon['level']
    main_ps = weapon['main_properties']
    weapon_ps = weapon['properties']
    weapon_rarity_icon = get_rarity_img(weapon['rarity'])
    weapon_star_icon = Image.open(STAR_PATH / f'{weapon["star"]}.png')
    weapon_img = await get_weapon(weapon['id'])
    weapon_img = weapon_img.resize((260, 260)).convert('RGBA')

    weapon_bg = Image.open(TEXT_PATH / 'weapon_bg.png')
    weapon_draw = ImageDraw.Draw(weapon_bg)

    weapon_bg.paste(weapon_rarity_icon, (30, 37), weapon_rarity_icon)
    weapon_bg.paste(weapon_star_icon, (16, 113), weapon_star_icon)
    weapon_bg.paste(weapon_img, (250, 33), weapon_img)
    weapon_draw.text((112, 76), weapon_name, 'white', zzz_font_34, 'lm')
    weapon_draw.rounded_rectangle((195, 114, 281, 148), 10, (255, 200, 0))
    weapon_draw.text(
        (238, 130),
        f'Lv.{weapon_level}',
        (40, 40, 40),
        zzz_font_28,
        'mm',
    )
    main_p = main_ps[0]
    main_prop_id = main_p['property_id']
    main_prop_img = get_prop_img(main_prop_id)
    weapon_draw.rounded_rectangle((26, 164, 286, 209), 30, BLUE)
    weapon_bg.paste(main_prop_img, (40, 167), main_prop_img)
    weapon_draw.text(
        (86, 187),
        main_p['property_name'],
        GREY,
        zzz_font_24,
        'lm',
    )
    weapon_draw.text(
        (273, 187),
        main_p['base'],
        'white',
        zzz_font_30,
        'rm',
    )

    for pindex, p in enumerate(weapon_ps):
        wp_o = pindex * 60
        prop_id = p['property_id']
        prop_img = get_prop_img(prop_id)
        weapon_draw.rounded_rectangle(
            (26, 224 + wp_o, 286, 269 + wp_o),
            30,
            (0, 0, 0, 130),
        )
        weapon_bg.paste(prop_img, (40, 227 + wp_o), prop_img)

        weapon_draw.text(
            (86, 247 + wp_o),
            p['property_name'],
            GREY,
            zzz_font_24,
            'lm',
        )
        weapon_draw.text(
            (273, 247 + wp_o),
            p['base'],
            'white',
            zzz_font_30,
            'rm',
        )
    img.paste(weapon_bg, (487, 810), weapon_bg)

    # 驱动盘
    _equips = data['equip']
    equips = []
    for s in range(6):
        for i in _equips:
            if i['equipment_type'] == s + 1:
                equips.append(i)
                break
        else:
            equips.append({'equipment_type': s + 1})

    equip_all_bg = Image.open(TEXT_PATH / 'equip_all_bg.png')
    equip_fg = Image.open(TEXT_PATH / 'equip_fg.png')
    for equip in equips:
        equip_bg = Image.open(TEXT_PATH / 'equip_bg.png')
        _type = equip['equipment_type']
        ox = ((_type - 1) % 3) * 285
        oy = ((_type - 1) // 3) * 419
        if 'id' in equip:
            equip_id = equip['id']
            equip_level = equip['level']
            equip_name = equip['name'][:-3]
            eq_mp = equip['main_properties'][0]
            eq_p = equip['properties']

            equip_bg.paste(equip_fg, (0, 0), equip_fg)
            equip_draw = ImageDraw.Draw(equip_bg)

            equip_draw.text(
                (185, 95),
                f'等级{equip_level}',
                'white',
                zzz_font_20,
                'mm',
            )
            equip_draw.text(
                (186, 140),
                equip_name,
                'white',
                zzz_font_30,
                'mm',
            )

            equip_img = get_equip_img(equip_id).convert('RGBA')
            equip_rarity = get_rarity_img(equip['rarity'])
            equip_bg.paste(equip_rarity, (240, 59), equip_rarity)
            equip_bg.paste(equip_img, (21, 21), equip_img)

            equip_draw.rounded_rectangle((63, 167, 309, 213), 30, BLUE)
            mp_img = get_prop_img(eq_mp['property_id'], 45, 45)
            equip_bg.paste(mp_img, (76, 165), mp_img)
            equip_draw.text(
                (123, 190),
                eq_mp['property_name'],
                'white',
                zzz_font_24,
                'lm',
            )
            equip_draw.text(
                (288, 190),
                eq_mp['base'],
                'white',
                zzz_font_30,
                'rm',
            )

            for eindex, ep in enumerate(eq_p):
                equip_bar = Image.open(TEXT_PATH / 'equip_bar.png')
                equip_bar_draw = ImageDraw.Draw(equip_bar)
                ep_prop_img = get_prop_img(ep['property_id'], 36, 36)
                equip_bar.paste(ep_prop_img, (40, 7), ep_prop_img)
                equip_bar_draw.text(
                    (85, 23),
                    ep['property_name'],
                    'white',
                    zzz_font_24,
                    'lm',
                )
                equip_bar_draw.text(
                    (236, 23),
                    ep['base'],
                    YELLOW,
                    zzz_font_24,
                    'rm',
                )
                equip_bg.paste(equip_bar, (41, 221 + eindex * 46), equip_bar)
        else:
            empty = Image.open(TEXT_PATH / 'empty_equip.png')
            equip_bg.paste(empty, (0, 0), empty)
        equip_all_bg.paste(equip_bg, (5 + ox, 113 + oy), equip_bg)
    img.paste(equip_all_bg, (0, 1083), equip_all_bg)

    img = add_footer(img)
    img = await convert_img(img)
    return img
