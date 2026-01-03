from typing import List, TypedDict

# =================================================
# 1. 基础与通用组件 (Basic & Common Components)
# =================================================


class TimeData(TypedDict):
    """通用的时间结构 (年/月/日/时/分/秒)"""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int


# 兼容旧代码的别名
FloorChallengeTime = TimeData
ChallengeTime = TimeData


class Buff(TypedDict):
    """通用Buff结构: 标题与文本"""

    title: str
    text: str


# =================================================
# 2. 玩家状态与便签 (User Status & Note)
# =================================================


class EnergyProgress(TypedDict):
    max: int
    current: int


class Energy(TypedDict):
    progress: EnergyProgress
    restore: int
    day_type: int
    hour: int
    minute: int


class Vitality(TypedDict):
    max: int
    current: int


class VhsSale(TypedDict):
    sale_state: str


class BountyCommission(TypedDict):
    num: int
    total: int


class SurveyPoints(TypedDict):
    num: int
    total: int
    is_max_level: bool


class ZZZWeeklyTask(TypedDict):
    refresh_time: int
    cur_point: int
    max_point: int


class ZZZNoteResp(TypedDict):
    energy: Energy
    vitality: Vitality
    vhs_sale: VhsSale
    card_sign: str
    bounty_commission: BountyCommission
    s2_bounty_commission: BountyCommission
    survey_points: SurveyPoints
    weekly_task: ZZZWeeklyTask
    is_switch_new: bool


class ZZZWidgetNoteResp(ZZZNoteResp):
    vitality_refresh: int
    abyss_refresh: int
    has_signed: bool
    sign_url: str
    home_url: str
    note_url: str


class ZZZUser(TypedDict):
    game_biz: str
    region: str
    game_uid: str
    nickname: str
    level: int
    is_chosen: bool
    region_name: str
    is_official: bool


class RoleBasicInfo(TypedDict):
    server: str
    nickname: str
    icon: str


# =================================================
# 3. 角色、装备与邦布 (Avatar, Equip & Buddy)
# =================================================


class AvatarIconPaths(TypedDict):
    group_icon_path: str
    hollow_icon_path: str


class Avatar(TypedDict):
    """基础角色完整信息"""

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


class MEMAvatar(TypedDict):
    """挑战/深渊记录中的简略角色信息"""

    id: int
    level: int
    rarity: str
    element_type: int
    avatar_profession: int
    rank: int
    role_square_url: str
    sub_element_type: int


class ChallengeAvatar(TypedDict):
    id: int
    level: int
    rarity: str
    element_type: int


class Buddy(TypedDict):
    id: int
    name: str
    rarity: str
    level: int
    star: int


class MEMBuddy(TypedDict):
    """挑战/深渊记录中的简略邦布信息"""

    id: int
    rarity: str
    level: int
    bangboo_rectangle_url: str


class ChallengeBangboo(TypedDict):
    id: int
    rarity: str
    level: int


class ZZZBangboo(TypedDict):
    id: int
    name: str
    rarity: str
    level: int
    star: int


class BangbooWiki(TypedDict):
    item_id: str
    wiki_url: str


class EquipProperty(TypedDict):
    property_name: str
    property_id: int
    base: str
    level: int
    valid: bool
    system_id: int
    add: int


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
    """角色详情页面完整信息"""

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


# =================================================
# 4. 抽卡记录 (Gacha Log)
# =================================================


class SingleGachaLog(TypedDict):
    uid: str
    gacha_id: str
    gacha_type: str  # 1-常驻, 2-限定, 3-音擎
    item_id: str
    count: str
    time: str
    name: str
    lang: str
    item_type: str
    rank_type: str  # 2-B, 3-A, 4-S
    id: str


class ZZZGachaLogResp(TypedDict):
    page: str
    size: str
    list: List[SingleGachaLog]
    region: str
    region_time_zone: int


# =================================================
# 5. 旧版挑战/式舆防卫战 (Standard Challenge / Shiyu Defense V1)
# =================================================


class MonsterInfo(TypedDict):
    id: int
    name: str
    weak_element_type: int


