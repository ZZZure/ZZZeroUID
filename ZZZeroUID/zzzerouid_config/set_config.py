from typing import Optional

from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.database.models import GsUser
from gsuid_core.utils.database.config_switch import set_database_value

from .zzzero_config import ZZZ_CONFIG
from ..utils.database.model import ZzzPush
from .config_default import CONFIG_DEFAULT

PUSH_MAP = {
    '体力': 'energy',
}
OPTION_MAP = ['自动签到']


async def set_push_value(bot_id: str, func: str, uid: str, value: int):
    if func in PUSH_MAP:
        status = PUSH_MAP[func]
    else:
        return '该配置项不存在!'
    logger.info('[设置推送阈值]func: {}, value: {}'.format(status, value))
    if (
        await ZzzPush.update_data_by_uid(
            uid, bot_id, 'zzz', **{f'{status}_value': value}
        )
        == 0
    ):
        return f'设置成功!\n当前{func}推送阈值:{value}'
    else:
        return '设置失败!\n请检查参数是否正确!'


async def set_config_func(
    bot_id: str,
    ev: Event,
    config_name: str = '',
    uid: str = '0',
    option: str = '0',
    query: Optional[bool] = None,
    is_admin: bool = False,
):
    # 这里将传入的中文config_name转换为英文status
    for _name in CONFIG_DEFAULT:
        config = CONFIG_DEFAULT[_name]
        if config.title == config_name and isinstance(config.data, bool):
            name = _name
            break
    else:
        logger.info(
            f'uid: {uid}, option: {option}, config_name: {config_name}'
        )
        _config_name = config_name.replace('推送', '')
        if _config_name in PUSH_MAP:
            await ZzzPush.update_data_by_uid(
                uid,
                bot_id,
                'zzz',
                **{
                    f'{PUSH_MAP[_config_name]}_push': option,
                },
            )
            await GsUser.update_data_by_uid(
                uid, bot_id, 'zzz', zzz_push_switch=option
            )
        elif _config_name in OPTION_MAP:
            if '开启' in ev.command:
                if ev.user_type == 'direct':
                    value = 'on'
                else:
                    if ev.group_id:
                        value = ev.group_id
                    else:
                        value = 'on'
            else:
                value = 'off'
            im = await set_database_value(
                GsUser,
                'zzz',
                'zzz开启',
                ev.text.strip(),
                uid,
                ev.bot_id,
                value,
            )
            if im is not None:
                return im
            else:
                return '设置失败!'
        else:
            return '该配置项不存在!'

        if option == 'on':
            succeed_msg = '开启至私聊消息!'
        elif option == 'off':
            succeed_msg = '关闭!'
        else:
            succeed_msg = f'开启至群{option}'
        return f'{config_name}已{succeed_msg}'

    if is_admin:
        logger.info(f'config_name:{config_name},query:{query}')
        # 执行设置
        if query is not None:
            ZZZ_CONFIG.set_config(name, query)
            im = '成功设置{}为{}。'.format(
                config_name, '开' if query else '关'
            )
        else:
            im = '未传入参数query!'
    else:
        im = '只有管理员才能设置群服务。'
    return im
