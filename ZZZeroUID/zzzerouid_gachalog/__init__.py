from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from ..zzzzerouid_utils.zzzero_prefix import PREFIX
from ..zzzzerouid_utils.uid import get_uid
from get_gachalogs import save_gachalogs
import asyncio


sv_gacha_log = SV(f'{PREFIX}抽卡记录')
sv_get_gachalog_by_link = SV(f'{PREFIX}导入抽卡链接', area='DIRECT')


@sv_gacha_log.on_fullmatch(f'{PREFIX}抽卡记录')
async def send_gacha_log_card_info(bot: Bot, ev: Event):
    return await bot.send("TODO")


@sv_get_gachalog_by_link.on_command(f'{PREFIX}导入抽卡链接')
async def get_gachalog_by_link(bot: Bot, ev: Event):
    url = ev.text.strip()
    user_id = ev.user_id
    await bot.logger.info(f'开始导入抽卡链接 url={url}, userid={user_id}')
    uid = await get_uid(bot, ev)
    if not url or not isinstance(url, str):
        return await bot.send("请给出正确的抽卡链接")
    await bot.send(f'开始强制刷新{uid}抽卡记录，需要一定时间，请勿重复执行.....')
    im = await save_gachalogs(uid, url, None, True)
    return await bot.send(im)



url = "https://public-operation-nap.mihoyo.com/common/gacha_record/api/nap/getGachaLog?authkey_ver=1&sign_type=2&auth_appid=webview_gacha&win_mode=fullscreen&gacha_id=a41a5a30e2f7b64126e5ca80ac06af304273bc&timestamp=1713267923&authkey=Q0wzN8Ds%2BeDaYeAksbj65IHWZJ8jmv33Ja%2Bv%2FSY8TQY%2BSyhk5PEHnw3DJ%2FgExCVtmt3bNYWGGtmyZYNieH9Xby49KBedDJ11l7VKrfcyui5khaDirinHOS%2BQ%2BY0SY%2F53PFEAXLom7AqfSO%2By8UaGHXHwYsyxQwAOgl2P%2FCdyc%2FI3RXI7mrPBqzOi3yHVJqYkkDBA64prjTl6OQEAbsOA5ESvmX4qMC396iCfeNO2vu2%2Fosj06yq86INodn%2FKAGObQYff5culI5LUKS1L8W%2F0LY9UCf5HJcGIJ9rUlgbOvlxVgy2xi5wRGLogRbnAywM6G4XNyhfA0wCss2Jz9KRnfndPqLG5u3FFHO%2FgIwLC1YZBEbryUCJ77fNGHZvfrt78kVNFhtWzIdLCOLaEtp6NO61pG5ixzVos%2FBpVoSlDSwYGpGFlj5WfcrIG9x2LitXS9bJzFvLZSCbb14sc9vaO1GqI92dPkxoLbxCaux5NyQMCxeYYf0t1pI0JKY0S5SkcPKIEavF3ALkuolpF4AB7pyYlpplUV3uSLrne593OAZUTFbhvcDA5zc%2BjbQqzBW3LelvEj7njZEmJ%2FbSIhq9A0Q%3D%3D&lang=zh-cn&region=prod_cb02_cn&game_biz=nap_cn&win_mode=fullscreen&init_log_gacha_type=1001&ui_layout=&button_mode=default&gacha_type=1001&end_id="
asyncio.run(save_gachalogs("test", url))

