from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from ..utils.zzzero_prefix import PREFIX

sv_gacha_log = SV('zzz抽卡记录')
sv_get_gachalog_by_link = SV('zzz导入抽卡链接', area='DIRECT')


@sv_gacha_log.on_fullmatch(f'{PREFIX}抽卡记录')
async def send_gacha_log_card_info(bot: Bot, ev: Event):
    return await bot.send("TODO")


@sv_get_gachalog_by_link.on_command(f'{PREFIX}导入抽卡链接')
async def get_gachalog_by_link(bot: Bot, ev: Event):
    return await bot.send("TODO")
