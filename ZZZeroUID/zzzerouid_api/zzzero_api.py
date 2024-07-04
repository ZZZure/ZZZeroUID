from typing import Dict, Union

import msgspec
from gsuid_core.utils.api.mys_api import _MysApi

from .models import GachaLog

GACHA_TYPE = {
    '2001': '',
}


class ZZZApi(_MysApi):
    async def get_gacha_record_by_link(
        self,
        url: str,
        gacha_type: str = '2001',
        page: int = 1,
        page_size: int = 10,
    ) -> Union[int, GachaLog]:
        if url is None:
            raise Exception('[zzz] gacha_record url is None')
        data = await self._mys_request(
            url=url,
            method='GET',
            params={
                'size': page_size,
                'page': page,
                'gacha_type': gacha_type,
                'init_log_gacha_type': gacha_type,
            },
        )
        if isinstance(data, Dict):
            data = msgspec.convert(data['data'], type=GachaLog)
        return data


zzz_api = ZZZApi()
