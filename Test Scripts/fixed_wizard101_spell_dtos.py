"""
Fixed Wizard101 Spell Template DTOs
===================================
DTOs with proper default values for handling incomplete spell data.

All fields have sensible defaults to ensure DTOs can be created
even when some properties are missing from the source data.
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

class GardenSpellType(Enum):
    GS_SoilPreparation = 0
    GS_Growing = 1
    GS_InsectFighting = 2
    GS_PlantProtection = 3
    GS_PlantUtility = 4

class FishingSpellType(Enum):
    FS_Catching = 0
    FS_Utility = 1
    FS_PredatorBanishment = 2

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

# ===== BASE DTO CLASSES =====

@dataclass
class ReqGardeningLevelDTO:
    """Base DTO for ReqGardeningLevel"""
    m_applyNOT: Optional[bool] = False
    m_numericValue: Optional[float] = 0.0
    m_operator: Optional[int] = 0
    m_operatorType: Optional[int] = 0

@dataclass
class ReqHasBadgeDTO:
    """Base DTO for ReqHasBadge"""
    m_applyNOT: Optional[bool] = False
    m_badgeName: Optional[str] = ""
    m_operator: Optional[int] = 0

@dataclass
class ReqMagicLevelDTO:
    """Base DTO for ReqMagicLevel"""
    m_applyNOT: Optional[bool] = False
    m_magicSchool: Optional[str] = ""
    m_numericValue: Optional[float] = 0.0
    m_operator: Optional[int] = 0
    m_operatorType: Optional[int] = 0

@dataclass
class RequirementListDTO:
    """Base DTO for RequirementList"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_requirements: List[ReqHasBadgeDTO] = field(default_factory=list)

@dataclass
class SpellEffectDTO:
    """Base DTO for SpellEffect"""
    m_act: Optional[bool] = False
    m_actNum: Optional[int] = 0
    m_armorPiercingParam: Optional[int] = 0
    m_bypassProtection: Optional[bool] = False
    m_chancePerTarget: Optional[int] = 0
    m_cloaked: Optional[bool] = False
    m_converted: Optional[bool] = False
    m_damageType: Optional[int] = 0
    m_disposition: Optional[int] = 0
    m_effectParam: Optional[int] = 0
    m_effectTarget: Optional[int] = 0
    m_effectType: Optional[int] = 0
    m_enchantmentSpellTemplateID: Optional[int] = 0
    m_healModifier: Optional[float] = 0.0
    m_numRounds: Optional[int] = 0
    m_paramPerRound: Optional[int] = 0
    m_pipNum: Optional[int] = 0
    m_protected: Optional[bool] = False
    m_rank: Optional[int] = 0
    m_sDamageType: Optional[str] = ""
    m_spellTemplateID: Optional[int] = 0

@dataclass
class SpellRankDTO:
    """Base DTO for SpellRank"""
    m_balancePips: Optional[int] = 0
    m_deathPips: Optional[int] = 0
    m_firePips: Optional[int] = 0
    m_icePips: Optional[int] = 0
    m_lifePips: Optional[int] = 0
    m_mythPips: Optional[int] = 0
    m_shadowPips: Optional[int] = 0
    m_spellRank: Optional[int] = 0
    m_stormPips: Optional[int] = 0
    m_xPipSpell: Optional[bool] = False

