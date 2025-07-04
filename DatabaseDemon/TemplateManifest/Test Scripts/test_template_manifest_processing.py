#!/usr/bin/env python3
"""
TemplateManifest Processing Validation Script
============================================

Comprehensive validation script for TemplateManifest processing system.
Tests all components from WAD processing to database creation.

This script:
1. Tests type validation and WAD access
2. Tests TemplateManifest processing and DTO conversion
3. Tests database creation and population
4. Validates template ID to filename lookup functionality
5. Tests analysis and reporting capabilities
"""

import json
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import traceback

# Add parent directories to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

# Import test dependencies
try:
    import katsuba
    from katsuba.wad import Archive
    from katsuba.op import LazyObject, LazyList, TypeList, Serializer, SerializerOptions
    print("[OK] Katsuba import successful")
except ImportError as e:
    print(f"[ERROR] Failed to import katsuba: {e}")
    sys.exit(1)

# Import TemplateManifest components
from processors import TemplateManifestWADProcessor, TemplateManifestDatabaseCreator, TemplateManifestDatabaseSchema
from dtos import TemplateManifestDTO, TemplateLocationDTO, TemplateManifestDTOFactory
from dtos.TemplateManifestEnums import TypeHashes, validate_template_id, validate_filename


class TemplateManifestValidationSuite:
    """Comprehensive validation suite for TemplateManifest system"""
    
    def __init__(self):
        """Initialize validation suite"""
        self.test_results = {}
        self.processing_stats = {}
        self.temp_db_path = None
        
        # Get platform-specific paths
        self.wad_path, self.types_path = self._get_platform_paths()
    
    def _get_platform_paths(self):
        """Get platform-specific paths"""
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json")
        else:  # Linux/WSL
            wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
        
        return wad_path, types_path
    
    def run_all_tests(self) -> bool:
        """Run complete validation suite"""
        print("TemplateManifest Processing Validation Suite")
        print("=" * 60)
        print(f"Started: {datetime.now()}")
        print()
        
        tests = [
            ("Prerequisites Check", self.test_prerequisites),
            ("Type System Validation", self.test_type_system),
            ("WAD Processing", self.test_wad_processing),
            ("DTO Conversion", self.test_dto_conversion),
            ("Database Creation", self.test_database_creation),
            ("Template Lookup", self.test_template_lookup),
            ("Analysis Functions", self.test_analysis_functions),
            ("Performance Test", self.test_performance),
            ("Integration Test", self.test_integration)
        ]
        
        overall_success = True
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                start_time = datetime.now()
                result = test_func()
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                self.test_results[test_name] = {
                    'success': result,
                    'duration': duration,
                    'timestamp': start_time
                }
                
                status = "PASS" if result else "FAIL"
                print(f"[{status}] {test_name} ({duration:.3f}s)")
                
                if not result:
                    overall_success = False
                    
            except Exception as e:
                print(f"[ERROR] {test_name} failed with exception: {e}")
                traceback.print_exc()
                self.test_results[test_name] = {
                    'success': False,
                    'error': str(e),
                    'duration': 0
                }
                overall_success = False
        
        # Generate summary report
        self._generate_validation_report()
        
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = "PASS" if result['success'] else "FAIL"
            print(f"{status:>6} | {test_name:<30} | {result['duration']:>8.3f}s")
        
        if overall_success:
            print(f"\n[SUCCESS] All tests passed! TemplateManifest system is working correctly.")
        else:
            print(f"\n[FAILURE] Some tests failed. Please check the errors above.")
        
        # Cleanup
        self._cleanup()
        
        return overall_success
    
    def test_prerequisites(self) -> bool:
        """Test that all prerequisites are met"""
        try:
            # Check WAD file
            if not self.wad_path.exists():
                print(f"[ERROR] Root.wad not found: {self.wad_path}")
                return False
            print(f"[OK] Found Root.wad: {self.wad_path}")
            
            # Check types.json
            if not self.types_path.exists():
                print(f"[ERROR] types.json not found: {self.types_path}")
                return False
            print(f"[OK] Found types.json: {self.types_path}")
            
            # Check types contain required hashes
            with open(self.types_path, 'r') as f:
                types_data = json.load(f)
            
            required_hashes = [str(TypeHashes.TEMPLATE_MANIFEST), str(TypeHashes.TEMPLATE_LOCATION)]
            classes = types_data.get('classes', {})
            
            for hash_str in required_hashes:
                if hash_str not in classes:
                    print(f"[ERROR] Required type hash {hash_str} not found in types.json")
                    return False
            
            print(f"[OK] All required type hashes found")
            return True
            
        except Exception as e:
            print(f"[ERROR] Prerequisites check failed: {e}")
            return False
    
    def test_type_system(self) -> bool:
        """Test type system and katsuba setup"""
        try:
            # Load types
            with open(self.types_path, 'r') as f:
                types_data = json.load(f)
            
            type_list = TypeList(types_data)
            print(f"[OK] Loaded TypeList with {len(types_data.get('classes', {}))} classes")
            
            # Test serializer options
            options = SerializerOptions()
            options.shallow = False
            options.skip_unknown_types = True
            
            serializer = Serializer(options, type_list)
            print("[OK] Created Serializer with recommended options")
            
            # Test DTO factory
            factory = TemplateManifestDTOFactory(type_list)
            print("[OK] Created TemplateManifestDTOFactory")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Type system test failed: {e}")
            return False
    
    def test_wad_processing(self) -> bool:
        """Test WAD file processing"""
        try:
            # Create processor
            processor = TemplateManifestWADProcessor(self.wad_path, self.types_path)
            
            # Initialize processor
            if not processor.initialize():
                print("[ERROR] Failed to initialize WAD processor")
                return False
            print("[OK] WAD processor initialized")
            
            # Process TemplateManifest
            template_manifest = processor.process_template_manifest()
            if not template_manifest:
                print("[ERROR] Failed to process TemplateManifest")
                return False
            
            print(f"[OK] Processed TemplateManifest with {len(template_manifest.m_serializedTemplates)} templates")
            
            # Basic validation
            if len(template_manifest.m_serializedTemplates) == 0:
                print("[ERROR] No templates found in TemplateManifest")
                return False
            
            # Test a few template lookups
            sample_templates = template_manifest.m_serializedTemplates[:5]
            for template in sample_templates:
                if not template.m_filename or template.m_id <= 0:
                    print(f"[ERROR] Invalid template: ID={template.m_id}, filename='{template.m_filename}'")
                    return False
            
            print("[OK] Template data validation passed")
            
            # Store for later tests
            self.processing_stats['template_manifest'] = template_manifest
            self.processing_stats['wad_processor'] = processor
            
            return True
            
        except Exception as e:
            print(f"[ERROR] WAD processing test failed: {e}")
            return False
    
    def test_dto_conversion(self) -> bool:
        """Test DTO conversion functionality"""
        try:
            template_manifest = self.processing_stats.get('template_manifest')
            if not template_manifest:
                print("[ERROR] No template manifest available from previous test")
                return False
            
            # Test template manifest DTO
            if not isinstance(template_manifest, TemplateManifestDTO):
                print(f"[ERROR] Expected TemplateManifestDTO, got {type(template_manifest)}")
                return False
            print("[OK] TemplateManifestDTO validation passed")
            
            # Test template location DTOs
            if not template_manifest.m_serializedTemplates:
                print("[ERROR] No template locations in manifest")
                return False
            
            sample_template = template_manifest.m_serializedTemplates[0]
            if not isinstance(sample_template, TemplateLocationDTO):
                print(f"[ERROR] Expected TemplateLocationDTO, got {type(sample_template)}")
                return False
            print("[OK] TemplateLocationDTO validation passed")
            
            # Test DTO methods
            stats = template_manifest.get_statistics()
            if not isinstance(stats, dict) or 'total_templates' not in stats:
                print("[ERROR] DTO statistics method failed")
                return False
            print(f"[OK] DTO methods working - {stats['total_templates']} templates")
            
            # Test lookup functionality
            if len(template_manifest.m_serializedTemplates) > 0:
                test_id = template_manifest.m_serializedTemplates[0].m_id
                lookup_result = template_manifest.lookup_by_id(test_id)
                if not lookup_result:
                    print(f"[ERROR] Lookup by ID {test_id} failed")
                    return False
                print(f"[OK] Template lookup working - ID {test_id} -> {lookup_result.deck_name}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] DTO conversion test failed: {e}")
            return False
    
    def test_database_creation(self) -> bool:
        """Test database creation and population"""
        try:
            # Create temporary database
            import tempfile
            temp_dir = Path(tempfile.mkdtemp())
            self.temp_db_path = temp_dir / "test_template_manifest.db"
            
            # Create database creator
            creator = TemplateManifestDatabaseCreator(temp_dir)
            
            # Create database
            success = creator.create_database(skip_validation=True)  # Skip validation for speed
            if not success:
                print("[ERROR] Database creation failed")
                return False
            
            print("[OK] Database created successfully")
            
            # Verify database exists and has data
            if not creator.db_path.exists():
                print("[ERROR] Database file not created")
                return False
            
            # Connect and check content
            conn = sqlite3.connect(str(creator.db_path))
            cursor = conn.cursor()
            
            # Check table exists
            cursor.execute("SELECT COUNT(*) FROM template_locations")
            count = cursor.fetchone()[0]
            if count == 0:
                print("[ERROR] No data in template_locations table")
                conn.close()
                return False
            
            print(f"[OK] Database contains {count} template locations")
            
            # Test a lookup query
            cursor.execute("SELECT template_id, filename, deck_name FROM template_locations LIMIT 1")
            row = cursor.fetchone()
            if not row:
                print("[ERROR] No data returned from lookup query")
                conn.close()
                return False
            
            print(f"[OK] Sample lookup: ID {row[0]} -> {row[2]}")
            
            conn.close()
            
            # Store database path for later tests
            self.processing_stats['database_path'] = creator.db_path
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Database creation test failed: {e}")
            return False
    
    def test_template_lookup(self) -> bool:
        """Test template ID to filename lookup functionality"""
        try:
            db_path = self.processing_stats.get('database_path')
            if not db_path or not db_path.exists():
                print("[ERROR] No database available from previous test")
                return False
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Test various lookup scenarios
            test_cases = [
                "SELECT template_id, filename FROM template_locations WHERE is_mob_deck = TRUE LIMIT 5",
                "SELECT template_id, filename FROM template_locations WHERE is_boss_deck = TRUE LIMIT 5",
                "SELECT template_id, filename FROM template_locations WHERE deck_type = 'polymorph' LIMIT 5"
            ]
            
            lookup_count = 0
            for query in test_cases:
                cursor.execute(query)
                results = cursor.fetchall()
                lookup_count += len(results)
                
                for template_id, filename in results:
                    if not filename or template_id <= 0:
                        print(f"[ERROR] Invalid lookup result: ID={template_id}, filename='{filename}'")
                        conn.close()
                        return False
            
            print(f"[OK] Tested {lookup_count} template lookups successfully")
            
            # Test view queries
            cursor.execute("SELECT COUNT(*) FROM template_lookup")
            view_count = cursor.fetchone()[0]
            print(f"[OK] Template lookup view contains {view_count} valid templates")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] Template lookup test failed: {e}")
            return False
    
    def test_analysis_functions(self) -> bool:
        """Test analysis and reporting functions"""
        try:
            template_manifest = self.processing_stats.get('template_manifest')
            if not template_manifest:
                print("[ERROR] No template manifest available")
                return False
            
            # Test statistics
            stats = template_manifest.get_statistics()
            required_stats = ['total_templates', 'template_types', 'template_categories']
            for stat in required_stats:
                if stat not in stats:
                    print(f"[ERROR] Missing statistic: {stat}")
                    return False
            print(f"[OK] Statistics generation working")
            
            # Test template categorization
            mob_templates = template_manifest.get_mob_templates()
            boss_templates = template_manifest.get_boss_templates()
            polymorph_templates = template_manifest.get_polymorph_templates()
            
            total_categorized = len(mob_templates) + len(boss_templates) + len(polymorph_templates)
            print(f"[OK] Categorization: {len(mob_templates)} mob, {len(boss_templates)} boss, {len(polymorph_templates)} polymorph")
            
            # Test validation functionality
            if len(template_manifest.m_serializedTemplates) > 0:
                sample_ids = [t.m_id for t in template_manifest.m_serializedTemplates[:10]]
                validation_result = template_manifest.validate_template_ids(sample_ids)
                
                if validation_result['found_count'] != len(sample_ids):
                    print(f"[ERROR] Validation failed: expected {len(sample_ids)}, found {validation_result['found_count']}")
                    return False
                
                print(f"[OK] Template ID validation working")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Analysis functions test failed: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Test performance with timing"""
        try:
            template_manifest = self.processing_stats.get('template_manifest')
            if not template_manifest:
                print("[ERROR] No template manifest available")
                return False
            
            # Test lookup performance
            import time
            
            # Get sample IDs
            sample_ids = [t.m_id for t in template_manifest.m_serializedTemplates[:1000]]
            
            # Time lookup operations
            start_time = time.time()
            lookup_count = 0
            for template_id in sample_ids:
                result = template_manifest.lookup_by_id(template_id)
                if result:
                    lookup_count += 1
            end_time = time.time()
            
            duration = end_time - start_time
            lookups_per_second = lookup_count / duration if duration > 0 else 0
            
            print(f"[OK] Performance test: {lookup_count} lookups in {duration:.3f}s ({lookups_per_second:.0f} lookups/sec)")
            
            # Performance should be reasonable
            if lookups_per_second < 1000:  # At least 1000 lookups per second
                print(f"[WARNING] Lookup performance may be slow: {lookups_per_second:.0f} lookups/sec")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Performance test failed: {e}")
            return False
    
    def test_integration(self) -> bool:
        """Test end-to-end integration"""
        try:
            # Simulate typical usage: mob item list lookup
            db_path = self.processing_stats.get('database_path')
            template_manifest = self.processing_stats.get('template_manifest')
            
            if not db_path or not template_manifest:
                print("[ERROR] Required components not available")
                return False
            
            # Simulate mob item list
            sample_item_list = [t.m_id for t in template_manifest.m_serializedTemplates[:5]]
            print(f"[INFO] Testing with sample item list: {sample_item_list}")
            
            # Test DTO-based lookup
            deck_filenames = []
            for item_id in sample_item_list:
                filename = template_manifest.get_deck_filename(item_id)
                if filename:
                    deck_filenames.append(filename)
                else:
                    print(f"[ERROR] Failed to find filename for item ID {item_id}")
                    return False
            
            print(f"[OK] DTO lookup found {len(deck_filenames)} deck filenames")
            
            # Test database-based lookup
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            db_filenames = []
            for item_id in sample_item_list:
                cursor.execute("SELECT filename FROM template_locations WHERE template_id = ?", (item_id,))
                result = cursor.fetchone()
                if result:
                    db_filenames.append(result[0])
                else:
                    print(f"[ERROR] Database lookup failed for item ID {item_id}")
                    conn.close()
                    return False
            
            conn.close()
            print(f"[OK] Database lookup found {len(db_filenames)} deck filenames")
            
            # Verify consistency
            if deck_filenames != db_filenames:
                print("[ERROR] DTO and database lookups returned different results")
                return False
            
            print("[OK] DTO and database lookups are consistent")
            
            # Test complete workflow
            print("[OK] Integration test: Complete workflow working correctly")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Integration test failed: {e}")
            return False
    
    def _generate_validation_report(self):
        """Generate validation report"""
        try:
            report_dir = Path("Reports") / "TemplateManifest Reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_path = report_dir / "validation_report.txt"
            
            with open(report_path, 'w') as f:
                f.write("TemplateManifest Validation Report\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                
                f.write("TEST RESULTS\n")
                f.write("-" * 15 + "\n")
                
                for test_name, result in self.test_results.items():
                    status = "PASS" if result['success'] else "FAIL"
                    f.write(f"{status:>6} | {test_name:<30} | {result['duration']:>8.3f}s\n")
                
                # Add processing statistics if available
                if self.processing_stats:
                    f.write("\nPROCESSING STATISTICS\n")
                    f.write("-" * 25 + "\n")
                    
                    template_manifest = self.processing_stats.get('template_manifest')
                    if template_manifest:
                        stats = template_manifest.get_statistics()
                        f.write(f"Total templates: {stats['total_templates']}\n")
                        f.write(f"Template types: {len(stats['template_types'])}\n")
                        f.write(f"Template categories: {len(stats['template_categories'])}\n")
            
            print(f"[OK] Validation report saved: {report_path}")
            
        except Exception as e:
            print(f"[WARNING] Failed to generate validation report: {e}")
    
    def _cleanup(self):
        """Clean up test resources"""
        try:
            # Clean up WAD processor
            wad_processor = self.processing_stats.get('wad_processor')
            if wad_processor:
                wad_processor.cleanup()
            
            # Clean up temp database
            if self.temp_db_path and self.temp_db_path.exists():
                self.temp_db_path.unlink()
                parent_dir = self.temp_db_path.parent
                if parent_dir.exists():
                    parent_dir.rmdir()
            
        except Exception as e:
            print(f"[WARNING] Cleanup failed: {e}")


def main():
    """Run validation suite"""
    try:
        suite = TemplateManifestValidationSuite()
        success = suite.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n[INFO] Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"[ERROR] Validation suite failed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())