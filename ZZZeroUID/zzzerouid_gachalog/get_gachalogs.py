import json
import shutil
import asyncio
from typing import Any, Dict, List
from datetime import datetime, timedelta

import msgspec
import aiofiles

from gsuid_core.logger import logger

from ..utils.hint import error_reply
from .check_gachalogs import (
    merge_gacha_list,
    upsert_gacha_item,
    gacha_list_contains,
)
from ..utils.zzzero_api import zzz_api
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH

NULL_GACHA_LOG = {
    "音擎频段": [],
    "独家频段": [],
    "常驻频段": [],
    "邦布频段": [],
    "独家重映": [],
    "音擎回响": [],
}

gacha_type_meta_data = {
    "音擎频段": ["3001"],
    "独家频段": ["2001"],
    "常驻频段": ["1001"],
    "邦布频段": ["5001"],
    "独家重映": ["12002"],
    "音擎回响": ["13002"],
}

# init_log_gacha_base_type / real_gacha_type
GACHA_BASE_TYPE_MAP = {
    "3001": "3",
    "2001": "2",
    "1001": "1",
    "5001": "5",
    "12002": "102",
    "13002": "103",
}

OPTIONAL_GACHA_NAMES = ("独家重映", "音擎回响")

GACHA_NUM_MAP = {
    "常驻频段": "normal_gacha_num",
    "独家频段": "char_gacha_num",
    "音擎频段": "weapon_gacha_num",
    "邦布频段": "bangboo_gacha_num",
    "独家重映": "char_rerun_gacha_num",
    "音擎回响": "weapon_echo_gacha_num",
}


def _to_record_list(items: List[Any]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            records.append(dict(item))
    return records


def _drop_empty_optional_pools(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    for name in OPTIONAL_GACHA_NAMES:
        if name in data and not data[name]:
            data.pop(name)
    return data


async def get_new_gachalog(uid: str, full_data: Dict, is_force: bool):
    server_id = zzz_api._get_region(uid)
    authkey_rawdata = await zzz_api.get_authkey_by_cookie(
        uid,
        "nap_cn",
        server_id,
        "zzz",
    )
    if isinstance(authkey_rawdata, int):
        return authkey_rawdata
    authkey = authkey_rawdata["authkey"]

    temp: List[Dict[str, Any]] = []
    for gacha_name in gacha_type_meta_data:
        for gacha_type in gacha_type_meta_data[gacha_name]:
            end_id = "0"
            base_type = GACHA_BASE_TYPE_MAP.get(gacha_type, gacha_type[:1])
            is_optional = gacha_name in OPTIONAL_GACHA_NAMES

            for page in range(1, 999):
                data = await zzz_api.get_zzz_gacha_log_by_authkey(
                    uid,
                    authkey,
                    gacha_type,
                    base_type,
                    page,
                    end_id,
                )
                await asyncio.sleep(0.9)
                if isinstance(data, int):
                    if is_optional:
                        logger.warning(f"[ZZZ刷新抽卡记录] {gacha_name}({gacha_type}) 拉取失败({data})，已跳过")
                        break
                    return data
                records = _to_record_list(list((data or {}).get("list") or []))
                if not records:
                    break
                end_id = str(records[-1]["id"])

                if gacha_name not in full_data:
                    full_data[gacha_name] = []

                # 到达已缓存区间：按预设 key/id 合并后停止，不按整 dict 判断
                if gacha_list_contains(full_data[gacha_name], records[-1]) and not is_force:
                    for item in records:
                        if not gacha_list_contains(full_data[gacha_name], item):
                            temp.append(item)
                        else:
                            upsert_gacha_item(full_data[gacha_name], item)
                    full_data[gacha_name][0:0] = temp
                    temp = []
                    break
                if len(full_data[gacha_name]) >= 1:
                    if int(records[-1]["id"]) <= int(full_data[gacha_name][0]["id"]):
                        full_data[gacha_name].extend(records)
                    else:
                        full_data[gacha_name][0:0] = records
                else:
                    full_data[gacha_name].extend(records)
                await asyncio.sleep(0.5)
    for pool_name in full_data:
        full_data[pool_name] = merge_gacha_list(full_data[pool_name])
    return full_data


def remove_gachalog(gachalog: Dict, month: int = 5):
    now = datetime.now()
    threshold = now - timedelta(days=month * 30)

    data = gachalog.get("data") or {}
    for gacha_name, gachanum_name in GACHA_NUM_MAP.items():
        if gacha_name not in data:
            continue
        filtered = [
            item for item in data[gacha_name] if datetime.strptime(item["time"], "%Y-%m-%d %H:%M:%S") <= threshold
        ]
        if gacha_name in OPTIONAL_GACHA_NAMES and not filtered:
            del data[gacha_name]
            gachalog.pop(gachanum_name, None)
            continue
        data[gacha_name] = filtered
        gachalog[gachanum_name] = len(filtered)
    gachalog["data"] = data
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
    result: Dict[str, Any] = {}

    # 抽卡记录json路径
    gachalogs_path = path / "gacha_logs.json"
    old_nums = {name: 0 for name in GACHA_NUM_MAP}
    if gachalogs_path.exists():
        async with aiofiles.open(gachalogs_path, "r", encoding="UTF-8") as f:
            gacha_log = json.loads(await f.read())
        gachalogs_history = gacha_log.get("data") or {}
        if not isinstance(gachalogs_history, dict):
            return "抽卡记录文件格式错误，请检查本地 gacha_logs.json！"
        for name in GACHA_NUM_MAP:
            items = gachalogs_history.get(name, [])
            old_nums[name] = len(items) if isinstance(items, list) else 0
    else:
        gachalogs_history = {}

    for i in gachalogs_history:
        if len(gachalogs_history[i]) >= 1:
            gachalogs_history[i].sort(key=lambda x: -int(x["id"]))
    raw_data = await get_new_gachalog(uid, gachalogs_history, is_force)
    if isinstance(raw_data, int):
        return error_reply(raw_data)

    raw_data = _drop_empty_optional_pools(raw_data)

    result["uid"] = uid
    result["data_time"] = current_time
    for name, key in GACHA_NUM_MAP.items():
        count = len(raw_data.get(name, []))
        if name in OPTIONAL_GACHA_NAMES and count == 0:
            continue
        result[key] = count
    for i in raw_data:
        if len(raw_data[i]) > 1:
            raw_data[i].sort(key=lambda x: -int(x["id"]))
    result["data"] = raw_data

    # 计算数据
    adds = {name: result.get(key, 0) - old_nums[name] for name, key in GACHA_NUM_MAP.items()}
    all_add = sum(adds.values())

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
            f"常驻频段{adds['常驻频段']}个！\n独家频段{adds['独家频段']}个！\n"
            f"音擎频段{adds['音擎频段']}个！\n邦布频段{adds['邦布频段']}个！"
        )
        extra = []
        if adds["独家重映"]:
            extra.append(f"独家重映{adds['独家重映']}个！")
        if adds["音擎回响"]:
            extra.append(f"音擎回响{adds['音擎回响']}个！")
        if extra:
            im += "\n" + "\n".join(extra)
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
