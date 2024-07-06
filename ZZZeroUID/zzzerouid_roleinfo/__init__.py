from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from ..utils.zzzero_prefix import PREFIX
from .draw_role_info import draw_role_img

sv_get_info = SV('zzz查询信息')


@sv_get_info.on_fullmatch((f'{PREFIX}查询'), block=True)
async def send_role_info(bot: Bot, ev: Event):
    logger.info('开始执行[ZZZ查询]')
    uid = await get_uid(bot, ev)
    logger.info(f'[ZZZ查询] UID: {uid}')
    if not uid:
        return await bot.send(BIND_UID_HINT)
    im = await draw_role_img(uid, ev)
    await bot.send(im)
