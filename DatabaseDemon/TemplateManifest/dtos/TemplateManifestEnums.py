#!/usr/bin/env python3
"""
TemplateManifest Enums and Constants
===================================

Enumerated values, constants, and type definitions for TemplateManifest system.
Provides centralized constants for type hashes, deck types, and other classifications.
"""

from enum import Enum, IntEnum
from typing import Dict, List, Set


class TypeHashes(IntEnum):
    """Type hash constants for TemplateManifest system"""
    TEMPLATE_MANIFEST = 171021254
    TEMPLATE_LOCATION = 1128060484


class DeckType(Enum):
    """Deck type classifications"""
    MOB = "mob"
    BOSS = "boss"
    HERO = "hero"
    POLYMORPH = "polymorph"
    TUTORIAL = "tutorial"
    SPELL = "spell"
    NPC = "npc"
    UNKNOWN = "unknown"


class DeckCategory(Enum):
    """Deck category classifications"""
    FIRE = "fire"
    ICE = "ice"
    STORM = "storm"
    MYTH = "myth"
    LIFE = "life"
    DEATH = "death"
    BALANCE = "balance"
    SHADOW = "shadow"
    RANKED = "ranked"
    LEVEL_BASED = "level_based"
    ELITE = "elite"
    BOSS = "boss"
    GENERAL = "general"
    UNKNOWN = "unknown"


class School(Enum):
    """Magic school classifications"""
    FIRE = "fire"
    ICE = "ice"
    STORM = "storm"
    MYTH = "myth"
    LIFE = "life"
    DEATH = "death"
    BALANCE = "balance"
    SHADOW = "shadow"
    STAR = "star"
    SUN = "sun"
    MOON = "moon"
    UNKNOWN = "unknown"


# Deck type detection patterns
DECK_TYPE_PATTERNS = {
    DeckType.MOB: ['mdeck', 'mobdeck'],
    DeckType.BOSS: ['bdeck', 'bossdeck'],
    DeckType.HERO: ['hdeck', 'herodeck'],
    DeckType.POLYMORPH: ['pdeck', 'polymorphdeck', 'polymorph'],
    DeckType.TUTORIAL: ['tdeck', 'tutorialdeck'],
    DeckType.SPELL: ['sdeck', 'spelldecks'],
    DeckType.NPC: ['ndeck', 'npcdeck']
}

# School detection keywords
SCHOOL_KEYWORDS = {
    School.FIRE: ['fire', 'flame', 'pyro', 'burn', 'ember'],
    School.ICE: ['ice', 'frost', 'frozen', 'chill', 'snow'],
    School.STORM: ['storm', 'thunder', 'lightning', 'bolt', 'tempest'],
    School.MYTH: ['myth', 'conjure', 'minotaur', 'cyclops'],
    School.LIFE: ['life', 'nature', 'heal', 'sprite', 'unicorn'],
    School.DEATH: ['death', 'necro', 'dark', 'vampire', 'skeleton'],
    School.BALANCE: ['balance', 'equi', 'ra', 'judgement'],
    School.SHADOW: ['shadow', 'dark', 'void', 'eclipse']
}

# Database constants
DATABASE_SCHEMA_VERSION = 1
DEFAULT_DATABASE_NAME = "template_manifest.db"
DEFAULT_BATCH_SIZE = 1000

# File path constants
TEMPLATE_MANIFEST_PATH = "TemplateManifest.xml"
DECK_PATH_PREFIX = "ObjectData/Decks/"

# Validation constants
MIN_TEMPLATE_ID = 1
MAX_TEMPLATE_ID = 999999999  # Reasonable upper bound
REQUIRED_TEMPLATE_FIELDS = ['m_filename', 'm_id']

# Analysis constants
TOP_TEMPLATES_LIMIT = 100
STATISTICS_DECIMAL_PLACES = 2

