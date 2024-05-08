from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from ..utils.message import send_diff_msg
from ..utils.zzzero_prefix import PREFIX
from ..zzzerouid_config.zzzero_config import ZZZ_GAME_NAME
from ..utils.uid import get_uid
from get_gachalogs import save_gachalogs


sv_gacha_log = SV(f'{PREFIX}抽卡记录')
sv_get_gachalog_by_link = SV(f'{PREFIX}导入抽卡链接', area='DIRECT')


@sv_gacha_log.on_fullmatch(f'{PREFIX}抽卡记录')
async def send_gacha_log_card_info(bot: Bot, ev: Event):
    return await bot.send("TODO")


@sv_get_gachalog_by_link.on_command(f'{PREFIX}导入抽卡链接')
async def get_gachalog_by_link(bot: Bot, ev: Event):
    url = ev.text.strip()
    user_id = ev.user_id
    await bot.logger.info(f'开始导入抽卡链接 url={url}, userid={user_id}')
    uid = await get_uid(bot, ev)
    if not url or not isinstance(url, str):
        return await bot.send("请给出正确的抽卡链接")
    await bot.send(f'开始强制刷新{uid}抽卡记录，需要一定时间，请勿重复执行.....')
    im = await save_gachalogs(uid, url, None, True)
    return await bot.send(im)



