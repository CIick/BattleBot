"""
Wizard101 Items DTOs
===================
Data Transfer Object classes for Wizard101 item data structures based on 
WizItemTemplate and 117 discovered nested types. All fields have sensible 
defaults to ensure DTOs can be created from incomplete data.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Union
from .ItemsEnums import *


# ===== BASE DTO CLASSES =====

@dataclass
class BehaviorTemplateDTO:
    """Base DTO for BehaviorTemplate - foundation for all item behaviors"""
    m_behaviorName: Optional[str] = ""


# ===== CORE ITEM DTOS =====

@dataclass
class StatisticEffectInfoDTO:
    """DTO for StatisticEffectInfo (168,047 occurrences) - most common nested type"""
    m_effectName: Optional[str] = ""
    m_lookupIndex: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_effectPercent: Optional[float] = 0.0
    m_schoolName: Optional[str] = ""
    m_effectType: Optional[int] = 0


@dataclass
class AvatarOptionDTO:
    """DTO for AvatarOption (62,234 occurrences) - avatar customization data"""
    m_mesh: Optional[str] = ""
    m_noMesh: Optional[bool] = False
    m_geometry: Optional[str] = ""
    m_conditionFlags: List[str] = field(default_factory=list)
    m_assetName: Optional[str] = ""
    m_materialName: Optional[str] = ""


@dataclass
class AvatarTextureOptionDTO:
    """DTO for AvatarTextureOption (57,232 occurrences) - texture customization"""
    m_conditionFlags: List[str] = field(default_factory=list)
    m_decals: List[str] = field(default_factory=list)
    m_decals2: List[str] = field(default_factory=list)
    m_materialName: Optional[str] = ""
    m_textures: List[str] = field(default_factory=list)
    m_tintColorNames: List[str] = field(default_factory=list)
    m_tintColors: List[Any] = field(default_factory=list)
    m_useTintColor: Optional[bool] = False


@dataclass
class WizAvatarItemInfoDTO:
    """DTO for WizAvatarItemInfo - container for avatar customization data"""
    m_defaultOption: Optional[AvatarOptionDTO] = None
    m_defaultTextureOption: Optional[AvatarTextureOptionDTO] = None
    m_flags: List[str] = field(default_factory=list)
    m_options: List[AvatarOptionDTO] = field(default_factory=list)
    m_partName: Optional[str] = ""
    m_slotName: Optional[str] = ""
    m_textureOptions: List[AvatarTextureOptionDTO] = field(default_factory=list)


# ===== BEHAVIOR DTO CLASSES =====

@dataclass
class RenderBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for RenderBehaviorTemplate (59,104 occurrences) - rendering behavior"""
    m_assetName: Optional[str] = ""
    m_proxyName: Optional[str] = ""
    m_scale: Optional[float] = 1.0
    m_opacity: Optional[float] = 1.0
    m_bCastsShadow: Optional[bool] = True
    m_bStaticObject: Optional[bool] = False
    m_height: Optional[float] = 0.0
    m_nLightType: Optional[int] = 1


@dataclass
class EquipmentBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for EquipmentBehaviorTemplate - equipment statistics and effects"""
    m_equipSlot: Optional[str] = ""
    m_equipSchool: Optional[str] = ""
    m_levelRequirement: Optional[int] = 0
    m_statisticEffects: List[StatisticEffectInfoDTO] = field(default_factory=list)
    m_equipmentFlags: List[str] = field(default_factory=list)


@dataclass
class AnimationBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for AnimationBehaviorTemplate - animation and visual effects"""
    m_animationAssetName: Optional[str] = ""
    m_animationEventList: List[Any] = field(default_factory=list)
    m_assetName: Optional[str] = ""
    m_bCastsShadow: Optional[bool] = True
    m_bFadesIn: Optional[bool] = True
    m_bFadesOut: Optional[bool] = True
    m_bPortalExcluded: Optional[bool] = False
    m_bStaticObject: Optional[bool] = False
    m_dataLookupAssetName: Optional[str] = ""
    m_height: Optional[float] = 0.0
    m_idleAnimationName: Optional[str] = ""
    m_movementScale: Optional[float] = 1.0
    m_nLightType: Optional[int] = 1
    m_opacity: Optional[float] = 1.0
    m_proxyName: Optional[str] = ""
    m_scale: Optional[float] = 1.0
    m_skeletonID: Optional[int] = 0


