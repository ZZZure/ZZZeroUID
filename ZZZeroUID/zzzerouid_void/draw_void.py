from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.download_resource.download_file import download

from ..utils.hint import error_reply
from ..utils.zzzero_api import zzz_api
from ..zzzerouid_mem.draw_mem import draw_boss
from ..utils.resource.RESOURCE_PATH import TEMP_PATH
from ..zzzerouid_mem.draw_mem import TEXT_PATH as MEM_TEXT_PATH
from ..utils.api.models import Boss, MEMBuddy, MainChallengeRecord
from ..zzzerouid_roleinfo.draw_role_info import draw_avatar, draw_bangboo
from ..utils.image import BLACK_G, add_footer, get_zzz_bg, get_player_card_min
from ..utils.fonts.zzz_fonts import (
    zzz_font_20,
    zzz_font_22,
    zzz_font_26,
    zzz_font_38,
    zzz_font_44,
    zzz_font_50,
    zzz_font_54,
    zzz_font_60,
)

TEXT_PATH = Path(__file__).parent / 'texture2d'


def time_to_str(time):
    t1 = f'{time["year"]}.{time["month"]:02d}.{time["day"]:02d}'
    t2 = f'{time["hour"]:02d}:{time["minute"]:02d}:{time["second"]:02d}'
    return f'{t1} {t2}'


async def draw_team(avatar_list: list, buddy: Optional[MEMBuddy] = None):
    img = Image.new('RGBA', (634, 171))
    for aindex, agent in enumerate(avatar_list):
        avatar_img = await draw_avatar(agent)
        avatar_img = avatar_img.resize((171, 198))
        img.paste(
            avatar_img,
            (-13 + aindex * 171, -16),
            avatar_img,
        )

    if buddy:
        bangboo_img = await draw_bangboo(buddy)
        bangboo_img = bangboo_img.resize((137, 158))
        img.paste(
            bangboo_img,
            (510, 17),
            bangboo_img,
        )

    return img


async def draw_stage(
    boss_stage_data: MainChallengeRecord,
    boss_name: str = '',
    boss_info: Optional[Boss] = None,
):
    if len(boss_stage_data['sub_challenge_record']) >= 4:
        stage_bg = Image.open(TEXT_PATH / 'stage_bg_4.png')
    else:
        stage_bg = Image.open(TEXT_PATH / 'stage_bg.png')

    team_pic = await draw_team(
        boss_stage_data['avatar_list'],
        boss_stage_data['buddy'],
    )
    stage_bg.paste(team_pic, (58, 256), team_pic)

    star_img = Image.open(TEXT_PATH / f'{boss_stage_data["star"]}_Level_S.png')
    stage_bg.paste(star_img, (62, 67), star_img)

    stage_bg_draw = ImageDraw.Draw(stage_bg)
    for subindex, sub in enumerate(boss_stage_data['sub_challenge_record']):
        sub_pic = Image.new('RGBA', (643, 145))
        team_pic = await draw_team(
            sub['avatar_list'],
            sub['buddy'],
        )
        team_pic = team_pic.resize((482, 130))
        sub_pic.paste(team_pic, (118, 8), team_pic)
        star_img = Image.open(TEXT_PATH / f'{sub["star"]}_Level_S.png')
        sub_pic.paste(star_img, (28, 18), star_img)
        sub_draw = ImageDraw.Draw(sub_pic)
        sub_draw.text(
            (60, 118),
            f'{sub["name"]}',
            font=zzz_font_26,
            fill='white',
            anchor='mm',
        )
        stage_bg.paste(
            sub_pic,
            (84, 440 + subindex * 142),
            sub_pic,
        )
    stage_bg_draw.text(
        (150, 154),
        f'{boss_stage_data["score"]}',
        font=zzz_font_60,
        fill='white',
        anchor='lm',
    )

    if boss_info:
        boss_img = await draw_boss(boss_info)
        boss_img = boss_img.resize((144, 200))
        stage_bg.paste(boss_img, (555, 50), boss_img)
    else:
        buffer = boss_stage_data['buffer']
        buffer_url = buffer['icon']
        buffer_name = buffer_url.split('/')[-1]
        buffer_path = TEMP_PATH / buffer_name
        if not buffer_path.exists():
            await download(buffer_url, TEMP_PATH, buffer_name)
        buffer_img = Image.open(buffer_path).resize((117, 117))
        stage_bg.paste(buffer_img, (564, 60), buffer_img)
        stage_bg_draw.text(
            (621, 208),
            f'{buffer["name"]}',
            font=zzz_font_26,
            fill='white',
            anchor='mm',
        )

    if boss_name.startswith('STAGE'):
        boss_color = (8, 153, 255)
    else:
        boss_color = (255, 114, 8)

    stage_bg_draw.text(
        (150, 91),
        f'{boss_name}',
        font=zzz_font_44,
        fill=boss_color,
        anchor='lm',
    )

    if boss_stage_data["score"] >= 1000000:
        off = -50
    elif boss_stage_data["score"] >= 100000:
        off = 0
    elif boss_stage_data["score"] >= 10000:
        off = 50
    else:
        off = 100

    stage_bg_draw.rounded_rectangle(
        (393 - off, 150, 468 - off, 178),
        radius=20,
        fill=(120, 38, 184),
    )
    stage_bg_draw.text(
        (430 - off, 164),
        f'x{boss_stage_data["score_ratio"]}',
        font=zzz_font_22,
        fill='white',
        anchor='mm',
    )
    time = time_to_str(boss_stage_data['challenge_time'])
    stage_bg_draw.text(
        (150, 208),
        time,
        font=zzz_font_20,
        fill=(177, 177, 177),
        anchor='lm',
    )
    return stage_bg


