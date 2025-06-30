"""
Wizard101 Spell Template DTOs
==============================
Auto-generated Data Transfer Objects for Wizard101 spell templates.

This module contains:
- 16 spell template DTO classes
- 11 enum definitions
- Factory class for creating DTOs from spell data

Generated automatically by class_generator.py
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Type
from enum import Enum

# ===== ENUM DEFINITIONS =====

class kSpellSourceType(Enum):
    kCaster = 0
    kPet = 1
    kShadowCreature = 2
    kWeapon = 3
    kEquipment = 4

class kDelayOrder(Enum):
    SpellEffect_kAnyOrder = 0
    SpellEffect_kFirst = 1
    SpellEffect_kSecond = 2

class GardenSpellType(Enum):
    GS_SoilPreparation = 0
    GS_Growing = 1
    GS_InsectFighting = 2
    GS_PlantProtection = 3
    GS_PlantUtility = 4

class UtilitySpellType(Enum):
    US_None = 0
    US_Zap = 1
    US_Revive = 2
    US_Inspect = 3
    US_Stasis = 4
    US_PlowAll = 5
    US_PlantAll = 6
    US_HarvestNow = 7

class CastleMagicSpellType(Enum):
    CM_Action = 0
    CM_Effect = 1
    CM_Utility = 2
    CM_Logic = 3

class CastleMagicSpellEffect(Enum):
    CM_None = 0
    CM_MakeInvisible = 1
    CM_MakeVisible = 2
    CM_PlaySpellEffect = 3
    CM_PlaySoundEffect = 4
    CM_RestoreObject = 5
    CM_MoveObject = 6
    CM_TurnObject = 7
    CM_ScaleObject = 8
    CM_TeleportObject = 9
    CM_MoveObjectToMe = 10
    CM_MoveTowardMe = 11
    CM_PlayMusicScroll = 12
    CM_MoveObjectForward = 13
    CM_MoveObjectBackward = 14
    CM_TurnLikeMe = 15
    CM_TurnTowardMe = 16
    CM_LogicEffect = 17
    CM_StartTimer = 18
    CM_StopTimer = 19
    CM_ActivateReflector = 20
    CM_CameraShake = 21
    CM_SetCounter = 22
    CM_SetBrazier = 23
    CM_UseItem = 24
    CM_Solidify = 25
    CM_PetControl = 26
    CM_MountControl = 27
    CM_CameraControl = 28
    CM_TeleportPlayer = 29
    CM_PVPSigilControl = 30
    CM_TeleportAllPlayers = 31
    CM_MakeTranslucent = 32
    CM_MakeOpaque = 33
    CM_SilenceItem = 34
    CM_MoveFaster = 35
    CM_PVPDuelModifier = 36
    CM_StopMovement = 37
    CM_UnsilenceItem = 38
    CM_PlayInstrumentLoop = 39
    CM_StopMusic = 40
    CM_PlayMusicPlayer = 41
    CM_PlayAsPetControl = 42

class FishingSpellType(Enum):
    FS_Catching = 0
    FS_Utility = 1
    FS_PredatorBanishment = 2

class STACKING_RULE(Enum):
    STACKING_ALLOWED = 0
    STACKING_NOSTACK = 1
    STACKING_REPLACE = 2

class CantripsSpellType(Enum):
    CS_Teleportation = 0
    CS_Incantation = 1
    CS_Beneficial = 2
    CS_Ritual = 3
    CS_Sigil = 4

class CantripsSpellEffect(Enum):
    CSE_None = 0
    CSE_PlayEffect = 1
    CSE_Mark = 2
    CSE_Recall = 3
    CSE_Heal = 4
    CSE_NoAggro = 5
    CSE_Teleport = 6
    CSE_Invisibility = 7
    CSE_Emote = 8
    CSE_Ritual = 9
    CSE_Sigil = 10
    CSE_Beneficial = 11
    CSE_PlaySchoolEffect = 12

# ===== DTO CLASSES =====

@dataclass
class SpellTemplateDTO:
    """Base DTO for SpellTemplate with all core properties"""
    m_PvE: bool
    m_PvP: bool
    m_Treasure: bool
    m_accuracy: int
    m_adjectives: List[str]
    m_advancedDescription: str
    m_affectedRadius: int
    m_alwaysFizzle: bool
    m_animationKFM: str
    m_animationKFMs: List[str]
    m_animationName: str
    m_animationNameLarge: str
    m_animationNameSmall: str
    m_animationNames: List[str]
    m_animationSequence: str
    m_bIsOnPet: bool
    m_backRowFriendly: bool
    m_baseCost: int
    m_battlegroundsOnly: bool
    m_behaviors: List[Any]
    m_boosterPackIcon: str
    m_bugZapLevel: int
    m_cantripsSpellEffect: CantripsSpellEffect
    m_cantripsSpellImageIndex: int
    m_cantripsSpellImageName: str
    m_cantripsSpellType: CantripsSpellType
    m_cardFront: str
    m_casterInvisible: bool
    m_castleMagicSpellEffect: CastleMagicSpellEffect
    m_castleMagicSpellType: CastleMagicSpellType
    m_cloaked: bool
    m_cloakedName: str
    m_cooldownSeconds: int
    m_creditsCost: int
    m_delayEnchantment: bool
    m_delayEnchantmentOrder: kDelayOrder
    m_description: str
    m_descriptionCombatHUD: str
    m_descriptionTrainer: str
    m_displayIndex: int
    m_displayName: str
    m_displayRequirements: Optional[Any]
    m_duration: float
    m_effectCategory: str
    m_effectName: str
    m_effectParameter: str
    m_effectSchool: str
    m_effects: List[Optional[Any]]
    m_energyCost: int
    m_fishingSchoolFocus: str
    m_fishingSpellImageIndex: int
    m_fishingSpellImageName: str
    m_fishingSpellType: FishingSpellType
    m_gardenSpellImageIndex: int
    m_gardenSpellImageName: str
    m_gardenSpellType: GardenSpellType
    m_hiddenFromEffectsWindow: bool
    m_ignoreCharms: bool
    m_ignoreDispel: bool
    m_imageIndex: int
    m_imageName: str
    m_isPersistent: bool
    m_isPublic: bool
    m_leavesPlayWhenCast: bool
    m_levelRestriction: int
    m_maxCopies: int
    m_name: str
    m_nextTierSpells: List[str]
    m_noDiscard: bool
    m_noPvEEnchant: bool
    m_noPvPEnchant: bool
    m_onAddFunctorName: str
    m_onRemoveFunctorName: str
    m_previousSpellName: str
    m_protectionTemplateID: int
    m_providesMagic: bool
    m_providesMusic: bool
    m_providesPollination: bool
    m_providesSun: bool
    m_providesWater: bool
    m_purchaseRequirements: Optional[Any]
    m_pvpCurrencyCost: int
    m_pvpTourneyCurrencyCost: int
    m_requiredSchoolName: str
    m_requirements: Optional[Any]
    m_retired: bool
    m_sMagicSchoolName: str
    m_sTypeName: str
    m_secondarySchoolName: str
    m_shardCost: int
    m_showPolymorphedName: bool
    m_skipTruncation: bool
    m_soilTemplateID: int
    m_sortOrder: int
    m_soundEffectGain: float
    m_soundEffectName: str
    m_specialUnits: str
    m_spellBase: str
    m_spellCategory: str
    m_spellFusion: int
    m_spellName: str
    m_spellRank: Optional[Optional[Any]]
    m_spellSourceType: kSpellSourceType
    m_stackingCategories: List[str]
    m_stackingRule: STACKING_RULE
    m_trainingCost: int
    m_unitMovement: str
    m_useGloss: bool
    m_utilitySpellType: UtilitySpellType
    m_validTargetSpells: List[int]
    m_visualEffectAddName: str
    m_visualEffectRemoveName: str
    m_yOffset: float

@dataclass
class TieredSpellTemplateDTO(SpellTemplateDTO):
    """DTO for TieredSpellTemplate - specialized spell template"""
    pass

@dataclass
class SpellTemplateDTO(SpellTemplateDTO):
    """DTO for SpellTemplate - specialized spell template"""
    pass

@dataclass
class CastleMagicSpellTemplateDTO(SpellTemplateDTO):
    """DTO for CastleMagicSpellTemplate - specialized spell template"""
    pass

@dataclass
class WhirlyBurlySpellTemplateDTO(SpellTemplateDTO):
    """DTO for WhirlyBurlySpellTemplate - specialized spell template"""
    pass

@dataclass
class CastleMagicSpellTemplateDTO(SpellTemplateDTO):
    """DTO for CastleMagicSpellTemplate - specialized spell template"""
    pass

@dataclass
class WhirlyBurlySpellTemplateDTO(SpellTemplateDTO):
    """DTO for WhirlyBurlySpellTemplate - specialized spell template"""
    pass

@dataclass
class GardenSpellTemplateDTO(SpellTemplateDTO):
    """DTO for GardenSpellTemplate - specialized spell template"""
    pass

@dataclass
class TieredSpellTemplateDTO(SpellTemplateDTO):
    """DTO for TieredSpellTemplate - specialized spell template"""
    pass

@dataclass
class FishingSpellTemplateDTO(SpellTemplateDTO):
    """DTO for FishingSpellTemplate - specialized spell template"""
    pass

@dataclass
class FishingSpellTemplateDTO(SpellTemplateDTO):
    """DTO for FishingSpellTemplate - specialized spell template"""
    pass

@dataclass
class CantripsSpellTemplateDTO(SpellTemplateDTO):
    """DTO for CantripsSpellTemplate - specialized spell template"""
    pass

@dataclass
class CantripsSpellTemplateDTO(SpellTemplateDTO):
    """DTO for CantripsSpellTemplate - specialized spell template"""
    pass

@dataclass
class NonCombatMayCastSpellTemplateDTO(SpellTemplateDTO):
    """DTO for NonCombatMayCastSpellTemplate - specialized spell template"""
    pass

@dataclass
class NonCombatMayCastSpellTemplateDTO(SpellTemplateDTO):
    """DTO for NonCombatMayCastSpellTemplate - specialized spell template"""
    pass

@dataclass
class GardenSpellTemplateDTO(SpellTemplateDTO):
    """DTO for GardenSpellTemplate - specialized spell template"""
    pass

# ===== FACTORY CLASS =====

class SpellTemplateDTOFactory:
    """Factory for creating appropriate DTO instances from spell data"""
    
    # Hash to DTO class mapping
    TYPE_MAPPING: Dict[int, Type] = {
        1015536062: TieredSpellTemplateDTO,
        1864220971: SpellTemplateDTO,
        1864220976: SpellTemplateDTO,
        1087768358: CastleMagicSpellTemplateDTO,
        1093865471: WhirlyBurlySpellTemplateDTO,
        1112934182: CastleMagicSpellTemplateDTO,
        1135808511: WhirlyBurlySpellTemplateDTO,
        1182462215: GardenSpellTemplateDTO,
        2089277885: TieredSpellTemplateDTO,
        2095072306: FishingSpellTemplateDTO,
        2095072282: FishingSpellTemplateDTO,
        443111413: CantripsSpellTemplateDTO,
        443110133: CantripsSpellTemplateDTO,
        920052956: NonCombatMayCastSpellTemplateDTO,
        919856348: NonCombatMayCastSpellTemplateDTO,
        108720390: GardenSpellTemplateDTO,
    }
    
    @classmethod
    def create_dto(cls, type_hash: int, spell_data: Dict[str, Any]) -> Optional[Any]:
        """Create appropriate DTO instance based on type hash"""
        dto_class = cls.TYPE_MAPPING.get(type_hash)
        if dto_class:
            try:
                # Filter spell_data to only include fields that exist in the DTO
                filtered_data = cls.filter_data_for_dto(dto_class, spell_data)
                return dto_class(**filtered_data)
            except Exception as e:
                print(f"Error creating DTO for hash {type_hash}: {e}")
                return None
        else:
            print(f"No DTO class found for hash {type_hash}")
            return None
    
    @classmethod
    def filter_data_for_dto(cls, dto_class: Type, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data to only include fields that exist in the DTO class"""
        if hasattr(dto_class, "__annotations__"):
            valid_fields = set(dto_class.__annotations__.keys())
            return {k: v for k, v in data.items() if k in valid_fields}
        return data
    
    @classmethod
    def get_supported_hashes(cls) -> List[int]:
        """Get list of all supported type hashes"""
        return list(cls.TYPE_MAPPING.keys())