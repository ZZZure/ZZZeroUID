from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.database.models import GsBind
from gsuid_core.utils.sign.sign import sign_in
from .data_source import get_code_msg

from ..utils.hint import BIND_UID_HINT
from ..utils.zzzero_prefix import PREFIX

sv_zzz_code = SV('绝区零前瞻兑换码')


@sv_zzz_code.on_fullmatch(f'{PREFIX}兑换码')
async def get_sign_func(bot: Bot, ev: Event):
    try:
        codes = await get_code_msg()
    except Exception as e:
        logger.opt(exception=e).error("获取前瞻兑换码失败")
        codes = "获取前瞻兑换码失败"
    await bot.send(codes)
