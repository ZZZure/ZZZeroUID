from typing import Dict, List, Union, Literal, TypedDict


class Stats(TypedDict):
    Armor: int
    ArmorGrowth: int
    Attack: int
    AttackGrowth: int
    AvatarPieceId: int
    BreakStun: int
    BuffResistBurnPossibilityDelta: int
    BuffResistBurnPossibilityRatio: float
    BuffResistElectricPossibilityDelta: int
    BuffResistElectricPossibilityRatio: float
    BuffResistFrozenPossibilityDelta: int
    BuffResistFrozenPossibilityRatio: float
    Crit: int
    CritDamage: int
    CritDmgRes: int
    CritRes: int
    Defence: int
    DefenceGrowth: int
    ElementAbnormalPower: int
    ElementMystery: int
    Endurance: int
    HpGrowth: int
    HpMax: int
    Luck: int
    PenDelta: int
    PenRate: float
    Rbl: int
    RblCorrectionFactor: int
    RblProbability: float
    Shield: int
    ShieldGrowth: int
    SpBarPoint: int
    SpRecover: int
    StarInitial: int
    Stun: int
    Tags: List[str]


class LevelUpMaterials(TypedDict):
    _10: int
    _100215: int
    _100225: int
    _100235: int
    _100113: int
    _100123: int
    _100133: int
    _100941: int


class Level(TypedDict):
    HpMax: int
    Attack: int
    Defence: int
    LevelMax: int
    LevelMin: int
    Materials: LevelUpMaterials


class ExtraLevel(TypedDict):
    MaxLevel: int
    Extra: Dict[str, Dict[str, Union[str, int, float]]]


class SkillDescription(TypedDict):
    Name: str
    Desc: str


class SkillValue(TypedDict):
    Main: int
    Growth: int
    Format: str


class SkillParam(TypedDict):
    Name: str
    Desc: str
    Param: Dict[str, SkillValue]


class SkillParamDesc(TypedDict):
    Skill: int
    Prop: int


class SkillDescription2(TypedDict):
    Name: str
    Param: SkillParam


class SkillDetail(TypedDict):
    Description: List[Union[SkillDescription, SkillDescription2]]
    Material: Dict[str, Dict[str, int]]


class Skill(TypedDict):
    Basic: Dict[str, SkillDetail]
    Dodge: Dict[str, SkillDetail]
    Special: Dict[str, SkillDetail]
    Chain: Dict[str, SkillDetail]
    Assist: Dict[str, SkillDetail]


class PassiveLevel(TypedDict):
    Level: int
    Id: int
    Name: List[str]
    Desc: List[str]


class Passive(TypedDict):
    Level: Dict[int, PassiveLevel]
    Materials: Dict[str, Dict[str, int]]


class TalentLevel(TypedDict):
    Level: int
    Name: str
    Desc: str
    Desc2: str


class Talent(TypedDict):
    Heroism: TalentLevel
    YouthfulArrogance: TalentLevel
    Insensitive: TalentLevel
    OriginalAspiration: TalentLevel
    LongingDistance: TalentLevel
    Idealism: TalentLevel


class CharacterData(TypedDict):
    Id: int
    Icon: str
    Name: str
    CodeName: str
    Rarity: int
    WeaponType: Dict[str, str]
    ElementType: Dict[str, str]
    HitType: Dict[str, str]
    Camp: Dict[str, str]
    Gender: int
    PartnerInfo: Dict
    Stats: Stats
    Level: Dict[Literal['1', '2', '3', '4', '5', '6'], Level]
    ExtraLevel: Dict[Literal['1', '2', '3', '4', '5', '6'], ExtraLevel]
    Skill: Skill
    Passive: Passive
    Talent: Talent