class ChallengeNode(TypedDict):
    avatars: List[ChallengeAvatar]
    buddy: ChallengeBangboo
    element_type_list: List[int]
    monster_info: MonsterInfo


class FloorDetail(TypedDict):
    layer_index: int
    rating: str
    layer_id: int
    buffs: List[Buff]
    node_1: ChallengeNode
    node_2: ChallengeNode
    challenge_time: int
    zone_name: str
    floor_challenge_time: TimeData


class Rating(TypedDict):
    times: int
    rating: str


class ZZZChallenge(TypedDict):
    schedule_id: int
    begin_time: int
    end_time: int
    rating_list: List[Rating]
    has_data: bool
    all_floor_detail: List[FloorDetail]
    fast_layer_time: int
    max_layer: int
    hadal_begin_time: dict
    hadal_end_time: dict


# =================================================
# 6. 深渊/哈达尔数据 V2 (Hadal Zone V2 - from av.json)
# =================================================


class FifthLayerChallengeItem(TypedDict):
    """第五层具体关卡的详细信息"""

    layer_id: int
    rating: str
    buffer: Buff  # 复用通用的 Buff (title, text)
    score: int
    avatar_list: List[MEMAvatar]  # 复用 MEMAvatar
    buddy: MEMBuddy  # 复用 MEMBuddy
    battle_time: int
    monster_pic: str
    max_score: int


class FitfhLayerDetail(TypedDict):
    """第五层总览"""

    layer_challenge_info_list: List[FifthLayerChallengeItem]


class FourthLayerChallengeItem(TypedDict):
    """第四层具体关卡的详细信息"""

    layer_id: int
    battle_time: int
    avatar_list: List[MEMAvatar]
    buddy: MEMBuddy


class FourthLayerDetail(TypedDict):
    """第四层总览"""

    buffer: Buff
    challenge_time: TimeData
    rating: str
    layer_challenge_info_list: List[FourthLayerChallengeItem]


class HadalBriefInfo(TypedDict):
    """Hadal V2 简报信息"""

    cur_period_zone_layer_count: int
    score: int
    rank_percent: int
    battle_time: int
    rating: str
    challenge_time: TimeData
    max_score: int


class HadalInfoV2(TypedDict):
    """深渊/哈达尔区域详细信息 V2"""

    zone_id: int
    hadal_begin_time: TimeData
    hadal_end_time: TimeData
    pass_fifth_floor: bool
    brief: HadalBriefInfo
    # 注意：此处键名严格匹配 JSON 中的拼写错误
    fitfh_layer_detail: FitfhLayerDetail
    fourth_layer_detail: FourthLayerDetail
    begin_time: str
    end_time: str


class ZZZHadalData(TypedDict):
    """Hadal V2 数据载体"""

    hadal_ver: str
    hadal_info_v2: HadalInfoV2
    nick_name: str
    icon: str


class ZZZHadalResp(TypedDict):
    """Hadal V2 完整响应"""

    retcode: int
    message: str
    data: ZZZHadalData


# =================================================
# 7. 恶名狩猎/其他挑战 (Notorious Hunt / MEM Info)
# =================================================


class Boss(TypedDict):
    race_icon: str
    icon: str
    name: str
    bg_icon: str


class Buffer(TypedDict):
    """旧版 MEM Buffer 结构"""

    desc: str
    icon: str
    name: str


class ListItem(TypedDict):
    star: int
    score: int
    boss: List[Boss]
    buffer: List[Buffer]
    buddy: Buddy
    total_star: int
    challenge_time: TimeData
    avatar_list: List[Avatar]


class ZZZMEMInfo(TypedDict):
    end_time: TimeData
    nick_name: str
    avatar_icon: str
    has_data: bool
    start_time: TimeData
    zone_id: int
    total_star: int
    rank_percent: int
    list: List[ListItem]
    total_score: int


# =================================================
# 8. 纷争节点/虚无前线 (Void Front Battle)
# =================================================


class VoidFrontBattleBuffer(TypedDict):
    desc: str
    icon: str
    name: str