@dataclass
class CollisionBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for CollisionBehaviorTemplate - collision detection"""
    m_bAutoClickBox: Optional[bool] = True
    m_bClientOnly: Optional[bool] = False
    m_bDisableCollision: Optional[bool] = False
    m_solidCollisionFilename: Optional[str] = ""
    m_walkableCollisionFilename: Optional[str] = ""


@dataclass
class FurnitureInfoBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for FurnitureInfoBehaviorTemplate - housing furniture properties"""
    m_bounce: Optional[bool] = False
    m_cameraOffsetX: Optional[float] = 0.0
    m_cameraOffsetY: Optional[float] = 0.0
    m_cameraOffsetZ: Optional[float] = 0.0
    m_pitch: Optional[float] = 0.0
    m_roll: Optional[float] = 0.0
    m_rotate: Optional[bool] = False
    m_textureFilename: Optional[str] = ""
    m_textureIndex: Optional[int] = 0
    m_yaw: Optional[float] = 0.0


# ===== PET-RELATED DTO CLASSES =====

@dataclass
class PetStatDTO:
    """DTO for PetStat - individual pet statistic"""
    m_name: Optional[str] = ""
    m_statID: Optional[int] = 0
    m_value: Optional[int] = 0


@dataclass
class PetLevelInfoDTO:
    """DTO for PetLevelInfo - pet level progression data"""
    m_level: Optional[int] = 0
    m_lootTable: List[str] = field(default_factory=list)
    m_powerCardCount: Optional[int] = 0
    m_powerCardName: Optional[str] = ""
    m_powerCardName2: Optional[str] = ""
    m_powerCardName3: Optional[str] = ""
    m_requiredXP: Optional[int] = 0
    m_template: Optional[int] = 0


@dataclass
class MorphingExceptionDTO:
    """DTO for MorphingException - pet morphing rules"""
    m_eggTemplateID: Optional[int] = 0
    m_probability: Optional[float] = 0.0
    m_secondPetTemplateID: Optional[int] = 0


@dataclass
class PetDyeToTextureDTO:
    """DTO for PetDyeToTexture - pet coloring system"""
    m_dye: Optional[int] = 0
    m_texture: Optional[int] = 0


