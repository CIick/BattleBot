"""
Wizard101 Spell DTOs
===================
Data Transfer Object classes for Wizard101 spell data structures.
All fields have sensible defaults to ensure DTOs can be created from incomplete data.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from .SpellsEnums import *


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
    m_requirements: List[Any] = field(default_factory=list)  # Can contain any requirement type


# ===== REQUIREMENT DTO CLASSES =====

@dataclass
class ReqIsSchoolDTO:
    """DTO for ReqIsSchool requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_magicSchoolName: Optional[str] = ""


@dataclass
class ReqHangingCharmDTO:
    """DTO for ReqHangingCharm requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_disposition: Optional[int] = 0
    m_minCount: Optional[int] = 0
    m_maxCount: Optional[int] = 0


@dataclass
class ReqHangingWardDTO:
    """DTO for ReqHangingWard requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_disposition: Optional[int] = 0
    m_minCount: Optional[int] = 0
    m_maxCount: Optional[int] = 0


@dataclass
class ReqHangingOverTimeDTO:
    """DTO for ReqHangingOverTime requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_disposition: Optional[int] = 0
    m_minCount: Optional[int] = 0
    m_maxCount: Optional[int] = 0


@dataclass
class ReqHangingEffectTypeDTO:
    """DTO for ReqHangingEffectType requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_effectType: Optional[int] = 0
    m_minCount: Optional[int] = 0
    m_maxCount: Optional[int] = 0


@dataclass
class ReqHangingAuraDTO:
    """DTO for ReqHangingAura requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_disposition: Optional[int] = 0
    m_minCount: Optional[int] = 0
    m_maxCount: Optional[int] = 0


@dataclass
class ReqSchoolOfFocusDTO:
    """DTO for ReqSchoolOfFocus requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_magicSchoolName: Optional[str] = ""


@dataclass
class ReqMinionDTO:
    """DTO for ReqMinion requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_minCount: Optional[int] = 0
    m_maxCount: Optional[int] = 0


@dataclass
class ReqHasEntryDTO:
    """DTO for ReqHasEntry requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_entryName: Optional[str] = ""


@dataclass
class ReqCombatHealthDTO:
    """DTO for ReqCombatHealth requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_fMinPercent: Optional[float] = 0.0
    m_fMaxPercent: Optional[float] = 0.0


@dataclass
class ReqPvPCombatDTO:
    """DTO for ReqPvPCombat requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0


@dataclass
class ReqShadowPipCountDTO:
    """DTO for ReqShadowPipCount requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_minPips: Optional[int] = 0
    m_maxPips: Optional[int] = 0


@dataclass
class ReqCombatStatusDTO:
    """DTO for ReqCombatStatus requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_combatStatus: Optional[int] = 0


