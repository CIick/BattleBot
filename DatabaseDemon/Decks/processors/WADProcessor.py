"""
Wizard101 Decks XML Processor
=============================
Processor for handling deck XML files that contain serialized deck data.

This module adapts the WAD processing pattern for XML files containing
deck data that was manually extracted from Root.wad files. Since the
deck data is already in XML format, this processor focuses on:

- Reading and parsing XML files containing JSON deck data
- Applying validation and error handling
- Batch processing with progress tracking
- Following katsuba best practices for consistency
- Integration with existing processing patterns

Note: Unlike Spells/Mobs systems that use katsuba to process WAD files directly,
this system processes pre-extracted XML files since deck parsing had issues
with the katsuba Python bindings.
"""

import json
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Tuple
from datetime import datetime
import xml.etree.ElementTree as ET

# Import our modules
try:
    from ..dtos.DecksDTOFactory import DecksDTOFactory
    from ..dtos.DecksDTO import DeckTemplateDTO
    from ..dtos.DecksEnums import TypeHashes
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "dtos"))
    from DecksDTOFactory import DecksDTOFactory
    from DecksDTO import DeckTemplateDTO
    from DecksEnums import TypeHashes


class WADProcessor:
    """Processor for deck XML files following WAD processing patterns."""
    
    def __init__(self):
        """Initialize the XML processor."""
        self.factory = DecksDTOFactory()
        self.processing_stats = {
            'files_found': 0,
            'files_processed': 0,
            'successful_parses': 0,
            'failed_parses': 0,
            'validation_errors': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }
    
    def get_platform_paths(self):
        """Get platform-specific paths for deck and type files."""
        system = platform.system().lower()
        if system == "windows":
            deck_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/Decks/MobDecks")
            types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json") 
            deck_types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/deck_types.json")
        else:  # Linux/WSL
            deck_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/Decks/MobDecks")
            types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
            deck_types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/deck_types.json")
        
        return deck_path, types_path, deck_types_path
    
    def validate_xml_file(self, xml_path: Path) -> bool:
        """Validate that an XML file contains valid deck data.
        
        Args:
            xml_path: Path to XML file to validate
            
        Returns:
            True if file contains valid deck data
        """
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Parse as JSON
            data = json.loads(content)
            
            # Check for required fields
            if not isinstance(data, dict):
                return False
            
            if '$__type' not in data:
                return False
            
            # Check if it's a DeckTemplate
            type_hash = data.get('$__type')
            if isinstance(type_hash, str):
                type_hash = int(type_hash)
            
            if type_hash != TypeHashes.DECK_TEMPLATE:
                return False
            
            # Check for expected properties
            required_props = ['m_name', 'm_spellNameList', 'm_behaviors']
            if not all(prop in data for prop in required_props):
                return False
            
            return True
            
        except Exception as e:
            self.processing_stats['errors'].append(f"Validation error for {xml_path.name}: {e}")
            return False
    
    def parse_xml_file(self, xml_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single XML file and extract deck data.
        
        Args:
            xml_path: Path to XML file to parse
            
        Returns:
            Dictionary containing deck data or None if parsing fails
        """
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Parse JSON content from XML file
            deck_data = json.loads(content)
            
            # Add metadata
            deck_data['_source_file'] = xml_path.name
            deck_data['_processed_at'] = datetime.now().isoformat()
            
            return deck_data
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parse error in {xml_path.name}: {e}"
            self.processing_stats['errors'].append(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error parsing {xml_path.name}: {e}"
            self.processing_stats['errors'].append(error_msg)
            return None
    
    def find_deck_files(self, directory: Path) -> List[Path]:
        """Find all deck XML files in a directory.
        
        Args:
            directory: Directory to search for XML files
            
        Returns:
            List of XML file paths
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        xml_files = list(directory.glob("*.xml"))
        
        # Filter for files that contain deck data
        valid_files = []
        for xml_file in xml_files:
            if self.validate_xml_file(xml_file):
                valid_files.append(xml_file)
        
        self.processing_stats['files_found'] = len(valid_files)
        print(f"Found {len(valid_files)} valid deck XML files in {directory}")
        
        return valid_files
    
    def process_file_batch(self, xml_files: List[Path], batch_size: int = 100) -> Iterator[Tuple[List[Dict[str, Any]], List[str]]]:
        """Process XML files in batches for memory efficiency.
        
        Args:
            xml_files: List of XML files to process
            batch_size: Number of files to process per batch
            
        Yields:
            Tuple of (successful_data_list, error_list) for each batch
        """
        total_files = len(xml_files)
        print(f"Processing {total_files} files in batches of {batch_size}")
        
        for i in range(0, total_files, batch_size):
            batch = xml_files[i:i + batch_size]
            batch_data = []
            batch_errors = []
            
            print(f"Processing batch {i//batch_size + 1}: files {i+1}-{min(i+batch_size, total_files)}")
            
            for xml_file in batch:
                self.processing_stats['files_processed'] += 1
                
                deck_data = self.parse_xml_file(xml_file)
                if deck_data:
                    batch_data.append(deck_data)
                    self.processing_stats['successful_parses'] += 1
                else:
                    batch_errors.append(f"Failed to parse: {xml_file.name}")
                    self.processing_stats['failed_parses'] += 1
            
            yield batch_data, batch_errors
    
    def convert_to_dtos(self, deck_data_list: List[Dict[str, Any]]) -> List[DeckTemplateDTO]:
        """Convert parsed deck data to DTOs using DecksDTOFactory.
        
        Args:
            deck_data_list: List of parsed deck data dictionaries
            
        Returns:
            List of DeckTemplateDTO instances
        """
        dtos = []
        
        for deck_data in deck_data_list:
            filename = deck_data.get('_source_file', 'unknown.xml')
            dto = self.factory.convert_from_xml_data(deck_data, filename)
            
            if dto:
                dtos.append(dto)
            else:
                self.processing_stats['validation_errors'] += 1
        
        return dtos
    
    def process_all_decks(self, directory: Optional[Path] = None) -> List[DeckTemplateDTO]:
        """Process all deck XML files in the specified directory.
        
        Args:
            directory: Directory containing deck XML files (auto-detected if None)
            
        Returns:
            List of successfully processed DeckTemplateDTO instances
        """
        self.processing_stats['start_time'] = datetime.now()
        
        # Get directory path
        if directory is None:
            directory, _, _ = self.get_platform_paths()
        
        print(f"Starting deck processing from: {directory}")
        
        # Find all deck files
        xml_files = self.find_deck_files(directory)
        
        if not xml_files:
            print("No valid deck XML files found")
            return []
        
        # Process files in batches
        all_dtos = []
        
        for batch_data, batch_errors in self.process_file_batch(xml_files):
            # Convert batch to DTOs
            batch_dtos = self.convert_to_dtos(batch_data)
            all_dtos.extend(batch_dtos)
            
            # Log any errors
            for error in batch_errors:
                print(f"  Error: {error}")
        
        self.processing_stats['end_time'] = datetime.now()
        
        # Print final statistics
        self.print_processing_stats()
        
        return all_dtos
    
    def export_processed_data(self, dtos: List[DeckTemplateDTO], output_path: Path):
        """Export processed DTOs to JSON for analysis or backup.
        
        Args:
            dtos: List of DTOs to export
            output_path: Path where to save the exported data
        """
        try:
            # Prepare export data
            export_data = {
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'total_decks': len(dtos),
                    'processing_stats': self.get_processing_stats(),
                    'processor_version': '1.0'
                },
                'decks': []
            }
            
            # Convert DTOs to dictionaries
            for dto in dtos:
                deck_dict = self.factory.to_dict(dto)
                export_data['decks'].append(deck_dict)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"Exported {len(dtos)} decks to {output_path}")
            
        except Exception as e:
            print(f"Error exporting processed data: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics.
        
        Returns:
            Dictionary containing processing statistics
        """
        stats = dict(self.processing_stats)
        
        # Calculate derived statistics
        if stats['files_processed'] > 0:
            stats['success_rate'] = stats['successful_parses'] / stats['files_processed']
            stats['failure_rate'] = stats['failed_parses'] / stats['files_processed']
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        # Calculate processing time
        if stats['start_time'] and stats['end_time']:
            duration = stats['end_time'] - stats['start_time']
            stats['processing_duration'] = str(duration)
            stats['files_per_second'] = stats['files_processed'] / duration.total_seconds()
        
        return stats
    
    def print_processing_stats(self):
        """Print processing statistics to console."""
        stats = self.get_processing_stats()
        
        print("\n" + "=" * 50)
        print("DECK XML PROCESSING STATISTICS")
        print("=" * 50)
        print(f"Files found: {stats['files_found']:,}")
        print(f"Files processed: {stats['files_processed']:,}")
        print(f"Successful parses: {stats['successful_parses']:,}")
        print(f"Failed parses: {stats['failed_parses']:,}")
        print(f"Validation errors: {stats['validation_errors']:,}")
        print(f"Success rate: {stats['success_rate']:.2%}")
        
        if 'processing_duration' in stats:
            print(f"Processing time: {stats['processing_duration']}")
            print(f"Files per second: {stats['files_per_second']:.2f}")
        
        if stats['errors']:
            print(f"\nErrors encountered: {len(stats['errors'])}")
            if len(stats['errors']) <= 10:
                for error in stats['errors']:
                    print(f"  - {error}")
            else:
                for error in stats['errors'][:10]:
                    print(f"  - {error}")
                print(f"  ... and {len(stats['errors']) - 10} more errors")
        
        print("=" * 50)
    
    def validate_type_definitions(self) -> bool:
        """Validate that required type definitions are available.
        
        Returns:
            True if all required types are available
        """
        _, types_path, deck_types_path = self.get_platform_paths()
        
        try:
            # Check if type files exist
            if not types_path.exists():
                print(f"Error: types.json not found at {types_path}")
                return False
            
            # Load and validate type definitions
            with open(types_path, 'r', encoding='utf-8') as f:
                types_data = json.load(f)
            
            # Check for DeckTemplate type
            classes = types_data.get('classes', {})
            if str(TypeHashes.DECK_TEMPLATE) not in classes:
                print(f"Error: DeckTemplate (hash {TypeHashes.DECK_TEMPLATE}) not found in types.json")
                return False
            
            print("Type definitions validated successfully")
            return True
            
        except Exception as e:
            print(f"Error validating type definitions: {e}")
            return False


def process_deck_directory(directory: Optional[Path] = None) -> List[DeckTemplateDTO]:
    """Convenience function to process all decks in a directory.
    
    Args:
        directory: Directory containing deck XML files (auto-detected if None)
        
    Returns:
        List of processed DeckTemplateDTO instances
    """
    processor = WADProcessor()
    
    # Validate type definitions first
    if not processor.validate_type_definitions():
        print("Type definition validation failed")
        return []
    
    return processor.process_all_decks(directory)


def export_deck_analysis(dtos: List[DeckTemplateDTO], output_dir: Path):
    """Export comprehensive deck analysis to files.
    
    Args:
        dtos: List of deck DTOs to analyze
        output_dir: Directory where to save analysis files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export raw processed data
    processor = WADProcessor()
    processor.export_processed_data(dtos, output_dir / "processed_decks.json")
    
    # Export analysis using factory
    factory = DecksDTOFactory()
    analysis = factory.analyze_deck_collection(dtos)
    
    # Save analysis report
    analysis_file = output_dir / "deck_collection_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis exported to {output_dir}")


def main():
    """Main entry point for XML processing."""
    print("Wizard101 Deck XML Processor")
    print("=" * 35)
    
    # Process all decks
    dtos = process_deck_directory()
    
    if dtos:
        print(f"\nSuccessfully processed {len(dtos)} decks")
        
        # Export analysis
        system = platform.system().lower()
        if system == "windows":
            output_dir = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/Reports/Deck Reports")
        else:
            output_dir = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/Reports/Deck Reports")
        
        export_deck_analysis(dtos, output_dir)
        
    else:
        print("No decks were successfully processed")
    
    return len(dtos)


if __name__ == "__main__":
    exit(0 if main() > 0 else 1)