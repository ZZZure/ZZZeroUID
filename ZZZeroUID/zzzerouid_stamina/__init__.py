from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from ..utils.zzzero_prefix import PREFIX
from .draw_zzz_stamina import draw_stamina_img

sv_get_stamina = SV('绝区零查询体力')


@sv_get_stamina.on_fullmatch(
    (
        f'{PREFIX}每日',
        f'{PREFIX}mr',
        f'{PREFIX}实时便笺',
        f'{PREFIX}便笺',
        f'{PREFIX}便签',
    )
)
async def send_daily_info_pic(bot: Bot, ev: Event):
    logger.info('开始执行[ZZZ每日信息]')
    uid = await get_uid(bot, ev)
    logger.info(f'[ZZZ每日] UID: {uid}')
    if not uid:
        return await bot.send(BIND_UID_HINT)
    im = await draw_stamina_img(uid, ev)
    await bot.send(im)
