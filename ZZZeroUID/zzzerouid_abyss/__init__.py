from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from .draw_abyss import draw_abyss_img
from ..utils.zzzero_prefix import PREFIX

sv_get_abyss = SV('zzz查询深渊')


@sv_get_abyss.on_fullmatch(
    (
        f'{PREFIX}查询深渊',
        f'{PREFIX}深渊',
        '‌式舆防卫战',
        f'{PREFIX}‌式舆防卫战',
        f'{PREFIX}查询上期深渊',
        f'{PREFIX}上期深渊',
        '上期‌式舆防卫战',
        f'{PREFIX}上期‌式舆防卫战',
        f'{PREFIX}查询完整深渊',
        f'{PREFIX}完整深渊',
        '‌完整式舆防卫战',
        f'{PREFIX}完整‌式舆防卫战',
        f'{PREFIX}查询上期完整深渊',
        f'{PREFIX}上期完整深渊',
        '上期完整‌式舆防卫战',
        f'{PREFIX}上期完整‌式舆防卫战',
    ),
    block=True,
)
async def send_abyss_info(bot: Bot, ev: Event):
    logger.info('开始执行[绝区零深渊]')
    uid = await get_uid(bot, ev)
    logger.info(f'[绝区零深渊] UID: {uid}')
    if not uid:
        return await bot.send(BIND_UID_HINT)
    if '上期' in ev.command:
        schedule_type = 2
    else:
        schedule_type = 1

    if '完整' in ev.command:
        is_full = True
    else:
        is_full = False

    im = await draw_abyss_img(uid, ev, schedule_type, is_full)
    await bot.send(im)
