import re
from typing import List, Tuple, Union, Optional, overload

from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.database.models import GsBind

from ..zzzerouid_config.zzzero_config import ZZZ_CONFIG

prefix = get_plugin_available_prefix("ZZZeroUID")
_IGNORE_AT_LIST: List[str] = ZZZ_CONFIG.get_config("ZZZIgnoreAt").data
IGNORE_AT_LIST = [f"{prefix}{i}" for i in _IGNORE_AT_LIST]


@overload
async def get_uid(bot: Bot, ev: Event, get_user_id: bool = False, only_uid: bool = False) -> Union[None, str]: ...


@overload
async def get_uid(
    bot: Bot, ev: Event, get_user_id: bool = True, only_uid: bool = False
) -> Tuple[Optional[str], str]: ...


async def get_uid(
    bot: Bot, ev: Event, get_user_id: bool = False, only_uid: bool = False
) -> Union[Optional[str], Tuple[Optional[str], str]]:
    uid_data = re.findall(r"\d{8,10}", ev.text)
    if ev.command in IGNORE_AT_LIST and ev.at:
        await bot.send("[绝区零] 该功能的@查询方式已被禁止！")
        raise Exception(f"[绝区零] [{ev.command}] 该功能的@查询方式已被禁止！")

    user_id = ev.at if ev.at else ev.user_id
    if uid_data:
        zzz_uid: Optional[str] = uid_data[0]
        if zzz_uid:
            ev.text = ev.text.replace(zzz_uid, "")
    else:
        zzz_uid = await GsBind.get_uid_by_game(user_id, ev.bot_id, "zzz")
    if only_uid:
        zzz_uid = await GsBind.get_uid_by_game(user_id, ev.bot_id, "zzz")
    if get_user_id:
        return zzz_uid, user_id
    return zzz_uid
