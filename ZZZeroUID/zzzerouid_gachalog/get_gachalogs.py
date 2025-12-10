import json
import shutil
import asyncio
from typing import Dict
from datetime import datetime, timedelta

import msgspec
import aiofiles

from gsuid_core.logger import logger

from ..utils.hint import error_reply
from ..utils.zzzero_api import zzz_api
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH

NULL_GACHA_LOG = {
    "音擎频段": [],
    "独家频段": [],
    "常驻频段": [],
    "邦布频段": [],
}

gacha_type_meta_data = {
    "音擎频段": ["3001"],
    "独家频段": ["2001"],
    "常驻频段": ["1001"],
    "邦布频段": ["5001"],
}


async def get_new_gachalog(uid: str, full_data: Dict, is_force: bool):
    temp = []
    for gacha_name in gacha_type_meta_data:
        for gacha_type in gacha_type_meta_data[gacha_name]:
            end_id = "0"

            server_id = zzz_api._get_region(uid)
            authkey_rawdata = await zzz_api.get_authkey_by_cookie(
                uid,
                "nap_cn",
                server_id,
            )
            if isinstance(authkey_rawdata, int):
                return authkey_rawdata
            authkey = authkey_rawdata["authkey"]

            for page in range(1, 999):
                data = await zzz_api.get_zzz_gacha_log_by_authkey(
                    uid,
                    authkey,
                    gacha_type,
                    gacha_type[0],
                    page,
                    end_id,
                )
                await asyncio.sleep(0.9)
                if isinstance(data, int):
                    return data
                data = data["list"]
                if data == []:
                    break
                end_id = data[-1]["id"]

                if gacha_name not in full_data:
                    full_data[gacha_name] = []

                if data[-1] in full_data[gacha_name] and not is_force:
                    for item in data:
                        if item not in full_data[gacha_name]:
                            temp.append(item)
                    full_data[gacha_name][0:0] = temp
                    temp = []
                    break
                if len(full_data[gacha_name]) >= 1:
                    full_id = full_data[gacha_name][0]["id"]
                    if int(data[0]["id"]) <= int(full_id):
                        full_data[gacha_name][0:0] = data
                    else:
                        full_data[gacha_name].extend(data)
                else:
                    full_data[gacha_name][0:0] = data
                await asyncio.sleep(0.5)
    return full_data


def remove_gachalog(gachalog: Dict, month: int = 5):
    now = datetime.now()
    threshold = now - timedelta(days=month * 30)

    map_num = {
        "常驻频段": "normal_gacha_num",
        "独家频段": "char_gacha_num",
        "音擎频段": "weapon_gacha_num",
        "邦布频段": "bangboo_gacha_num",
    }
    for gacha_name in map_num:
        gachanum_name = map_num[gacha_name]
        gachalog["data"][gacha_name] = [
            item
            for item in gachalog["data"][gacha_name]
            if datetime.strptime(item["time"], "%Y-%m-%d %H:%M:%S") <= threshold
        ]
        gachalog[gachanum_name] = len(gachalog["data"][gacha_name])

    return gachalog


async def save_gachalogs(
    uid: str,
    is_force: bool = False,
) -> str:
    path = PLAYER_PATH / str(uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H-%M-%S")
    result = {}

    # 抽卡记录json路径
    gachalogs_path = path / "gacha_logs.json"
    if gachalogs_path.exists():
        async with aiofiles.open(gachalogs_path, "r", encoding="UTF-8") as f:
            gacha_log = json.loads(await f.read())
        gachalogs_history = gacha_log["data"]
        old_normal_gacha_num = len(gachalogs_history.get("常驻频段", []))
        old_char_gacha_num = len(gachalogs_history.get("独家频段", []))
        old_weapon_gacha_num = len(gachalogs_history.get("音擎频段", []))
        old_bangboo_gacha_num = len(gachalogs_history.get("邦布频段", []))
    else:
        gachalogs_history = {}
        (
            old_normal_gacha_num,
            old_char_gacha_num,
            old_weapon_gacha_num,
            old_bangboo_gacha_num,
        ) = (0, 0, 0, 0)

    for i in gachalogs_history:
        if len(gachalogs_history[i]) >= 1:
            gachalogs_history[i].sort(key=lambda x: (-int(x["id"])))
    raw_data = await get_new_gachalog(uid, gachalogs_history, is_force)
    if isinstance(raw_data, int):
        return error_reply(raw_data)

    result["uid"] = uid
    result["data_time"] = current_time
    result["normal_gacha_num"] = len(raw_data.get("常驻频段", []))
    result["char_gacha_num"] = len(raw_data.get("独家频段", []))
    result["weapon_gacha_num"] = len(raw_data.get("音擎频段", []))
    result["bangboo_gacha_num"] = len(raw_data.get("邦布频段", []))
    for i in raw_data:
        if len(raw_data[i]) > 1:
            raw_data[i].sort(key=lambda x: (-int(x["id"])))
    result["data"] = raw_data

    # 计算数据
    normal_add = result["normal_gacha_num"] - old_normal_gacha_num
    char_add = result["char_gacha_num"] - old_char_gacha_num
    weapon_add = result["weapon_gacha_num"] - old_weapon_gacha_num
    bangboo_add = result["bangboo_gacha_num"] - old_bangboo_gacha_num
    all_add = normal_add + char_add + weapon_add + bangboo_add

    vo = msgspec.to_builtins(result)
    async with aiofiles.open(gachalogs_path, "w", encoding="UTF-8") as file:
        await file.write(json.dumps(vo, indent=2, ensure_ascii=False))

    # 回复文字
    if all_add == 0:
        im = f"🌱UID{uid}没有新增调频数据!"
    else:
        im = (
            f"✅UID{uid}数据更新成功！"
            f"本次更新{all_add}个数据\n"
            f"常驻频段{normal_add}个！\n独家频段{char_add}个！\n"
            f"音擎频段{weapon_add}个！\n邦布频段{bangboo_add}个！"
        )
    return im


full_lock = []


async def get_full_gachalog(uid: str):
    if uid in full_lock:
        return "当前正在全量刷新抽卡记录中, 请勿重试!请稍后再试...!"

    full_lock.append(uid)
    path = PLAYER_PATH / str(uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H-%M-%S")
    # 抽卡记录json路径
    gachalogs_path = path / "gacha_logs.json"
    if gachalogs_path.exists():
        gacha_log_backup_path = path / f"gacha_logs_{current_time}.json"
        shutil.copy(gachalogs_path, gacha_log_backup_path)
        logger.info(f"[全量刷新抽卡记录] 已备份抽卡记录到{gacha_log_backup_path}")
        async with aiofiles.open(gachalogs_path, "r", encoding="UTF-8") as f:
            gachalogs_history: Dict = json.loads(await f.read())
        gachalogs_history = remove_gachalog(gachalogs_history)
        async with aiofiles.open(gachalogs_path, "w", encoding="UTF-8") as f:
            await f.write(
                json.dumps(
                    gachalogs_history,
                    ensure_ascii=False,
                )
            )
        im = await save_gachalogs(uid)
    else:
        im = "你还没有已缓存的抽卡记录, 请使用刷新抽卡记录！"
    full_lock.remove(uid)
    return im
