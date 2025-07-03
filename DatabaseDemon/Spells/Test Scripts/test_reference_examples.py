#!/usr/bin/env python3
"""
Test Reference Examples
=======================
Validates current DTO processing against all reference spell examples.
Compares database output with expected JSON structure.
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor
from dtos import FixedSpellDTOFactory


class ReferenceExampleTester:
    """Tests reference examples against current DTO processing"""
    
    def __init__(self):
        self.reference_dir = Path("../Reference SpellClass Examples")
        self.db_path = Path("../database/r777820.Wizard_1_580_0_Live_spells - Backup.db")
        self.processor = None
        self.test_results = []
    
    def initialize(self):
        """Initialize WAD processor"""
        self.processor = WADProcessor()
        return self.processor.initialize()
    
    def get_reference_examples(self) -> List[Tuple[str, Dict[str, Any]]]:
        """Load all reference examples"""
        examples = []
        
        if not self.reference_dir.exists():
            print(f"Reference directory not found: {self.reference_dir}")
            return examples
        
        json_files = list(self.reference_dir.glob("*.json"))
        print(f"Found {len(json_files)} reference examples")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    examples.append((json_file.stem, data))
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        return examples
    
    def find_matching_wad_file(self, spell_name: str) -> str:
        """Find matching WAD file for a reference example"""
        # Reference examples use the spell name, need to find matching WAD file
        possible_paths = [
            f"Spells/{spell_name}.xml",
            f"Spells/{spell_name} - MOB.xml",
            f"Spells/{spell_name} - Amulet.xml"
        ]
        
        # Get all spell files from WAD to find exact match
        if self.processor:
            all_files = self.processor.get_all_spell_files()
            for file_path in all_files:
                if spell_name in file_path:
                    return file_path
        
        return f"Spells/{spell_name}.xml"  # Default guess
    
    def test_reference_example(self, name: str, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single reference example"""
        print(f"\nTesting: {name}")
        print("-" * 50)
        
        result = {
            "name": name,
            "reference_spell_type": reference_data.get("$__type", "Unknown"),
            "success": False,
            "issues": [],
            "effects_analysis": {},
            "dto_analysis": {},
            "database_analysis": {}
        }
        
        try:
            # 1. Test DTO factory on reference data
            print("1. Testing DTO factory on reference data...")
            dto_from_reference = FixedSpellDTOFactory.create_from_json_data(reference_data)
            
            if dto_from_reference:
                result["dto_analysis"]["reference_dto_created"] = True
                result["dto_analysis"]["reference_dto_type"] = type(dto_from_reference).__name__
                print(f"   ✓ Created DTO: {type(dto_from_reference).__name__}")
                
                # Analyze effects in reference DTO
                if hasattr(dto_from_reference, "m_effects"):
                    effects = dto_from_reference.m_effects
                    result["dto_analysis"]["effects_count"] = len(effects) if effects else 0
                    result["dto_analysis"]["effect_types"] = []
                    
                    if effects:
                        for i, effect in enumerate(effects):
                            effect_type = type(effect).__name__
                            result["dto_analysis"]["effect_types"].append(effect_type)
                            print(f"   DTO Effect {i}: {effect_type}")
                            
                            # Check for RandomSpellEffect
                            if hasattr(effect, "m_effectList"):
                                sub_effects = effect.m_effectList
                                sub_count = len(sub_effects) if sub_effects else 0
                                result["dto_analysis"][f"effect_{i}_sub_effects"] = sub_count
                                print(f"     Sub-effects: {sub_count}")
            else:
                result["dto_analysis"]["reference_dto_created"] = False
                result["issues"].append("Failed to create DTO from reference data")
                print("   ✗ Failed to create DTO from reference data")
            
            # 2. Test WAD processing
            print("2. Testing WAD processing...")
            wad_file = self.find_matching_wad_file(name)
            print(f"   WAD file: {wad_file}")
            
            if self.processor:
                success, spell_dict, spell_dto, error_msg = self.processor.process_single_spell(wad_file)
                
                if success and spell_dto:
                    result["dto_analysis"]["wad_dto_created"] = True
                    result["dto_analysis"]["wad_dto_type"] = type(spell_dto).__name__
                    print(f"   ✓ WAD DTO created: {type(spell_dto).__name__}")
                    
                    # Compare spell types
                    ref_type = reference_data.get("$__type", "").replace("class ", "")
                    wad_type = spell_dict.get("$__type", "").replace("class ", "")
                    
                    if ref_type == wad_type:
                        print(f"   ✓ Spell types match: {ref_type}")
                    else:
                        result["issues"].append(f"Spell type mismatch: ref={ref_type}, wad={wad_type}")
                        print(f"   ✗ Spell type mismatch: ref={ref_type}, wad={wad_type}")
                    
                    # Analyze WAD effects
                    if hasattr(spell_dto, "m_effects"):
                        wad_effects = spell_dto.m_effects
                        wad_effects_count = len(wad_effects) if wad_effects else 0
                        result["effects_analysis"]["wad_effects_count"] = wad_effects_count
                        print(f"   WAD effects count: {wad_effects_count}")
                        
                        if wad_effects:
                            for i, effect in enumerate(wad_effects):
                                effect_type = type(effect).__name__
                                print(f"   WAD Effect {i}: {effect_type}")
                                
                                # Check if effect is actually a dict (the problem we're fixing)
                                if isinstance(effect, dict):
                                    result["issues"].append(f"WAD Effect {i} is dict, not DTO")
                                    print(f"     ✗ Effect is dict, not DTO!")
                else:
                    result["issues"].append(f"WAD processing failed: {error_msg}")
                    print(f"   ✗ WAD processing failed: {error_msg}")
            
            # 3. Check database entries
            print("3. Checking database entries...")
            self.check_database_entries(name, wad_file, result)
            
            # 4. Compare effects in detail
            print("4. Comparing effects in detail...")
            self.compare_effects_detail(reference_data, result)
            
            result["success"] = len(result["issues"]) == 0
            
        except Exception as e:
            result["issues"].append(f"Test failed with exception: {e}")
            print(f"   ✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    def check_database_entries(self, name: str, wad_file: str, result: Dict[str, Any]):
        """Check database entries for this spell"""
        if not self.db_path.exists():
            result["issues"].append("Database not found")
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Check main spell entry
            cursor.execute("SELECT spell_type FROM spell_cards WHERE filename = ?", (wad_file,))
            spell_entry = cursor.fetchone()
            
            if spell_entry:
                result["database_analysis"]["spell_found"] = True
                result["database_analysis"]["db_spell_type"] = spell_entry[0]
                print(f"   ✓ Found in database: {spell_entry[0]}")
            else:
                result["database_analysis"]["spell_found"] = False
                result["issues"].append("Spell not found in database")
                print(f"   ✗ Spell not found in database")
                return
            
            # Check spell effects
            cursor.execute("""
                SELECT effect_order, effect_type, m_effectType, m_sDamageType 
                FROM spell_effects 
                WHERE filename = ? 
                ORDER BY effect_order
            """, (wad_file,))
            
            effects = cursor.fetchall()
            result["database_analysis"]["effects_count"] = len(effects)
            result["database_analysis"]["effect_types"] = []
            
            print(f"   Database effects: {len(effects)}")
            
            dict_effects = 0
            for effect_order, effect_type, m_effectType, m_sDamageType in effects:
                result["database_analysis"]["effect_types"].append(effect_type)
                print(f"   DB Effect {effect_order}: {effect_type}")
                
                if effect_type == "dict":
                    dict_effects += 1
            
            if dict_effects > 0:
                result["issues"].append(f"{dict_effects} effects stored as 'dict'")
                print(f"   ✗ {dict_effects} effects stored as 'dict'")
            
            # Check random spell effects (specifically for 3PFrostDragon_Trainable)
            cursor.execute("SELECT COUNT(*) FROM random_spell_effects WHERE filename = ?", (wad_file,))
            random_effects_count = cursor.fetchone()[0]
            result["database_analysis"]["random_effects_count"] = random_effects_count
            
            if "3PFrostDragon_Trainable" in name:
                expected_random = 5  # From reference JSON
                if random_effects_count == expected_random:
                    print(f"   ✓ Random effects count correct: {random_effects_count}")
                else:
                    result["issues"].append(f"Random effects count wrong: got {random_effects_count}, expected {expected_random}")
                    print(f"   ✗ Random effects count wrong: got {random_effects_count}, expected {expected_random}")
            
        finally:
            conn.close()
    
    def compare_effects_detail(self, reference_data: Dict[str, Any], result: Dict[str, Any]):
        """Compare effects in detail between reference and processed data"""
        if "m_effects" not in reference_data:
            return
        
        ref_effects = reference_data["m_effects"]
        result["effects_analysis"]["reference_effects_count"] = len(ref_effects)
        result["effects_analysis"]["reference_effect_details"] = []
        
        for i, effect in enumerate(ref_effects):
            effect_detail = {
                "order": i,
                "type": effect.get("$__type", "Unknown"),
                "effectType": effect.get("m_effectType"),
                "effectParam": effect.get("m_effectParam"),
                "damageType": effect.get("m_sDamageType")
            }
            
            # Check for RandomSpellEffect
            if "RandomSpellEffect" in effect.get("$__type", ""):
                effect_list = effect.get("m_effectList", [])
                effect_detail["sub_effects_count"] = len(effect_list)
                effect_detail["sub_effects"] = []
                
                for j, sub_effect in enumerate(effect_list):
                    sub_detail = {
                        "order": j,
                        "type": sub_effect.get("$__type", "Unknown"),
                        "effectParam": sub_effect.get("m_effectParam"),
                        "damageType": sub_effect.get("m_sDamageType")
                    }
                    effect_detail["sub_effects"].append(sub_detail)
            
            result["effects_analysis"]["reference_effect_details"].append(effect_detail)
            print(f"   Ref Effect {i}: {effect_detail['type']}")
            
            if "sub_effects_count" in effect_detail:
                print(f"     Sub-effects: {effect_detail['sub_effects_count']}")
    
    def run_all_tests(self):
        """Run tests on all reference examples"""
        print("Testing Reference Examples Against Current DTO Processing")
        print("=" * 60)
        
        if not self.initialize():
            print("Failed to initialize WAD processor")
            return
        
        examples = self.get_reference_examples()
        if not examples:
            print("No reference examples found")
            return
        
        print(f"Testing {len(examples)} reference examples...")
        
        try:
            for name, reference_data in examples:
                result = self.test_reference_example(name, reference_data)
                self.test_results.append(result)
            
            self.generate_summary_report()
            
        finally:
            if self.processor:
                self.processor.cleanup()
    
    def generate_summary_report(self):
        """Generate summary report of all tests"""
        print("\n" + "=" * 60)
        print("REFERENCE EXAMPLES TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        print("\nFailed Tests:")
        for result in self.test_results:
            if not result["success"]:
                print(f"  ✗ {result['name']}: {len(result['issues'])} issues")
                for issue in result["issues"]:
                    print(f"    - {issue}")
        
        print("\nIssue Categories:")
        all_issues = []
        for result in self.test_results:
            all_issues.extend(result["issues"])
        
        # Count issue types
        issue_counts = {}
        for issue in all_issues:
            if "dict" in issue.lower():
                issue_counts["Dict effects"] = issue_counts.get("Dict effects", 0) + 1
            elif "random effects" in issue.lower():
                issue_counts["Random effects"] = issue_counts.get("Random effects", 0) + 1
            elif "dto" in issue.lower():
                issue_counts["DTO creation"] = issue_counts.get("DTO creation", 0) + 1
            else:
                issue_counts["Other"] = issue_counts.get("Other", 0) + 1
        
        for issue_type, count in issue_counts.items():
            print(f"  {issue_type}: {count}")
        
        print("\nKey Findings:")
        dict_issues = sum(1 for r in self.test_results 
                         if any("dict" in issue.lower() for issue in r["issues"]))
        if dict_issues > 0:
            print(f"  - {dict_issues} spells have dict effects (main issue to fix)")
        
        random_issues = sum(1 for r in self.test_results 
                           if any("random" in issue.lower() for issue in r["issues"]))
        if random_issues > 0:
            print(f"  - {random_issues} spells have random effects issues")
        
        print("\nNext Steps:")
        print("1. Fix DTO factory to prevent dict effects")
        print("2. Fix RandomSpellEffect processing")
        print("3. Update database insertion logic")
        print("4. Regenerate database and retest")


def main():
    """Main test function"""
    tester = ReferenceExampleTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()