@dataclass
class PetItemBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for PetItemBehaviorTemplate - pet-specific behavior"""
    m_Levels: List[PetLevelInfoDTO] = field(default_factory=list)
    m_animationEventList: List[Any] = field(default_factory=list)
    m_conversionLevel: Optional[int] = 0
    m_conversionStats: List[PetStatDTO] = field(default_factory=list)
    m_conversionTalents: List[str] = field(default_factory=list)
    m_conversionXP: Optional[int] = 0
    m_derbyTalents: List[str] = field(default_factory=list)
    m_duckSound: Optional[str] = ""
    m_eGender: Optional[int] = 0
    m_eRace: Optional[int] = 0
    m_eggColor: Optional[int] = 0
    m_eggName: Optional[str] = ""
    m_excludeFromHatchOfTheDay: Optional[bool] = False
    m_exclusivePet: Optional[bool] = False
    m_fScale: Optional[float] = 1.0
    m_favoriteSnackCategories: List[str] = field(default_factory=list)
    m_flyingOffset: Optional[float] = 0.0
    m_guaranteedDerbyTalents: List[str] = field(default_factory=list)
    m_guaranteedTalents: List[str] = field(default_factory=list)
    m_hatchesAsID: Optional[int] = 0
    m_hatchmakingInitalCooldownTime: Optional[int] = 0
    m_hatchmakingMaximumHatches: Optional[int] = 0
    m_hideName: Optional[bool] = False
    m_houseGuestOpacity: Optional[float] = 1.0
    m_jumpSound: Optional[str] = ""
    m_maxStats: List[PetStatDTO] = field(default_factory=list)
    m_morphingExceptions: List[MorphingExceptionDTO] = field(default_factory=list)
    m_patternToTexture: List[PetDyeToTextureDTO] = field(default_factory=list)
    m_primaryDyeToTexture: List[PetDyeToTextureDTO] = field(default_factory=list)
    m_sHatchRate: Optional[str] = ""
    m_secondaryDyeToTexture: List[PetDyeToTextureDTO] = field(default_factory=list)
    m_startStats: List[PetStatDTO] = field(default_factory=list)
    m_talents: List[str] = field(default_factory=list)
    m_wowFactor: Optional[int] = 0


# ===== MOUNT-RELATED DTO CLASSES =====

@dataclass
class MountDyeToTextureDTO:
    """DTO for MountDyeToTexture - mount coloring system"""
    m_dye: Optional[int] = 0
    m_texture: Optional[int] = 0


@dataclass
class MountItemBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for MountItemBehaviorTemplate - mount-specific behavior"""
    m_animationEventList: List[Any] = field(default_factory=list)
    m_conversionLevel: Optional[int] = 0
    m_conversionStats: List[Any] = field(default_factory=list)
    m_conversionTalents: List[str] = field(default_factory=list)
    m_eGender: Optional[int] = 0
    m_eRace: Optional[int] = 0
    m_fScale: Optional[float] = 1.0
    m_flyingOffset: Optional[float] = 0.0
    m_guaranteedTalents: List[str] = field(default_factory=list)
    m_hideName: Optional[bool] = False
    m_houseGuestOpacity: Optional[float] = 1.0
    m_maxSpeed: Optional[float] = 100.0
    m_mountType: Optional[str] = ""
    m_patternToTexture: List[MountDyeToTextureDTO] = field(default_factory=list)
    m_primaryDyeToTexture: List[MountDyeToTextureDTO] = field(default_factory=list)
    m_secondaryDyeToTexture: List[MountDyeToTextureDTO] = field(default_factory=list)
    m_talents: List[str] = field(default_factory=list)


# ===== JEWEL AND SOCKET DTO CLASSES =====

@dataclass
class JewelSocketDTO:
    """DTO for JewelSocket - individual socket for jewels"""
    m_bLockable: Optional[bool] = False
    m_socketType: Optional[int] = 0


@dataclass
class JewelSocketBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for JewelSocketBehaviorTemplate - jewel socketing system"""
    m_jewelSockets: List[JewelSocketDTO] = field(default_factory=list)
    m_socketDeleted: Optional[bool] = False


# ===== REQUIREMENT DTO CLASSES =====

@dataclass
class RequirementListDTO:
    """DTO for RequirementList - container for equipment requirements"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_requirements: List[Any] = field(default_factory=list)


@dataclass
class ReqMagicLevelDTO:
    """DTO for ReqMagicLevel - magic level requirement"""
    m_applyNOT: Optional[bool] = False
    m_magicSchool: Optional[str] = ""
    m_numericValue: Optional[float] = 0.0
    m_operator: Optional[int] = 0
    m_operatorType: Optional[int] = 0


@dataclass
class ReqSchoolOfFocusDTO:
    """DTO for ReqSchoolOfFocus - school requirement"""
    m_applyNOT: Optional[bool] = False
    m_magicSchool: Optional[str] = ""
    m_operator: Optional[int] = 0


@dataclass
class ReqHasBadgeDTO:
    """DTO for ReqHasBadge - badge requirement"""
    m_applyNOT: Optional[bool] = False
    m_badgeName: Optional[str] = ""
    m_operator: Optional[int] = 0


