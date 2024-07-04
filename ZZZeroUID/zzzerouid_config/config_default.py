from typing import Dict

from gsuid_core.utils.plugins_config.models import GSC, GsStrConfig

CONFIG_DEFAULT: Dict[str, GSC] = {
    'ZZZPrefix': GsStrConfig(
        '插件命令前缀（确认无冲突再修改）',
        '用于设置ZZZeroUID前缀的配置',
        'zzz',
    )
}
