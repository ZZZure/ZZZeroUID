import json
from typing import Union
from datetime import datetime

from ..utils.hint import error_reply
from ..utils.zzzero_api import zzz_api
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH


async def refresh_char(uid: str) -> Union[str, bytes]:
    raw_data = await zzz_api.get_zzz_avatar_basic_info(uid)
    if isinstance(raw_data, int):
        return error_reply(raw_data)
    id_list = [i["id"] for i in raw_data]
    data = await zzz_api.get_zzz_avatar_info(uid, id_list)
    if isinstance(data, int):
        return error_reply(data)

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    path = PLAYER_PATH / str(uid)
    path.mkdir(parents=True, exist_ok=True)
    im = []
    for avatar in data:
        save_data = {}
        save_data.update(avatar)
        _id = avatar["id"]
        save_data["uid"] = uid
        save_data["current_time"] = current_time

        with open(path / f"{_id}.json", "wb") as f:
            d = json.dumps(
                save_data,
                ensure_ascii=False,
                indent=4,
            ).encode("utf-8")
            f.write(d)

        im.append(avatar["name_mi18n"])
    msg = f"[绝区零] 刷新完成！本次刷新{len(im)}个角色!"
    msg += f'\n刷新角色列表:{",".join(im)}'
    return msg
