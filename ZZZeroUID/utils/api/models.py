from typing import List, TypedDict


class EnergyProgress(TypedDict):
    max: int
    current: int


class Energy(TypedDict):
    progress: EnergyProgress
    restore: int


class Vitality(TypedDict):
    max: int
    current: int


class VhsSale(TypedDict):
    sale_state: str


class ZZZNoteResp(TypedDict):
    energy: Energy
    vitality: Vitality
    vhs_sale: VhsSale
    card_sign: str


class SingleGachaLog(TypedDict):
    uid: str
    gacha_id: str
    gacha_type: str
    """gacha_type: 1-常驻, 2-限定, 3-音擎"""
    item_id: str
    count: str
    time: str
    name: str
    lang: str
    item_type: str
    rank_type: str
    """rank_type: 2-B, 3-A, 4-S"""
    id: str


class ZZZGachaLogResp(TypedDict):
    page: str
    size: str
    list: List[SingleGachaLog]
    region: str
    region_time_zone: int


class Avatar(TypedDict):
    id: int
    level: int
    name_mi18n: str
    full_name_mi18n: str
    element_type: int
    camp_name_mi18n: str
    avatar_profession: int
    rarity: str
    group_icon_path: str
    hollow_icon_path: str
    rank: int
    is_chosen: bool


class Buddy(TypedDict):
    id: int
    name: str
    rarity: str
    level: int
    star: int


class Stats(TypedDict):
    active_days: int
    avatar_num: int
    world_level_name: str
    cur_period_zone_layer_count: int
    buddy_num: int


class ZZZIndexResp(TypedDict):
    stats: Stats
    avatar_list: List[Avatar]
    cur_head_icon_url: str
    buddy_list: List[Buddy]


class ZZZBangboo(TypedDict):
    id: int
    name: str
    rarity: str
    level: int
    star: int


class BangbooWiki(TypedDict):
    item_id: str
    wiki_url: str


class AvatarIconPaths(TypedDict):
    group_icon_path: str
    hollow_icon_path: str


class ZZZAvatarBasic(TypedDict):
    id: int
    level: int
    name_mi18n: str
    full_name_mi18n: str
    element_type: int
    camp_name_mi18n: str
    avatar_profession: int
    rarity: str
    icon_paths: AvatarIconPaths
    rank: int
    is_chosen: bool


class EquipProperty(TypedDict):
    property_name: str
    property_id: int
    base: str  # Base value, could be an empty string if not applicable


class EquipMainProperty(TypedDict):
    property_name: str
    property_id: int
    base: str


class EquipSuit(TypedDict):
    suit_id: int
    name: str
    own: int
    desc1: str
    desc2: str


class Equip(TypedDict):
    id: int
    level: int
    name: str
    icon: str
    rarity: str
    properties: List[EquipProperty]
    main_properties: List[EquipMainProperty]
    equip_suit: EquipSuit
    equipment_type: int


class Weapon(TypedDict):
    id: int
    level: int
    name: str
    star: int
    icon: str
    rarity: str
    properties: List[EquipProperty]
    main_properties: List[EquipMainProperty]
    talent_title: str
    talent_content: str
    profession: int


class Property(TypedDict):
    property_name: str
    property_id: int
    base: str
    add: str
    final: str


class SkillItem(TypedDict):
    title: str
    text: str


class Skill(TypedDict):
    level: int
    skill_type: int
    items: List[SkillItem]


class Rank(TypedDict):
    id: int
    name: str
    desc: str
    pos: int
    is_unlocked: bool


class ZZZAvatarInfo(TypedDict):
    id: int
    level: int
    name_mi18n: str
    full_name_mi18n: str
    element_type: int
    camp_name_mi18n: str
    avatar_profession: int
    rarity: str
    group_icon_path: str
    hollow_icon_path: str
    equip: List[Equip]
    weapon: Weapon
    properties: List[Property]
    skills: List[Skill]
    rank: int
    ranks: List[Rank]


class ZZZUser(TypedDict):
    game_biz: str
    region: str
    game_uid: str
    nickname: str
    level: int
    is_chosen: bool
    region_name: str
    is_official: bool
