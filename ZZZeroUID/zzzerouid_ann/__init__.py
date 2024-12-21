from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger
from gsuid_core.subscribe import gs_subscribe

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from .consume_remind import comsume_all_remind

sv_zzz_ann = SV('清空公告红点')
sv_ann_schedule = SV('定时清空公告红点', priority=3)


@sv_zzz_ann.on_fullmatch(('清空公告红点', '清除公告红点'))
async def get_ann_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    logger.info(f'[绝区零][清空公告红点] UID: {uid}')

    if not uid:
        return await bot.send(BIND_UID_HINT)
    logger.info('[绝区零][清空公告红点] 正在执行中!')

    msg = await comsume_all_remind(uid)
    await bot.send(msg)


@sv_ann_schedule.on_fullmatch(('开启自动清红', '关闭自动清红'))
async def get_ann_schedule_msg(bot: Bot, ev: Event):
    uid = await get_uid(bot, ev)
    if not uid:
        return await bot.send(BIND_UID_HINT)

    logger.info(f'[绝区零][开启定时清空公告红点] UID: {uid}')
    await gs_subscribe.add_subscribe(
        'single',
        '[绝区零] 自动清红',
        ev,
        extra_message=uid,
    )
    await bot.send(f'UID{uid}已开启自动清红!')


@scheduler.scheduled_job('cron', hour='*/2')
async def send_ann_schedule():
    logger.info('[绝区零][定时清空公告红点] 正在执行中!')
    datas = await gs_subscribe.get_subscribe('[绝区零] 自动清红')
    if datas:
        for subscribe in datas:
            if subscribe.extra_message:
                await comsume_all_remind(subscribe.extra_message)
