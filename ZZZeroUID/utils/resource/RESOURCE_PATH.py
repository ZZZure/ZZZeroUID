import sys
from pathlib import Path

from gsuid_core.data_store import get_res_path

MAIN_PATH = get_res_path() / "ZZZeroUID"
sys.path.append(str(MAIN_PATH))

# 配置文件
CONFIG_PATH = MAIN_PATH / "config.json"

# 用户数据保存文件
PLAYER_PATH = MAIN_PATH / "players"
# 自定义背景
CU_BG_PATH = MAIN_PATH / "bg"

# WIKI文件夹
WIKI_PATH = MAIN_PATH / "wiki"

# 攻略文件夹
GUIDE_PATH = MAIN_PATH / "guide"
# 花佬攻略库
FLOWER_GUIDE_PATH = GUIDE_PATH / "flower"
# 猫冬攻略库
CAT_GUIDE_PATH = GUIDE_PATH / "cat"

# 自定义面板
CUSTOM_PATH = MAIN_PATH / "custom"

# 游戏素材
RESOURCE_PATH = MAIN_PATH / "resource"
SQUARE_AVATAR = RESOURCE_PATH / "square_avatar"
SQUARE_BANGBOO = RESOURCE_PATH / "square_bangbo"
WEAPON_PATH = RESOURCE_PATH / "weapon"
ROLECIRCLE_PATH = RESOURCE_PATH / "role_circle"
ROLEGENERAL_PATH = RESOURCE_PATH / "role_general"
ROLE_PATH = RESOURCE_PATH / "role"
SUIT_PATH = RESOURCE_PATH / "suit"
SUIT_3D_PATH = RESOURCE_PATH / "3d_suit"
CAMP_PATH = RESOURCE_PATH / "camp"
MIND_PATH = RESOURCE_PATH / "mind"
BBS_T_PATH = RESOURCE_PATH / "bbs_t"
MONSTER_PATH = RESOURCE_PATH / "monster"
TEMP_PATH = RESOURCE_PATH / "temp"


# 游戏数据
ZZZ_DATA_PATH = MAIN_PATH / "zzz_data"
CHAR_DATA_PATH = ZZZ_DATA_PATH / "char"


# 插件数据通用素材（随仓库分发，不进数据目录）
TEXT2D_PATH = Path(__file__).parents[1] / "texture2d"


def init_dir():
    for i in [
        MAIN_PATH,
        CU_BG_PATH,
        PLAYER_PATH,
        RESOURCE_PATH,
        WIKI_PATH,
        GUIDE_PATH,
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
        CAMP_PATH,
        MIND_PATH,
        CUSTOM_PATH,
        BBS_T_PATH,
        MONSTER_PATH,
        TEMP_PATH,
    ]:
        i.mkdir(parents=True, exist_ok=True)


init_dir()


def _register_backup_hints() -> None:
    # 宿主 Core 无该模块（旧版本）时跳过，不报错
    try:
        from gsuid_core.utils.backup.hints import register_backup_path
    except ImportError:
        return
    register_backup_path(
        "ZZZeroUID",
        PLAYER_PATH,
        "user_data",
        "按 UID 存档的抽卡记录与角色面板",
    )
    register_backup_path("ZZZeroUID", CONFIG_PATH, "config", "插件配置", default_selected=True)
    register_backup_path("ZZZeroUID", CU_BG_PATH, "config", "自定义背景图")
    register_backup_path("ZZZeroUID", CUSTOM_PATH, "config", "自定义角色立绘")
    register_backup_path(
        "ZZZeroUID",
        RESOURCE_PATH,
        "regenerable",
        "图片素材，可用「zzz下载全部资源」命令重新下载",
    )
    register_backup_path(
        "ZZZeroUID",
        WIKI_PATH,
        "regenerable",
        "图鉴缓存数据，可自动或通过命令重新拉取",
    )
    register_backup_path(
        "ZZZeroUID",
        GUIDE_PATH,
        "regenerable",
        "角色攻略图，可用「zzz下载全部资源」命令重新下载",
    )
    register_backup_path(
        "ZZZeroUID",
        ZZZ_DATA_PATH,
        "regenerable",
        "角色基础数据，可自动或通过命令重新拉取",
    )


_register_backup_hints()
