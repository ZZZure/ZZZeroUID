import time
from copy import deepcopy
from typing import Dict, List, Union, Literal, Optional, cast

from gsuid_core.utils.api.mys_api import _MysApi
from gsuid_core.utils.api.mys.models import MysGame
from gsuid_core.utils.database.models import GsUser

from .models import (
    ZZZUser,
    ZZZBangboo,
    ZZZNoteResp,
    ZZZIndexResp,
    ZZZAvatarInfo,
    ZZZAvatarBasic,
    ZZZGachaLogResp,
)
from .api import (
    ZZZ_API,
    ZZZ_OS_API,
    ZZZ_BIND_API,
    ZZZ_NOTE_API,
    ZZZ_INDEX_API,
    ZZZ_BIND_OS_API,
    ZZZ_GAME_INFO_API,
    ZZZ_BUDDY_INFO_API,
    ZZZ_AVATAR_INFO_API,
    ZZZ_AVATAR_BASIC_API,
    ZZZ_GET_GACHA_LOG_API,
)

# from gsuid_core.utils.api.mys.tools import get_ds_token

REGION_MAP = {
    '10': 'prod_gf_us',
    '13': 'prod_gf_jp',
    '15': 'prod_gf_eu',
    '17': 'prod_gf_sg',
}


class ZZZApi(_MysApi):
    def __init__(self):
        self.ZZZ_HEADER = deepcopy(self._HEADER)
        del self.ZZZ_HEADER['x-rpc-client_type']
        self.ZZZ_HEADER.update(
            {
                'x-rpc-page': 'v1.0.14_#/zzz',
                'x-rpc-platform': '2',
                'Referer': 'https://act.mihoyo.com/',
                'Origin': 'https://act.mihoyo.com',
            }
        )

    def _get_region(self, uid: str):
        if len(uid) < 10:
            server_id = 'prod_gf_cn'
        else:
            server_id = REGION_MAP.get(uid[:2], 'prod_gf_jp')
        return server_id

    async def get_ck(
        self, uid: str, mode: Literal['OWNER', 'RANDOM'] = 'RANDOM'
    ) -> Optional[str]:
        if mode == 'RANDOM':
            return await GsUser.get_random_cookie(
                uid,
                game_name='zzz',
                condition=(
                    {
                        'zzz_region': self._get_region(uid),
                    }
                    if len(uid) >= 10
                    else None
                ),
            )
        else:
            return await GsUser.get_user_cookie_by_uid(uid, game_name='zzz')

    async def get_stoken(self, uid: str) -> Optional[str]:
        return await GsUser.get_user_stoken_by_uid(uid, game_name='zzz')

    async def get_zzz_user_info_g(self, uid: str) -> Union[MysGame, int]:
        is_os = False if len(uid) < 10 else True
        mys_id = await GsUser.get_user_attr_by_uid(
            uid, 'mys_id', game_name='zzz'
        )
        if mys_id is None:
            return -100
        ck = await self.get_ck(uid, 'OWNER')
        if ck is None:
            return -51

        data = await self.get_mihoyo_bbs_info(mys_id, ck, is_os)
        if isinstance(data, int):
            return data
        for i in data:
            if uid == i['game_role_id'] and i['game_id'] == 8:
                return i
        else:
            return -51

    async def get_zzz_user_info(self, uid: str) -> Union[int, ZZZUser]:
        if len(uid) < 10:
            base_url = ZZZ_BIND_API
        else:
            base_url = ZZZ_BIND_OS_API

        header = deepcopy(self.ZZZ_HEADER)
        ck = await self.get_ck(uid, 'OWNER')
        if not ck:
            return -51
        header['Cookie'] = ck
        data = await self._mys_request(
            ZZZ_GAME_INFO_API,
            header=header,
            base_url=base_url,
        )
        if isinstance(data, Dict):
            for i in data['data']['list']:
                if uid == i['game_uid']:
                    return cast(ZZZUser, i)
            else:
                return -51
        return data

    async def get_zzz_note_info(self, uid: str) -> Union[int, ZZZNoteResp]:
        data = await self.simple_zzz_req(ZZZ_NOTE_API, uid)
        if isinstance(data, Dict):
            data = cast(ZZZNoteResp, data['data'])
        return data

    async def get_zzz_index_info(self, uid: str) -> Union[int, ZZZIndexResp]:
        data = await self.simple_zzz_req(ZZZ_INDEX_API, uid)
        if isinstance(data, Dict):
            data = cast(ZZZIndexResp, data['data'])
        return data

    async def get_zzz_bangboo_info(self, uid: str) -> Union[
        int,
        List[ZZZBangboo],
    ]:
        data = await self.simple_zzz_req(ZZZ_BUDDY_INFO_API, uid)
        if isinstance(data, Dict):
            data = cast(List[ZZZBangboo], data['data']['list'])
        return data

    async def get_zzz_avatar_info(
        self,
        uid: str,
        id_list: Union[List[int], List[str]],
    ) -> Union[
        int,
        List[ZZZAvatarInfo],
    ]:
        ck = await self.get_ck(uid, 'OWNER')
        if ck is None:
            return -51
        data = await self.simple_zzz_req(
            ZZZ_AVATAR_INFO_API,
            uid,
            {
                'id_list[]': [str(i) for i in id_list],
                'need_wiki': False,
            },
            cookie=ck,
        )
        if isinstance(data, Dict):
            data = cast(List[ZZZAvatarInfo], data['data']['avatar_list'])
        return data

    async def get_zzz_avatar_basic_info(self, uid: str) -> Union[
        int,
        List[ZZZAvatarBasic],
    ]:
        data = await self.simple_zzz_req(ZZZ_AVATAR_BASIC_API, uid)
        if isinstance(data, Dict):
            data = cast(List[ZZZAvatarBasic], data['data']['avatar_list'])
        return data

    async def get_zzz_gacha_log_by_authkey(
        self,
        uid: str,
        gacha_type: str = '2001',
        init_log_gacha_base_type: str = '2',
        page: int = 1,
        end_id: str = '0',
    ):
        server_id = self._get_region(uid)
        authkey_rawdata = await self.get_authkey_by_cookie(
            uid,
            'nap_cn',
            server_id,
        )
        if isinstance(authkey_rawdata, int):
            return authkey_rawdata
        authkey = authkey_rawdata['authkey']
        url = ZZZ_GET_GACHA_LOG_API
        data = await self._mys_request(
            url=url,
            method='GET',
            header=self._HEADER,
            params={
                'authkey_ver': '1',
                'sign_type': '2',
                'auth_appid': 'webview_gacha',
                'init_log_gacha_type': gacha_type,
                'init_log_gacha_base_type': init_log_gacha_base_type,
                'gacha_id': '2c1f5692fdfbb733a08733f9eb69d32aed1d37',
                'timestamp': str(int(time.time())),
                'lang': 'zh-cn',
                'device_type': 'mobile',
                'plat_type': 'ios',
                'region': server_id,
                'authkey': authkey,
                'game_biz': 'nap_cn',
                'gacha_type': gacha_type,
                'real_gacha_type': init_log_gacha_base_type,
                'page': page,
                'size': '20',
                'end_id': end_id,
            },
        )
        if isinstance(data, Dict):
            data = cast(ZZZGachaLogResp, data['data'])
        return data

    async def get_zzz_gacha_record_by_link(
        self,
        url: str,
        gacha_type: str = '2001',
        page: int = 1,
        page_size: int = 10,
    ) -> Union[int, ZZZGachaLogResp]:
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
            data = cast(ZZZGachaLogResp, data['data'])
        return data

    async def simple_zzz_req(
        self,
        URL: str,
        uid: str,
        params: Dict = {},  # noqa: B006
        header: Dict = {},  # noqa: B006
        cookie: Optional[str] = None,
    ) -> Union[Dict, int]:
        server_id = self._get_region(uid)
        if len(uid) < 10:
            base_url = ZZZ_API
        else:
            base_url = ZZZ_OS_API

        params.update({'role_id': uid, 'server': server_id})
        HEADER = deepcopy(self.ZZZ_HEADER)
        HEADER.update(header)

        # ex_params = '&'.join([f'{k}={v}' for k, v in params.items()])
        # HEADER['DS'] = get_ds_token(ex_params)

        if cookie is not None:
            HEADER['Cookie'] = cookie
        elif 'Cookie' not in HEADER and isinstance(uid, str):
            ck = await self.get_ck(uid)
            if ck is None:
                return -51
            HEADER['Cookie'] = ck

        data = await self._mys_request(
            url=URL,
            method='GET',
            header=HEADER,
            params=params,
            base_url=base_url,
        )
        return data
        return data
        return data
