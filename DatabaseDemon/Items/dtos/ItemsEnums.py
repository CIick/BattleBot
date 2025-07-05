"""
Items Enumerations
==================
Enumerations for Wizard101 item data structures including schools, rarity, 
object types, and other constants extracted from class definitions.
"""

from enum import Enum, IntEnum


class SchoolType(Enum):
    """Magic school types for items"""
    FIRE = "Fire"
    ICE = "Ice"
    STORM = "Storm"
    MYTH = "Myth"
    LIFE = "Life"
    DEATH = "Death"
    BALANCE = "Balance"
    STAR = "Star"
    SUN = "Sun"
    MOON = "Moon"
    SHADOW = "Shadow"
    NONE = ""


class ItemType(IntEnum):
    """Object type enumeration for items"""
    UNKNOWN = 0
    HAT = 1
    ROBE = 2
    BOOTS = 3
    WAND = 4
    ATHAME = 5
    AMULET = 6
    RING = 7
    DECK = 8
    PET = 9
    MOUNT = 10
    HOUSING = 11
    REAGENT = 12
    TREASURE_CARD = 13
    JEWEL = 14
    ELIXIR = 15


class RarityType(IntEnum):
    """Item rarity levels"""
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    ULTRA_RARE = 3
    EPIC = 4
    LEGENDARY = 5
    EXCLUSIVE = 6


class EquipmentSlot(Enum):
    """Equipment slot names"""
    HAT = "Hat"
    ROBE = "Robe"
    BOOTS = "Boots"
    WAND = "Wand"
    ATHAME = "Athame"
    AMULET = "Amulet"
    RING = "Ring"
    DECK = "Deck"
    PET = "Pet"
    MOUNT = "Mount"


class StatisticType(Enum):
    """Types of statistics that can be affected by items"""
    HEALTH = "Health"
    MANA = "Mana"
    DAMAGE = "Damage"
    RESIST = "Resist"
    ACCURACY = "Accuracy"
    CRITICAL = "Critical"
    BLOCK = "Block"
    PIERCE = "Pierce"
    POWER_PIP_CHANCE = "PowerPipChance"
    HEALING = "Healing"
    FISHING_LUCK = "FishingLuck"
    STUN_RESIST = "StunResist"
    SHADOW_PIP_RATING = "ShadowPipRating"


class PetStatType(Enum):
    """Pet statistic types"""
    STRENGTH = "Strength"
    INTELLECT = "Intellect"
    AGILITY = "Agility"
    WILL = "Will"
    POWER = "Power"


class JewelSocketType(IntEnum):
    """Types of jewel sockets"""
    CIRCLE = 1
    SQUARE = 2
    TRIANGLE = 3
    TEAR = 4
    POWER = 5


class BehaviorType(Enum):
    """Types of item behaviors"""
    RENDER = "RenderBehavior"
    EQUIPMENT = "EquipmentBehavior"
    PET_ITEM = "PetItemBehavior"
    MOUNT_ITEM = "MountItemBehavior"
    FURNITURE_INFO = "FurnitureInfoBehavior"
    JEWEL_SOCKET = "JewelSocketBehavior"
    ANIMATION = "AnimationBehavior"
    COLLISION = "CollisionBehavior"
    SCRIPT = "ScriptBehavior"
    CUSTOM_EMOTE = "CustomEmoteBehavior"
    HOUSING_MUSIC = "HousingMusicBehavior"
    TELEPORTER = "HousingTeleporterBehavior"


class RequirementType(Enum):
    """Types of equipment requirements"""
    MAGIC_LEVEL = "ReqMagicLevel"
    SCHOOL_OF_FOCUS = "ReqSchoolOfFocus"
    HAS_BADGE = "ReqHasBadge"
    HAS_ENTRY = "ReqHasEntry"
    ENERGY = "ReqEnergy"
    HEALTH_PERCENT = "ReqHealthPercent"
    MANA_PERCENT = "ReqManaPercent"
    IS_GENDER = "ReqIsGender"
    IN_COMBAT = "ReqInCombat"
    HIGHEST_CHARACTER_LEVEL = "ReqHighestCharacterLevelOnAccount"


class EffectType(Enum):
    """Types of item effects"""
    STATISTIC = "StatisticEffectInfo"
    TRANSFORMATION = "TransformationEffectInfo"
    GAME_EFFECT = "GameEffectInfo"
    SPEED = "SpeedEffectInfo"
    STARTING_PIP = "StartingPipEffectInfo"
    FX_BY_SLOT = "FXBySlotEffectInfo"


class GenderType(Enum):
    """Gender types for avatar items"""
    MALE = "MALE"
    FEMALE = "FEMALE"
    BOTH = "BOTH"


class LightType(IntEnum):
    """Light types for rendering"""
    NONE = 0
    POINT = 1
    DIRECTIONAL = 2
    SPOT = 3


class AnimationEventType(Enum):
    """Types of animation events"""
    SOUND = "Sound"
    PARTICLE = "Particle"
    SCRIPT = "Script"
    EFFECT = "Effect"


class HousingItemType(Enum):
    """Types of housing items"""
    FURNITURE = "Furniture"
    WALLPAPER = "Wallpaper"
    FLOORING = "Flooring"
    MUSIC_PLAYER = "MusicPlayer"
    TELEPORTER = "Teleporter"
    GARDENING = "Gardening"
    PET_HOUSE = "PetHouse"


class ElixirType(Enum):
    """Types of elixirs"""
    EXPERIENCE = "Experience"
    GOLD = "Gold"
    ENERGY = "Energy"
    MANA = "Mana"
    HEALTH = "Health"
    FISHING_LUCK = "FishingLuck"
    LEVEL_UP = "LevelUp"


class MountType(Enum):
    """Types of mounts"""
    GROUND = "Ground"
    FLYING = "Flying"
    SWIMMING = "Swimming"
    HYBRID = "Hybrid"


class PetType(Enum):
    """Types of pets"""
    FIRST_GENERATION = "FirstGeneration"
    HYBRID = "Hybrid"
    SCHOOL_PET = "SchoolPet"
    RARE = "Rare"
    CROWN_SHOP = "CrownShop"