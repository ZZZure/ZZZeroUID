from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.database.models import GsBind

from .zzzero_config import ZZZ_CONFIG
from .set_config import set_config_func

PREFIX = ZZZ_CONFIG.get_config('ZZZPrefix').data

sv_self_config = SV('绝区零配置')


@sv_self_config.on_prefix((f'{PREFIX}开启', f'{PREFIX}关闭'))
async def open_switch_func(bot: Bot, ev: Event):
    uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, "zzz")
    if uid is None:
        return await bot.send('[绝区零] 你还没有绑定UID哦！')
    logger.info(
        f'[{ev.user_id}] [UID{uid}]尝试[{ev.command[2:]}]了[{ev.text}]功能'
    )
    await bot.send(await set_config_func(uid, ev))
