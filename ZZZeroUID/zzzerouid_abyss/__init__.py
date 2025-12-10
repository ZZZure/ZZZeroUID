from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event

from ..utils.uid import get_uid
from .draw_abyss import draw_abyss_img
from ..utils.hint import BIND_UID_HINT

sv_get_abyss = SV("zzz查询零号空洞")


@sv_get_abyss.on_fullmatch(
    (
        "查询零号空洞",
        "零号空洞",
    ),
    block=True,
)
async def send_abyss_info(bot: Bot, ev: Event):
    logger.info("开始执行[零号空洞]")
    uid = await get_uid(bot, ev)
    logger.info(f"[零号空洞] UID: {uid}")
    if not uid:
        return await bot.send(BIND_UID_HINT)

    im = await draw_abyss_img(uid, ev)
    await bot.send(im)
