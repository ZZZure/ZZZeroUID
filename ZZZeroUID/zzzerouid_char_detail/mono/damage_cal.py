from .Character import Character
from ...utils.data import get_hakush_char


async def get_damage_cal(char: Character):
    _id = char.id
    char_info = await get_hakush_char(_id)
    if char_info is None:
        return "该角色暂无数据..."
