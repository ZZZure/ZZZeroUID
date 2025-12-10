from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event

from .draw_mem import draw_mem_img
from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT

sv_get_mem = SV("zzz查询危局强袭战")


@sv_get_mem.on_fullmatch(
    (
        "查询危局强袭战",
        "危局强袭战",
        "强袭战",
        "上期危局强袭战",
        "上期强袭战",
        "查询上期强袭战",
    ),
    block=True,
)
async def send_mem_info(bot: Bot, ev: Event):
    logger.info("开始执行[危局强袭战]")
    uid = await get_uid(bot, ev)
    logger.info(f"[危局强袭战] UID: {uid}")
    if not uid:
        return await bot.send(BIND_UID_HINT)

    if "上期" in ev.command:
        schedule_type = 2
    else:
        schedule_type = 1

    im = await draw_mem_img(uid, ev, schedule_type)
    await bot.send(im)