# Error categories
ERROR_CATEGORIES = {
    'MISSING_FILENAME': 'Template location missing filename',
    'INVALID_ID': 'Template location has invalid ID',
    'DUPLICATE_ID': 'Duplicate template ID found',
    'INVALID_PATH': 'Template filename has invalid path',
    'CONVERSION_ERROR': 'Failed to convert LazyObject to DTO',
    'VALIDATION_ERROR': 'DTO validation failed'
}

# Common deck name patterns for advanced categorization
DECK_NAME_PATTERNS = {
    'level_based': [r'l\d+', r'level\d+'],
    'ranked': [r'r\d+', r'rank\d+'],
    'elite': [r'elite', r'champion'],
    'boss': [r'boss', r'master', r'lord'],
    'minion': [r'minion', r'pet', r'companion'],
    'spell_specific': [r'spell', r'magic', r'enchant']
}

# Quality thresholds
QUALITY_THRESHOLDS = {
    'min_success_rate': 0.95,  # 95% conversion success rate
    'min_templates': 100,      # Minimum number of templates expected
    'max_missing_filenames': 0.01,  # 1% missing filenames allowed
    'max_invalid_ids': 0.01     # 1% invalid IDs allowed
}


def get_deck_type_from_filename(filename: str) -> DeckType:
    """
    Determine deck type from filename
    
    Args:
        filename: Deck filename
        
    Returns:
        DeckType enum value
    """
    if not filename:
        return DeckType.UNKNOWN
    
    filename_lower = filename.lower()
    
    for deck_type, patterns in DECK_TYPE_PATTERNS.items():
        if any(pattern in filename_lower for pattern in patterns):
            return deck_type
    
    return DeckType.UNKNOWN


def get_school_from_filename(filename: str) -> School:
    """
    Determine school from filename
    
    Args:
        filename: Deck filename
        
    Returns:
        School enum value
    """
    if not filename:
        return School.UNKNOWN
    
    filename_lower = filename.lower()
    
    for school, keywords in SCHOOL_KEYWORDS.items():
        if any(keyword in filename_lower for keyword in keywords):
            return school
    
    return School.UNKNOWN


def validate_template_id(template_id: int) -> bool:
    """
    Validate template ID is within acceptable range
    
    Args:
        template_id: Template ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    return MIN_TEMPLATE_ID <= template_id <= MAX_TEMPLATE_ID


def validate_filename(filename: str) -> bool:
    """
    Validate template filename
    
    Args:
        filename: Filename to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not filename:
        return False
    
    # Check for reasonable path structure
    if not filename.endswith('.xml'):
        return False
    
    # Check for expected path structure
    if not filename.startswith(DECK_PATH_PREFIX):
        return False
    
    return True


def get_validation_errors(template_id: int, filename: str) -> List[str]:
    """
    Get list of validation errors for template data
    
    Args:
        template_id: Template ID
        filename: Template filename
        
    Returns:
        List of error messages
    """
    errors = []
    
    if not validate_template_id(template_id):
        errors.append(f"Invalid template ID: {template_id}")
    
    if not validate_filename(filename):
        errors.append(f"Invalid filename: {filename}")
    
    return errors


# Export all enums and constants
__all__ = [
    'TypeHashes',
    'DeckType',
    'DeckCategory',
    'School',
    'DECK_TYPE_PATTERNS',
    'SCHOOL_KEYWORDS',
    'DATABASE_SCHEMA_VERSION',
    'DEFAULT_DATABASE_NAME',
    'DEFAULT_BATCH_SIZE',
    'TEMPLATE_MANIFEST_PATH',
    'DECK_PATH_PREFIX',
    'MIN_TEMPLATE_ID',
    'MAX_TEMPLATE_ID',
    'REQUIRED_TEMPLATE_FIELDS',
    'TOP_TEMPLATES_LIMIT',
    'STATISTICS_DECIMAL_PLACES',
    'ERROR_CATEGORIES',
    'DECK_NAME_PATTERNS',
    'QUALITY_THRESHOLDS',
    'get_deck_type_from_filename',
    'get_school_from_filename',
    'validate_template_id',
    'validate_filename',
    'get_validation_errors'
]