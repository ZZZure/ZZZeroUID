import re

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from ..zzzzerouid_utils.zzzero_prefix import PREFIX

sv_get_info = SV('zzz查询信息')


@sv_get_info.on_command(f'{PREFIX}uid')
async def send_role_info(bot: Bot, ev: Event):
    pass


@sv_get_info.on_command(f'{PREFIX}练度统计')
async def send_detail_info(bot: Bot, ev: Event):
    pass
