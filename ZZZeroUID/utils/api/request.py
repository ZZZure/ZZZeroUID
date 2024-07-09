import time
from copy import deepcopy
from typing import Dict, List, Union, Literal, Optional, cast

from gsuid_core.utils.api.mys_api import _MysApi
from gsuid_core.utils.database.models import GsUser

from .models import (
    ZZZUser,
    ZZZNoteResp,
    ZZZIndexResp,
    ZZZAvatarInfo,
    ZZZAvatarBasic,
    ZZZBangbooResp,
    ZZZGachaLogResp,
)
from .api import (
    ZZZ_NOTE_API,
    ZZZ_INDEX_API,
    ZZZ_GAME_INFO_API,
    ZZZ_BUDDY_INFO_API,
    ZZZ_AVATAR_INFO_API,
    ZZZ_AVATAR_BASIC_API,
    ZZZ_GET_GACHA_LOG_API,
)

# from gsuid_core.utils.api.mys.tools import get_ds_token


class ZZZApi(_MysApi):
    def __init__(self):
        self.ZZZ_HEADER = deepcopy(self._HEADER)
        del self.ZZZ_HEADER["x-rpc-client_type"]
        self.ZZZ_HEADER.update(
            {
                "x-rpc-page": "v1.0.14_#/zzz",
                "x-rpc-platform": "2",
                "Referer": "https://act.mihoyo.com/",
                "Origin": "https://act.mihoyo.com",
            }
        )

    async def get_ck(
        self, uid: str, mode: Literal["OWNER", "RANDOM"] = "RANDOM"
    ) -> Optional[str]:
        if mode == "RANDOM":
            return await GsUser.get_random_cookie(uid, game_name="zzz")
        else:
            return await GsUser.get_user_cookie_by_uid(uid, game_name="zzz")

    async def get_stoken(self, uid: str) -> Optional[str]:
        return await GsUser.get_user_stoken_by_uid(uid, game_name="zzz")

    async def get_zzz_user_info(self, uid: str) -> Union[int, ZZZUser]:
        header = deepcopy(self.ZZZ_HEADER)
        ck = await self.get_ck(uid, "OWNER")
        if not ck:
            return -51
        header["Cookie"] = ck
        data = await self._mys_request(ZZZ_GAME_INFO_API, header=header)
        if isinstance(data, Dict):
            for i in data["data"]["list"]:
                if uid == i["game_uid"]:
                    return cast(ZZZUser, i)
            else:
                return -51
        return data

    async def get_zzz_note_info(self, uid: str) -> Union[int, ZZZNoteResp]:
        data = await self.simple_zzz_req(ZZZ_NOTE_API, uid)
        if isinstance(data, Dict):
            data = cast(ZZZNoteResp, data["data"])
        return data

    async def get_zzz_index_info(self, uid: str) -> Union[int, ZZZIndexResp]:
        data = await self.simple_zzz_req(ZZZ_INDEX_API, uid)
        if isinstance(data, Dict):
            data = cast(ZZZIndexResp, data["data"])
        return data

    async def get_zzz_bangboo_info(self, uid: str) -> Union[
        int,
        ZZZBangbooResp,
    ]:
        data = await self.simple_zzz_req(ZZZ_BUDDY_INFO_API, uid)
        if isinstance(data, Dict):
            data = cast(ZZZBangbooResp, data["data"])
        return data

    async def get_zzz_avatar_info(
        self,
        uid: str,
        id_list: Union[List[int], List[str]],
    ) -> Union[
        int,
        List[ZZZAvatarInfo],
    ]:
        data = await self.simple_zzz_req(
            ZZZ_AVATAR_INFO_API,
            uid,
            {
                "id_list[]": [str(i) for i in id_list],
                "need_wiki": False,
            },
        )
        if isinstance(data, Dict):
            data = cast(List[ZZZAvatarInfo], data["data"]["avatar_list"])
        return data

    async def get_zzz_avatar_basic_info(self, uid: str) -> Union[
        int,
        List[ZZZAvatarBasic],
    ]:
        data = await self.simple_zzz_req(ZZZ_AVATAR_BASIC_API, uid)
        if isinstance(data, Dict):
            data = cast(List[ZZZAvatarBasic], data["data"]["avatar_list"])
        return data

    async def get_zzz_gacha_log_by_authkey(
        self,
        uid: str,
        gacha_type: str = "2001",
        init_log_gacha_base_type: str = "2",
        page: int = 1,
        end_id: str = "0",
    ):
        server_id = "prod_gf_cn"
        authkey_rawdata = await self.get_authkey_by_cookie(
            uid,
            "nap_cn",
            server_id,
        )
        if isinstance(authkey_rawdata, int):
            return authkey_rawdata
        authkey = authkey_rawdata["authkey"]
        url = ZZZ_GET_GACHA_LOG_API
        data = await self._mys_request(
            url=url,
            method="GET",
            header=self._HEADER,
            params={
                "authkey_ver": "1",
                "sign_type": "2",
                "auth_appid": "webview_gacha",
                "init_log_gacha_type": gacha_type,
                "init_log_gacha_base_type": init_log_gacha_base_type,
                "gacha_id": "2c1f5692fdfbb733a08733f9eb69d32aed1d37",
                "timestamp": str(int(time.time())),
                "lang": "zh-cn",
                "device_type": "mobile",
                "plat_type": "ios",
                "region": server_id,
                "authkey": authkey,
                "game_biz": "nap_cn",
                "gacha_type": gacha_type,
                "real_gacha_type": init_log_gacha_base_type,
                "page": page,
                "size": "20",
                "end_id": end_id,
            },
        )
        if isinstance(data, Dict):
            data = cast(ZZZGachaLogResp, data["data"])
        return data

    async def get_zzz_gacha_record_by_link(
        self,
        url: str,
        gacha_type: str = "2001",
        page: int = 1,
        page_size: int = 10,
    ) -> Union[int, ZZZGachaLogResp]:
        if url is None:
            raise Exception("[zzz] gacha_record url is None")
        data = await self._mys_request(
            url=url,
            method="GET",
            params={
                "size": page_size,
                "page": page,
                "gacha_type": gacha_type,
                "init_log_gacha_type": gacha_type,
            },
        )
        if isinstance(data, Dict):
            data = cast(ZZZGachaLogResp, data["data"])
        return data

    async def simple_zzz_req(
        self,
        URL: str,
        uid: Union[str, bool],
        params: Dict = {},  # noqa: B006
        header: Dict = {},  # noqa: B006
        cookie: Optional[str] = None,
    ) -> Union[Dict, int]:
        server_id = "prod_gf_cn"
        params.update({"role_id": uid, "server": server_id})
        print(params)
        HEADER = deepcopy(self.ZZZ_HEADER)
        HEADER.update(header)

        # ex_params = '&'.join([f'{k}={v}' for k, v in params.items()])
        # HEADER['DS'] = get_ds_token(ex_params)

        if cookie is not None:
            HEADER["Cookie"] = cookie
        elif "Cookie" not in HEADER and isinstance(uid, str):
            ck = await self.get_ck(uid)
            if ck is None:
                return -51
            HEADER["Cookie"] = ck

        data = await self._mys_request(
            url=URL,
            method="GET",
            header=HEADER,
            params=params,
        )
        return data
