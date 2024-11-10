from PIL import Image
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.help.utils import register_help
from gsuid_core.sv import SV, get_plugin_available_prefix

from .get_help import ICON, get_help

sv_zzz_help = SV('zzz帮助')


@sv_zzz_help.on_fullmatch('帮助')
async def send_help_img(bot: Bot, ev: Event):
    logger.info('开始执行[zzz帮助]')
    await bot.send(await get_help())


register_help(
    'ZZZeroUID',
    f'{get_plugin_available_prefix("ZZZeroUID")}帮助',
    Image.open(ICON),
)
