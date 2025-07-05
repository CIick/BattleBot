"""
Items DTOs Module
================
Data Transfer Objects for Wizard101 item data structures.
"""

from .ItemsDTO import *
from .ItemsDTOFactory import ItemsDTOFactory
from .ItemsEnums import *

__all__ = [
    # Main DTO classes
    'WizItemTemplateDTO',
    'StatisticEffectInfoDTO',
    'AvatarOptionDTO',
    'AvatarTextureOptionDTO',
    'WizAvatarItemInfoDTO',
    'RequirementListDTO',
    
    # Behavior DTOs
    'BehaviorTemplateDTO',
    'RenderBehaviorTemplateDTO',
    'EquipmentBehaviorTemplateDTO',
    'AnimationBehaviorTemplateDTO',
    'CollisionBehaviorTemplateDTO',
    'FurnitureInfoBehaviorTemplateDTO',
    
    # Pet DTOs
    'PetItemBehaviorTemplateDTO',
    'PetStatDTO',
    'PetLevelInfoDTO',
    'MorphingExceptionDTO',
    'PetDyeToTextureDTO',
    
    # Mount DTOs
    'MountItemBehaviorTemplateDTO',
    'MountDyeToTextureDTO',
    
    # Jewel DTOs
    'JewelSocketBehaviorTemplateDTO',
    'JewelSocketDTO',
    
    # Requirement DTOs
    'ReqMagicLevelDTO',
    'ReqSchoolOfFocusDTO',
    'ReqHasBadgeDTO',
    'ReqHasEntryDTO',
    'ReqEnergyDTO',
    'ReqHealthPercentDTO',
    'ReqManaPercentDTO',
    'ReqIsGenderDTO',
    'ReqInCombatDTO',
    'ReqHighestCharacterLevelOnAccountDTO',
    
    # Effect DTOs
    'GameEffectInfoDTO',
    'TransformationEffectInfoDTO',
    'SpeedEffectInfoDTO',
    'StartingPipEffectInfoDTO',
    'FXBySlotEffectInfoDTO',
    
    # Housing DTOs
    'HousingMusicBehaviorTemplateDTO',
    'HousingMusicPlayerBehaviorTemplateDTO',
    'HousingTeleporterBehaviorTemplateDTO',
    'HousingSigilBehaviorTemplateDTO',
    'HousingSignBehaviorTemplateDTO',
    'HousingTextureBehaviorTemplateDTO',
    
    # Elixir DTOs
    'ElixirBehaviorTemplateDTO',
    'ElixirBenefitBehaviorTemplateDTO',
    'LevelUpElixirBehaviorTemplateDTO',
    'WorldElixirBehaviorTemplateDTO',
    
    # Specialized DTOs
    'LeashBehaviorTemplateDTO',
    'LeashOffsetOverrideDTO',
    'CustomEmoteBehaviorTemplateDTO',
    'ScriptBehaviorTemplateDTO',
    'ObjectStateBehaviorTemplateDTO',
    'FidgetBehaviorTemplateDTO',
    
    # Factory
    'ItemsDTOFactory',
    
    # Enums
    'SchoolType',
    'ItemType',
    'RarityType',
    'EquipmentSlot',
    'StatisticType',
    'PetStatType',
    'JewelSocketType',
    'BehaviorType',
    'RequirementType',
    'EffectType',
    'GenderType',
    'LightType',
    'AnimationEventType',
    'HousingItemType',
    'ElixirType',
    'MountType',
    'PetType'
]