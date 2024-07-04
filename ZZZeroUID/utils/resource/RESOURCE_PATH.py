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

# 游戏素材
RESOURCE_PATH = MAIN_PATH / 'resource'

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
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()
