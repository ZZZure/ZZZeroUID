from typing import List

from msgspec import Struct


class SingleGachaLog(Struct):
    uid: str
    gacha_id: str
    gacha_type: str
    '''gacha_type: 1-常驻, 2-限定, 3-音擎'''
    item_id: str
    count: str
    time: str
    name: str
    lang: str
    item_type: str
    rank_type: str
    '''rank_type: 2-B, 3-A, 4-S'''
    id: str


class GachaLog(Struct):
    page: str
    size: str
    list: List[SingleGachaLog]
    region: str
    region_time_zone: int