@dataclass
class ReqHasEntryDTO:
    """DTO for ReqHasEntry - entry requirement"""
    m_applyNOT: Optional[bool] = False
    m_entryName: Optional[str] = ""
    m_displayName: Optional[str] = ""
    m_isQuestRegistry: Optional[bool] = False
    m_operator: Optional[int] = 0
    m_questName: Optional[str] = ""


@dataclass
class ReqEnergyDTO:
    """DTO for ReqEnergy - energy requirement"""
    m_applyNOT: Optional[bool] = False
    m_numericValue: Optional[float] = 0.0
    m_operator: Optional[int] = 0
    m_operatorType: Optional[int] = 0


@dataclass
class ReqHealthPercentDTO:
    """DTO for ReqHealthPercent - health percentage requirement"""
    m_applyNOT: Optional[bool] = False
    m_fMinPercent: Optional[float] = 0.0
    m_fMaxPercent: Optional[float] = 100.0
    m_operator: Optional[int] = 0


@dataclass
class ReqManaPercentDTO:
    """DTO for ReqManaPercent - mana percentage requirement"""
    m_applyNOT: Optional[bool] = False
    m_fMinPercent: Optional[float] = 0.0
    m_fMaxPercent: Optional[float] = 100.0
    m_operator: Optional[int] = 0


@dataclass
class ReqIsGenderDTO:
    """DTO for ReqIsGender - gender requirement"""
    m_applyNOT: Optional[bool] = False
    m_gender: Optional[str] = ""
    m_operator: Optional[int] = 0


@dataclass
class ReqInCombatDTO:
    """DTO for ReqInCombat - combat state requirement"""
    m_applyNOT: Optional[bool] = False
    m_operator: Optional[int] = 0


@dataclass
class ReqHighestCharacterLevelOnAccountDTO:
    """DTO for ReqHighestCharacterLevelOnAccount - account level requirement"""
    m_applyNOT: Optional[bool] = False
    m_numericValue: Optional[float] = 0.0
    m_operator: Optional[int] = 0
    m_operatorType: Optional[int] = 0


# ===== EFFECT DTO CLASSES =====

@dataclass
class GameEffectInfoDTO:
    """DTO for GameEffectInfo - general game effects"""
    m_effectName: Optional[str] = ""
    m_lookupIndex: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_effectPercent: Optional[float] = 0.0
    m_effectType: Optional[int] = 0
    m_duration: Optional[int] = 0
    m_schoolName: Optional[str] = ""


@dataclass
class TransformationEffectInfoDTO:
    """DTO for TransformationEffectInfo - transformation effects"""
    m_effectName: Optional[str] = ""
    m_lookupIndex: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_effectPercent: Optional[float] = 0.0
    m_effectType: Optional[int] = 0
    m_schoolName: Optional[str] = ""
    m_transformationType: Optional[str] = ""
    m_transformationTarget: Optional[str] = ""
    m_duration: Optional[int] = 0


@dataclass
class SpeedEffectInfoDTO:
    """DTO for SpeedEffectInfo - speed modification effects"""
    m_effectName: Optional[str] = ""
    m_lookupIndex: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_effectPercent: Optional[float] = 0.0
    m_effectType: Optional[int] = 0
    m_schoolName: Optional[str] = ""
    m_speedMultiplier: Optional[float] = 1.0
    m_duration: Optional[int] = 0
    m_movementType: Optional[str] = ""


@dataclass
class StartingPipEffectInfoDTO:
    """DTO for StartingPipEffectInfo - starting pip effects"""
    m_effectName: Optional[str] = ""
    m_lookupIndex: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_effectPercent: Optional[float] = 0.0
    m_effectType: Optional[int] = 0
    m_pipCount: Optional[int] = 0
    m_pipType: Optional[str] = ""
    m_schoolName: Optional[str] = ""


