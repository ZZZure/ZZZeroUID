import json
from pathlib import Path
from typing import Union

import aiofiles
from gsuid_core.utils.image.convert import convert_img

from ..utils.zzzero_prefix import PREFIX
from ..utils.image import add_footer, get_zzz_bg
from ..utils.name_convert import char_name_to_char_id
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH

TEXT_PATH = Path(__file__).parent / "texture2d"


async def draw_char_detail_img(uid: str, char: str) -> Union[str, bytes]:
    char_id = char_name_to_char_id(char)
    path = PLAYER_PATH / str(uid) / f"{char_id}.json"
    if not path.exists():
        return f"[绝区零] 未找到该角色信息, 请先使用[{PREFIX}刷新面板]进行刷新!"

    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        data = json.loads(await f.read())  # noqa: F841

    img = get_zzz_bg(950, 2100)

    img = add_footer(img)
    img = await convert_img(img)
    return "TODO"
