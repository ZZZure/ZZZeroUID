import json
from pathlib import Path
from typing import Union

import aiofiles
from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.zzzero_prefix import PREFIX
from ..utils.name_convert import char_name_to_char_id
from ..utils.resource.download_file import get_weapon
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from .utils import BLUE, YELLOW, WEAPON_EQUIP_POS, get_skill_dict
from ..utils.fonts.zzz_fonts import (
    zzz_font_28,
    zzz_font_30,
    zzz_font_40,
    zzz_font_50,
    zzz_font_thin,
)
from ..utils.image import (
    add_footer,
    get_zzz_bg,
    get_pro_img,
    get_camp_img,
    get_prop_img,
    get_rank_img,
    get_equip_img,
    get_rarity_img,
    get_element_img,
    get_mind_role_img,
    get_player_card_min,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'
STAR_PATH = TEXT_PATH / 'star'


async def draw_char_detail_img(
    uid: str, ev: Event, char: str
) -> Union[str, bytes]:
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

    img = get_zzz_bg(1100, 2400, 'bg3')

    # 角色部分
    char_bg = Image.new('RGBA', (1100, 645))
    char_img = get_mind_role_img(char_id).convert('RGBA')
    new_size = int(char_img.size[0] * 0.85), int(char_img.size[1] * 0.85)
    char_img = char_img.resize(new_size)
    char_bg.paste(char_img, (-582, -150), char_img)
    img.paste(char_bg, (0, 195), char_bg)

    # title部分
    title = Image.open(TEXT_PATH / 'title.png')
    player_card = await get_player_card_min(uid, ev)
    title.paste(player_card, (-63, 65), player_card)
    title_draw = ImageDraw.Draw(title)
    avatar_name = data['name_mi18n']
    level = data['level']
    profession = data['avatar_profession']

    pro_icon = get_pro_img(profession, 70, 70)
    element_icon = get_element_img(data['element_type'], 70, 70)

    title_draw.text(
        (918, 131),
        avatar_name,
        'white',
        zzz_font_50,
        'rm',
    )

    rank = data['rank']
    for r in range(rank + 1):
        if r == 0:
            continue
        rank_icon = Image.open(TEXT_PATH / 'ranks' / f'{r}.png')
        rank_icon = rank_icon.resize((31, 31)).convert('RGBA')
        title.paste(rank_icon, (737 + 34 * (r - 1), 184), rank_icon)

    title_draw.text((1013, 198), f'Lv.{level}', 'white', zzz_font_30, 'mm')
    title.paste(pro_icon, (937, 97), pro_icon)
    title.paste(element_icon, (1009, 97), element_icon)
    img.paste(title, (0, -56), title)

    # 属性部分
    props = data['properties']
    property_bg = Image.open(TEXT_PATH / 'prop_bg.png')
    property_draw = ImageDraw.Draw(property_bg)
    for pindex, prop in enumerate(props):
        name = prop['property_name']
        value = prop["final"]
        y = int(96 + pindex * 58.6)
        property_draw.text(
            (431, y),
            value,
            'white',
            zzz_font_thin(32),
            'rm',
        )
        property_draw.text(
            (114, y),
            name,
            'white',
            zzz_font_thin(32),
            'lm',
        )
    img.paste(property_bg, (631, 169), property_bg)

    # 技能部分
    skill_dict = get_skill_dict(data)
    skill_bg = Image.open(TEXT_PATH / 'skill_bar.png')
    skill_draw = ImageDraw.Draw(skill_bg)
    for skill_pos_num in skill_dict:
        skill_level, skill_color = skill_dict[skill_pos_num]
        skill_draw.text(
            (551 + skill_pos_num * 94, 88),
            f'{skill_level}',
            skill_color,
            zzz_font_28,
            'mm',
        )
    img.paste(skill_bg, (0, 832), skill_bg)

    weapon_bg = Image.open(TEXT_PATH / 'weapon_bar.png')
    all_score_value = 0
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

    equip_bg = Image.open(TEXT_PATH / 'equip_bg.png')
    for equip in equips:
        equip_bar = Image.open(TEXT_PATH / 'equip_bar.png')
        _type = equip['equipment_type']
        ox = ((_type - 1) % 3) * 354
        oy = ((_type - 1) // 3) * 458
        if 'id' in equip:
            equip_id = equip['id']
            equip_level = equip['level']
            equip_name = equip['name'][:-3]
            eq_mp = equip['main_properties'][0]
            eq_p = equip['properties']

            equip_draw = ImageDraw.Draw(equip_bar)

            equip_draw.text(
                (209, 86),
                f'等级{equip_level}',
                'white',
                zzz_font_thin(20),
                'mm',
            )
            equip_draw.text(
                (160, 145),
                equip_name,
                'white',
                zzz_font_thin(28),
                'mm',
            )

            score_value = 35
            score_color = (255, 196, 1)

            all_score_value += score_value

            equip_draw.rounded_rectangle(
                (264, 128, 350, 162),
                10,
                score_color,
            )
            equip_draw.text(
                (307, 145),
                f'{score_value}分',
                'black',
                zzz_font_thin(26),
                'mm',
            )
            if equip['rarity'] == 'A':
                equip_color = (177, 0, 255)
            elif equip['rarity'] == 'S':
                equip_color = (255, 146, 0)
            elif equip['rarity'] == 'B':
                equip_color = (0, 167, 255)
            else:
                equip_color = (90, 90, 90)

            equip_img = Image.new('RGBA', (400, 400))
            equip_img_draw = ImageDraw.Draw(equip_img)
            equip_img_draw.ellipse((0, 0, 400, 400), equip_color)
            _equip_img = get_equip_img(equip_id, 380, 380)
            equip_img.paste(_equip_img, (10, 10), _equip_img)

            weapon_equip_img = equip_img.resize((140, 140))
            weapon_equip_pos = WEAPON_EQUIP_POS[_type]
            weapon_bg.paste(
                weapon_equip_img,
                weapon_equip_pos,
                weapon_equip_img,
            )

            equip_img = equip_img.resize((100, 100))

            equip_rarity = get_rarity_img(equip['rarity'])
            equip_bar.paste(equip_rarity, (272, 46), equip_rarity)
            equip_bar.paste(equip_img, (22, 0), equip_img)

            equip_draw.rounded_rectangle((71, 186, 350, 231), 8, BLUE)
            mp_img = get_prop_img(eq_mp['property_id'], 38, 38)
            equip_bar.paste(mp_img, (92, 190), mp_img)
            equip_draw.text(
                (139, 208),
                eq_mp['property_name'],
                'white',
                zzz_font_thin(20),
                'lm',
            )
            equip_draw.text(
                (329, 208),
                eq_mp['base'],
                'white',
                zzz_font_thin(30),
                'rm',
            )

            for eindex, ep in enumerate(eq_p):
                equip_prop_bar = Image.new('RGBA', (290, 46))
                equip_prop_draw = ImageDraw.Draw(equip_prop_bar)
                equip_prop_draw.rounded_rectangle((5, 4, 285, 42), 8)
                ep_prop_img = get_prop_img(ep['property_id'], 35, 35)
                equip_prop_bar.paste(ep_prop_img, (14, 7), ep_prop_img)
                equip_prop_draw.text(
                    (60, 23),
                    ep['property_name'],
                    'white',
                    zzz_font_thin(22),
                    'lm',
                )
                equip_prop_draw.text(
                    (266, 23),
                    ep['base'],
                    YELLOW,
                    zzz_font_thin(22),
                    'rm',
                )
                equip_bar.paste(
                    equip_prop_bar,
                    (66, 252 + eindex * 46),
                    equip_prop_bar,
                )
        else:
            empty = Image.open(TEXT_PATH / 'empty_equip.png')
            equip_bar.paste(empty, (0, 0), empty)
        equip_bg.paste(equip_bar, (-5 + ox, 113 + oy), equip_bar)

    img.paste(equip_bg, (0, 1272), equip_bg)

    # 武器部分
    weapon = data['weapon']
    weapon_name = weapon['name']
    weapon_level = weapon['level']
    main_ps = weapon['main_properties']
    weapon_ps = weapon['properties']
    camp_img = get_camp_img(data['camp_name_mi18n'])

    weapon_rank_icon = get_rank_img(weapon['rarity'], 64, 64)
    weapon_star_icon = Image.open(STAR_PATH / f'{weapon["star"]}.png')
    weapon_img = await get_weapon(weapon['id'])
    weapon_img = weapon_img.resize((240, 240)).convert('RGBA')

    weapon_draw = ImageDraw.Draw(weapon_bg)

    weapon_bg.paste(weapon_rank_icon, (559, 151), weapon_rank_icon)
    weapon_bg.paste(weapon_star_icon, (643, 216), weapon_star_icon)
    weapon_bg.paste(weapon_img, (140, 157), weapon_img)
    weapon_draw.text((632, 183), weapon_name, 'white', zzz_font_40, 'lm')
    weapon_draw.text(
        (604, 236),
        f'Lv.{weapon_level}',
        (40, 40, 40),
        zzz_font_28,
        'mm',
    )
    main_p = main_ps[0]
    main_prop_id = main_p['property_id']
    main_prop_img = get_prop_img(main_prop_id, 45, 45)
    weapon_draw.rounded_rectangle((561, 265, 861, 313), 8, BLUE)
    weapon_bg.paste(main_prop_img, (570, 266), main_prop_img)
    weapon_draw.text(
        (620, 289),
        main_p['property_name'],
        'White',
        zzz_font_thin(26),
        'lm',
    )
    weapon_draw.text(
        (842, 289),
        main_p['base'],
        YELLOW,
        zzz_font_thin(26),
        'rm',
    )

    for pindex, p in enumerate(weapon_ps):
        wp_o = pindex * 60
        prop_id = p['property_id']
        prop_img = get_prop_img(prop_id, 45, 45)
        weapon_draw.rounded_rectangle(
            (561, 326 + wp_o, 861, 374 + wp_o),
            8,
            (40, 40, 40),
        )
        weapon_bg.paste(prop_img, (570, 327 + wp_o), prop_img)

        weapon_draw.text(
            (620, 350 + wp_o),
            p['property_name'],
            'white',
            zzz_font_thin(26),
            'lm',
        )
        weapon_draw.text(
            (842, 350 + wp_o),
            p['base'],
            YELLOW,
            zzz_font_thin(26),
            'rm',
        )

    if all_score_value >= 200:
        equip_rank = 'S'
    elif all_score_value >= 150:
        equip_rank = 'A'
    else:
        equip_rank = 'B'
    weapon_equip_rank = get_rank_img(equip_rank, 49, 49)
    weapon_bg.paste(weapon_equip_rank, (563, 437), weapon_equip_rank)
    weapon_bg.paste(camp_img, (875, 156), camp_img)
    weapon_draw.text(
        (739, 448),
        f'{all_score_value}分',
        'white',
        zzz_font_thin(45),
        'mm',
    )
    img.paste(weapon_bg, (0, 824), weapon_bg)

    img = add_footer(img)
    img = await convert_img(img)
    return img
