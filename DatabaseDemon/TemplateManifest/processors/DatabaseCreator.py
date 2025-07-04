#!/usr/bin/env python3
"""
TemplateManifest Database Creator
===============================

Main processing logic for creating TemplateManifest databases.
Handles complete pipeline from WAD processing to database population.

Key functionality:
- Process TemplateManifest.xml from Root.wad
- Create and populate SQLite database
- Generate comprehensive analysis reports
- Provide template ID to filename lookup capabilities
"""

import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import traceback

# Add parent directories to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from processors.WADProcessor import TemplateManifestWADProcessor, create_template_manifest_processor
from processors.DatabaseSchema import TemplateManifestDatabaseSchema, create_database_schema
from dtos import TemplateManifestDTO, TemplateLocationDTO
from dtos.TemplateManifestEnums import validate_template_id, validate_filename, get_validation_errors


class TemplateManifestDatabaseCreator:
    """Main database creator for TemplateManifest system"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize database creator
        
        Args:
            output_dir: Output directory for database and reports
        """
        self.output_dir = output_dir or Path(".")
        self.database_dir = self.output_dir / "database"
        self.reports_dir = self.output_dir / "Reports" / "TemplateManifest Reports"
        
        # Processing components
        self.wad_processor = None
        self.database_schema = None
        self.db_path = None
        
        # Statistics
        self.processing_stats = {
            'start_time': None,
            'end_time': None,
            'duration': 0,
            'templates_processed': 0,
            'templates_inserted': 0,
            'validation_errors': 0,
            'processing_errors': 0
        }
        
        # Data storage
        self.template_manifest = None
        self.validation_results = {}
        
        # Ensure output directories exist
        self.database_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def create_database(self, skip_validation: bool = False) -> bool:
        """
        Create complete TemplateManifest database
        
        Args:
            skip_validation: Skip validation for faster processing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("=" * 60)
            print("TemplateManifest Database Creator")
            print("=" * 60)
            
            self.processing_stats['start_time'] = datetime.now()
            
            # Step 1: Process TemplateManifest from WAD
            if not self._process_template_manifest():
                return False
            
            # Step 2: Create database schema
            if not self._create_database_schema():
                return False
            
            # Step 3: Populate database
            if not self._populate_database():
                return False
            
            # Step 4: Validate data (optional)
            if not skip_validation:
                if not self._validate_database():
                    print("[WARNING] Database validation found issues")
            
            # Step 5: Generate reports
            if not self._generate_reports():
                print("[WARNING] Report generation failed")
            
            self.processing_stats['end_time'] = datetime.now()
            self.processing_stats['duration'] = (
                self.processing_stats['end_time'] - self.processing_stats['start_time']
            ).total_seconds()
            
            print(f"\n[SUCCESS] Database created successfully!")
            print(f"Database: {self.db_path}")
            print(f"Processing time: {self.processing_stats['duration']:.2f} seconds")
            print(f"Templates processed: {self.processing_stats['templates_processed']}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Database creation failed: {e}")
            traceback.print_exc()
            return False
        finally:
            self._cleanup()
    
    def _process_template_manifest(self) -> bool:
        """Process TemplateManifest.xml from WAD"""
        try:
            print("\n--- Step 1: Processing TemplateManifest ---")
            
            # Create WAD processor
            self.wad_processor = create_template_manifest_processor()
            print("[OK] WAD processor initialized")
            
            # Process TemplateManifest
            self.template_manifest = self.wad_processor.process_template_manifest()
            if not self.template_manifest:
                print("[ERROR] Failed to process TemplateManifest")
                return False
            
            # Update statistics
            self.processing_stats['templates_processed'] = len(self.template_manifest.m_serializedTemplates)
            
            print(f"[OK] Processed {self.processing_stats['templates_processed']} template locations")
            
            # Basic validation
            validation_results = self.wad_processor.validate_template_manifest(self.template_manifest)
            self.validation_results = validation_results
            
            if not validation_results['valid']:
                print(f"[WARNING] Validation issues found: {validation_results['issues']}")
                self.processing_stats['validation_errors'] = len(validation_results['issues'])
            
            return True
            
        except Exception as e:
            print(f"[ERROR] TemplateManifest processing failed: {e}")
            self.processing_stats['processing_errors'] += 1
            return False
    
    def _create_database_schema(self) -> bool:
        """Create database schema"""
        try:
            print("\n--- Step 2: Creating Database Schema ---")
            
            # Generate unique database filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.db_path = self.database_dir / f"template_manifest_{timestamp}.db"
            
            # Create schema
            self.database_schema = create_database_schema(self.db_path)
            print(f"[OK] Database schema created: {self.db_path}")
            
            # Validate schema
            schema_validation = self.database_schema.validate_schema()
            if not schema_validation['valid']:
                print(f"[ERROR] Schema validation failed: {schema_validation}")
                return False
            
            print(f"[OK] Schema validated: {schema_validation['table_count']} tables, {schema_validation['view_count']} views")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Database schema creation failed: {e}")
            return False
    
    def _populate_database(self) -> bool:
        """Populate database with template data"""
        try:
            print("\n--- Step 3: Populating Database ---")
            
            cursor = self.database_schema.connection.cursor()
            
            # Insert template locations
            insert_count = 0
            error_count = 0
            
            for template in self.template_manifest.m_serializedTemplates:
                try:
                    # Simple validation - just check basic requirements
                    is_valid = template.m_id > 0 and bool(template.m_filename)
                    
                    # Insert template location
                    cursor.execute("""
                        INSERT INTO template_locations (
                            template_id, filename, file_name, file_type, file_directory, is_valid
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        template.m_id,
                        template.m_filename,
                        template.file_name,
                        template.file_type,
                        template.file_directory,
                        is_valid
                    ))
                    
                    insert_count += 1
                    
                except Exception as e:
                    error_count += 1
                    if error_count < 10:  # Only print first 10 errors
                        print(f"[ERROR] Failed to insert template {template.m_id}: {e}")
            
            # Insert statistics summary
            self._insert_statistics_summary(cursor)
            
            # Commit changes
            self.database_schema.connection.commit()
            
            self.processing_stats['templates_inserted'] = insert_count
            print(f"[OK] Inserted {insert_count} template locations")
            
            if error_count > 0:
                print(f"[WARNING] {error_count} insertion errors occurred")
                self.processing_stats['processing_errors'] += error_count
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Database population failed: {e}")
            if self.database_schema and self.database_schema.connection:
                self.database_schema.connection.rollback()
            return False
    
    def _insert_statistics_summary(self, cursor: sqlite3.Cursor):
        """Insert processing statistics summary"""
        stats = self.template_manifest.get_statistics()
        
        cursor.execute("""
            INSERT INTO template_statistics (
                total_templates, valid_templates, invalid_templates,
                file_type_distribution, validation_success_rate,
                processing_version, source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            stats['total_templates'],
            stats['valid_templates'],
            stats['total_templates'] - stats['valid_templates'],
            json.dumps(stats['file_types']),
            (stats['valid_templates'] / max(1, stats['total_templates'])) * 100,
            "1.0.0",  # Processing version
            "TemplateManifest.xml"
        ))
    
    def _validate_database(self) -> bool:
        """Validate database contents"""
        try:
            print("\n--- Step 4: Validating Database ---")
            
            cursor = self.database_schema.connection.cursor()
            
            # Check total count
            cursor.execute("SELECT COUNT(*) FROM template_locations")
            total_count = cursor.fetchone()[0]
            
            # Check valid count
            cursor.execute("SELECT COUNT(*) FROM template_locations WHERE is_valid = TRUE")
            valid_count = cursor.fetchone()[0]
            
            # Check for duplicates
            cursor.execute("SELECT template_id, COUNT(*) FROM template_locations GROUP BY template_id HAVING COUNT(*) > 1")
            duplicates = cursor.fetchall()
            
            # Validation results
            validation_success = (valid_count / max(1, total_count)) * 100
            
            print(f"[OK] Database validation complete:")
            print(f"     Total templates: {total_count}")
            print(f"     Valid templates: {valid_count}")
            print(f"     Validation rate: {validation_success:.2f}%")
            
            if duplicates:
                print(f"[WARNING] Found {len(duplicates)} duplicate template IDs")
                return False
            
            # Simple validation - just ensure we have reasonable data
            if validation_success < 50:  # Much lower threshold since many aren't files
                print(f"[WARNING] Very low validation success rate: {validation_success:.2f}%")
                return False
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Database validation failed: {e}")
            return False
    
    def _generate_reports(self) -> bool:
        """Generate comprehensive analysis reports"""
        try:
            print("\n--- Step 5: Generating Reports ---")
            
            # Processing statistics report
            self._generate_processing_report()
            
            # Template analysis report
            self._generate_template_analysis_report()
            
            # Database statistics report
            self._generate_database_statistics_report()
            
            # Template lookup examples
            self._generate_lookup_examples_report()
            
            print(f"[OK] Reports generated in {self.reports_dir}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Report generation failed: {e}")
            return False
    
    def _generate_processing_report(self):
        """Generate processing statistics report"""
        report_path = self.reports_dir / "processing_statistics.txt"
        
        with open(report_path, 'w') as f:
            f.write("TemplateManifest Processing Statistics Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            f.write("PROCESSING SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total templates processed: {self.processing_stats['templates_processed']}\n")
            f.write(f"Templates inserted: {self.processing_stats['templates_inserted']}\n")
            f.write(f"Processing errors: {self.processing_stats['processing_errors']}\n")
            f.write(f"Validation errors: {self.processing_stats['validation_errors']}\n")
            f.write(f"Processing time: {self.processing_stats['duration']:.3f} seconds\n")
            
            success_rate = (self.processing_stats['templates_inserted'] / 
                          max(1, self.processing_stats['templates_processed'])) * 100
            f.write(f"Success rate: {success_rate:.2f}%\n")
    
    def _generate_template_analysis_report(self):
        """Generate template analysis report"""
        report_path = self.reports_dir / "template_analysis.txt"
        
        cursor = self.database_schema.connection.cursor()
        
        with open(report_path, 'w') as f:
            f.write("TemplateManifest Template Analysis Report\n")
            f.write("=" * 45 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            # Deck type distribution
            f.write("DECK TYPE DISTRIBUTION\n")
            f.write("-" * 25 + "\n")
            cursor.execute("SELECT * FROM deck_type_summary")
            for row in cursor.fetchall():
                f.write(f"{row[0]}: {row[1]} templates ({row[3]:.1f}% valid)\n")
            
            f.write("\nDECK CATEGORY DISTRIBUTION\n")
            f.write("-" * 30 + "\n")
            cursor.execute("SELECT * FROM deck_category_summary LIMIT 20")
            for row in cursor.fetchall():
                f.write(f"{row[0]}: {row[1]} templates\n")
            
            # Validation summary
            f.write("\nVALIDATION SUMMARY\n")
            f.write("-" * 20 + "\n")
            cursor.execute("SELECT * FROM validation_summary")
            row = cursor.fetchone()
            if row:
                f.write(f"Total templates: {row[0]}\n")
                f.write(f"Valid templates: {row[1]}\n")
                f.write(f"Invalid filenames: {row[2]}\n")
                f.write(f"Invalid IDs: {row[3]}\n")
                f.write(f"Validation success rate: {row[4]:.2f}%\n")
    
    def _generate_database_statistics_report(self):
        """Generate database statistics report"""
        report_path = self.reports_dir / "database_statistics.txt"
        
        cursor = self.database_schema.connection.cursor()
        
        with open(report_path, 'w') as f:
            f.write("TemplateManifest Database Statistics Report\n")
            f.write("=" * 45 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            f.write("DATABASE OVERVIEW\n")
            f.write("-" * 20 + "\n")
            
            # Basic statistics
            cursor.execute("SELECT COUNT(*) FROM template_locations")
            total_templates = cursor.fetchone()[0]
            f.write(f"Total templates: {total_templates}\n")
            
            # Database size
            db_size = self.db_path.stat().st_size / (1024 * 1024)  # MB
            f.write(f"Database size: {db_size:.2f} MB\n")
            
            # Template ID range
            cursor.execute("SELECT MIN(template_id), MAX(template_id) FROM template_locations")
            min_id, max_id = cursor.fetchone()
            f.write(f"Template ID range: {min_id} - {max_id}\n")
            
            # Top deck types
            f.write("\nTOP DECK TYPES\n")
            f.write("-" * 15 + "\n")
            cursor.execute("SELECT deck_type, COUNT(*) FROM template_locations GROUP BY deck_type ORDER BY COUNT(*) DESC LIMIT 10")
            for row in cursor.fetchall():
                f.write(f"{row[0]}: {row[1]}\n")
    
    def _generate_lookup_examples_report(self):
        """Generate template lookup examples"""
        report_path = self.reports_dir / "lookup_examples.txt"
        
        cursor = self.database_schema.connection.cursor()
        
        with open(report_path, 'w') as f:
            f.write("TemplateManifest Lookup Examples Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            f.write("TEMPLATE ID LOOKUP EXAMPLES\n")
            f.write("-" * 30 + "\n")
            f.write("These examples show how to use template IDs from mob m_itemList to find deck filenames.\n\n")
            
            # Sample lookups
            cursor.execute("SELECT template_id, filename, deck_name, deck_type FROM template_lookup ORDER BY RANDOM() LIMIT 20")
            
            f.write("FORMAT: Template ID -> Deck Filename (Deck Name, Type)\n")
            f.write("-" * 60 + "\n")
            
            for row in cursor.fetchall():
                f.write(f"{row[0]} -> {row[1]} ({row[2]}, {row[3]})\n")
            
            f.write("\nUSAGE EXAMPLE:\n")
            f.write("If mob m_itemList contains [211553, 4589, 324086], you can look up:\n")
            f.write("- Template ID 211553 -> Find corresponding deck filename\n")
            f.write("- Load deck data using the filename\n")
            f.write("- Analyze mob's available spells and strategies\n")
    
    def _cleanup(self):
        """Clean up resources"""
        if self.wad_processor:
            self.wad_processor.cleanup()
        
        if self.database_schema:
            self.database_schema.close()
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        stats = dict(self.processing_stats)
        
        if self.wad_processor:
            stats['wad_processor_stats'] = self.wad_processor.get_processing_statistics()
        
        if self.validation_results:
            stats['validation_results'] = self.validation_results
        
        if self.template_manifest:
            stats['template_manifest_stats'] = self.template_manifest.get_statistics()
        
        return stats


def create_template_manifest_database(output_dir: Optional[Path] = None, skip_validation: bool = False) -> bool:
    """
    Create TemplateManifest database with all processing steps
    
    Args:
        output_dir: Output directory for database and reports
        skip_validation: Skip validation for faster processing
        
    Returns:
        True if successful, False otherwise
    """
    creator = TemplateManifestDatabaseCreator(output_dir)
    return creator.create_database(skip_validation)


# Export main classes
__all__ = [
    'TemplateManifestDatabaseCreator',
    'create_template_manifest_database'
]