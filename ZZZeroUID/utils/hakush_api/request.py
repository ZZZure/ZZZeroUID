from __future__ import annotations

from typing import Any, Dict, Union, Literal, Optional, cast

from httpx import AsyncClient

from ...version import ZZZero_version
from .api import (
    ZZZ_NEW,
    ZZZ_WEAPON,
    ZZZ_ALL_CHAR,
    ZZZ_CHARACTER,
    ZZZ_ALL_WEAPON,
)
from .models import (
    NewData,
    WeaponData,
    CharacterData,
    WeaponDatabase,
    CharacterDatabase,
)

AnyDict = Dict[str, Any]
_HEADER = {'User-Agent': f'ZZZeroUID/{ZZZero_version}'}


async def get_hakush_char_data(
    id: Union[int, str],
) -> Optional[CharacterData]:
    data = await _hakush_request(ZZZ_CHARACTER.format(id))
    if isinstance(data, Dict):
        return cast(CharacterData, data)
    return None


async def get_hakush_all_char_data() -> Optional[Dict[str, CharacterDatabase]]:
    data = await _hakush_request(ZZZ_ALL_CHAR)
    if isinstance(data, Dict):
        return cast(Dict[str, CharacterDatabase], data)
    return None


async def get_hakush_all_weapon_data() -> Optional[Dict[str, WeaponDatabase]]:
    data = await _hakush_request(ZZZ_ALL_WEAPON)
    if isinstance(data, Dict):
        return cast(Dict[str, WeaponDatabase], data)
    return None


async def get_hakush_weapon_data(
    id: Union[int, str],
) -> Optional[WeaponData]:
    data = await _hakush_request(ZZZ_WEAPON.format(id))
    if isinstance(data, Dict):
        return cast(WeaponData, data)
    return None


async def get_hakush_new_data() -> Optional[NewData]:
    data = await _hakush_request(ZZZ_NEW)
    if isinstance(data, Dict):
        return cast(NewData, data)
    return None


async def _hakush_request(
    url: str,
    method: Literal['GET', 'POST'] = 'GET',
    header: AnyDict = _HEADER,
    params: Optional[AnyDict] = None,
    data: Optional[AnyDict] = None,
) -> Optional[AnyDict]:
    async with AsyncClient(timeout=None) as client:
        req = await client.request(
            method,
            url=url,
            headers=header,
            params=params,
            json=data,
        )
        data = req.json()
        return data