@dataclass
class ReqPipCountDTO:
    """DTO for ReqPipCount requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_targetType: Optional[int] = 0
    m_minPips: Optional[int] = 0
    m_maxPips: Optional[int] = 0


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


# ===== SPELL DTO CLASS =====

@dataclass
class SpellDTO:
    """DTO for Spell class - represents the root spell object"""
    # Core spell identification
    m_spellID: Optional[int] = 0
    m_spellName: Optional[str] = ""
    m_spellTemplate: Optional[SpellTemplateDTO] = None
    
    # Spell state and runtime data
    m_bIsEnchanted: Optional[bool] = False
    m_bIsPolymorphed: Optional[bool] = False
    m_bIsNaturalAttack: Optional[bool] = False
    m_bIsGadget: Optional[bool] = False
    m_bIsItem: Optional[bool] = False
    m_bIsMinion: Optional[bool] = False
    m_bIsFromSpellbook: Optional[bool] = False
    
    # Spell targeting and effects
    m_caster: Optional[Any] = None  # SharedPointer to caster object
    m_targets: List[Any] = field(default_factory=list)  # List of target objects
    m_effects: List[SpellEffectDTO] = field(default_factory=list)
    
    # Spell execution data
    m_spellRank: Optional[SpellRankDTO] = None
    m_accuracy: Optional[int] = 100
    m_damage: Optional[int] = 0
    m_heal: Optional[int] = 0
    m_rounds: Optional[int] = 0
    
    # Enhancement and modification data
    m_enchantments: List[Any] = field(default_factory=list)
    m_modifiers: List[Any] = field(default_factory=list)
    m_bonuses: List[Any] = field(default_factory=list)
    
    # Runtime tracking
    m_castTime: Optional[float] = 0.0
    m_animationTime: Optional[float] = 0.0
    m_cooldownTime: Optional[float] = 0.0


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
class DelaySpellEffectDTO(SpellEffectDTO):
    """DTO for DelaySpellEffect - inherits from SpellEffectDTO"""
    # Additional fields specific to DelaySpellEffect beyond SpellEffect
    m_damage: Optional[int] = 0
    m_rounds: Optional[int] = 0
    m_spellDelayedTemplateID: Optional[int] = 0
    m_spellDelayedTemplateDamageID: Optional[int] = 0
    m_spellEnchanterTemplateID: Optional[int] = 0
    m_targetSubcircleList: List[int] = field(default_factory=list)
    m_spellHits: Optional[int] = 0  # char -> int for simplicity
    m_spell: Optional[Any] = None  # SharedPointer<Spell> -> Any for now


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


# ===== EFFECT DTO CLASSES =====

@dataclass
class ConditionalSpellElementDTO:
    """DTO for ConditionalSpellElement - simple container for requirement + effect"""
    m_pReqs: Optional['RequirementListDTO'] = None
    m_pEffect: Optional['SpellEffectDTO'] = None


@dataclass
class ConditionalSpellEffectDTO(SpellEffectDTO):
    """DTO for ConditionalSpellEffect - inherits from SpellEffectDTO"""
    m_elements: List['ConditionalSpellElementDTO'] = field(default_factory=list)


@dataclass
class VariableSpellEffectDTO(SpellEffectDTO):
    """DTO for VariableSpellEffect - inherits from SpellEffectDTO"""
    m_effectList: List['SpellEffectDTO'] = field(default_factory=list)


@dataclass
class EffectListSpellEffectDTO(SpellEffectDTO):
    """DTO for EffectListSpellEffect - inherits from SpellEffectDTO"""
    m_effectList: List['SpellEffectDTO'] = field(default_factory=list)


@dataclass
class TargetCountSpellEffectDTO(SpellEffectDTO):
    """DTO for TargetCountSpellEffect - inherits from SpellEffectDTO"""
    m_effectLists: List['EffectListSpellEffectDTO'] = field(default_factory=list)


@dataclass
class HangingConversionSpellEffectDTO(SpellEffectDTO):
    """DTO for HangingConversionSpellEffect - inherits from SpellEffectDTO"""
    # Enum fields
    m_hangingEffectType: Optional[int] = 0  # HangingEffectType enum
    m_outputSelector: Optional[int] = 0  # OutputEffectSelector enum
    
    # Effect filtering and conversion
    m_specificEffectTypes: List[int] = field(default_factory=list)  # kSpellEffects enum list
    m_minEffectValue: Optional[int] = 0
    m_maxEffectValue: Optional[int] = 0
    m_minEffectCount: Optional[int] = 0
    m_maxEffectCount: Optional[int] = 0
    
    # Conversion behavior
    m_notDamageType: Optional[bool] = False
    m_scaleSourceEffectValue: Optional[bool] = False
    m_sourceEffectValuePercent: Optional[float] = 0.0
    m_applyToEffectSource: Optional[bool] = False
    
    # Output effects
    m_outputEffect: List['SpellEffectDTO'] = field(default_factory=list)


@dataclass
class ShadowSpellEffectDTO(EffectListSpellEffectDTO):
    """DTO for ShadowSpellEffect - inherits from EffectListSpellEffectDTO"""
    m_shadowType: Optional[int] = 0  # Additional shadow-specific field


@dataclass
class RandomPerTargetSpellEffectDTO(RandomSpellEffectDTO):
    """DTO for RandomPerTargetSpellEffect - inherits from RandomSpellEffectDTO"""
    # Inherits m_effectList from RandomSpellEffectDTO - no additional fields needed
    pass


@dataclass
class CountBasedSpellEffectDTO(SpellEffectDTO):
    """DTO for CountBasedSpellEffect - inherits from SpellEffectDTO"""
    m_effectList: List['SpellEffectDTO'] = field(default_factory=list)
    m_countThreshold: Optional[int] = 0  # Count-based threshold field