@dataclass
class SpellTemplateDTO:
    """Base DTO for SpellTemplate"""
    m_PvE: Optional[bool] = False
    m_PvP: Optional[bool] = False
    m_Treasure: Optional[bool] = False
    m_accuracy: Optional[int] = 0
    m_adjectives: List[Any] = field(default_factory=list)
    m_advancedDescription: Optional[str] = ""
    m_alwaysFizzle: Optional[bool] = False
    m_backRowFriendly: Optional[bool] = False
    m_baseCost: Optional[int] = 0
    m_battlegroundsOnly: Optional[bool] = False
    m_behaviors: List[Any] = field(default_factory=list)
    m_boosterPackIcon: Optional[str] = ""
    m_cardFront: Optional[str] = ""
    m_casterInvisible: Optional[bool] = False
    m_cloaked: Optional[bool] = False
    m_cloakedName: Optional[str] = ""
    m_creditsCost: Optional[int] = 0
    m_delayEnchantment: Optional[bool] = False
    m_delayEnchantmentOrder: Any = None
    m_description: Optional[str] = ""
    m_descriptionCombatHUD: Optional[str] = ""
    m_descriptionTrainer: Optional[str] = ""
    m_displayIndex: Optional[int] = 0
    m_displayName: Optional[str] = ""
    m_displayRequirements: Optional[Any] = None
    m_effects: List[SpellEffectDTO] = field(default_factory=list)
    m_hiddenFromEffectsWindow: Optional[bool] = False
    m_ignoreCharms: Optional[bool] = False
    m_ignoreDispel: Optional[bool] = False
    m_imageIndex: Optional[int] = 0
    m_imageName: Optional[str] = ""
    m_leavesPlayWhenCast: Optional[bool] = False
    m_levelRestriction: Optional[int] = 0
    m_maxCopies: Optional[int] = 0
    m_name: Optional[str] = ""
    m_noDiscard: Optional[bool] = False
    m_noPvEEnchant: Optional[bool] = False
    m_noPvPEnchant: Optional[bool] = False
    m_previousSpellName: Optional[str] = ""
    m_purchaseRequirements: Optional[Any] = None
    m_pvpCurrencyCost: Optional[int] = 0
    m_pvpTourneyCurrencyCost: Optional[int] = 0
    m_requiredSchoolName: Optional[str] = ""
    m_sMagicSchoolName: Optional[str] = ""
    m_sTypeName: Optional[str] = ""
    m_secondarySchoolName: Optional[str] = ""
    m_showPolymorphedName: Optional[bool] = False
    m_skipTruncation: Optional[bool] = False
    m_spellBase: Optional[str] = ""
    m_spellCategory: Optional[str] = ""
    m_spellFusion: Optional[int] = 0
    m_spellRank: Optional[SpellRankDTO] = None
    m_spellSourceType: Optional[int] = 0
    m_trainingCost: Optional[int] = 0
    m_useGloss: Optional[bool] = False
    m_validTargetSpells: List[Any] = field(default_factory=list)

# ===== DERIVED DTO CLASSES =====

@dataclass
class CantripsSpellTemplateDTO(SpellTemplateDTO):
    """DTO for CantripsSpellTemplate - inherits from SpellTemplateDTO"""
    m_animationKFMs: List[Any] = field(default_factory=list)
    m_animationNames: List[str] = field(default_factory=list)
    m_cantripsSpellEffect: Optional[int] = 0
    m_cantripsSpellImageIndex: Optional[int] = 0
    m_cantripsSpellImageName: Optional[str] = ""
    m_cantripsSpellType: Optional[int] = 0
    m_cooldownSeconds: Optional[int] = 0
    m_effectParameter: Optional[str] = ""
    m_energyCost: Optional[int] = 0
    m_soundEffectGain: Optional[float] = 0.0
    m_soundEffectName: Optional[str] = ""

@dataclass
class CastleMagicSpellTemplateDTO(SpellTemplateDTO):
    """DTO for CastleMagicSpellTemplate - inherits from SpellTemplateDTO"""
    m_animationKFM: Optional[str] = ""
    m_animationSequence: Optional[str] = ""
    m_castleMagicSpellEffect: Optional[int] = 0
    m_castleMagicSpellType: Optional[int] = 0
    m_effectSchool: Optional[str] = ""

@dataclass
class FishingSpellTemplateDTO(SpellTemplateDTO):
    """DTO for FishingSpellTemplate - inherits from SpellTemplateDTO"""
    m_animationKFM: Optional[str] = ""
    m_animationName: Optional[str] = ""
    m_energyCost: Optional[int] = 0
    m_fishingSchoolFocus: Optional[str] = ""
    m_fishingSpellImageIndex: Optional[int] = 0
    m_fishingSpellImageName: Optional[str] = ""
    m_fishingSpellType: Optional[int] = 0
    m_soundEffectGain: Optional[float] = 0.0
    m_soundEffectName: Optional[str] = ""

@dataclass
class GardenSpellTemplateDTO(SpellTemplateDTO):
    """DTO for GardenSpellTemplate - inherits from SpellTemplateDTO"""
    m_affectedRadius: Optional[int] = 0
    m_animationKFM: Optional[str] = ""
    m_animationName: Optional[str] = ""
    m_animationNameLarge: Optional[str] = ""
    m_animationNameSmall: Optional[str] = ""
    m_bugZapLevel: Optional[int] = 0
    m_energyCost: Optional[int] = 0
    m_gardenSpellImageIndex: Optional[int] = 0
    m_gardenSpellImageName: Optional[str] = ""
    m_gardenSpellType: Optional[int] = 0
    m_protectionTemplateID: Optional[int] = 0
    m_providesMagic: Optional[bool] = False
    m_providesMusic: Optional[bool] = False
    m_providesPollination: Optional[bool] = False
    m_providesSun: Optional[bool] = False
    m_providesWater: Optional[bool] = False
    m_soilTemplateID: Optional[int] = 0
    m_soundEffectGain: Optional[float] = 0.0
    m_soundEffectName: Optional[str] = ""
    m_utilitySpellType: Optional[int] = 0
    m_yOffset: Optional[float] = 0.0

