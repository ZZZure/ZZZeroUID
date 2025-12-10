from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from .draw_char_list import draw_char_list_img

sv_char_list = SV("zzz角色练度统计")


@sv_char_list.on_fullmatch(
    (
        "练度统计",
        "角色列表",
    )
)
async def send_char_list_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f"[绝区零] [练度统计] UID: {uid}")

    if not uid:
        return await bot.send(BIND_UID_HINT)

    im = await draw_char_list_img(uid, ev)
    return await bot.send(im)
