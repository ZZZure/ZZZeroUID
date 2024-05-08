import json
import asyncio
from pathlib import Path
from urllib import parse
from datetime import datetime
from typing import Dict, List, Optional

import msgspec
from gsuid_core.plugins.ZZZeroUID.ZZZeroUID.utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..zzzerouid_api.models import SingleGachaLog
from ..zzzerouid_api.zzzero_api import zzz_api


def get_new_chalogs_by_link(uid: str, gacha_url: str, full_data: Dict, is_force: bool):
    path = PLAYER_PATH / str(uid)

async def save_gachalogs(
    uid: str,
    gacha_url: str,
    raw_data: Optional[Dict] = None,
    is_force: bool = False,
) -> str:
    path = PLAYER_PATH / str(uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime('%Y-%m-%d %H-%M-%S')

    # 抽卡记录json路径
    gachalogs_path = path / 'gacha_logs.json'

    vo = zzz_api.get_gacha_record_by_link(gacha_url)
    result = msgspec.to_builtins(vo)
    with Path.open(gachalogs_path, 'w', encoding='UTF-8') as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    # 回复文字
    res_msg = f'{uid}抽卡记录刷新成功!'
    return res_msg


