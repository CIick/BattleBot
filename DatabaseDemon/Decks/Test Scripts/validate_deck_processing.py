#!/usr/bin/env python3
"""
Deck Processing Validation Script
=================================
Comprehensive validation script to test the complete deck processing pipeline.

This script:
1. Tests DTO conversion from XML files
2. Validates database schema creation
3. Tests complete database population
4. Verifies data integrity and analysis functions
5. Generates comprehensive validation reports

Usage:
    python validate_deck_processing.py

Output:
    - Console validation results
    - validation_report.txt with detailed findings
    - test_database.db for verification
"""

import sys
import os
import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directories to path for imports
deck_parent = Path(__file__).parent.parent
sys.path.insert(0, str(deck_parent))
sys.path.insert(0, str(deck_parent / "dtos"))
sys.path.insert(0, str(deck_parent / "processors"))

try:
    from DecksDTOFactory import DecksDTOFactory, convert_mobdecks_directory
    from DecksDTO import DeckTemplateDTO, validate_deck_dto
    from DecksEnums import categorize_deck_by_name, get_difficulty_from_name
    from DatabaseSchema import DatabaseSchema, create_database
    from DatabaseCreator import DatabaseCreator
    from WADProcessor import WADProcessor, process_deck_directory
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the correct directory")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {Path(__file__).parent}")
    print(f"Parent directory: {deck_parent}")
    print(f"Python path: {sys.path[:3]}")
    sys.exit(1)


