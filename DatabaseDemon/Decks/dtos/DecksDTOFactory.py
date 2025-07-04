"""
Wizard101 Decks DTO Factory
===========================
Factory class for converting Wizard101 deck objects to DTOs.

This factory handles:
- Type hash mapping for deck-related objects
- Conversion from LazyObjects to structured DTOs
- Error handling for unknown/missing types
- Centralized conversion utilities usage

Based on analysis:
- 3,556 deck files all use DeckTemplate (hash: 4737210)
- No behaviors found in current dataset
- 4,167 unique spell names across dataset
"""

import json
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict

# Import our DTOs and enums
try:
    from .DecksDTO import (
        DeckTemplateDTO, BehaviorTemplateDTO, MobDeckBehaviorTemplateDTO,
        create_deck_from_xml_data, validate_deck_dto
    )
    from .DecksEnums import TypeHashes, SpellSchool, DeckType
except ImportError:
    from DecksDTO import (
        DeckTemplateDTO, BehaviorTemplateDTO, MobDeckBehaviorTemplateDTO,
        create_deck_from_xml_data, validate_deck_dto
    )
    from DecksEnums import TypeHashes, SpellSchool, DeckType


class DecksDTOFactory:
    """Factory for converting deck objects to DTOs using type hash mappings."""
    
    # Type hash to DTO class mapping
    TYPE_HASH_TO_DTO = {
        TypeHashes.DECK_TEMPLATE: DeckTemplateDTO,
        TypeHashes.BEHAVIOR_TEMPLATE: BehaviorTemplateDTO,
        TypeHashes.MOB_DECK_BEHAVIOR_TEMPLATE: MobDeckBehaviorTemplateDTO,
    }
    
    # Reverse mapping for serialization
    DTO_TO_TYPE_HASH = {v: k for k, v in TYPE_HASH_TO_DTO.items()}
    
    def __init__(self):
        """Initialize the factory with type definitions."""
        self.supported_types = set(self.TYPE_HASH_TO_DTO.keys())
        self.conversion_stats = {
            'successful_conversions': 0,
            'failed_conversions': 0,
            'unknown_types': set(),
            'validation_errors': []
        }
    
    def get_platform_paths(self):
        """Get platform-specific paths for type definition files."""
        system = platform.system().lower()
        if system == "windows":
            types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json")
            deck_types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/deck_types.json")
            mob_deck_types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/mobdeckbehaviortypes.json")
        else:  # Linux/WSL
            types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
            deck_types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/deck_types.json")
            mob_deck_types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/mobdeckbehaviortypes.json")
        
        return types_path, deck_types_path, mob_deck_types_path
    
    def convert_from_xml_data(self, xml_data: dict, filename: str = "") -> Optional[DeckTemplateDTO]:
        """Convert XML data dictionary to appropriate DTO.
        
        Args:
            xml_data: Dictionary containing parsed deck JSON data from XML
            filename: Source filename for metadata
            
        Returns:
            DTO instance or None if conversion fails
        """
        try:
            type_hash = xml_data.get('$__type')
            if not type_hash:
                self.conversion_stats['failed_conversions'] += 1
                return None
            
            # Convert to int if it's a string
            if isinstance(type_hash, str):
                type_hash = int(type_hash)
            
            # Check if we support this type
            if type_hash not in self.supported_types:
                self.conversion_stats['unknown_types'].add(type_hash)
                self.conversion_stats['failed_conversions'] += 1
                return None
            
            # Convert based on type hash
            if type_hash == TypeHashes.DECK_TEMPLATE:
                dto = create_deck_from_xml_data(xml_data, filename)
                
                # Validate the created DTO
                validation_errors = validate_deck_dto(dto)
                if validation_errors:
                    self.conversion_stats['validation_errors'].extend(
                        [f"{filename}: {error}" for error in validation_errors]
                    )
                
                self.conversion_stats['successful_conversions'] += 1
                return dto
            
            elif type_hash == TypeHashes.BEHAVIOR_TEMPLATE:
                dto = BehaviorTemplateDTO(
                    m_behaviorName=xml_data.get('m_behaviorName', ''),
                    extra_properties={k: v for k, v in xml_data.items() 
                                    if k not in ['$__type', 'm_behaviorName']}
                )
                self.conversion_stats['successful_conversions'] += 1
                return dto
            
            elif type_hash == TypeHashes.MOB_DECK_BEHAVIOR_TEMPLATE:
                dto = MobDeckBehaviorTemplateDTO(
                    m_behaviorName=xml_data.get('m_behaviorName', ''),
                    m_spellList=xml_data.get('m_spellList', [])
                )
                self.conversion_stats['successful_conversions'] += 1
                return dto
            
            else:
                self.conversion_stats['failed_conversions'] += 1
                return None
                
        except Exception as e:
            print(f"Error converting XML data from {filename}: {e}")
            self.conversion_stats['failed_conversions'] += 1
            return None
    
    def convert_from_xml_file(self, xml_file_path: Path) -> Optional[DeckTemplateDTO]:
        """Convert a deck XML file directly to DTO.
        
        Args:
            xml_file_path: Path to the XML file containing deck data
            
        Returns:
            DeckTemplateDTO instance or None if conversion fails
        """
        try:
            with open(xml_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Parse JSON from XML file
            xml_data = json.loads(content)
            
            return self.convert_from_xml_data(xml_data, xml_file_path.name)
            
        except Exception as e:
            print(f"Error reading XML file {xml_file_path}: {e}")
            self.conversion_stats['failed_conversions'] += 1
            return None
    
    def batch_convert_directory(self, directory_path: Path) -> List[DeckTemplateDTO]:
        """Convert all XML files in a directory to DTOs.
        
        Args:
            directory_path: Path to directory containing deck XML files
            
        Returns:
            List of successfully converted DTOs
        """
        if not directory_path.exists():
            print(f"Directory not found: {directory_path}")
            return []
        
        xml_files = list(directory_path.glob("*.xml"))
        converted_dtos = []
        
        print(f"Converting {len(xml_files)} XML files from {directory_path}")
        
        for i, xml_file in enumerate(xml_files):
            if i % 500 == 0:
                print(f"Progress: {i}/{len(xml_files)} files processed")
            
            dto = self.convert_from_xml_file(xml_file)
            if dto:
                converted_dtos.append(dto)
        
        print(f"Conversion complete: {len(converted_dtos)} successful, "
              f"{len(xml_files) - len(converted_dtos)} failed")
        
        return converted_dtos
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get detailed conversion statistics."""
        return {
            'successful_conversions': self.conversion_stats['successful_conversions'],
            'failed_conversions': self.conversion_stats['failed_conversions'],
            'success_rate': (
                self.conversion_stats['successful_conversions'] / 
                max(1, self.conversion_stats['successful_conversions'] + self.conversion_stats['failed_conversions'])
            ),
            'unknown_types': list(self.conversion_stats['unknown_types']),
            'validation_errors_count': len(self.conversion_stats['validation_errors']),
            'sample_validation_errors': self.conversion_stats['validation_errors'][:10]
        }
    
    def reset_stats(self):
        """Reset conversion statistics."""
        self.conversion_stats = {
            'successful_conversions': 0,
            'failed_conversions': 0,
            'unknown_types': set(),
            'validation_errors': []
        }
    
    def to_dict(self, dto: Union[DeckTemplateDTO, BehaviorTemplateDTO, MobDeckBehaviorTemplateDTO]) -> Dict[str, Any]:
        """Convert DTO back to dictionary format.
        
        Args:
            dto: DTO instance to convert
            
        Returns:
            Dictionary representation of the DTO
        """
        base_dict = asdict(dto)
        
        # Add type hash for round-trip compatibility
        dto_class = type(dto)
        if dto_class in self.DTO_TO_TYPE_HASH:
            base_dict['$__type'] = self.DTO_TO_TYPE_HASH[dto_class]
        
        return base_dict
    
    def export_to_json(self, dtos: List[DeckTemplateDTO], output_path: Path):
        """Export DTOs to JSON file for analysis.
        
        Args:
            dtos: List of DTOs to export
            output_path: Path where to save the JSON file
        """
        try:
            export_data = {
                'metadata': {
                    'total_decks': len(dtos),
                    'conversion_stats': self.get_conversion_stats(),
                    'export_timestamp': str(__import__('datetime').datetime.now())
                },
                'decks': [self.to_dict(dto) for dto in dtos]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"Exported {len(dtos)} decks to {output_path}")
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
    
    def analyze_deck_collection(self, dtos: List[DeckTemplateDTO]) -> Dict[str, Any]:
        """Perform comprehensive analysis on a collection of deck DTOs.
        
        Args:
            dtos: List of deck DTOs to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if not dtos:
            return {'error': 'No DTOs provided for analysis'}
        
        # Basic statistics
        total_decks = len(dtos)
        total_spells = sum(dto.spell_count for dto in dtos)
        unique_spells = set()
        for dto in dtos:
            unique_spells.update(dto.m_spellNameList)
        
        # School distribution analysis
        school_counts = {school.value: 0 for school in SpellSchool}
        deck_types = {deck_type.value: 0 for deck_type in DeckType}
        
        for dto in dtos:
            primary_school = dto.get_primary_school()
            school_counts[primary_school] += 1
            
            # Categorize deck type from name
            try:
                from .DecksEnums import categorize_deck_by_name
            except ImportError:
                from DecksEnums import categorize_deck_by_name
            deck_type = categorize_deck_by_name(dto.m_name)
            deck_types[deck_type.value] += 1
        
        # Spell frequency analysis
        all_spells = []
        for dto in dtos:
            all_spells.extend(dto.m_spellNameList)
        
        from collections import Counter
        spell_frequency = Counter(all_spells)
        
        # Deck size analysis
        spell_counts = [dto.spell_count for dto in dtos]
        
        return {
            'summary': {
                'total_decks': total_decks,
                'total_spell_references': total_spells,
                'unique_spells': len(unique_spells),
                'average_spells_per_deck': total_spells / total_decks if total_decks > 0 else 0
            },
            'school_distribution': school_counts,
            'deck_type_distribution': deck_types,
            'spell_statistics': {
                'min_spells_per_deck': min(spell_counts) if spell_counts else 0,
                'max_spells_per_deck': max(spell_counts) if spell_counts else 0,
                'median_spells_per_deck': sorted(spell_counts)[len(spell_counts) // 2] if spell_counts else 0
            },
            'top_spells': dict(spell_frequency.most_common(20)),
            'decks_with_behaviors': len([dto for dto in dtos if dto.has_behaviors]),
            'boss_decks': len([dto for dto in dtos if dto.is_boss_deck()]),
            'school_focused_decks': len([dto for dto in dtos if dto.is_school_specific()])
        }


# ===== UTILITY FUNCTIONS =====

def create_factory() -> DecksDTOFactory:
    """Create and return a new DecksDTOFactory instance."""
    return DecksDTOFactory()


def convert_mobdecks_directory() -> List[DeckTemplateDTO]:
    """Convenience function to convert the entire MobDecks directory.
    
    Returns:
        List of converted deck DTOs
    """
    factory = create_factory()
    
    # Get platform-specific path
    system = platform.system().lower()
    if system == "windows":
        deck_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/Decks/MobDecks")
    else:  # Linux/WSL
        deck_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/Decks/MobDecks")
    
    return factory.batch_convert_directory(deck_path)


def export_analysis_report(dtos: List[DeckTemplateDTO], output_path: Path):
    """Generate and export a comprehensive analysis report.
    
    Args:
        dtos: List of deck DTOs to analyze
        output_path: Path where to save the analysis report
    """
    factory = create_factory()
    analysis = factory.analyze_deck_collection(dtos)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Wizard101 Deck Collection Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Generated: {__import__('datetime').datetime.now()}\n\n")
            
            # Summary section
            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            for key, value in analysis['summary'].items():
                f.write(f"{key.replace('_', ' ').title()}: {value:,}\n")
            f.write("\n")
            
            # School distribution
            f.write("SCHOOL DISTRIBUTION\n")
            f.write("-" * 20 + "\n")
            for school, count in sorted(analysis['school_distribution'].items(), 
                                      key=lambda x: x[1], reverse=True):
                if count > 0:
                    f.write(f"{school}: {count:,}\n")
            f.write("\n")
            
            # Top spells
            f.write("TOP 20 SPELLS\n")
            f.write("-" * 15 + "\n")
            for spell, count in analysis['top_spells'].items():
                f.write(f"{spell}: {count:,}\n")
            f.write("\n")
            
            # Other statistics
            f.write("ADDITIONAL STATISTICS\n")
            f.write("-" * 22 + "\n")
            f.write(f"Boss decks: {analysis['boss_decks']:,}\n")
            f.write(f"School-focused decks: {analysis['school_focused_decks']:,}\n")
            f.write(f"Decks with behaviors: {analysis['decks_with_behaviors']:,}\n")
        
        print(f"Analysis report exported to {output_path}")
        
    except Exception as e:
        print(f"Error exporting analysis report: {e}")


if __name__ == "__main__":
    # Test the factory
    print("Testing DecksDTOFactory...")
    dtos = convert_mobdecks_directory()
    
    if dtos:
        factory = create_factory()
        print(f"\nConversion complete!")
        print(f"Statistics: {factory.get_conversion_stats()}")
        
        # Generate analysis
        analysis = factory.analyze_deck_collection(dtos)
        print(f"\nAnalysis: {analysis['summary']}")
    else:
        print("No DTOs were successfully converted.")