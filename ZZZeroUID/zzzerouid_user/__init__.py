from typing import List

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.database.models import GsBind

from ..utils.message import send_diff_msg
from ..utils.zzzero_prefix import PREFIX
from ..zzzerouid_config.zzzero_config import ZZZ_GAME_NAME

sv_user_config = SV(f'{PREFIX}用户管理', pm=2)
sv_user_info = SV(f'{PREFIX}用户信息')


@sv_user_info.on_fullmatch(f'{PREFIX}绑定uid')
async def bind_uid(bot: Bot, ev: Event):
    qid = ev.user_id
    uid = ev.text.strip()
    await bot.logger.info(f'zzz开始执行uid绑定, qid={qid}, uid={uid}')
    data = await GsBind.insert_uid(qid, ev.bot_id, uid, ev.group_id, 32, game_name=ZZZ_GAME_NAME)
    return await send_diff_msg(bot, data, {
        0: f'绑定uid[{uid}]成功!',
        -1: f'uid[{uid}]的位数不正确!',
        -2: f'uid[{uid}]已经绑定过了!',
        -3: '你输入了错误的格式!'
        }
    )


@sv_user_info.on_fullmatch(f'{PREFIX}切换uid')
async def bind_uid(bot: Bot, ev: Event):
    qid = ev.user_id
    uid = ev.text.strip()
    data = await GsBind.switch_uid_by_game(qid, ev.bot_id, uid, ZZZ_GAME_NAME)
    if isinstance(data, List):
        return await bot.send(f'切换uid[{uid}]成功!')
    return await bot.send(f'尚未绑定该uid[{uid}]')



@sv_user_info.on_fullmatch(f'{PREFIX}解绑uid')
async def unbind_uid(bot: Bot, ev: Event):
    pass


@sv_user_info.on_fullmatch(f'{PREFIX}删除uid')
async def delete_uid(bot: Bot, ev: Event):
    qid = ev.user_id
    uid = ev.text.strip()
    data = await GsBind.delete_uid(qid, ev.bot_id, uid, ZZZ_GAME_NAME)
    return await send_diff_msg(
        bot,
        data,
        {
            0: f'删除uid[{uid}]成功!',
            -1: f'该uid[{uid}]不在已绑定列表中!',
        }
    )
