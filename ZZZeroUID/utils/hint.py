from copy import deepcopy

from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.utils.error_reply import ERROR_CODE

prefix = get_plugin_available_prefix("ZZZeroUID")
BIND_UID_HINT = f"你还没有绑定UID哦, 请使用 {prefix}绑定uid 完成绑定！"

ZZZ_ERROR_CODE = deepcopy(ERROR_CODE)
ZZZ_ERROR_CODE.update()


def error_reply(retcode: int, msg: str = "") -> str:
    msg_list = [f"❌错误代码为: {retcode}"]
    if msg:
        msg_list.append(f"📝错误信息: {msg}")
    elif retcode in ZZZ_ERROR_CODE:
        msg_list.append(f"📝错误信息: {ZZZ_ERROR_CODE[retcode]}")
    return "\n".join(msg_list)
