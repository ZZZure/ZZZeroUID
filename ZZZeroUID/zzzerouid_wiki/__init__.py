from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.name_convert import alias_to_char_name
from ..zzzerouid_config.zzzero_config import ZZZ_CONFIG
from ..utils.resource.RESOURCE_PATH import CAT_GUIDE_PATH, FLOWER_GUIDE_PATH

sv_zzz_wiki = SV('绝区零WIKI')
sv_zzz_guide = SV('绝区零攻略')


@sv_zzz_wiki.on_prefix('角色图鉴')
async def send_role_wiki_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_guide.on_prefix('角色攻略')
@sv_zzz_guide.on_suffix('攻略')
async def send_role_guide_pic(bot: Bot, ev: Event):
    name = alias_to_char_name(ev.text.strip())
    logger.info(f'[绝区零] 角色攻略: {name}')
    gp = ZZZ_CONFIG.get_config('ZZZGuideProvide').data
    logger.info(f'[绝区零] 攻略提供方: {gp}')
    if gp == '猫冬':
        path = CAT_GUIDE_PATH / f'{name}.jpg'
    else:
        path1 = FLOWER_GUIDE_PATH / f'{name}.jpg'
        path2 = FLOWER_GUIDE_PATH / f'{name}.png'
        path = path1 if path1.exists() else path2

    if path.exists():
        img = await convert_img(path)
        await bot.send(img)
    else:
        await bot.send('[绝区零] 该角色攻略不存在, 请检查输入角色是否正确！')


@sv_zzz_guide.on_prefix('音擎攻略')
async def send_weapon_guide_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_wiki.on_prefix('驱动盘')
async def send_relic_wiki_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_wiki.on_prefix('突破材料')
async def send_material_for_role_wiki_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_wiki.on_prefix('武器')
async def send_light_cone_wiki_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_wiki.on_prefix('邦布')
async def send_bang_boo_wiki_pic(bot: Bot, ev: Event):
    pass
