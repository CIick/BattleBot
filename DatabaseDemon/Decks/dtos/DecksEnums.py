"""
Wizard101 Deck Enums
====================
Enumerated values and constants for Wizard101 deck data processing.

Based on analysis of 3,556 deck files and type definitions.
"""

from enum import Enum, IntEnum
from typing import Dict, List


class DeckType(Enum):
    """Types of decks found in the data."""
    UNKNOWN = "unknown"
    MOB = "mob"
    BOSS = "boss"
    ELITE = "elite"
    POLYMORPH = "polymorph"
    PLAYER_HERO = "hero"  # Hdeck prefix
    MOON_DECK = "moon"
    STAR_DECK = "star"
    TUTORIAL = "tutorial"


class SpellSchool(Enum):
    """Wizard101 spell schools for categorization."""
    FIRE = "Fire"
    ICE = "Ice" 
    STORM = "Storm"
    DEATH = "Death"
    MYTH = "Myth"
    LIFE = "Life"
    BALANCE = "Balance"
    SUN = "Sun"
    MOON = "Moon"
    STAR = "Star"
    SHADOW = "Shadow"
    UNKNOWN = "Unknown"


class DeckDifficulty(Enum):
    """Estimated deck difficulty levels."""
    TUTORIAL = "tutorial"  # L01, L02, L03 prefixes
    NORMAL = "normal"
    ELITE = "elite"
    BOSS = "boss"
    UNKNOWN = "unknown"


# ===== TYPE HASH CONSTANTS =====

class TypeHashes:
    """Type hash constants for deck-related objects."""
    DECK_TEMPLATE = 4737210
    BEHAVIOR_TEMPLATE = 1197808594
    MOB_DECK_BEHAVIOR_TEMPLATE = 1451865413


# ===== DECK NAME PATTERNS =====

class DeckNamePatterns:
    """Regex patterns and keywords for deck categorization."""
    
    # Deck type indicators from filename analysis
    BOSS_INDICATORS = [
        'boss', 'elite', 'chief', 'master', 'lord', 'king', 'queen',
        'commander', 'captain', 'warden', 'admiral', 'general'
    ]
    
    POLYMORPH_INDICATORS = [
        'polymorph', 'transform', 'colossus', 'cyclops', 'draconian',
        'elf', 'fairy', 'krok', 'minotaur', 'ninjapig', 'ratthief',
        'wolfwarrior', 'babayagaegg', 'jaguar', 'moonskull', 'penguin',
        'unicorn', 'pteranodon', 'statue', 'thunderhorn'
    ]
    
    SCHOOL_INDICATORS = {
        SpellSchool.FIRE: ['fire', 'flame', 'burn', 'scorch', 'phoenix', 'dragon', 'helephant'],
        SpellSchool.ICE: ['ice', 'frost', 'freeze', 'blizzard', 'colossus', 'mammoth'],
        SpellSchool.STORM: ['storm', 'thunder', 'lightning', 'shock', 'triton', 'leviathan'],
        SpellSchool.DEATH: ['death', 'drain', 'steal', 'wraith', 'vampire', 'scarecrow', 'poison'],
        SpellSchool.MYTH: ['myth', 'minotaur', 'cyclops', 'orthrus', 'hydra', 'earthquake'],
        SpellSchool.LIFE: ['life', 'heal', 'regenerate', 'unicorn', 'centaur', 'rebirth'],
        SpellSchool.BALANCE: ['balance', 'judgement', 'ra', 'spectral', 'hydra', 'chimera'],
        SpellSchool.SUN: ['sun', 'colossal', 'gargantuan', 'epic', 'tough', 'strong'],
        SpellSchool.MOON: ['moon', 'polymorph', 'transform'],
        SpellSchool.STAR: ['star', 'aura', 'amplify', 'fortify'],
        SpellSchool.SHADOW: ['shadow', 'shadow-enhanced', 'backlash']
    }
    
    # Level patterns from filenames
    TUTORIAL_PREFIXES = ['L01', 'L02', 'L03']
    HERO_PREFIXES = ['Hdeck']
    MOB_PREFIXES = ['MDeck', 'Mdeck']


# ===== ANALYSIS CONSTANTS =====

class AnalysisConstants:
    """Constants for deck analysis and validation."""
    
    # Thresholds for deck categorization
    SCHOOL_FOCUS_THRESHOLD = 0.6  # 60% of spells must be from one school
    MAX_REASONABLE_SPELL_COUNT = 500
    MIN_SPELL_COUNT_FOR_ANALYSIS = 1
    
    # School abbreviations used in deck names
    SCHOOL_ABBREVIATIONS = {
        'B': SpellSchool.BALANCE,
        'D': SpellSchool.DEATH,
        'F': SpellSchool.FIRE,
        'I': SpellSchool.ICE,
        'L': SpellSchool.LIFE,
        'M': SpellSchool.MYTH,
        'S': SpellSchool.STORM,
        'SH': SpellSchool.SHADOW,
        'SUN': SpellSchool.SUN,
        'Moon': SpellSchool.MOON,
        'Stars': SpellSchool.STAR
    }


