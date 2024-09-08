from typing import Dict

from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsIntConfig,
    GsStrConfig,
    GsBoolConfig,
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
    'SignTime': GsListStrConfig(
        '每晚签到时间设置',
        '每晚米游社签到时间设置（时，分）',
        ['0', '59'],
    ),
    'SchedSignin': GsBoolConfig(
        '定时签到',
        '开启后每晚00:59将开始自动签到任务',
        True,
    ),
    'SchedEnergyPush': GsBoolConfig(
        '定时检查体力',
        '开启后每隔半小时检查一次开启推送的人的体力状态',
        True,
    ),
    'PrivateSignReport': GsBoolConfig(
        '签到私聊报告',
        '关闭后将不再给任何人推送当天签到任务完成情况',
        False,
    ),
    'RefreshBG': GsStrConfig(
        '刷新面板背景',
        '刷新面板背景',
        'bg2',
        options=[
            'bg1',
            'bg2',
            'bg3',
        ],
    ),
    'ZZZGuideProvide': GsStrConfig(
        '角色攻略图提供方',
        '使用zzz角色攻略时选择的提供方',
        '猫冬',
        options=[
            '猫冬',
            '听雨惊花',
        ],
    ),
    'RefreshCardUsePic': GsBoolConfig(
        '刷新面板时使用图片返回',
        '关闭后刷新面板将使用文字返回信息',
        True,
    ),
    'EnableCustomCharBG': GsBoolConfig(
        '查询面板使用自定义角色图',
        '查询面板使用自定义角色图',
        False,
    ),
}
