from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..zzzzerouid_utils.zzzero_prefix import PREFIX

sv_zzz_help = SV('zzz帮助')


@sv_zzz_help.on_fullmatch(f'{PREFIX}帮助')
async def send_help_img(bot: Bot, ev: Event):
    logger.info('开始执行[zzz帮助]')
    await bot.send("todo")
