from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from .get_gachalogs import save_gachalogs, get_full_gachalog
from .draw_gachalogs import draw_card

sv_gacha_log = SV("zzz抽卡记录")
sv_get_refresh_gachalog = SV("zzz刷新抽卡记录")


@sv_gacha_log.on_fullmatch(("抽卡记录"))
async def send_gacha_log_card_info(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f"[ZZZ抽卡记录] UID: {uid}")

    if not uid:
        return await bot.send(BIND_UID_HINT)

    im = await draw_card(uid, ev)
    return await bot.send(im)


@sv_get_refresh_gachalog.on_fullmatch(
    ("刷新抽卡记录", "更新抽卡记录"),
)
async def send_refresh_gachalog_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f"[ZZZ刷新抽卡记录] UID: {uid}")

    if not uid:
        return await bot.send(BIND_UID_HINT)

    await bot.send(f"开始刷新{uid}抽卡记录，需要一定时间，请勿重复执行.....")
    im = await save_gachalogs(uid)
    return await bot.send(im)


@sv_get_refresh_gachalog.on_fullmatch(("全量刷新抽卡记录", "全量更新抽卡记录"))
async def send_full_refresh_gacha_info(bot: Bot, ev: Event):
    logger.info("开始执行[全量刷新抽卡记录]")
    uid = await get_uid(bot, ev)
    if uid is None:
        return await bot.send(BIND_UID_HINT)
    await bot.send(f"UID{uid}开始执行[全量刷新抽卡记录],需要一定时间...请勿重复触发！")
    im = await get_full_gachalog(uid)
    return await bot.send(im)
