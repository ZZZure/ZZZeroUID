from typing import Dict, List

from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.logger import logger
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.utils.database.models import Subscribe

from ..utils.api.models import ZZZNoteResp
from ..utils.zzzero_api import zzz_api

prefix = get_plugin_available_prefix("ZZZeroUID")
ZZZ_NOTICE = f"可发送[{prefix}便签]或者[{prefix}每日]来查看更多信息!"

NOTICE = {
    "stamina": "🔋 你的体力快满啦！",
}
NOTICE_MAP = {
    "stamina": "体力",
}


async def get_notice_list():
    datas = await gs_subscribe.get_subscribe("[绝区零] 推送")
    datas = await gs_subscribe._to_dict(datas)

    stamina_datas = await gs_subscribe.get_subscribe("[绝区零] 体力")
    stamina_datas = await gs_subscribe._to_dict(stamina_datas)

    for uid in datas:
        if uid:
            raw_data = await zzz_api.get_zzz_note_info(uid)
            if isinstance(raw_data, int):
                logger.error(f"[绝区零推送提醒] 获取{uid}的数据失败!")
                continue

            for mode in NOTICE:
                _datas: Dict[str, List[Subscribe]] = locals()[f"{mode}_datas"]
                if uid in _datas:
                    _data_list = _datas[uid]
                    for _data in _data_list:
                        if _data.extra_message:
                            res = await check(
                                mode,
                                raw_data,
                                int(_data.extra_message),
                            )
                            if res:
                                mlist = [
                                    f"🚨 绝区零推送提醒 - UID{uid}",
                                    res,
                                    ZZZ_NOTICE,
                                ]
                                await _data.send("\n".join(mlist))


async def check(mode: str, data: ZZZNoteResp, limit: int) -> str:
    energy_data = data["energy"]
    progress = energy_data["progress"]
    current = progress["current"]
    max_power = progress["max"]
    base_notice = "你的电量"
    if current >= max_power:
        return base_notice + "已满！" + ZZZ_NOTICE
    if current >= limit:
        current_status = f"当前{current}/{max_power}，将于"
        if energy_data["day_type"] == 1:
            current_status += "今"
        else:
            current_status += "明"
        minute = str(energy_data["minute"]).zfill(2)
        current_status += f"日{energy_data['hour']}:{minute}回满"
        return base_notice + "已达提醒阈值！\n" + current_status
    return ""
