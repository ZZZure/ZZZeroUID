from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from ..utils.zzzero_prefix import PREFIX
from .get_month_data import draw_month_info

sv_month_info = SV(f'{PREFIX}绳网月报')


@sv_month_info.on_fullmatch(
    (
        f'{PREFIX}绳网月报',
        f'{PREFIX}月历',
        f'{PREFIX}札记',
    )
)
async def send_month_info(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f'[绝区零] [绳网月报] UID: {uid}')

    if not uid:
        return await bot.send(BIND_UID_HINT)

    im = await draw_month_info(uid, ev)
    return await bot.send(im)