async def draw_void_img(uid: str, ev: Event):
    data = await zzz_api.get_zzz_void_info(uid)
    if isinstance(data, int):
        return error_reply(data)

    if not data['main_challenge_record_list']:
        return '你还没有挑战本期【临界推演】/或数据未刷新!'

    player_card = await get_player_card_min(uid, ev)
    if isinstance(player_card, int):
        return error_reply(player_card)

    stage_bgs: List[Image.Image] = []
    if data['boss_challenge_record']:
        boss_record = data['boss_challenge_record']
        boss_name = boss_record['boss_info']['name']
        boss_stage_data = boss_record['main_challenge_record']
        stage_bgs.append(
            await draw_stage(
                boss_stage_data,
                boss_name,
                boss_record['boss_info'],
            )
        )

    for i in data['main_challenge_record_list']:
        stage_bg = await draw_stage(i, i['name'])
        stage_bgs.append(stage_bg)

    x_offset = 30  # 每行起始X
    x_gap = 750  # 两列之间X间距
    y_start = 776  # 初始Y
    y = y_start

    # 每行2张图片
    cols = 2
    total_height = sum(
        max(im.height for im in stage_bgs[i : i + cols])
        for i in range(0, len(stage_bgs), cols)
    )

    w, h = 1560, 860 + total_height

    void_front = data['void_front_battle_abstract_info_brief']

    rank_percent = void_front['rank_percent'] / 100
    if rank_percent <= 1:
        rank_tag = 'tier_5'
    elif rank_percent <= 10:
        rank_tag = 'tier_4'
    elif rank_percent <= 25:
        rank_tag = 'tier_3'
    elif rank_percent <= 50:
        rank_tag = 'tier_2'
    else:
        rank_tag = 'tier_1'

    rank_img = Image.open(MEM_TEXT_PATH / f'{rank_tag}.png')
    rank_draw = ImageDraw.Draw(rank_img)
    rank_draw.text(
        (137, 49),
        f'{rank_percent:.2f}%',
        font=zzz_font_38,
        fill=BLACK_G,
        anchor='mm',
    )

    player_card = await get_player_card_min(uid, ev)
    if isinstance(player_card, int):
        return error_reply(player_card)

    title = Image.open(TEXT_PATH / 'title.png')
    title.paste(player_card, (0, 244), player_card)
    title_draw = ImageDraw.Draw(title)
    title_draw.text(
        (1248, 357),
        f"{void_front['total_score']}",
        font=zzz_font_54,
        fill='white',
        anchor='rm',
        stroke_width=2,
        stroke_fill='black',
    )
    title.paste(rank_img, (1222, 307), rank_img)

    img = get_zzz_bg(w, h, 'bg3')

    img.paste(title, (0, 0), title)

    title_bgf = Image.open(TEXT_PATH / 'title_bgf.png')
    title_bgf_draw = ImageDraw.Draw(title_bgf)

    s_count = 0
    all_battle = 0

    if data['boss_challenge_record']:
        if (
            data['boss_challenge_record']['main_challenge_record']['star']
            == 'S'
        ):
            s_count += 1
        all_battle += 1

    for i in data['main_challenge_record_list']:
        if i['star'] == 'S':
            s_count += 1
        for j in i['sub_challenge_record']:
            all_battle += 1
            if j['star'] == 'S':
                s_count += 1
        all_battle += 1

    end = void_front['ending_record_name'].split('·')
    bar_data = {
        end[0]: end[1],
        '总分': void_front['total_score'],
        '本场ID': void_front['void_front_id'],
        '获取S数量': f'{s_count} / {all_battle}',
    }

    end_url = void_front['ending_record_bg_pic']
    end_name = end_url.split('/')[-1]
    end_path = TEMP_PATH / end_name
    if not end_path.exists():
        await download(end_url, TEMP_PATH, end_name)
    end_img = Image.open(end_path).resize((220, 117)).convert('RGBA')
    title_bgf.paste(end_img, (189, 133), end_img)

    for i, (k, v) in enumerate(bar_data.items()):
        x = int(566 + i * 235.7)
        title_bgf_draw.text(
            (x, 221),
            k,
            font=zzz_font_26,
            fill=(212, 212, 212),
            anchor='mm',
        )
        title_bgf_draw.text(
            (x, 178),
            str(v),
            font=zzz_font_50,
            fill='white',
            anchor='mm',
        )

    img.paste(title_bgf, (0, 418), title_bgf)

    # 按行处理
    for row_start in range(0, len(stage_bgs), cols):
        row_imgs = stage_bgs[row_start : row_start + cols]

        # 计算当前行的最大高度
        max_h = max(im.height for im in row_imgs)

        # 粘贴当前行的图片
        for i, im in enumerate(row_imgs):
            x = x_offset + i * x_gap
            img.paste(im, (x, y), im)

        # 移动到下一行
        y += max_h

    img = add_footer(img, 1100)
    res = await convert_img(img)
    return res
