import re
from typing import Tuple, Union, Optional, overload

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.database.models import GsBind


@overload
async def get_uid(
    bot: Bot, ev: Event, get_user_id: bool = False, only_uid: bool = False
) -> Optional[str]: ...


@overload
async def get_uid(
    bot: Bot, ev: Event, get_user_id: bool = True, only_uid: bool = False
) -> Tuple[Optional[str], str]: ...


async def get_uid(
    bot: Bot, ev: Event, get_user_id: bool = False, only_uid: bool = False
) -> Union[Optional[str], Tuple[Optional[str], str]]:
    uid_data = re.findall(r'\d', ev.text)
    user_id = ev.at if ev.at else ev.user_id
    if uid_data:
        zzz_uid: Optional[str] = uid_data[0]
        if zzz_uid:
            ev.text = ev.text.replace(zzz_uid, '')
    else:
        zzz_uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, 'zzz')
    if only_uid:
        zzz_uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, 'zzz')
    if get_user_id:
        return zzz_uid, user_id
    return zzz_uid
