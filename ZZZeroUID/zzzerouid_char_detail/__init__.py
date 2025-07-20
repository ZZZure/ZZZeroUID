from typing import List

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from ..zzzerouid_config.zzzero_config import ZZZ_CONFIG
from .refresh_char_detail import refresh_char_by_config
from .draw_new_char_detail_card import draw_char_detail_img

sv_char_detail_refresh = SV('zzz角色面板刷新')
sv_char_detail = SV('zzz角色面板')


@sv_char_detail_refresh.on_command(
    (
        '刷新面板',
        '强制刷新',
        '更新面板',
    )
)
async def send_refresh_char_detail_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f'[绝区零] [刷新面板] UID: {uid}')

    if not uid:
        return await bot.send(BIND_UID_HINT)

    data_list: List[str] = ZZZ_CONFIG.get_config('RefreshDataList').data
    for i in data_list:
        im = await refresh_char_by_config(i, uid, ev)
        if isinstance(im, bytes):
            return await bot.send(im)
    else:
        return await bot.send(im)


@sv_char_detail.on_prefix(('角色面板', '查询'))
@sv_char_detail.on_suffix('面板')
async def send_char_detail_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    char = ev.text.strip(' ')

    if char in ('刷新', '强制刷新', '更新'):
        return

    logger.info(f'[绝区零] [角色面板] CHAR: {char}')
    logger.info(f'[绝区零] [角色面板] UID: {uid}')

    if not char:
        return

    if not uid:
        return await bot.send(BIND_UID_HINT)

    im = await draw_char_detail_img(uid, ev, char)
    return await bot.send(im)
