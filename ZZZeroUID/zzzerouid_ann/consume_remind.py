from typing import List

from ..utils.hint import error_reply
from ..utils.api.models import InnerListItem
from ..utils.zzzero_api import zzz_api


async def comsume_all_remind(uid: str):
    platform = ["pc"]
    ids: List[InnerListItem] = []
    for p in platform:
        ann_list = await zzz_api.get_zzz_ann(
            uid,
            platform=p,
            _type="getAnnList",
        )
        if isinstance(ann_list, int):
            return error_reply(ann_list)
        for label in ann_list["list"]:
            ids += list(filter(lambda x: x["remind"] == 1, label["list"]))
    all_remind_id = [x["ann_id"] for x in ids]
    msg = f"✅[绝区零] 取消公告红点完毕! \n📝一共取消了{len(ids)}个！"

    success = 0
    for ann_id in all_remind_id:
        for p in platform:
            retcode = await zzz_api.get_zzz_ann(
                uid,
                platform=p,
                _type="consumeRemind",
                ann_id=ann_id,
            )
            if retcode != 0:
                if success != 0:
                    im = f"❌[绝区零] 取消公告红点途中失败！ \n📝一共取消了{success}个！"
                else:
                    im = "❌[绝区零] 取消公告红点失败！"
                im += f"\n📌{error_reply(retcode)}"
                return im
            success += 1
    return msg
