from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger
from gsuid_core.utils.database.models import GsBind
from gsuid_core.utils.sign.sign import sign_in, daily_sign
from gsuid_core.utils.boardcast.send_msg import send_board_cast_msg

from ..utils.hint import BIND_UID_HINT
from ..utils.zzzero_prefix import PREFIX
from ..zzzerouid_config.zzzero_config import ZZZ_CONFIG

sv_zzz_sign = SV('绝区零米游社签到')
sv_zzz_sign_config = SV('绝区零米游社签到配置', pm=1)

SIGN_TIME = ZZZ_CONFIG.get_config('SignTime').data
IS_REPORT = ZZZ_CONFIG.get_config('PrivateSignReport').data


@sv_zzz_sign.on_fullmatch(f'{PREFIX}签到')
async def get_sign_func(bot: Bot, ev: Event):
    logger.info(f'[绝区零] [签到] 用户: {ev.user_id}')
    uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, 'zzz')
    if uid is None:
        return await bot.send(BIND_UID_HINT)
    logger.info(f'[绝区零] [签到] UID: {uid}')
    await bot.send(await sign_in(uid, 'zzz'))


@sv_zzz_sign_config.on_fullmatch(f'{PREFIX}全部重签')
async def recheck(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[全部重签]')
    await bot.send('[绝区零] [全部重签] 已开始执行!')
    result = await daily_sign('zzz')
    if not IS_REPORT:
        result['private_msg_dict'] = {}
    await send_board_cast_msg(result)
    await bot.send('[绝区零] [全部重签] 执行完成!')


# 每日零点半执行米游社原神签到
@scheduler.scheduled_job('cron', hour=SIGN_TIME[0], minute=SIGN_TIME[1])
async def zzz_sign_at_night():
    if ZZZ_CONFIG.get_config('SchedSignin').data:
        result = await daily_sign('zzz')
        if not IS_REPORT:
            result['private_msg_dict'] = {}
        await send_board_cast_msg(result)
