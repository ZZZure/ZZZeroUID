from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from ..utils.zzzero_prefix import PREFIX
from .refresh_char_detail import refresh_char

sv_char_detail_refresh = SV(f"{PREFIX}角色面板刷新")
sv_char_detail = SV(f"{PREFIX}角色面板")


@sv_char_detail_refresh.on_fullmatch(
    (
        f"{PREFIX}刷新面板",
        f"{PREFIX}强制刷新",
    )
)
async def send_refresh_char_detail_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f"[绝区零] [刷新面板] UID: {uid}")

    if not uid:
        return await bot.send(BIND_UID_HINT)

    im = await refresh_char(uid)
    return await bot.send(im)
