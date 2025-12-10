from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.database.models import GsBind

from ..utils.message import send_diff_msg
from ..zzzerouid_config.zzzero_config import ZZZ_GAME_NAME

sv_user_info = SV("zzz用户信息")


@sv_user_info.on_command(
    (
        "绑定uid",
        "绑定UID",
        "绑定",
    ),
    block=True,
)
async def bind_uid(bot: Bot, ev: Event):
    qid = ev.user_id
    uid = ev.text.strip()
    await bot.logger.info(f"zzz开始执行uid绑定, qid={qid}, uid={uid}")

    if not uid:
        return await bot.send("[绝区零] 你需要在命令后面加入你绝区零的UID！")

    data = await GsBind.insert_uid(qid, ev.bot_id, uid, ev.group_id, game_name=ZZZ_GAME_NAME)

    return await send_diff_msg(
        bot,
        data,
        {
            0: f"✅[绝区零]绑定uid[{uid}]成功!",
            -1: f"❎[绝区零]uid[{uid}]的位数不正确!",
            -2: f"❎[绝区零]uid[{uid}]已经绑定过了!",
            -3: "❎[绝区零]你输入了错误的格式!",
        },
    )


@sv_user_info.on_command(
    (
        "切换uid",
        "切换UID",
        "切换",
    ),
    block=True,
)
async def switch_uid(bot: Bot, ev: Event):
    qid = ev.user_id
    uid = ev.text.strip()
    if uid and not uid.isdigit():
        return await bot.send("[绝区零] 你需要在切换命令后面加入你绝区零的UID或者直接输入切换命令！")

    data = await GsBind.switch_uid_by_game(
        qid,
        ev.bot_id,
        uid,
        ZZZ_GAME_NAME,
    )

    return await send_diff_msg(
        bot,
        data,
        {
            0: f"✅[绝区零]切换uid{uid}成功!",
            -1: "❎[绝区零]不存在绑定记录!",
            -2: "❎[绝区零]请绑定两个以上UID再进行切换!",
            -3: "❎[绝区零]请绑定两个以上UID再进行切换!",
        },
    )


@sv_user_info.on_command(
    (
        "删除uid",
        "解绑uid",
        "删除UID",
        "解绑",
        "删除UID",
        "删除",
    ),
    block=True,
)
async def delete_uid(bot: Bot, ev: Event):
    qid = ev.user_id
    uid = ev.text.strip()
    if not uid:
        return await bot.send("[绝区零] 你需要在解绑命令后面加入你绝区零的UID！")
    data = await GsBind.delete_uid(qid, ev.bot_id, uid, ZZZ_GAME_NAME)
    return await send_diff_msg(
        bot,
        data,
        {
            0: f"✅[绝区零]删除uid[{uid}]成功!",
            -1: f"❎[绝区零]该uid[{uid}]不在已绑定列表中!",
        },
    )