class SubChallengeRecord(TypedDict):
    avatar_list: List[MEMAvatar]
    buddy: MEMBuddy
    buffer: VoidFrontBattleBuffer
    battle_id: int
    name: str
    star: str


class MainChallengeRecord(TypedDict):
    score_ratio: str
    challenge_time: TimeData
    battle_id: int
    star: str
    node_id: int
    buddy: MEMBuddy
    buffer: VoidFrontBattleBuffer
    max_score: int
    avatar_list: List[MEMAvatar]
    sub_challenge_record: List[SubChallengeRecord]
    score: int
    name: str


class BossChallengeRecord(TypedDict):
    main_challenge_record: MainChallengeRecord
    boss_info: Boss


class VoidFrontBattleAbstractInfoBrief(TypedDict):
    end_ts: int
    left_ts: int
    max_score: int
    end_ts_over_42_days: bool
    void_front_id: int
    has_ending_record: bool
    ending_record_bg_pic: str
    rank_percent: int
    ending_record_name: str
    ending_record_id: int
    total_score: int


class ZZZVoidFrontBattleData(TypedDict):
    main_challenge_record_list: List[MainChallengeRecord]
    boss_challenge_record: BossChallengeRecord
    void_front_battle_abstract_info_brief: VoidFrontBattleAbstractInfoBrief
    role_basic_info: RoleBasicInfo


# =================================================
# 9. 杂项与公告 (Misc & Announcements)
# =================================================


class AbyssLevel(TypedDict):
    cur_level: int
    max_level: int
    icon: str


class AbyssPoint(TypedDict):
    cur_point: int
    max_point: int


class AbyssDuty(TypedDict):
    cur_duty: int
    max_duty: int


class AbyssTalent(TypedDict):
    cur_talent: int
    max_talent: int


class AbyssCollect(TypedDict):
    type: int
    cur_collect: int
    max_collect: int


class AbyssNest(TypedDict):
    is_nest: bool


class AbyssThrone(TypedDict):
    is_throne: bool
    max_damage: str


class ZZZAbyssData(TypedDict):
    abyss_level: AbyssLevel
    abyss_point: AbyssPoint
    abyss_duty: AbyssDuty
    abyss_talent: AbyssTalent
    refresh_time: int
    abyss_collect: List[AbyssCollect]
    abyss_nest: AbyssNest
    abyss_throne: AbyssThrone
    unlock: bool


class IncomeComponent(TypedDict):
    action: str
    num: int
    percent: int


class MonthDataEntry(TypedDict):
    data_type: str
    count: int
    data_name: str


class MonthData(TypedDict):
    list: List[MonthDataEntry]
    income_components: List[IncomeComponent]


class RoleInfo(TypedDict):
    nickname: str
    avatar: str


class ZZZMonthInfo(TypedDict):
    uid: str
    region: str
    current_month: str
    data_month: str
    month_data: MonthData
    optional_month: List[str]
    role_info: RoleInfo


class InnerListItem(TypedDict):
    ann_id: int
    title: str
    subtitle: str
    banner: str
    content: str
    type_label: str
    tag_label: str
    tag_icon: str
    login_alert: int
    lang: str
    start_time: str
    end_time: str
    type: int
    remind: int
    alert: int
    tag_start_time: str
    tag_end_time: str
    remind_ver: int
    has_content: bool
    extra_remind: int
    tag_icon_hover: str
    logout_remind: int
    logout_remind_ver: int


class OuterListItem(TypedDict):
    list: List[InnerListItem]
    type_id: int
    type_label: str


class TypeListItem(TypedDict):
    id: int
    name: str
    mi18n_name: str


class PicListItem(TypedDict):
    pass


class PicTypeListItem(TypedDict):
    pass


class ZZZAnnData(TypedDict):
    list: List[OuterListItem]
    total: int
    type_list: List[TypeListItem]
    alert: bool
    alert_id: int
    timezone: int
    t: str
    pic_list: List[PicListItem]
    pic_total: int
    pic_type_list: List[PicTypeListItem]
    pic_alert: bool
    pic_alert_id: int
    static_sign: str
    banner: str
