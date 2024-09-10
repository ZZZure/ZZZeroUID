import re

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.error_reply import UID_HINT
from gsuid_core.utils.database.models import GsBind

from .zzzero_config import ZZZ_CONFIG
from .set_config import set_push_value, set_config_func

sv_self_config = SV('绝区零配置')

PREFIX = ZZZ_CONFIG.get_config('ZZZPrefix').data


@sv_self_config.on_prefix((f'{PREFIX}设置'))
async def send_config_ev(bot: Bot, ev: Event):
    logger.info('[ZZZ] 开始执行[设置阈值信息]')
    uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, 'zzz')
    if uid is None:
        return await bot.send(UID_HINT)

    func = ''.join(re.findall('[\u4e00-\u9fa5]', ev.text.replace('阈值', '')))
    value = re.findall(r'\d+', ev.text)
    value = value[0] if value else None

    if value is None:
        return await bot.send('请输入正确的阈值数字...')

    logger.info('[ZZZ设置阈值信息] func: {}, value: {}'.format(func, value))
    im = await set_push_value(ev.bot_id, func, uid, int(value))
    await bot.send(im)


# 开启 自动签到 和 推送树脂提醒 功能
@sv_self_config.on_prefix(
    (
        f'{PREFIX}开启',
        f'{PREFIX}关闭',
    )
)
async def open_switch_func(bot: Bot, ev: Event):
    user_id = ev.user_id
    config_name = ev.text

    logger.info(f'[{user_id}]尝试[{ev.command[2:]}]了[{ev.text}]功能')

    if ev.command == f'{PREFIX}开启':
        query = True
        gid = ev.group_id if ev.group_id else 'on'
    else:
        query = False
        gid = 'off'

    is_admin = ev.user_pm <= 2
    if ev.at and is_admin:
        user_id = ev.at
    elif ev.at:
        return await bot.send('你没有权限...')

    uid = await GsBind.get_uid_by_game(ev.user_id, ev.bot_id, 'zzz')
    if uid is None:
        return await bot.send(UID_HINT)

    im = await set_config_func(
        ev.bot_id,
        config_name=config_name,
        uid=uid,
        user_id=user_id,
        option=gid,
        query=query,
        is_admin=is_admin,
    )
    await bot.send(im)
