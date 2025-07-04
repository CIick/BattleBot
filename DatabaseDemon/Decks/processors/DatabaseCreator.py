"""
Wizard101 Decks Database Creator
================================
Core logic for processing deck XML files and creating SQLite database.

This module handles:
- Batch processing of deck XML files using DecksDTOFactory
- Database insertion with comprehensive error handling
- Spell analysis and categorization
- Progress tracking and detailed logging
- Database optimization and maintenance

Based on analysis of 3,556 deck files with 84,827 spell references.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import Counter
import platform

# Import our modules
try:
    from .DatabaseSchema import DatabaseSchema, create_database
    from ..dtos.DecksDTOFactory import DecksDTOFactory, create_factory
    from ..dtos.DecksDTO import DeckTemplateDTO, validate_deck_dto
    from ..dtos.DecksEnums import (
        categorize_deck_by_name, get_difficulty_from_name, 
        extract_school_from_name, get_spell_school,
        SpellSchool, DeckType, CommonSpells
    )
except ImportError:
    from DatabaseSchema import DatabaseSchema, create_database
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "dtos"))
    from DecksDTOFactory import DecksDTOFactory, create_factory
    from DecksDTO import DeckTemplateDTO, validate_deck_dto
    from DecksEnums import (
        categorize_deck_by_name, get_difficulty_from_name, 
        extract_school_from_name, get_spell_school,
        SpellSchool, DeckType, CommonSpells
    )


class DatabaseCreator:
    """Main class for creating and populating deck databases."""
    
    def __init__(self, db_path: Path):
        """Initialize database creator.
        
        Args:
            db_path: Path where to create/update the database
        """
        self.db_path = db_path
        self.schema = DatabaseSchema(db_path)
        self.factory = create_factory()
        
        # Processing statistics
        self.stats = {
            'total_files_processed': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'database_insertions': 0,
            'validation_errors': 0,
            'start_time': None,
            'end_time': None,
            'processing_errors': []
        }
    
    def get_platform_paths(self):
        """Get platform-specific paths for deck files."""
        system = platform.system().lower()
        if system == "windows":
            deck_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/Decks/MobDecks")
            reports_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/Reports/Deck Reports")
        else:  # Linux/WSL
            deck_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/Decks/MobDecks")
            reports_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/Reports/Deck Reports")
        
        # Ensure reports directory exists
        reports_path.mkdir(parents=True, exist_ok=True)
        
        return deck_path, reports_path
    
    def setup_database(self) -> sqlite3.Connection:
        """Setup database with schema and return connection."""
        print(f"Setting up database: {self.db_path}")
        return self.schema.setup_database()
    
    def insert_deck_dto(self, connection: sqlite3.Connection, dto: DeckTemplateDTO) -> bool:
        """Insert a single deck DTO into the database.
        
        Args:
            connection: SQLite database connection
            dto: DeckTemplateDTO to insert
            
        Returns:
            True if insertion successful, False otherwise
        """
        try:
            cursor = connection.cursor()
            
            # Analyze deck properties
            deck_type = categorize_deck_by_name(dto.m_name)
            difficulty = get_difficulty_from_name(dto.m_name)
            primary_school = dto.get_primary_school()
            school_distribution = dto.get_school_distribution()
            
            # Insert main deck record
            cursor.execute("""
                INSERT OR REPLACE INTO decks (
                    filename, deck_name, type_hash, spell_count, unique_spell_count,
                    spell_names_json, deck_type, difficulty, primary_school,
                    is_school_focused, is_boss_deck, has_behaviors, behavior_count,
                    behaviors_json, data_version, raw_data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dto.source_filename,
                dto.m_name,
                dto.type_hash,
                dto.spell_count,
                dto.unique_spell_count,
                json.dumps(dto.m_spellNameList),
                deck_type.value if deck_type != DeckType.UNKNOWN else None,
                difficulty.value,
                primary_school if primary_school != 'Unknown' else None,
                dto.is_school_specific(),
                dto.is_boss_deck(),
                dto.has_behaviors,
                len(dto.m_behaviors),
                json.dumps([]),  # Currently all empty
                1,
                json.dumps({
                    'type_hash': dto.type_hash,
                    'm_name': dto.m_name,
                    'm_spellNameList': dto.m_spellNameList,
                    'm_behaviors': []
                })
            ))
            
            # Get the deck ID
            deck_id = cursor.lastrowid
            
            # Insert spell references
            spell_frequency = dto.get_spell_frequency()
            for position, spell_name in enumerate(dto.m_spellNameList):
                cursor.execute("""
                    INSERT INTO deck_spells (deck_id, spell_name, position, spell_count)
                    VALUES (?, ?, ?, ?)
                """, (deck_id, spell_name, position, spell_frequency.get(spell_name, 1)))
            
            # Insert school analysis
            for school_name, spell_count in school_distribution.items():
                if spell_count > 0:
                    percentage = (spell_count / dto.spell_count * 100) if dto.spell_count > 0 else 0
                    cursor.execute("""
                        INSERT INTO deck_school_analysis (deck_id, school_name, spell_count, percentage)
                        VALUES (?, ?, ?, ?)
                    """, (deck_id, school_name, spell_count, percentage))
            
            self.stats['database_insertions'] += 1
            return True
            
        except Exception as e:
            error_msg = f"Error inserting deck {dto.source_filename}: {e}"
            print(error_msg)
            self.stats['processing_errors'].append(error_msg)
            return False
    
    def update_spell_summary(self, connection: sqlite3.Connection):
        """Update the spell summary table with aggregated statistics."""
        print("Updating spell summary...")
        cursor = connection.cursor()
        
        # Clear existing summary
        cursor.execute("DELETE FROM spell_summary")
        
        # Aggregate spell statistics
        cursor.execute("""
            INSERT INTO spell_summary (
                spell_name, total_occurrences, deck_count, avg_copies_per_deck,
                estimated_school, is_blade, is_shield, is_trap, is_global
            )
            SELECT 
                spell_name,
                COUNT(*) as total_occurrences,
                COUNT(DISTINCT deck_id) as deck_count,
                ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT deck_id), 2) as avg_copies_per_deck,
                NULL as estimated_school,  -- Will be updated below
                0 as is_blade,
                0 as is_shield, 
                0 as is_trap,
                0 as is_global
            FROM deck_spells
            GROUP BY spell_name
        """)
        
        # Update spell categorization
        cursor.execute("SELECT spell_name FROM spell_summary")
        spells = [row[0] for row in cursor.fetchall()]
        
        for spell_name in spells:
            # Determine school
            school = get_spell_school(spell_name)
            school_name = school.value if school != SpellSchool.UNKNOWN else None
            
            # Categorize spell type
            spell_lower = spell_name.lower()
            is_blade = 'blade' in spell_lower
            is_shield = 'shield' in spell_lower
            is_trap = 'trap' in spell_lower
            is_global = any(global_spell.lower() in spell_lower 
                          for global_spell in CommonSpells.GLOBAL_SPELLS)
            
            cursor.execute("""
                UPDATE spell_summary 
                SET estimated_school = ?, is_blade = ?, is_shield = ?, is_trap = ?, is_global = ?
                WHERE spell_name = ?
            """, (school_name, is_blade, is_shield, is_trap, is_global, spell_name))
        
        connection.commit()
        print(f"Updated spell summary for {len(spells)} unique spells")
    
    def process_deck_files(self, deck_directory: Path) -> List[DeckTemplateDTO]:
        """Process all deck XML files in a directory.
        
        Args:
            deck_directory: Directory containing deck XML files
            
        Returns:
            List of successfully converted DTOs
        """
        if not deck_directory.exists():
            raise FileNotFoundError(f"Deck directory not found: {deck_directory}")
        
        xml_files = list(deck_directory.glob("*.xml"))
        if not xml_files:
            raise ValueError(f"No XML files found in {deck_directory}")
        
        print(f"Processing {len(xml_files)} deck files from {deck_directory}")
        self.stats['total_files_processed'] = len(xml_files)
        self.stats['start_time'] = datetime.now()
        
        # Use factory to convert all files
        dtos = self.factory.batch_convert_directory(deck_directory)
        
        # Update our statistics
        factory_stats = self.factory.get_conversion_stats()
        self.stats['successful_conversions'] = factory_stats['successful_conversions']
        self.stats['failed_conversions'] = factory_stats['failed_conversions']
        self.stats['validation_errors'] = factory_stats['validation_errors_count']
        
        print(f"Conversion complete: {len(dtos)} successful DTOs")
        return dtos
    
    def populate_database(self, dtos: List[DeckTemplateDTO]) -> bool:
        """Populate database with deck DTOs.
        
        Args:
            dtos: List of deck DTOs to insert
            
        Returns:
            True if population successful
        """
        if not dtos:
            print("No DTOs to insert into database")
            return False
        
        print(f"Populating database with {len(dtos)} decks...")
        
        connection = self.setup_database()
        
        try:
            # Use transaction for better performance
            connection.execute("BEGIN TRANSACTION")
            
            # Insert all decks
            successful_inserts = 0
            for i, dto in enumerate(dtos):
                if i % 500 == 0:
                    print(f"Progress: {i}/{len(dtos)} decks inserted")
                
                if self.insert_deck_dto(connection, dto):
                    successful_inserts += 1
            
            # Update spell summary
            self.update_spell_summary(connection)
            
            # Commit transaction
            connection.commit()
            
            print(f"Database population complete: {successful_inserts}/{len(dtos)} decks inserted")
            return True
            
        except Exception as e:
            print(f"Database population failed: {e}")
            connection.rollback()
            return False
            
        finally:
            connection.close()
            self.stats['end_time'] = datetime.now()
    
    def create_full_database(self) -> bool:
        """Complete database creation from deck files.
        
        Returns:
            True if database creation successful
        """
        try:
            # Get platform-specific paths
            deck_path, reports_path = self.get_platform_paths()
            
            print("Starting complete deck database creation...")
            print(f"Source directory: {deck_path}")
            print(f"Database path: {self.db_path}")
            print(f"Reports directory: {reports_path}")
            
            # Process deck files
            dtos = self.process_deck_files(deck_path)
            
            if not dtos:
                print("No DTOs were successfully created")
                return False
            
            # Populate database
            success = self.populate_database(dtos)
            
            if success:
                # Generate reports
                self.generate_reports(reports_path)
                
                # Print final statistics
                self.print_final_stats()
            
            return success
            
        except Exception as e:
            print(f"Database creation failed: {e}")
            self.stats['processing_errors'].append(f"Database creation failed: {e}")
            return False
    
    def generate_reports(self, reports_path: Path):
        """Generate comprehensive analysis reports.
        
        Args:
            reports_path: Directory where to save reports
        """
        print("Generating analysis reports...")
        
        try:
            connection = sqlite3.connect(str(self.db_path))
            
            # Database statistics report
            stats_report = reports_path / "database_statistics.txt"
            with open(stats_report, 'w', encoding='utf-8') as f:
                f.write("Wizard101 Deck Database Statistics Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                
                # Get comprehensive stats
                db_stats = self.schema.get_database_stats(connection)
                
                f.write("DATABASE OVERVIEW\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total decks: {db_stats['total_decks']:,}\n")
                f.write(f"Total spell references: {db_stats['total_spell_references']:,}\n")
                f.write(f"Unique spells: {db_stats['unique_spells']:,}\n")
                f.write(f"Database size: {db_stats['database_size_mb']} MB\n\n")
                
                f.write("SPELL STATISTICS\n")
                f.write("-" * 16 + "\n")
                spell_stats = db_stats['spell_count_stats']
                f.write(f"Average spells per deck: {spell_stats['average']}\n")
                f.write(f"Minimum spells per deck: {spell_stats['minimum']}\n")
                f.write(f"Maximum spells per deck: {spell_stats['maximum']}\n\n")
                
                f.write("SCHOOL DISTRIBUTION\n")
                f.write("-" * 18 + "\n")
                for school, count in db_stats['school_distribution'].items():
                    f.write(f"{school}: {count:,}\n")
                f.write("\n")
                
                f.write("DECK TYPE DISTRIBUTION\n")
                f.write("-" * 22 + "\n")
                for deck_type, count in db_stats['deck_type_distribution'].items():
                    f.write(f"{deck_type}: {count:,}\n")
            
            # Top spells report
            spells_report = reports_path / "top_spells_analysis.txt"
            cursor = connection.cursor()
            cursor.execute("""
                SELECT spell_name, total_occurrences, deck_count, avg_copies_per_deck, estimated_school
                FROM spell_summary 
                ORDER BY total_occurrences DESC 
                LIMIT 50
            """)
            
            with open(spells_report, 'w', encoding='utf-8') as f:
                f.write("Top 50 Spells Analysis Report\n")
                f.write("=" * 35 + "\n\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                
                f.write("RANK | SPELL NAME | TOTAL USES | DECK COUNT | AVG COPIES | SCHOOL\n")
                f.write("-" * 80 + "\n")
                
                for i, (spell, total, decks, avg, school) in enumerate(cursor.fetchall(), 1):
                    school_display = school or 'Unknown'
                    f.write(f"{i:4} | {spell:30} | {total:10,} | {decks:10,} | {avg:10} | {school_display}\n")
            
            # Processing statistics report
            processing_report = reports_path / "processing_statistics.txt"
            with open(processing_report, 'w', encoding='utf-8') as f:
                f.write("Deck Processing Statistics Report\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                
                f.write("PROCESSING SUMMARY\n")
                f.write("-" * 18 + "\n")
                f.write(f"Total files processed: {self.stats['total_files_processed']:,}\n")
                f.write(f"Successful conversions: {self.stats['successful_conversions']:,}\n")
                f.write(f"Failed conversions: {self.stats['failed_conversions']:,}\n")
                f.write(f"Database insertions: {self.stats['database_insertions']:,}\n")
                f.write(f"Validation errors: {self.stats['validation_errors']:,}\n")
                
                if self.stats['start_time'] and self.stats['end_time']:
                    duration = self.stats['end_time'] - self.stats['start_time']
                    f.write(f"Processing time: {duration}\n")
                
                if self.stats['processing_errors']:
                    f.write(f"\nPROCESSING ERRORS ({len(self.stats['processing_errors'])})\n")
                    f.write("-" * 30 + "\n")
                    for error in self.stats['processing_errors'][:20]:  # Limit to first 20
                        f.write(f"{error}\n")
            
            connection.close()
            print(f"Reports generated in {reports_path}")
            
        except Exception as e:
            print(f"Error generating reports: {e}")
    
    def print_final_stats(self):
        """Print final processing statistics to console."""
        print("\n" + "=" * 60)
        print("DECK DATABASE CREATION COMPLETE")
        print("=" * 60)
        print(f"Database file: {self.db_path}")
        print(f"Files processed: {self.stats['total_files_processed']:,}")
        print(f"Successful conversions: {self.stats['successful_conversions']:,}")
        print(f"Database insertions: {self.stats['database_insertions']:,}")
        
        if self.stats['failed_conversions'] > 0:
            print(f"Failed conversions: {self.stats['failed_conversions']:,}")
        
        if self.stats['validation_errors'] > 0:
            print(f"Validation errors: {self.stats['validation_errors']:,}")
        
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            print(f"Processing time: {duration}")
        
        # Database file size
        if self.db_path.exists():
            size_mb = self.db_path.stat().st_size / (1024 * 1024)
            print(f"Database size: {size_mb:.2f} MB")
        
        print("=" * 60)


def create_deck_database(db_path: Path) -> bool:
    """Convenience function to create a complete deck database.
    
    Args:
        db_path: Path where to create the database
        
    Returns:
        True if database creation successful
    """
    creator = DatabaseCreator(db_path)
    return creator.create_full_database()


def main():
    """Main entry point for database creation."""
    # Determine output path
    system = platform.system().lower()
    if system == "windows":
        db_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/Decks/database/wizard101_decks.db")
    else:  # Linux/WSL
        db_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/Decks/database/wizard101_decks.db")
    
    # Ensure database directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Wizard101 Deck Database Creator")
    print("=" * 40)
    print(f"Target database: {db_path}")
    
    success = create_deck_database(db_path)
    
    if success:
        print("Database creation completed successfully!")
        return 0
    else:
        print("Database creation failed!")
        return 1


if __name__ == "__main__":
    exit(main())