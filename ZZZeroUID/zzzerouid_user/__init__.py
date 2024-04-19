from typing import List

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.database.models import GsBind

from ..utils.zzzero_prefix import PREFIX

sv_user_config = SV('zzz用户管理', pm=2)
sv_user_info = SV('zzz用户信息')


@sv_user_info.on_fullmatch(f'{PREFIX}绑定信息')
async def send_bind_card(bot: Bot, ev: Event):
    pass


@sv_user_info.on_command(
    (
        f'{PREFIX}绑定uid',
        f'{PREFIX}切换uid',
        f'{PREFIX}删除uid',
        f'{PREFIX}解绑uid',
    )
)
async def send_link_uid_msg(bot: Bot, ev: Event):
    pass