# ===== UTILITY FUNCTIONS =====

def categorize_deck_by_name(deck_name: str) -> DeckType:
    """Categorize a deck based on its name patterns."""
    if not deck_name:
        return DeckType.UNKNOWN
    
    name_lower = deck_name.lower()
    
    # Check for polymorph decks
    if any(indicator in name_lower for indicator in DeckNamePatterns.POLYMORPH_INDICATORS):
        return DeckType.POLYMORPH
    
    # Check for boss decks
    if any(indicator in name_lower for indicator in DeckNamePatterns.BOSS_INDICATORS):
        return DeckType.BOSS
    
    # Check prefixes
    if any(deck_name.startswith(prefix) for prefix in DeckNamePatterns.HERO_PREFIXES):
        return DeckType.PLAYER_HERO
    
    if any(deck_name.startswith(prefix) for prefix in DeckNamePatterns.MOB_PREFIXES):
        return DeckType.MOB
    
    if 'moon' in name_lower:
        return DeckType.MOON_DECK
    
    if 'star' in name_lower:
        return DeckType.STAR_DECK
    
    if any(deck_name.startswith(prefix) for prefix in DeckNamePatterns.TUTORIAL_PREFIXES):
        return DeckType.TUTORIAL
    
    return DeckType.UNKNOWN


def get_difficulty_from_name(deck_name: str) -> DeckDifficulty:
    """Determine deck difficulty from name patterns."""
    if not deck_name:
        return DeckDifficulty.UNKNOWN
    
    name_lower = deck_name.lower()
    
    if any(deck_name.startswith(prefix) for prefix in DeckNamePatterns.TUTORIAL_PREFIXES):
        return DeckDifficulty.TUTORIAL
    
    if 'boss' in name_lower:
        return DeckDifficulty.BOSS
    
    if 'elite' in name_lower:
        return DeckDifficulty.ELITE
    
    return DeckDifficulty.NORMAL


def extract_school_from_name(deck_name: str) -> SpellSchool:
    """Extract primary school from deck name using abbreviations."""
    if not deck_name:
        return SpellSchool.UNKNOWN
    
    # Try school abbreviations first
    for abbrev, school in AnalysisConstants.SCHOOL_ABBREVIATIONS.items():
        if f"-{abbrev}-" in deck_name or deck_name.startswith(f"{abbrev}-"):
            return school
    
    # Try full school names
    name_lower = deck_name.lower()
    for school, keywords in DeckNamePatterns.SCHOOL_INDICATORS.items():
        if any(keyword in name_lower for keyword in keywords):
            return school
    
    return SpellSchool.UNKNOWN


def get_spell_school(spell_name: str) -> SpellSchool:
    """Categorize a spell by school based on name patterns."""
    if not spell_name:
        return SpellSchool.UNKNOWN
    
    spell_lower = spell_name.lower()
    
    for school, keywords in DeckNamePatterns.SCHOOL_INDICATORS.items():
        if any(keyword in spell_lower for keyword in keywords):
            return school
    
    return SpellSchool.UNKNOWN


# ===== TOP SPELLS FROM ANALYSIS =====

class CommonSpells:
    """Most common spells found in deck analysis."""
    
    # Top 20 most frequent spells across all decks
    TOP_SPELLS = [
        'Balanceblade', 'Stormblade Self Mob', 'Tower Shield', 'Mythblade Self Mob',
        'Deathblade Self Mob', 'Weakness', 'Fireblade Self Mob', 'Lifeblade Self Mob',
        'Iceblade Self Mob', 'Dragonblade - Amulet', 'Brace', 'Hex', 'Fire Trap',
        'Ice Trap', 'Bladestorm', 'Myth Trap', 'Curse', 'Triton', 'Fire Dragon',
        'Scarecrow'
    ]
    
    # Common spell categories
    BLADE_SPELLS = [
        'Balanceblade', 'Stormblade Self Mob', 'Mythblade Self Mob', 'Deathblade Self Mob',
        'Fireblade Self Mob', 'Lifeblade Self Mob', 'Iceblade Self Mob', 'Dragonblade - Amulet'
    ]
    
    SHIELD_SPELLS = [
        'Tower Shield', 'Fire Shield', 'Ice Shield', 'Storm Shield', 'Death Shield',
        'Myth Shield', 'Life Shield'
    ]
    
    TRAP_SPELLS = [
        'Fire Trap', 'Ice Trap', 'Storm Trap', 'Death Trap', 'Myth Trap', 'Life Trap',
        'Balance Trap'
    ]
    
    GLOBAL_SPELLS = [
        'Brace', 'Bladestorm', 'Hex', 'Curse', 'Weakness'
    ]