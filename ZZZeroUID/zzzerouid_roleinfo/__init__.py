from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from ..utils.zzzero_prefix import PREFIX

sv_get_info = SV('zzz查询信息')


@sv_get_info.on_command(f'{PREFIX}查询', block=True)
async def send_role_info(bot: Bot, ev: Event):
    pass
