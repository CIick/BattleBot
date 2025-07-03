"""
Mobs Data Transfer Objects
=========================
DTO classes for Wizard101 mob data structures based on WizGameObjectTemplate
and associated behavior classes.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict, Union
from .MobsEnums import MobTitle, SchoolType, ObjectType, LightType, PathDirection, PathType


@dataclass
class BehaviorTemplateDTO:
    """Base DTO for BehaviorTemplate (hash: 360231646)"""
    m_behaviorName: Optional[str] = None


@dataclass
class AnimationBehaviorDTO(BehaviorTemplateDTO):
    """DTO for AnimationBehavior (hash: 101271634)"""
    m_animationAssetName: Optional[str] = None
    m_animationEventList: Optional[List[Any]] = field(default_factory=list)
    m_assetName: Optional[str] = None
    m_bCastsShadow: Optional[bool] = True
    m_bFadesIn: Optional[bool] = True
    m_bFadesOut: Optional[bool] = True
    m_bPortalExcluded: Optional[bool] = False
    m_bStaticObject: Optional[bool] = False
    m_dataLookupAssetName: Optional[str] = None
    m_height: Optional[float] = 0.0
    m_idleAnimationName: Optional[str] = None
    m_movementScale: Optional[float] = 1.0
    m_nLightType: Optional[int] = 1
    m_opacity: Optional[float] = 1.0
    m_proxyName: Optional[str] = None
    m_scale: Optional[float] = 1.0
    m_skeletonID: Optional[int] = 0


@dataclass
class WizardEquipmentBehaviorDTO(BehaviorTemplateDTO):
    """DTO for WizardEquipmentBehavior (hash: 892480983)"""
    m_equipmentTemplate: Optional[str] = None
    m_infoList: Optional[List[Any]] = field(default_factory=list)
    m_itemList: Optional[List[int]] = field(default_factory=list)


@dataclass
class BasicObjectStateBehaviorDTO(BehaviorTemplateDTO):
    """DTO for BasicObjectStateBehavior (hash: 1364452653)"""
    m_stateSetName: Optional[str] = None


@dataclass
class PathBehaviorDTO(BehaviorTemplateDTO):
    """DTO for PathBehavior (hash: 185541179)"""
    m_actionList: Optional[List[Any]] = field(default_factory=list)
    m_kPathType: Optional[int] = 0
    m_nPathDirection: Optional[int] = 1
    m_pathID: Optional[int] = 0
    m_pauseChance: Optional[int] = 0
    m_timeToPause: Optional[float] = 0.0


@dataclass
class PathMovementBehaviorDTO(BehaviorTemplateDTO):
    """DTO for PathMovementBehavior (hash: 1443896326)"""
    m_movementScale: Optional[float] = 1.0
    m_movementSpeed: Optional[float] = 133.0


@dataclass
class DuelistBehaviorDTO(BehaviorTemplateDTO):
    """DTO for DuelistBehavior (hash: 290147688)"""
    m_npcProximity: Optional[float] = 350.0


@dataclass
class NPCBehaviorDTO(BehaviorTemplateDTO):
    """DTO for NPCBehavior (hash: 1701337223)"""
    m_baseEffects: Optional[List[Any]] = field(default_factory=list)
    m_bossMob: Optional[bool] = False
    m_cylinderScaleValue: Optional[float] = 1.0
    m_fIntelligence: Optional[float] = 0.8
    m_fSelfishFactor: Optional[float] = 0.8
    m_maxShadowPips: Optional[int] = 0
    m_mobTitle: Optional[int] = 1  # MobTitle enum
    m_nAggressiveFactor: Optional[int] = 8
    m_nLevel: Optional[int] = 1
    m_nStartingHealth: Optional[int] = 100
    m_nameColor: Optional[str] = None  # Converted from Color object
    m_schoolOfFocus: Optional[str] = None
    m_secondarySchoolOfFocus: Optional[str] = None
    m_triggerList: Optional[str] = None
    m_turnTowardsPlayer: Optional[bool] = True


@dataclass
class CollisionBehaviorDTO(BehaviorTemplateDTO):
    """DTO for CollisionBehavior (hash: 2052493990)"""
    m_bAutoClickBox: Optional[bool] = True
    m_bClientOnly: Optional[bool] = False
    m_bDisableCollision: Optional[bool] = False
    m_solidCollisionFilename: Optional[str] = None
    m_walkableCollisionFilename: Optional[str] = None


@dataclass
class MobMonsterMagicBehaviorDTO(BehaviorTemplateDTO):
    """DTO for MobMonsterMagicBehavior (hash: 959047476)"""
    m_alternateMobTemplateID: Optional[int] = 0
    m_collectedAsTemplateID: Optional[int] = 0
    m_collectionResistance: Optional[int] = 0
    m_essencesPerHouseGuest: Optional[int] = 20
    m_essencesPerKillTC: Optional[int] = 15
    m_essencesPerSummonTC: Optional[int] = 10
    m_goldPerHouseGuest: Optional[int] = 1500
    m_goldPerKillTC: Optional[int] = 2000
    m_goldPerSummonTC: Optional[int] = 500
    m_houseGuestTemplateID: Optional[int] = 0
    m_isBoss: Optional[bool] = False
    m_worldName: Optional[str] = None


@dataclass
class WizGameObjectTemplateDTO:
    """Main DTO for WizGameObjectTemplate (hash: 701229577)"""
    # Core identification
    m_templateID: Optional[int] = None
    m_objectName: Optional[str] = None
    m_displayName: Optional[str] = None
    m_description: Optional[str] = None
    m_visualID: Optional[int] = 0
    m_nObjectType: Optional[int] = 0
    
    # School and combat properties
    m_primarySchoolName: Optional[str] = None
    
    # Lists and collections
    m_adjectiveList: Optional[List[str]] = field(default_factory=list)
    m_behaviors: Optional[List[Any]] = field(default_factory=list)  # Will contain behavior DTOs
    m_lootTable: Optional[List[str]] = field(default_factory=list)
    
    # Audio properties
    m_aggroSound: Optional[str] = None
    m_castSound: Optional[str] = None
    m_deathSound: Optional[str] = None
    m_hitSound: Optional[str] = None
    
    # Visual properties
    m_deathParticles: Optional[str] = None
    m_sIcon: Optional[str] = None
    
    # Gameplay properties
    m_exemptFromAOI: Optional[bool] = False
    m_locationPreference: Optional[str] = None
    m_leashOffsetOverride: Optional[Any] = None  # Can be null or specific object
    
    # Type information (preserved from conversion)
    type_hash: Optional[int] = 701229577