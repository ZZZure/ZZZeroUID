from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from .draw_gachalogs import draw_card
from ..utils.hint import BIND_UID_HINT
from ..utils.zzzero_prefix import PREFIX
from .get_gachalogs import save_gachalogs

sv_gacha_log = SV(f"{PREFIX}抽卡记录")
sv_get_refresh_gachalog = SV(f"{PREFIX}刷新抽卡记录")


@sv_gacha_log.on_fullmatch((f"{PREFIX}抽卡记录"))
async def send_gacha_log_card_info(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f"[ZZZ抽卡记录] UID: {uid}")

    if not uid:
        return await bot.send(BIND_UID_HINT)

    im = await draw_card(uid, ev)
    return await bot.send(im)


@sv_get_refresh_gachalog.on_fullmatch(
    (f"{PREFIX}刷新抽卡记录", f'{PREFIX}更新抽卡记录'),
)
async def send_refresh_gachalog_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f"[ZZZ刷新抽卡记录] UID: {uid}")

    if not uid:
        return await bot.send(BIND_UID_HINT)

    await bot.send(f"开始刷新{uid}抽卡记录，需要一定时间，请勿重复执行.....")
    im = await save_gachalogs(uid)
    return await bot.send(im)