@dataclass
class FXBySlotEffectInfoDTO:
    """DTO for FXBySlotEffectInfo - visual effects by equipment slot"""
    m_effectName: Optional[str] = ""
    m_lookupIndex: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_effectPercent: Optional[float] = 0.0
    m_schoolName: Optional[str] = ""
    m_slotName: Optional[str] = ""
    m_effectPath: Optional[str] = ""
    m_effectType: Optional[str] = ""


# ===== HOUSING DTO CLASSES =====

@dataclass
class HousingMusicBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for HousingMusicBehaviorTemplate - housing music system"""
    m_musicFiles: List[str] = field(default_factory=list)
    m_playOnApproach: Optional[bool] = True
    m_range: Optional[float] = 10.0
    m_volume: Optional[float] = 1.0


@dataclass
class HousingMusicPlayerBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for HousingMusicPlayerBehaviorTemplate - music player housing item"""
    m_playLists: List[str] = field(default_factory=list)
    m_defaultPlayList: Optional[str] = ""
    m_canShuffle: Optional[bool] = True
    m_canRepeat: Optional[bool] = True


@dataclass
class PlayListEntryDTO:
    """DTO for PlayListEntry - individual playlist entry"""
    m_songName: Optional[str] = ""
    m_songPath: Optional[str] = ""
    m_duration: Optional[float] = 0.0


@dataclass
class HousingTeleporterBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for HousingTeleporterBehaviorTemplate - teleporter housing item"""
    m_teleportName: Optional[str] = ""
    m_destinationWorldName: Optional[str] = ""
    m_destinationAreaName: Optional[str] = ""
    m_teleportCost: Optional[int] = 0


@dataclass
class SigilZoneInfoDTO:
    """DTO for SigilZoneInfo - sigil zone data"""
    m_zoneName: Optional[str] = ""
    m_zoneDisplayName: Optional[str] = ""
    m_levelRequirement: Optional[int] = 0
    m_questRequirement: Optional[str] = ""


@dataclass
class HousingSigilBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for HousingSigilBehaviorTemplate - sigil housing item"""
    m_sigilZones: List[SigilZoneInfoDTO] = field(default_factory=list)
    m_allowedPlayers: List[str] = field(default_factory=list)


@dataclass
class HousingSignBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for HousingSignBehaviorTemplate - sign housing item"""
    m_signText: Optional[str] = ""
    m_fontName: Optional[str] = ""
    m_fontSize: Optional[int] = 12
    m_textColor: Optional[str] = ""


@dataclass
class HousingTextureBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for HousingTextureBehaviorTemplate - texture housing item"""
    m_textureFile: Optional[str] = ""
    m_textureSlot: Optional[str] = ""
    m_repeatX: Optional[int] = 1
    m_repeatY: Optional[int] = 1


# ===== SPECIALIZED BEHAVIOR DTO CLASSES =====

@dataclass
class LeashOffsetOverrideDTO:
    """DTO for LeashOffsetOverride - pet leash positioning"""
    m_offsetX: Optional[float] = 0.0
    m_offsetY: Optional[float] = 0.0
    m_offsetZ: Optional[float] = 0.0


@dataclass
class LeashBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for LeashBehaviorTemplate - pet leash behavior"""
    m_leashLength: Optional[float] = 5.0
    m_leashOffset: Optional[LeashOffsetOverrideDTO] = None
    m_allowFreeRoam: Optional[bool] = False


@dataclass
class UserAnimationEventDTO:
    """DTO for UserAnimationEvent - user-triggered animation"""
    m_eventName: Optional[str] = ""
    m_animationName: Optional[str] = ""
    m_soundEffect: Optional[str] = ""
    m_particleEffect: Optional[str] = ""


@dataclass
class CustomEmoteBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for CustomEmoteBehaviorTemplate - custom emote system"""
    m_emoteName: Optional[str] = ""
    m_animationEvents: List[UserAnimationEventDTO] = field(default_factory=list)
    m_duration: Optional[float] = 1.0