class DeckProcessingValidator:
    """Comprehensive validator for the deck processing system."""
    
    def __init__(self):
        """Initialize the validator."""
        self.results = {
            'dto_conversion': {'passed': 0, 'failed': 0, 'errors': []},
            'database_schema': {'passed': 0, 'failed': 0, 'errors': []},
            'database_population': {'passed': 0, 'failed': 0, 'errors': []},
            'data_integrity': {'passed': 0, 'failed': 0, 'errors': []},
            'analysis_functions': {'passed': 0, 'failed': 0, 'errors': []},
            'overall_status': 'unknown'
        }
        self.test_dtos: List[DeckTemplateDTO] = []
        self.test_db_path: Optional[Path] = None
    
    def log_test_result(self, category: str, test_name: str, passed: bool, error_msg: str = ""):
        """Log a test result."""
        if passed:
            self.results[category]['passed'] += 1
            print(f"✓ {test_name}")
        else:
            self.results[category]['failed'] += 1
            self.results[category]['errors'].append(f"{test_name}: {error_msg}")
            print(f"✗ {test_name}: {error_msg}")
    
    def test_dto_conversion(self) -> bool:
        """Test DTO conversion from XML files."""
        print("\nTesting DTO Conversion...")
        print("-" * 30)
        
        try:
            # Test factory creation
            factory = DecksDTOFactory()
            self.log_test_result('dto_conversion', 'DecksDTOFactory creation', True)
            
            # Test platform path detection
            deck_path, types_path, deck_types_path = factory.get_platform_paths()
            path_exists = deck_path.exists() and types_path.exists()
            self.log_test_result('dto_conversion', 'Platform path detection', path_exists,
                               f"Paths: deck={deck_path.exists()}, types={types_path.exists()}")
            
            if not path_exists:
                return False
            
            # Test single file conversion
            xml_files = list(deck_path.glob("*.xml"))[:10]  # Test first 10 files
            if not xml_files:
                self.log_test_result('dto_conversion', 'XML files found', False, "No XML files found")
                return False
            
            self.log_test_result('dto_conversion', f'XML files found', True, f"Found {len(xml_files)} test files")
            
            # Test conversion of sample files
            successful_conversions = 0
            for xml_file in xml_files:
                dto = factory.convert_from_xml_file(xml_file)
                if dto:
                    successful_conversions += 1
                    self.test_dtos.append(dto)
            
            conversion_success = successful_conversions == len(xml_files)
            self.log_test_result('dto_conversion', f'Sample file conversions ({successful_conversions}/{len(xml_files)})', 
                               conversion_success, f"Failed: {len(xml_files) - successful_conversions}")
            
            # Test DTO validation
            if self.test_dtos:
                test_dto = self.test_dtos[0]
                validation_errors = validate_deck_dto(test_dto)
                validation_success = len(validation_errors) == 0
                self.log_test_result('dto_conversion', 'DTO validation', validation_success, 
                                   f"Validation errors: {validation_errors}")
                
                # Test DTO methods
                try:
                    _ = test_dto.get_spell_frequency()
                    _ = test_dto.get_school_distribution()
                    _ = test_dto.is_boss_deck()
                    _ = test_dto.is_school_specific()
                    _ = test_dto.get_primary_school()
                    self.log_test_result('dto_conversion', 'DTO methods', True)
                except Exception as e:
                    self.log_test_result('dto_conversion', 'DTO methods', False, str(e))
            
            return successful_conversions > 0
            
        except Exception as e:
            self.log_test_result('dto_conversion', 'DTO conversion system', False, str(e))
            return False
    
    def test_database_schema(self) -> bool:
        """Test database schema creation."""
        print("\nTesting Database Schema...")
        print("-" * 28)
        
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                self.test_db_path = Path(f.name)
            
            # Test schema creation
            schema = DatabaseSchema(self.test_db_path)
            connection = schema.setup_database()
            
            self.log_test_result('database_schema', 'Database creation', True)
            
            # Test table existence
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['decks', 'deck_spells', 'spell_summary', 'deck_school_analysis', 'database_metadata']
            tables_exist = all(table in tables for table in expected_tables)
            self.log_test_result('database_schema', 'Required tables created', tables_exist,
                               f"Missing tables: {set(expected_tables) - set(tables)}")
            
            # Test indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            has_indexes = len(indexes) > 5  # Should have multiple indexes
            self.log_test_result('database_schema', 'Indexes created', has_indexes,
                               f"Found {len(indexes)} indexes")
            
            # Test views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = [row[0] for row in cursor.fetchall()]
            has_views = len(views) > 0
            self.log_test_result('database_schema', 'Views created', has_views,
                               f"Found {len(views)} views")
            
            # Test schema version
            version = schema.get_schema_version(connection)
            version_valid = version > 0
            self.log_test_result('database_schema', 'Schema versioning', version_valid,
                               f"Version: {version}")
            
            connection.close()
            return tables_exist and has_indexes
            
        except Exception as e:
            self.log_test_result('database_schema', 'Database schema system', False, str(e))
            return False
    
    def test_database_population(self) -> bool:
        """Test database population with DTOs."""
        print("\nTesting Database Population...")
        print("-" * 31)
        
        if not self.test_dtos or not self.test_db_path:
            self.log_test_result('database_population', 'Prerequisites', False, "No test data available")
            return False
        
        try:
            # Test database creator
            creator = DatabaseCreator(self.test_db_path)
            connection = sqlite3.connect(str(self.test_db_path))
            
            # Test single DTO insertion
            test_dto = self.test_dtos[0]
            insert_success = creator.insert_deck_dto(connection, test_dto)
            self.log_test_result('database_population', 'Single DTO insertion', insert_success)
            
            if insert_success:
                # Verify insertion
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM decks")
                deck_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM deck_spells")
                spell_count = cursor.fetchone()[0]
                
                data_inserted = deck_count > 0 and spell_count > 0
                self.log_test_result('database_population', 'Data verification', data_inserted,
                                   f"Decks: {deck_count}, Spells: {spell_count}")
                
                # Test spell summary update
                creator.update_spell_summary(connection)
                cursor.execute("SELECT COUNT(*) FROM spell_summary")
                summary_count = cursor.fetchone()[0]
                
                summary_updated = summary_count > 0
                self.log_test_result('database_population', 'Spell summary update', summary_updated,
                                   f"Summary entries: {summary_count}")
            
            connection.close()
            return insert_success
            
        except Exception as e:
            self.log_test_result('database_population', 'Database population system', False, str(e))
            return False
    
    def test_data_integrity(self) -> bool:
        """Test data integrity in the database."""
        print("\nTesting Data Integrity...")
        print("-" * 26)
        
        if not self.test_db_path:
            self.log_test_result('data_integrity', 'Prerequisites', False, "No test database available")
            return False
        
        try:
            connection = sqlite3.connect(str(self.test_db_path))
            cursor = connection.cursor()
            
            # Test foreign key constraints
            cursor.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            fk_valid = len(fk_violations) == 0
            self.log_test_result('data_integrity', 'Foreign key constraints', fk_valid,
                               f"Violations: {len(fk_violations)}")
            
            # Test data consistency
            cursor.execute("""
                SELECT d.id, d.spell_count, COUNT(ds.id) as actual_spell_count
                FROM decks d
                LEFT JOIN deck_spells ds ON d.id = ds.deck_id
                GROUP BY d.id, d.spell_count
                HAVING d.spell_count != COUNT(ds.id)
            """)
            inconsistencies = cursor.fetchall()
            data_consistent = len(inconsistencies) == 0
            self.log_test_result('data_integrity', 'Spell count consistency', data_consistent,
                               f"Inconsistencies: {len(inconsistencies)}")
            
            # Test required fields
            cursor.execute("SELECT COUNT(*) FROM decks WHERE deck_name IS NULL OR deck_name = ''")
            null_names = cursor.fetchone()[0]
            names_valid = null_names == 0
            self.log_test_result('data_integrity', 'Required field validation', names_valid,
                               f"Null names: {null_names}")
            
            # Test JSON field validity
            cursor.execute("SELECT spell_names_json FROM decks LIMIT 5")
            json_valid = True
            for row in cursor.fetchall():
                try:
                    json.loads(row[0])
                except:
                    json_valid = False
                    break
            
            self.log_test_result('data_integrity', 'JSON field validity', json_valid)
            
            connection.close()
            return fk_valid and data_consistent and names_valid and json_valid
            
        except Exception as e:
            self.log_test_result('data_integrity', 'Data integrity system', False, str(e))
            return False
    
    def test_analysis_functions(self) -> bool:
        """Test analysis and reporting functions."""
        print("\nTesting Analysis Functions...")
        print("-" * 30)
        
        if not self.test_dtos:
            self.log_test_result('analysis_functions', 'Prerequisites', False, "No test DTOs available")
            return False
        
        try:
            # Test factory analysis
            factory = DecksDTOFactory()
            analysis = factory.analyze_deck_collection(self.test_dtos)
            
            analysis_valid = 'summary' in analysis and 'school_distribution' in analysis
            self.log_test_result('analysis_functions', 'Collection analysis', analysis_valid)
            
            # Test individual DTO analysis functions
            test_dto = self.test_dtos[0]
            
            try:
                spell_freq = test_dto.get_spell_frequency()
                freq_valid = isinstance(spell_freq, dict) and len(spell_freq) > 0
                self.log_test_result('analysis_functions', 'Spell frequency analysis', freq_valid)
            except Exception as e:
                self.log_test_result('analysis_functions', 'Spell frequency analysis', False, str(e))
            
            try:
                school_dist = test_dto.get_school_distribution()
                school_valid = isinstance(school_dist, dict) and 'Unknown' in school_dist
                self.log_test_result('analysis_functions', 'School distribution analysis', school_valid)
            except Exception as e:
                self.log_test_result('analysis_functions', 'School distribution analysis', False, str(e))
            
            # Test categorization functions
            try:
                deck_type = categorize_deck_by_name(test_dto.m_name)
                difficulty = get_difficulty_from_name(test_dto.m_name)
                categorization_valid = deck_type is not None and difficulty is not None
                self.log_test_result('analysis_functions', 'Deck categorization', categorization_valid)
            except Exception as e:
                self.log_test_result('analysis_functions', 'Deck categorization', False, str(e))
            
            # Test database views (if database exists)
            if self.test_db_path and self.test_db_path.exists():
                try:
                    connection = sqlite3.connect(str(self.test_db_path))
                    cursor = connection.cursor()
                    
                    # Test views
                    cursor.execute("SELECT COUNT(*) FROM deck_summary")
                    cursor.execute("SELECT COUNT(*) FROM top_spells")
                    cursor.execute("SELECT COUNT(*) FROM school_distribution")
                    
                    views_working = True
                    self.log_test_result('analysis_functions', 'Database views', views_working)
                    
                    connection.close()
                except Exception as e:
                    self.log_test_result('analysis_functions', 'Database views', False, str(e))
            
            return analysis_valid
            
        except Exception as e:
            self.log_test_result('analysis_functions', 'Analysis functions system', False, str(e))
            return False
    
    def run_full_validation(self) -> bool:
        """Run complete validation suite."""
        print("Wizard101 Deck Processing Validation")
        print("=" * 45)
        
        start_time = datetime.now()
        
        # Run all tests
        tests = [
            ('DTO Conversion', self.test_dto_conversion),
            ('Database Schema', self.test_database_schema),
            ('Database Population', self.test_database_population),
            ('Data Integrity', self.test_data_integrity),
            ('Analysis Functions', self.test_analysis_functions)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            try:
                passed = test_func()
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"Critical error in {test_name}: {e}")
                all_passed = False
        
        end_time = datetime.now()
        
        # Determine overall status
        if all_passed:
            self.results['overall_status'] = 'PASSED'
        else:
            self.results['overall_status'] = 'FAILED'
        
        # Print summary
        print(f"\nValidation Summary:")
        print("=" * 20)
        total_passed = sum(category['passed'] for category in self.results.values() if isinstance(category, dict))
        total_failed = sum(category['failed'] for category in self.results.values() if isinstance(category, dict))
        
        print(f"Overall Status: {self.results['overall_status']}")
        print(f"Tests Passed: {total_passed}")
        print(f"Tests Failed: {total_failed}")
        print(f"Validation Time: {end_time - start_time}")
        
        return all_passed
    
    def generate_validation_report(self, output_path: Path):
        """Generate detailed validation report."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Wizard101 Deck Processing Validation Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(f"Overall Status: {self.results['overall_status']}\n\n")
                
                for category_name, category_data in self.results.items():
                    if isinstance(category_data, dict) and 'passed' in category_data:
                        f.write(f"{category_name.upper().replace('_', ' ')}\n")
                        f.write("-" * len(category_name) + "\n")
                        f.write(f"Passed: {category_data['passed']}\n")
                        f.write(f"Failed: {category_data['failed']}\n")
                        
                        if category_data['errors']:
                            f.write("Errors:\n")
                            for error in category_data['errors']:
                                f.write(f"  - {error}\n")
                        
                        f.write("\n")
                
                # Test database info
                if self.test_db_path and self.test_db_path.exists():
                    f.write("TEST DATABASE INFORMATION\n")
                    f.write("-" * 28 + "\n")
                    f.write(f"Database path: {self.test_db_path}\n")
                    f.write(f"Database size: {self.test_db_path.stat().st_size} bytes\n")
                    f.write(f"Test DTOs processed: {len(self.test_dtos)}\n")
            
            print(f"Validation report saved to: {output_path}")
            
        except Exception as e:
            print(f"Error generating validation report: {e}")
    
    def cleanup(self):
        """Clean up test artifacts."""
        if self.test_db_path and self.test_db_path.exists():
            try:
                self.test_db_path.unlink()
                print(f"Cleaned up test database: {self.test_db_path}")
            except Exception as e:
                print(f"Error cleaning up test database: {e}")


def main():
    """Main validation entry point."""
    validator = DeckProcessingValidator()
    
    try:
        # Run validation
        success = validator.run_full_validation()
        
        # Generate report
        import platform
        system = platform.system().lower()
        if system == "windows":
            reports_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/Reports/Deck Reports")
        else:
            reports_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/Reports/Deck Reports")
        
        reports_path.mkdir(parents=True, exist_ok=True)
        report_file = reports_path / "validation_report.txt"
        validator.generate_validation_report(report_file)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        return 1
    except Exception as e:
        print(f"Validation failed with error: {e}")
        return 1
    finally:
        validator.cleanup()


if __name__ == "__main__":
    exit(main())