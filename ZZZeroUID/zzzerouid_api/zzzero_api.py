from gsuid_core.utils.api.mys_api import _MysApi
from gsuid_core.utils.database.models import GsUser
from string import digits, ascii_letters
from typing import Any, Dict, Union, Literal, Optional
import msgspec
import asyncio

from models import (
    GachaLog
)

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
            raise Exception('zzz gacha_record url is None')
        data = await self._mys_request(
            url=url,
            method='GET',
            params={
                'size': page_size,
                'page': page,
                'gacha_type': gacha_type,
                'init_log_gacha_type': gacha_type
            },
        )
        if isinstance(data, Dict):
            data = msgspec.convert(data['data'], type=GachaLog)
        return data

zzz_api = ZZZApi()

url = "https://public-operation-nap.mihoyo.com/common/gacha_record/api/nap/getGachaLog?authkey_ver=1&sign_type=2&auth_appid=webview_gacha&win_mode=fullscreen&gacha_id=a41a5a30e2f7b64126e5ca80ac06af304273bc&timestamp=1713267923&authkey=Q0wzN8Ds%2BeDaYeAksbj65IHWZJ8jmv33Ja%2Bv%2FSY8TQY%2BSyhk5PEHnw3DJ%2FgExCVtmt3bNYWGGtmyZYNieH9Xby49KBedDJ11l7VKrfcyui5khaDirinHOS%2BQ%2BY0SY%2F53PFEAXLom7AqfSO%2By8UaGHXHwYsyxQwAOgl2P%2FCdyc%2FI3RXI7mrPBqzOi3yHVJqYkkDBA64prjTl6OQEAbsOA5ESvmX4qMC396iCfeNO2vu2%2Fosj06yq86INodn%2FKAGObQYff5culI5LUKS1L8W%2F0LY9UCf5HJcGIJ9rUlgbOvlxVgy2xi5wRGLogRbnAywM6G4XNyhfA0wCss2Jz9KRnfndPqLG5u3FFHO%2FgIwLC1YZBEbryUCJ77fNGHZvfrt78kVNFhtWzIdLCOLaEtp6NO61pG5ixzVos%2FBpVoSlDSwYGpGFlj5WfcrIG9x2LitXS9bJzFvLZSCbb14sc9vaO1GqI92dPkxoLbxCaux5NyQMCxeYYf0t1pI0JKY0S5SkcPKIEavF3ALkuolpF4AB7pyYlpplUV3uSLrne593OAZUTFbhvcDA5zc%2BjbQqzBW3LelvEj7njZEmJ%2FbSIhq9A0Q%3D%3D&lang=zh-cn&region=prod_cb02_cn&game_biz=nap_cn&win_mode=fullscreen&init_log_gacha_type=1001&ui_layout=&button_mode=default&gacha_type=1001&end_id="
data = asyncio.run(zzz_api.get_gacha_record_by_link(url))
print(data)