@dataclass
class ScriptBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for ScriptBehaviorTemplate - scripted item behavior"""
    m_scriptName: Optional[str] = ""
    m_scriptParameters: Dict[str, Any] = field(default_factory=dict)
    m_autoExecute: Optional[bool] = False


@dataclass
class ObjectStateBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for ObjectStateBehaviorTemplate - object state management"""
    m_stateSetName: Optional[str] = ""
    m_defaultState: Optional[str] = ""
    m_allowStateChange: Optional[bool] = True


@dataclass
class FidgetStateInfoDTO:
    """DTO for FidgetStateInfo - fidget animation state"""
    m_stateName: Optional[str] = ""
    m_animationName: Optional[str] = ""
    m_probability: Optional[float] = 0.0
    m_duration: Optional[float] = 1.0


@dataclass
class FidgetBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for FidgetBehaviorTemplate - fidget animation system"""
    m_fidgetStates: List[FidgetStateInfoDTO] = field(default_factory=list)
    m_idleTime: Optional[float] = 5.0
    m_fidgetChance: Optional[float] = 0.5


# ===== ELIXIR DTO CLASSES =====

@dataclass
class ElixirBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for ElixirBehaviorTemplate - elixir item behavior"""
    m_elixirType: Optional[str] = ""
    m_effectDuration: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_stackable: Optional[bool] = False


@dataclass
class ElixirBenefitBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for ElixirBenefitBehaviorTemplate - elixir benefit system"""
    m_benefitType: Optional[str] = ""
    m_benefitValue: Optional[float] = 0.0
    m_benefitDuration: Optional[int] = 0
    m_schoolRestriction: Optional[str] = ""


@dataclass
class LevelUpElixirPropertyRegistryEntryDTO:
    """DTO for LevelUpElixirPropertyRegistryEntry - level up elixir registry"""
    m_propertyName: Optional[str] = ""
    m_propertyValue: Optional[float] = 0.0
    m_propertyType: Optional[str] = ""


@dataclass
class LevelUpElixirSchoolSpecificDataDTO:
    """DTO for LevelUpElixirSchoolSpecificData - school-specific elixir data"""
    m_schoolName: Optional[str] = ""
    m_bonusMultiplier: Optional[float] = 1.0
    m_specialEffects: List[str] = field(default_factory=list)


@dataclass
class LevelUpElixirBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for LevelUpElixirBehaviorTemplate - level up elixir behavior"""
    m_levelBonus: Optional[int] = 0
    m_experienceBonus: Optional[float] = 0.0
    m_registryEntries: List[LevelUpElixirPropertyRegistryEntryDTO] = field(default_factory=list)
    m_schoolData: List[LevelUpElixirSchoolSpecificDataDTO] = field(default_factory=list)


