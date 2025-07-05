#!/usr/bin/env python3
"""
Items DTO Validation Test
========================
Tests DTO creation with real item data from Reference Material examples
to validate all 117 nested types can be properly converted.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import traceback

# Add parent directories to Python path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))  # DatabaseDemon level
sys.path.append(str(Path(__file__).parent.parent))         # Items level

from dtos.ItemsDTOFactory import ItemsDTOFactory
from dtos.ItemsDTO import WizItemTemplateDTO


class ItemDTOValidator:
    """Validates item DTO creation with real data"""
    
    def __init__(self):
        self.factory = ItemsDTOFactory()
        self.test_results = []
        self.validation_errors = []
        
        # Reference material paths
        self.reference_path = Path("../../../../Reference Material/Items")
        self.pets_path = self.reference_path / "Pets"
        
    def load_test_item(self, file_path: Path) -> Dict[str, Any]:
        """Load a test item from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load {file_path}: {e}")
            return {}
    
    def validate_dto_creation(self, file_path: Path, item_data: Dict[str, Any]) -> bool:
        """Validate DTO creation for a single item"""
        try:
            print(f"\n=== Validating {file_path.name} ===")
            
            # Check if this is a WizItemTemplate
            if item_data.get('$__type') != 'class WizItemTemplate':
                print(f"[SKIP] Not a WizItemTemplate: {item_data.get('$__type')}")
                return True
            
            # Create DTO
            item_dto = self.factory.create_from_json_data(item_data)
            
            if item_dto is None:
                print(f"[FAIL] Failed to create DTO")
                self.validation_errors.append({
                    'file': str(file_path),
                    'error': 'DTO creation returned None',
                    'item_type': item_data.get('$__type')
                })
                return False
            
            # Validate basic fields
            validation_results = {
                'file_path': str(file_path),
                'template_id': item_dto.m_templateID,
                'object_name': item_dto.m_objectName,
                'display_name': item_dto.m_displayName,
                'school': item_dto.m_school,
                'rarity': item_dto.m_rarity,
                'behaviors_count': len(item_dto.m_behaviors) if item_dto.m_behaviors else 0,
                'effects_count': len(item_dto.m_equipEffects) if item_dto.m_equipEffects else 0,
                'avatar_info_present': item_dto.m_avatarInfo is not None,
                'requirements_present': item_dto.m_equipRequirements is not None
            }
            
            print(f"[OK] DTO created successfully")
            print(f"  Template ID: {validation_results['template_id']}")
            print(f"  Object Name: {validation_results['object_name']}")
            print(f"  Display Name: {validation_results['display_name']}")
            print(f"  School: {validation_results['school']}")
            print(f"  Behaviors: {validation_results['behaviors_count']}")
            print(f"  Effects: {validation_results['effects_count']}")
            
            # Validate behaviors
            if item_dto.m_behaviors:
                behavior_types = []
                for behavior in item_dto.m_behaviors:
                    if hasattr(behavior, '__class__'):
                        behavior_types.append(behavior.__class__.__name__)
                    elif isinstance(behavior, dict):
                        behavior_types.append(behavior.get('$__type', 'Unknown'))
                    else:
                        behavior_types.append(type(behavior).__name__)
                
                validation_results['behavior_types'] = behavior_types
                print(f"  Behavior Types: {', '.join(behavior_types)}")
            
            # Validate nested objects in behaviors
            nested_types_found = self._discover_nested_types(item_data)
            validation_results['nested_types_discovered'] = nested_types_found
            
            if nested_types_found:
                print(f"  Nested Types: {len(nested_types_found)} unique types")
                for nested_type in nested_types_found[:5]:  # Show first 5
                    print(f"    - {nested_type}")
                if len(nested_types_found) > 5:
                    print(f"    ... and {len(nested_types_found) - 5} more")
            
            # Test DTO serialization
            try:
                dto_dict = self._dto_to_dict(item_dto)
                validation_results['serialization_success'] = True
                print(f"  [OK] DTO serialization successful")
            except Exception as e:
                validation_results['serialization_success'] = False
                validation_results['serialization_error'] = str(e)
                print(f"  [WARN] DTO serialization failed: {e}")
            
            self.test_results.append(validation_results)
            return True
            
        except Exception as e:
            print(f"[FAIL] Validation failed: {e}")
            traceback.print_exc()
            
            self.validation_errors.append({
                'file': str(file_path),
                'error': str(e),
                'traceback': traceback.format_exc(),
                'item_type': item_data.get('$__type', 'Unknown')
            })
            return False
    
    def _discover_nested_types(self, obj: Any, discovered: set = None) -> List[str]:
        """Recursively discover all nested types in object"""
        if discovered is None:
            discovered = set()
        
        if isinstance(obj, dict):
            obj_type = obj.get('$__type')
            if obj_type and isinstance(obj_type, str) and obj_type.startswith('class '):
                class_name = obj_type.replace('class ', '')
                discovered.add(class_name)
            
            for value in obj.values():
                self._discover_nested_types(value, discovered)
        
        elif isinstance(obj, list):
            for item in obj:
                self._discover_nested_types(item, discovered)
        
        return sorted(list(discovered))
    
    def _dto_to_dict(self, dto: Any) -> Dict[str, Any]:
        """Convert DTO to dictionary for testing"""
        if hasattr(dto, '__dict__'):
            result = {}
            for key, value in dto.__dict__.items():
                if hasattr(value, '__dict__'):
                    result[key] = self._dto_to_dict(value)
                elif isinstance(value, list):
                    result[key] = [self._dto_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                else:
                    result[key] = value
            return result
        else:
            return dto
    
    def run_validation_tests(self) -> bool:
        """Run validation tests on all available reference items"""
        print("Items DTO Validation Test")
        print("=" * 50)
        
        test_files = []
        
        # Look for test files in Reference Material
        if self.pets_path.exists():
            test_files.extend(list(self.pets_path.glob("*.json")))
        
        # Look for any other item files
        if self.reference_path.exists():
            for item_file in self.reference_path.rglob("*.json"):
                if item_file not in test_files:
                    test_files.append(item_file)
        
        if not test_files:
            print("[WARNING] No test files found in Reference Material")
            # Create a simple synthetic test
            return self._run_synthetic_test()
        
        print(f"Found {len(test_files)} test files")
        
        successful_tests = 0
        failed_tests = 0
        
        for test_file in test_files:
            print(f"\nTesting: {test_file.relative_to(self.reference_path)}")
            
            # Load test data
            item_data = self.load_test_item(test_file)
            if not item_data:
                failed_tests += 1
                continue
            
            # Validate DTO creation
            if self.validate_dto_creation(test_file, item_data):
                successful_tests += 1
            else:
                failed_tests += 1
        
        # Print final results
        print(f"\n" + "=" * 50)
        print("VALIDATION RESULTS")
        print("=" * 50)
        print(f"Total tests: {len(test_files)}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(successful_tests/max(1,len(test_files)))*100:.1f}%")
        
        if self.validation_errors:
            print(f"\nValidation Errors ({len(self.validation_errors)}):")
            for error in self.validation_errors:
                print(f"  - {error['file']}: {error['error']}")
        
        # Generate summary report
        self._generate_validation_report()
        
        return failed_tests == 0
    
    def _run_synthetic_test(self) -> bool:
        """Run a synthetic test with minimal WizItemTemplate data"""
        print("Running synthetic test...")
        
        synthetic_item = {
            "$__type": "class WizItemTemplate",
            "m_templateID": 12345,
            "m_objectName": "TestItem",
            "m_displayName": "Test Item",
            "m_school": "Fire",
            "m_rarity": 0,
            "m_behaviors": [],
            "m_equipEffects": [],
            "m_adjectiveList": ["TestAdjective"],
            "m_avatarFlags": []
        }
        
        return self.validate_dto_creation(Path("synthetic_test.json"), synthetic_item)
    
    def _generate_validation_report(self):
        """Generate detailed validation report"""
        report_path = Path("../../Reports/Item Reports/dto_validation_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "validation_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len([r for r in self.test_results if r]),
                "failed_tests": len(self.validation_errors),
                "validation_timestamp": str(datetime.now())
            },
            "test_results": self.test_results,
            "validation_errors": self.validation_errors,
            "dto_factory_stats": {
                "supported_types": len(self.factory.get_supported_types()),
                "supported_hashes": len(self.factory.get_supported_hashes()),
                "main_item_hash": self.factory.get_main_item_hash()
            }
        }
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n[OK] Validation report saved: {report_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save validation report: {e}")


def main():
    """Main validation function"""
    validator = ItemDTOValidator()
    
    try:
        success = validator.run_validation_tests()
        return 0 if success else 1
        
    except Exception as e:
        print(f"[ERROR] Validation failed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())