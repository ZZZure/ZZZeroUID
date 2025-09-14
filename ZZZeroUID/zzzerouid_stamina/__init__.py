from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger

from ..utils.uid import get_uid
from .notice import get_notice_list
from ..utils.hint import BIND_UID_HINT
from .draw_zzz_stamina import draw_stamina_img
from ..zzzerouid_config.zzzero_config import ZZZ_CONFIG

sv_get_stamina = SV('绝区零查询体力')
sv_get_stamina_admin = SV('绝区零强制推送', pm=1)

is_check_energy = ZZZ_CONFIG.get_config('SchedEnergyPush').data


@sv_get_stamina.on_fullmatch(
    (
        '每日',
        'mr',
        '实时便笺',
        '便笺',
        '便签',
    )
)
async def send_daily_info_pic(bot: Bot, ev: Event):
    logger.info('[绝区零每日] 开始执行')
    uid = await get_uid(bot, ev)
    logger.info(f'[绝区零每日] UID: {uid}')
    if not uid:
        return await bot.send(BIND_UID_HINT)
    await draw_stamina_img(bot, ev)


@sv_get_stamina_admin.on_fullmatch(('强制推送体力提醒'))
async def force_notice_job(bot: Bot, ev: Event):
    await bot.send('🔨 [绝区零服务]\n🌱 开始执行强制推送体力提醒!')
    await zzz_notice_job(True)
    await bot.send('🔨 [绝区零服务]\n✅ 强制推送体力提醒执行完成!')


@scheduler.scheduled_job('cron', minute='*/30')
async def zzz_notice_job(force: bool = False):
    logger.info('[绝区零推送检查] 开始检查...')
    if is_check_energy or force:
        await get_notice_list()
        logger.info('[绝区零推送检查] 完成!等待消息推送中...')
    else:
        logger.info('[绝区零推送检查] 未开启, 跳过检查...')