@dataclass
class WorldElixirBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for WorldElixirBehaviorTemplate - world-specific elixir behavior"""
    m_worldName: Optional[str] = ""
    m_worldEffects: List[str] = field(default_factory=list)
    m_duration: Optional[int] = 0


# ===== MAIN WIZITEMTEMPLATE DTO =====

@dataclass
class WizItemTemplateDTO:
    """Main DTO for WizItemTemplate (69,497 occurrences) - the core item class"""
    # Core identification
    m_templateID: Optional[int] = 0
    m_objectName: Optional[str] = ""
    m_displayName: Optional[str] = ""
    m_description: Optional[str] = ""
    m_visualID: Optional[int] = 0
    m_nObjectType: Optional[int] = 0
    
    # School and classification
    m_school: Optional[str] = ""
    m_rarity: Optional[int] = 0
    m_rank: Optional[int] = 0
    
    # Costs and requirements
    m_baseCost: Optional[float] = 0.0
    m_creditsCost: Optional[float] = 0.0
    m_arenaPointCost: Optional[int] = 0
    m_pvpCurrencyCost: Optional[int] = 0
    m_pvpTourneyCurrencyCost: Optional[int] = 0
    m_equipRequirements: Optional[RequirementListDTO] = None
    m_purchaseRequirements: Optional[RequirementListDTO] = None
    
    # Visual and UI properties
    m_sIcon: Optional[str] = ""
    m_boyIconIndex: Optional[int] = 0
    m_girlIconIndex: Optional[int] = 0
    m_holidayFlag: Optional[str] = ""
    
    # Limits and restrictions
    m_itemLimit: Optional[int] = -1
    m_itemSetBonusTemplateID: Optional[int] = 0
    m_exemptFromAOI: Optional[bool] = False
    
    # Color and customization
    m_numPatterns: Optional[int] = 0
    m_numPrimaryColors: Optional[int] = 0
    m_numSecondaryColors: Optional[int] = 0
    
    # Collections and lists
    m_adjectiveList: List[str] = field(default_factory=list)
    m_avatarFlags: List[str] = field(default_factory=list)
    m_equipEffects: List[StatisticEffectInfoDTO] = field(default_factory=list)
    m_behaviors: List[Any] = field(default_factory=list)  # Polymorphic behavior DTOs
    
    # Avatar customization
    m_avatarInfo: Optional[WizAvatarItemInfoDTO] = None
    m_leashOffsetOverride: Optional[LeashOffsetOverrideDTO] = None
    
    # Type information (preserved from conversion)
    type_hash: Optional[int] = 991922385  # WizItemTemplate hash


# ===== ADDITIONAL DTO CLASSES FOR REMAINING TYPES =====

# Note: This covers the major types. Additional DTOs for the remaining ~50 types
# would follow the same pattern but are less frequently used. They can be added
# as needed based on discovery analysis.

@dataclass
class DependentResourceContainerDTO:
    """DTO for DependentResourceContainer - dependent resource management"""
    m_resourceName: Optional[str] = ""
    m_resourcePath: Optional[str] = ""
    m_resourceType: Optional[str] = ""


@dataclass
class DependentResourcesBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for DependentResourcesBehaviorTemplate - dependent resources behavior"""
    m_resources: List[DependentResourceContainerDTO] = field(default_factory=list)
    m_loadOnDemand: Optional[bool] = True


@dataclass
class CombatTriggerDescriptionDTO:
    """DTO for CombatTriggerDescription - combat trigger information"""
    m_triggerName: Optional[str] = ""
    m_triggerCondition: Optional[str] = ""
    m_triggerEffect: Optional[str] = ""


@dataclass
class ProvideCombatTriggerInfoDTO:
    """DTO for ProvideCombatTriggerInfo - combat trigger provider"""
    m_effectName: Optional[str] = ""
    m_lookupIndex: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_effectPercent: Optional[float] = 0.0
    m_effectType: Optional[int] = 0
    m_schoolName: Optional[str] = ""
    m_triggers: List[CombatTriggerDescriptionDTO] = field(default_factory=list)
    m_triggerChance: Optional[float] = 0.0


@dataclass
class ProvideSpellEffectInfoDTO:
    """DTO for ProvideSpellEffectInfo - spell effect provider"""
    m_spellName: Optional[str] = ""
    m_effectName: Optional[str] = ""
    m_lookupIndex: Optional[int] = 0
    m_effectValue: Optional[float] = 0.0
    m_effectPercent: Optional[float] = 0.0
    m_effectType: Optional[int] = 0
    m_schoolName: Optional[str] = ""
    m_castChance: Optional[float] = 0.0


@dataclass
class FXOverrideBehaviorInfoDTO:
    """DTO for FXOverrideBehaviorInfo - FX override information"""
    m_overrideName: Optional[str] = ""
    m_effectPath: Optional[str] = ""
    m_slotName: Optional[str] = ""


@dataclass
class FXOverrideBehaviorTemplateDTO(BehaviorTemplateDTO):
    """DTO for FXOverrideBehaviorTemplate - FX override behavior"""
    m_overrides: List[FXOverrideBehaviorInfoDTO] = field(default_factory=list)
    m_applyToAllSlots: Optional[bool] = False


# Additional specialized DTOs can be added here following the same pattern
# for the remaining ~40 less common types identified in the discovery report.