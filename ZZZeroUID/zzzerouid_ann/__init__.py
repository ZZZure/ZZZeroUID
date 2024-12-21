from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

sv_zzz_ann = SV('清空公告红点')


@sv_zzz_ann.on_fullmatch(('清空公告红点', '清除公告红点'))
async def get_ann_msg(bot: Bot, ev: Event):
    logger.info('[绝区零][清空公告红点] 正在执行中!')
    await bot.send('功能施工中...')
