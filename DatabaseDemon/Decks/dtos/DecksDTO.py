"""
Wizard101 Deck DTOs
===================
Data Transfer Object classes for Wizard101 deck data structures.
All fields have sensible defaults to ensure DTOs can be created from incomplete data.

Based on analysis of 3,556 deck XML files:
- All files use DeckTemplate (hash: 4737210)
- No behaviors found in current dataset (all m_behaviors arrays empty)
- 4,167 unique spell names across 84,827 spell references
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


# ===== BASE DTO CLASSES =====

@dataclass
class BehaviorTemplateDTO:
    """Base DTO for BehaviorTemplate (hash: 1197808594)"""
    # Most behavior templates have basic properties
    # This is included for future extensibility
    m_behaviorName: Optional[str] = ""
    
    # Generic fields for unknown behavior properties
    extra_properties: dict = field(default_factory=dict)


@dataclass 
class MobDeckBehaviorTemplateDTO:
    """DTO for MobDeckBehaviorTemplate (hash: 1451865413)
    
    Specialized behavior template for deck behaviors.
    Properties from mobdeckbehaviortypes.json:
    - m_behaviorName: std::string
    - m_spellList: List of spell name strings (references SpellTemplate)
    """
    m_behaviorName: Optional[str] = ""
    m_spellList: List[str] = field(default_factory=list)


@dataclass
class DeckTemplateDTO:
    """Main DTO for DeckTemplate (hash: 4737210)
    
    Properties from types.json analysis:
    - m_behaviors: Vector of BehaviorTemplate* (dynamic, usually empty)
    - m_name: std::string (deck name)
    - m_spellNameList: List of spell name strings (references SpellTemplate)
    
    This represents a complete Wizard101 mob deck with its spell composition.
    """
    # Core deck properties
    m_name: Optional[str] = ""
    m_spellNameList: List[str] = field(default_factory=list)
    m_behaviors: List[BehaviorTemplateDTO] = field(default_factory=list)
    
    # Metadata for database tracking
    source_filename: Optional[str] = ""
    type_hash: Optional[int] = None
    
    # Derived properties for analysis
    spell_count: int = field(init=False)
    unique_spell_count: int = field(init=False)
    has_behaviors: bool = field(init=False)
    
    def __post_init__(self):
        """Calculate derived properties after initialization."""
        self.spell_count = len(self.m_spellNameList)
        self.unique_spell_count = len(set(self.m_spellNameList))
        self.has_behaviors = len(self.m_behaviors) > 0
    
    def get_spell_frequency(self) -> dict:
        """Return frequency count of spells in this deck."""
        from collections import Counter
        return dict(Counter(self.m_spellNameList))
    
    def get_school_distribution(self) -> dict:
        """Analyze spell school distribution based on spell names.
        
        This uses basic heuristics to categorize spells by school.
        For more accurate analysis, would need to join with spell database.
        """
        schools = {
            'Fire': [], 'Ice': [], 'Storm': [], 'Death': [], 
            'Myth': [], 'Life': [], 'Balance': [], 'Sun': [], 
            'Moon': [], 'Star': [], 'Shadow': [], 'Unknown': []
        }
        
        # Basic keyword matching for school identification
        school_keywords = {
            'Fire': ['fire', 'flame', 'burn', 'scorch', 'phoenix', 'dragon', 'helephant'],
            'Ice': ['ice', 'frost', 'freeze', 'blizzard', 'colossus', 'mammoth'],
            'Storm': ['storm', 'thunder', 'lightning', 'shock', 'triton', 'leviathan'],
            'Death': ['death', 'drain', 'steal', 'wraith', 'vampire', 'scarecrow', 'poison'],
            'Myth': ['myth', 'minotaur', 'cyclops', 'orthrus', 'hydra', 'earthquake'],
            'Life': ['life', 'heal', 'regenerate', 'unicorn', 'centaur', 'rebirth'],
            'Balance': ['balance', 'judgement', 'ra', 'spectral', 'hydra', 'chimera'],
            'Sun': ['sun', 'colossal', 'gargantuan', 'epic', 'tough', 'strong'],
            'Moon': ['moon', 'polymorph', 'transform'],
            'Star': ['star', 'aura', 'amplify', 'fortify'],
            'Shadow': ['shadow', 'shadow-enhanced', 'backlash']
        }
        
        for spell in self.m_spellNameList:
            spell_lower = spell.lower()
            categorized = False
            
            for school, keywords in school_keywords.items():
                if any(keyword in spell_lower for keyword in keywords):
                    schools[school].append(spell)
                    categorized = True
                    break
            
            if not categorized:
                schools['Unknown'].append(spell)
        
        # Return counts instead of lists
        return {school: len(spells) for school, spells in schools.items()}
    
    def is_boss_deck(self) -> bool:
        """Determine if this appears to be a boss deck based on name patterns."""
        if not self.m_name:
            return False
            
        boss_indicators = ['boss', 'elite', 'chief', 'master', 'lord', 'king', 'queen']
        name_lower = self.m_name.lower()
        return any(indicator in name_lower for indicator in boss_indicators)
    
    def is_school_specific(self) -> bool:
        """Determine if deck is focused on a specific school."""
        distribution = self.get_school_distribution()
        total_spells = sum(distribution.values())
        
        if total_spells == 0:
            return False
            
        # Check if any single school represents >60% of spells
        for school, count in distribution.items():
            if school != 'Unknown' and count / total_spells > 0.6:
                return True
                
        return False
    
    def get_primary_school(self) -> str:
        """Get the primary school for this deck."""
        distribution = self.get_school_distribution()
        if not distribution:
            return 'Unknown'
            
        # Find school with most spells (excluding Unknown)
        school_counts = {k: v for k, v in distribution.items() if k != 'Unknown' and v > 0}
        if not school_counts:
            return 'Unknown'
            
        return max(school_counts, key=school_counts.get)


# ===== UTILITY FUNCTIONS =====

def create_deck_from_xml_data(xml_data: dict, filename: str = "") -> DeckTemplateDTO:
    """Create a DeckTemplateDTO from parsed XML data.
    
    Args:
        xml_data: Dictionary containing the parsed deck JSON data
        filename: Original filename for metadata tracking
        
    Returns:
        DeckTemplateDTO instance with all data populated
    """
    return DeckTemplateDTO(
        m_name=xml_data.get('m_name', ''),
        m_spellNameList=xml_data.get('m_spellNameList', []),
        m_behaviors=[],  # Currently all empty in dataset
        source_filename=filename,
        type_hash=xml_data.get('$__type')
    )


def validate_deck_dto(deck: DeckTemplateDTO) -> List[str]:
    """Validate a DeckTemplateDTO and return list of validation errors.
    
    Args:
        deck: DeckTemplateDTO to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not deck.m_name:
        errors.append("Deck name is empty")
    
    if not deck.m_spellNameList:
        errors.append("Spell list is empty")
    
    if deck.type_hash != 4737210:
        errors.append(f"Invalid type hash: {deck.type_hash} (expected 4737210)")
    
    # Check for reasonable spell count
    if len(deck.m_spellNameList) > 500:
        errors.append(f"Unusually large spell count: {len(deck.m_spellNameList)}")
    
    # Check for duplicate consecutive spells (might indicate parsing errors)
    if len(deck.m_spellNameList) > 1:
        consecutive_duplicates = 0
        for i in range(len(deck.m_spellNameList) - 1):
            if deck.m_spellNameList[i] == deck.m_spellNameList[i + 1]:
                consecutive_duplicates += 1
        
        if consecutive_duplicates > len(deck.m_spellNameList) * 0.8:
            errors.append("Excessive consecutive duplicate spells detected")
    
    return errors