from __future__ import annotations

from typing import Any, Dict, Union, Literal, Optional, cast

from httpx import AsyncClient

from .api import ZZZ_CHARACTER
from .models import CharacterData
from ...version import ZZZero_version

AnyDict = Dict[str, Any]
_HEADER = {'User-Agent': f'ZZZeroUID/{ZZZero_version}'}


async def get_hakush_char_data(
    id: Union[int, str],
) -> Optional[CharacterData]:
    data = await _hakush_request(url=ZZZ_CHARACTER.format(id))
    if isinstance(data, Dict):
        return cast(CharacterData, data)
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
            method, url=url, headers=header, params=params, json=data
        )
        data = req.json()
        return data
