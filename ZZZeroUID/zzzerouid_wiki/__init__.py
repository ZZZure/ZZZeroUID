from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..utils.zzzero_prefix import PREFIX
from ..utils.name_convert import alias_to_char_name
from ..utils.resource.RESOURCE_PATH import FLOWER_GUIDE_PATH

sv_zzz_wiki = SV('绝区零WIKI')
sv_zzz_guide = SV('绝区零攻略')


@sv_zzz_wiki.on_prefix(f'{PREFIX}角色图鉴')
async def send_role_wiki_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_guide.on_prefix(f'{PREFIX}角色攻略')
async def send_role_guide_pic(bot: Bot, ev: Event):
    name = alias_to_char_name(ev.text.strip())
    logger.info(f'[zzz] 角色攻略: {name}')
    path = FLOWER_GUIDE_PATH / f'{name}.png'
    if path.exists():
        img = await convert_img(path)
        await bot.send(img)
    else:
        await bot.send('[zzz] 该角色攻略不存在, 请检查输入角色是否正确！')


@sv_zzz_guide.on_prefix(f'{PREFIX}音擎攻略')
async def send_weapon_guide_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_wiki.on_prefix(f'{PREFIX}驱动盘')
async def send_relic_wiki_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_wiki.on_prefix(f'{PREFIX}突破材料')
async def send_material_for_role_wiki_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_wiki.on_prefix(f'{PREFIX}武器')
async def send_light_cone_wiki_pic(bot: Bot, ev: Event):
    pass


@sv_zzz_wiki.on_prefix(f'{PREFIX}邦布')
async def send_bang_boo_wiki_pic(bot: Bot, ev: Event):
    pass
