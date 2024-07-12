from typing import Dict

from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsStrConfig,
    GsListStrConfig,
)

CONFIG_DEFAULT: Dict[str, GSC] = {
    'ZZZPrefix': GsStrConfig(
        '插件命令前缀（确认无冲突再修改）',
        '用于设置ZZZeroUID前缀的配置',
        'zzz',
    ),
    'ZZZIgnoreAt': GsListStrConfig(
        '以下命令不接受@响应',
        '用于设置不接受@响应的命令列表',
        [],
        ['刷新抽卡记录', '更新抽卡记录', '每日'],
    ),
}
