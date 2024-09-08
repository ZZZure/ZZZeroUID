import asyncio

from gsuid_core.aps import scheduler
from gsuid_core.gss import gss
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from .notice import get_notice_list

from ..utils.uid import get_uid
from ..utils.hint import BIND_UID_HINT
from ..utils.zzzero_prefix import PREFIX
from .draw_zzz_stamina import draw_stamina_img

sv_get_stamina = SV('绝区零查询体力')


@sv_get_stamina.on_fullmatch(
    (
        f'{PREFIX}每日',
        f'{PREFIX}mr',
        f'{PREFIX}实时便笺',
        f'{PREFIX}便笺',
        f'{PREFIX}便签',
    )
)
async def send_daily_info_pic(bot: Bot, ev: Event):
    logger.info('开始执行[ZZZ每日信息]')
    uid = await get_uid(bot, ev)
    logger.info(f'[ZZZ每日] UID: {uid}')
    if not uid:
        return await bot.send(BIND_UID_HINT)
    await draw_stamina_img(bot, ev)


@scheduler.scheduled_job('cron', minute='*/30')
async def zzz_notice_job():
    result = await get_notice_list()
    logger.info('[zzz推送检查]完成!等待消息推送中...')
    logger.debug(result)

    # 执行私聊推送
    for bot_id in result:
        for BOT_ID in gss.active_bot:
            bot = gss.active_bot[BOT_ID]
            for user_id in result[bot_id]['direct']:
                msg = result[bot_id]['direct'][user_id]
                await bot.target_send(msg, 'direct', user_id, bot_id, '', '')
                await asyncio.sleep(0.5)
            logger.info('[sr推送检查] 私聊推送完成')
            for gid in result[bot_id]['group']:
                msg_list = []
                for user_id in result[bot_id]['group'][gid]:
                    msg_list.append(MessageSegment.at(user_id))
                    msg = result[bot_id]['group'][gid][user_id]
                    msg_list.append(MessageSegment.text(msg))
                await bot.target_send(msg_list, 'group', gid, bot_id, '', '')
                await asyncio.sleep(0.5)
            logger.info('[sr推送检查] 群聊推送完成')
