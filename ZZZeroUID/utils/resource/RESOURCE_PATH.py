import sys
from pathlib import Path

from gsuid_core.data_store import get_res_path

MAIN_PATH = get_res_path() / 'ZZZeroUID'
sys.path.append(str(MAIN_PATH))

# 配置文件
CONFIG_PATH = MAIN_PATH / 'config.json'

# 用户数据保存文件
PLAYER_PATH = MAIN_PATH / 'players'
# 自定义背景
CU_BG_PATH = MAIN_PATH / 'bg'

# WIKI文件夹
WIKI_PATH = MAIN_PATH / 'wiki'

# 攻略文件夹
GUIDE_PATH = MAIN_PATH / 'guide'
# 花佬攻略库
FLOWER_GUIDE_PATH = GUIDE_PATH / 'flower'
# 猫冬攻略库
CAT_GUIDE_PATH = GUIDE_PATH / 'cat'


# 游戏素材
RESOURCE_PATH = MAIN_PATH / 'resource'
SQUARE_AVATAR = RESOURCE_PATH / 'square_avatar'
SQUARE_BANGBOO = RESOURCE_PATH / 'square_bangbo'
WEAPON_PATH = RESOURCE_PATH / 'weapon'
ROLECIRCLE_PATH = RESOURCE_PATH / 'role_circle'
ROLEGENERAL_PATH = RESOURCE_PATH / 'role_general'
ROLE_PATH = RESOURCE_PATH / 'role'
SUIT_PATH = RESOURCE_PATH / 'suit'
SUIT_3D_PATH = RESOURCE_PATH / '3d_suit'

# 游戏数据
ZZZ_DATA_PATH = MAIN_PATH / 'zzz_data'
CHAR_DATA_PATH = ZZZ_DATA_PATH / 'char'


# 插件数据通用素材
TEXT2D_PATH = Path(__file__).parent / 'texture2d'


def init_dir():
    for i in [
        MAIN_PATH,
        CU_BG_PATH,
        PLAYER_PATH,
        RESOURCE_PATH,
        WIKI_PATH,
        GUIDE_PATH,
        TEXT2D_PATH,
        FLOWER_GUIDE_PATH,
        SQUARE_AVATAR,
        SQUARE_BANGBOO,
        WEAPON_PATH,
        ROLECIRCLE_PATH,
        ROLE_PATH,
        SUIT_PATH,
        SUIT_3D_PATH,
        CAT_GUIDE_PATH,
        ZZZ_DATA_PATH,
        CHAR_DATA_PATH,
        ROLEGENERAL_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
