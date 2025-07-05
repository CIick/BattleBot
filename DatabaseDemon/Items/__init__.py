"""
Wizard101 Items Database System
==============================
Complete database system for processing WizItemTemplate objects and all
nested types including pets, mounts, housing, equipment, and more.

This module provides:
- Comprehensive DTOs for 117+ discovered nested types
- WAD processing with SerializerOptions configuration
- Relational database schema with proper foreign keys
- Support for pets, mounts, housing, equipment, jewels, elixirs, etc.
- Complete error handling and statistics tracking

Usage:
    from DatabaseDemon.Items import ItemsDatabaseCreator
    
    creator = ItemsDatabaseCreator()
    creator.initialize_database()
    creator.process_all_items_from_wad()
"""

from .dtos import *
from .processors import *

# Main exports
__all__ = [
    # Core classes
    'ItemsDatabaseCreator',
    'ItemsWADProcessor', 
    'ItemsDatabaseSchema',
    'ItemsDTOFactory',
    
    # Primary DTOs
    'WizItemTemplateDTO',
    'StatisticEffectInfoDTO',
    'BehaviorTemplateDTO',
    'RequirementListDTO',
    
    # Specialized DTOs
    'PetItemBehaviorTemplateDTO',
    'MountItemBehaviorTemplateDTO',
    'FurnitureInfoBehaviorTemplateDTO',
    'JewelSocketBehaviorTemplateDTO',
    
    # Enums
    'SchoolType',
    'ItemType',
    'RarityType',
    'BehaviorType',
    'RequirementType'
]

# Version info
__version__ = '1.0.0'
__author__ = 'DatabaseDemon'
__description__ = 'Wizard101 Items Database System'