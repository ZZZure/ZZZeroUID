from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from .draw_void import draw_void_img
from ..utils.hint import BIND_UID_HINT

sv_get_mem = SV('zzz查询临界推演')


@sv_get_mem.on_fullmatch(
    ('查询临界推演', '临界推演', '临界', '推演'),
    block=True,
)
async def send_mem_info(bot: Bot, ev: Event):
    logger.info('开始执行[临界推演]')
    uid = await get_uid(bot, ev)
    logger.info(f'[临界推演] UID: {uid}')
    if not uid:
        return await bot.send(BIND_UID_HINT)

    im = await draw_void_img(uid, ev)
    await bot.send(im)
