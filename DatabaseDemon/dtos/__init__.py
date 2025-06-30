"""
Wizard101 Spell DTOs Package
============================
Complete package for handling Wizard101 spell data structures.
"""

from .SpellsEnums import *
from .SpellsDTO import *
from .SpellsDTOFactory import FixedSpellDTOFactory

__all__ = [
    # Enums
    'kSpellSourceType',
    'GardenSpellType', 
    'FishingSpellType',
    'CantripsSpellType',
    'CantripsSpellEffect',
    
    # Base DTOs
    'ReqGardeningLevelDTO',
    'ReqHasBadgeDTO',
    'ReqMagicLevelDTO',
    'RequirementListDTO',
    'SpellDTO',
    'SpellEffectDTO',
    'SpellRankDTO',
    'SpellTemplateDTO',
    
    # Derived DTOs
    'CantripsSpellTemplateDTO',
    'CastleMagicSpellTemplateDTO',
    'DelaySpellEffectDTO',
    'FishingSpellTemplateDTO',
    'GardenSpellTemplateDTO',
    'RandomSpellEffectDTO',
    'TieredSpellTemplateDTO',
    'WhirlyBurlySpellTemplateDTO',
    
    # Effect DTOs (all missing types now supported)
    'ConditionalSpellElementDTO',
    'ConditionalSpellEffectDTO',
    'VariableSpellEffectDTO',
    'EffectListSpellEffectDTO',
    'TargetCountSpellEffectDTO',
    'HangingConversionSpellEffectDTO',
    'ShadowSpellEffectDTO',
    'RandomPerTargetSpellEffectDTO',
    'CountBasedSpellEffectDTO',
    
    # Factory
    'FixedSpellDTOFactory'
]