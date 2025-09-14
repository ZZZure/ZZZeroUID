from typing import Union

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.utils.sign.sign import sign_in
from gsuid_core.utils.database.models import GsBind

from ..utils.hint import BIND_UID_HINT
from ..zzzerouid_config.zzzero_config import ZZZ_CONFIG

sv_zzz_sign = SV('绝区零米游社签到')
sv_zzz_sign_config = SV('绝区零米游社签到配置', pm=1)

SIGN_TIME = ZZZ_CONFIG.get_config('SignTime').data
IS_REPORT = ZZZ_CONFIG.get_config('PrivateSignReport').data


@sv_zzz_sign.on_fullmatch('签到')
async def get_sign_func(bot: Bot, ev: Event):
    logger.info(f'[绝区零] [签到] 用户: {ev.user_id}')
    uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, 'zzz')
    if uid is None:
        return await bot.send(BIND_UID_HINT)
    logger.info(f'[绝区零] [签到] UID: {uid}')
    await bot.send(await sign_in(uid, 'zzz'))


@sv_zzz_sign_config.on_fullmatch('全部重签')
async def recheck(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[全部重签]')
    await bot.send('🚩 [绝区零] [全部重签] 已开始执行!')
    await zzz_sign_at_night(True)
    await bot.send('🚩 [绝区零] [全部重签] 执行完成!')


async def sign_in_task(uid: Union[str, int]):
    return await sign_in(str(uid), 'zzz')


# 每日零点半执行米游社原神签到
@scheduler.scheduled_job('cron', hour=SIGN_TIME[0], minute=SIGN_TIME[1])
async def zzz_sign_at_night(force: bool = False):
    if ZZZ_CONFIG.get_config('SchedSignin').data or force:
        datas = await gs_subscribe.get_subscribe('[绝区零] 自动签到')
        priv_result, group_result = await gs_subscribe.muti_task(
            datas, sign_in_task, 'uid'
        )
        if not IS_REPORT:
            priv_result = {}

        for _, data in priv_result.items():
            im = '\n'.join(data['im'])
            event = data['event']
            await event.send(im)

        for _, data in group_result.items():
            im = '✅ 绝区零今日自动签到已完成！\n'
            im += f'📝 本群共签到成功{data["success"]}人，共签到失败{data["fail"]}人。'
            event = data['event']
            await event.send(im)

        logger.info('[绝区零] [每日全部签到]群聊推送完成')
