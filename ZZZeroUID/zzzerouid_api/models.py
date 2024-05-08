from typing import Any, Dict, List, Union

from msgspec import Struct

class SingleGachaLog(Struct):
    uid: str
    gacha_id: str
    gacha_type: str
    item_id: str
    count: str
    time: str
    name: str
    lang: str
    item_type: str
    rank_type: str
    id: str

class GachaLog(Struct):
    page: str
    size: str
    list: List[SingleGachaLog]
    region: str
    region_time_zone: int