@dataclass
class RandomSpellEffectDTO(SpellEffectDTO):
    """DTO for RandomSpellEffect - inherits from SpellEffectDTO"""
    m_effectList: List[SpellEffectDTO] = field(default_factory=list)

@dataclass
class TieredSpellTemplateDTO(SpellTemplateDTO):
    """DTO for TieredSpellTemplate - inherits from SpellTemplateDTO"""
    m_nextTierSpells: List[str] = field(default_factory=list)
    m_requirements: Optional[RequirementListDTO] = None
    m_retired: Optional[bool] = False
    m_shardCost: Optional[int] = 0

@dataclass
class WhirlyBurlySpellTemplateDTO(SpellTemplateDTO):
    """DTO for WhirlyBurlySpellTemplate - inherits from SpellTemplateDTO"""
    m_specialUnits: Optional[str] = ""
    m_unitMovement: Optional[str] = ""

# ===== ENHANCED FACTORY =====

class FixedSpellDTOFactory:
    """Fixed factory for creating spell DTOs with graceful error handling"""
    
    # Hash to DTO class mapping
    TYPE_MAPPING: Dict[int, Type] = {
        1864220976: SpellTemplateDTO,
        1225309305: SpellEffectDTO,
        853452777: SpellRankDTO,
        1015536062: TieredSpellTemplateDTO,
        1906855338: RandomSpellEffectDTO,
        1558190673: RequirementListDTO,
        258825572: ReqMagicLevelDTO,
        1087768358: CastleMagicSpellTemplateDTO,
        108720390: GardenSpellTemplateDTO,
        710415701: ReqGardeningLevelDTO,
        2095072282: FishingSpellTemplateDTO,
        443110133: CantripsSpellTemplateDTO,
        1914767513: ReqHasBadgeDTO,
        1093865471: WhirlyBurlySpellTemplateDTO,
    }
    
    @classmethod
    def create_dto(cls, type_hash: int, spell_data: Dict[str, Any]) -> Optional[Any]:
        """Create appropriate DTO instance based on type hash"""
        dto_class = cls.TYPE_MAPPING.get(type_hash)
        if dto_class:
            try:
                # Process nested objects recursively
                processed_data = cls.process_nested_objects(spell_data)
                
                # Create kwargs with only the fields that exist in both data and DTO
                kwargs = {}
                if hasattr(dto_class, "__annotations__"):
                    for field_name in dto_class.__annotations__.keys():
                        if field_name in processed_data:
                            kwargs[field_name] = processed_data[field_name]
                
                # Create the DTO instance (missing fields will use defaults)
                return dto_class(**kwargs)
            except Exception as e:
                print(f"Error creating DTO for hash {type_hash}: {e}")
                return None
        else:
            print(f"No DTO class found for hash {type_hash}")
            return None
    
    @classmethod
    def process_nested_objects(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively process nested objects to create DTOs"""
        if not isinstance(data, dict):
            return data
        
        processed = {}
        
        for key, value in data.items():
            if isinstance(value, dict) and "$__type" in value:
                # This is a nested typed object
                nested_type = value["$__type"].replace("class ", "")
                nested_hash = cls.find_hash_for_type(nested_type)
                if nested_hash:
                    processed[key] = cls.create_dto(nested_hash, value)
                else:
                    processed[key] = value
            
            elif isinstance(value, list):
                # Process list items
                processed_list = []
                for item in value:
                    if isinstance(item, dict) and "$__type" in item:
                        nested_type = item["$__type"].replace("class ", "")
                        nested_hash = cls.find_hash_for_type(nested_type)
                        if nested_hash:
                            processed_list.append(cls.create_dto(nested_hash, item))
                        else:
                            processed_list.append(item)
                    else:
                        processed_list.append(item)
                processed[key] = processed_list
            
            else:
                processed[key] = value
        
        return processed
    
    @classmethod
    def find_hash_for_type(cls, type_name: str) -> Optional[int]:
        """Find hash value for a given type name"""
        for hash_val, dto_class in cls.TYPE_MAPPING.items():
            if dto_class.__name__ == f"{type_name}DTO":
                return hash_val
        return None
    
    @classmethod
    def create_from_json_data(cls, json_data: Dict[str, Any]) -> Optional[Any]:
        """Create DTO from raw JSON data (with $__type field)"""
        if "$__type" not in json_data:
            print("No $__type field found in JSON data")
            return None
        
        type_name = json_data["$__type"].replace("class ", "")
        type_hash = cls.find_hash_for_type(type_name)
        
        if type_hash:
            return cls.create_dto(type_hash, json_data)
        else:
            print(f"No hash found for type: {type_name}")
            return None
    
    @classmethod
    def get_supported_hashes(cls) -> List[int]:
        """Get list of all supported type hashes"""
        return list(cls.TYPE_MAPPING.keys())