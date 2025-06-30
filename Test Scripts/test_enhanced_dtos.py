#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Wizard101 Spell DTOs
=========================================================
Tests the enhanced DTOs against all 7 reference examples to validate:
- Proper inheritance handling
- Nested object creation (SpellEffect, RequirementList, etc.)
- Polymorphic factory functionality
- Deep nesting support (RandomSpellEffect with effect lists)
- Type safety and data integrity

This test ensures the DTOs are ready for combat simulation.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our enhanced DTOs
try:
    import enhanced_wizard101_spell_dtos as dtos
    print("[OK] Successfully imported enhanced DTOs")
except ImportError as e:
    print(f"[FAIL] Failed to import enhanced DTOs: {e}")
    sys.exit(1)


class EnhancedDTOValidator:
    """Comprehensive validator for enhanced DTOs"""
    
    def __init__(self, reference_examples_dir: str):
        self.reference_examples_dir = Path(reference_examples_dir)
        self.factory = dtos.EnhancedSpellDTOFactory
        
        # Test results
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.overall_success = True
        
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("=" * 60)
        print("COMPREHENSIVE ENHANCED DTO VALIDATION")
        print("=" * 60)
        
        # Test 1: Factory functionality
        self.test_factory_basics()
        
        # Test 2: All reference examples
        self.test_all_reference_examples()
        
        # Test 3: Nested object handling
        self.test_nested_object_creation()
        
        # Test 4: Inheritance validation
        self.test_inheritance_handling()
        
        # Test 5: Deep nesting (RandomSpellEffect)
        self.test_deep_nesting()
        
        # Test 6: Polymorphic relationships
        self.test_polymorphic_relationships()
        
        # Generate final report
        self.generate_final_report()
    
    def test_factory_basics(self):
        """Test basic factory functionality"""
        print("\n--- Test 1: Factory Basics ---")
        
        test_name = "factory_basics"
        self.test_results[test_name] = {"success": True, "details": []}
        
        try:
            # Test supported hashes
            supported_hashes = self.factory.get_supported_hashes()
            expected_count = 14  # We should have 14 types
            
            if len(supported_hashes) == expected_count:
                self.test_results[test_name]["details"].append(f"[OK] Factory supports {len(supported_hashes)} types")
            else:
                self.test_results[test_name]["details"].append(f"✗ Expected {expected_count} types, got {len(supported_hashes)}")
                self.test_results[test_name]["success"] = False
            
            # Test polymorphic mappings
            polymorphic_types = self.factory.get_polymorphic_types()
            if "SpellTemplateDTO" in polymorphic_types and "SpellEffectDTO" in polymorphic_types:
                self.test_results[test_name]["details"].append("✓ Polymorphic mappings available")
            else:
                self.test_results[test_name]["details"].append("✗ Missing polymorphic mappings")
                self.test_results[test_name]["success"] = False
                
        except Exception as e:
            self.test_results[test_name]["success"] = False
            self.test_results[test_name]["details"].append(f"✗ Factory test failed: {e}")
    
    def test_all_reference_examples(self):
        """Test creating DTOs from all reference examples"""
        print("\n--- Test 2: All Reference Examples ---")
        
        reference_files = list(self.reference_examples_dir.glob("*.json"))
        
        for ref_file in reference_files:
            test_name = f"reference_{ref_file.stem}"
            self.test_results[test_name] = {"success": True, "details": []}
            
            try:
                # Load the reference file
                with open(ref_file, 'r', encoding='utf-8') as f:
                    spell_data = json.load(f)
                
                # Create DTO from the data
                spell_dto = self.factory.create_from_json_data(spell_data)
                
                if spell_dto:
                    self.test_results[test_name]["details"].append(f"✓ Created DTO for {ref_file.name}")
                    
                    # Validate the DTO has expected properties
                    if hasattr(spell_dto, 'm_name') and hasattr(spell_dto, 'm_spellRank'):
                        self.test_results[test_name]["details"].append(f"✓ DTO has core properties")
                    else:
                        self.test_results[test_name]["details"].append(f"✗ DTO missing core properties")
                        self.test_results[test_name]["success"] = False
                    
                    # Check specific properties based on spell type
                    self.validate_spell_specific_properties(spell_dto, spell_data, test_name)
                    
                else:
                    self.test_results[test_name]["success"] = False
                    self.test_results[test_name]["details"].append(f"✗ Failed to create DTO for {ref_file.name}")
                    
            except Exception as e:
                self.test_results[test_name]["success"] = False
                self.test_results[test_name]["details"].append(f"✗ Error testing {ref_file.name}: {e}")
    
    def validate_spell_specific_properties(self, spell_dto: Any, spell_data: Dict[str, Any], test_name: str):
        """Validate spell-specific properties"""
        spell_type = spell_data.get("$__type", "").replace("class ", "")
        
        if "TieredSpellTemplate" in spell_type:
            # Should have m_nextTierSpells and m_requirements
            if hasattr(spell_dto, 'm_nextTierSpells') and hasattr(spell_dto, 'm_requirements'):
                self.test_results[test_name]["details"].append("✓ TieredSpellTemplate specific properties present")
            else:
                self.test_results[test_name]["details"].append("✗ Missing TieredSpellTemplate properties")
                self.test_results[test_name]["success"] = False
        
        elif "CastleMagicSpellTemplate" in spell_type:
            # Should have castle magic specific properties
            if hasattr(spell_dto, 'm_castleMagicSpellType') and hasattr(spell_dto, 'm_effectSchool'):
                self.test_results[test_name]["details"].append("✓ CastleMagicSpellTemplate specific properties present")
            else:
                self.test_results[test_name]["details"].append("✗ Missing CastleMagicSpellTemplate properties")
                self.test_results[test_name]["success"] = False
        
        elif "GardenSpellTemplate" in spell_type:
            # Should have gardening specific properties
            if hasattr(spell_dto, 'm_gardenSpellType') and hasattr(spell_dto, 'm_energyCost'):
                self.test_results[test_name]["details"].append("✓ GardenSpellTemplate specific properties present")
            else:
                self.test_results[test_name]["details"].append("✗ Missing GardenSpellTemplate properties")
                self.test_results[test_name]["success"] = False
        
        elif "CantripsSpellTemplate" in spell_type:
            # Should have cantrips specific properties
            if hasattr(spell_dto, 'm_cantripsSpellType') and hasattr(spell_dto, 'm_cooldownSeconds'):
                self.test_results[test_name]["details"].append("✓ CantripsSpellTemplate specific properties present")
            else:
                self.test_results[test_name]["details"].append("✗ Missing CantripsSpellTemplate properties")
                self.test_results[test_name]["success"] = False
    
    def test_nested_object_creation(self):
        """Test creation of nested objects like SpellRank, SpellEffect"""
        print("\n--- Test 3: Nested Object Creation ---")
        
        test_name = "nested_objects"
        self.test_results[test_name] = {"success": True, "details": []}
        
        try:
            # Test with the Minotaur spell (has SpellEffect objects)
            minotaur_file = self.reference_examples_dir / "0P Minotaur - MOB.json"
            with open(minotaur_file, 'r', encoding='utf-8') as f:
                spell_data = json.load(f)
            
            spell_dto = self.factory.create_from_json_data(spell_data)
            
            if spell_dto:
                # Check SpellRank object
                if hasattr(spell_dto, 'm_spellRank') and isinstance(spell_dto.m_spellRank, dtos.SpellRankDTO):
                    self.test_results[test_name]["details"].append("✓ SpellRank DTO created correctly")
                else:
                    self.test_results[test_name]["details"].append("✗ SpellRank DTO not created properly")
                    self.test_results[test_name]["success"] = False
                
                # Check SpellEffect objects in effects list
                if hasattr(spell_dto, 'm_effects') and spell_dto.m_effects:
                    effect = spell_dto.m_effects[0]
                    if isinstance(effect, dtos.SpellEffectDTO):
                        self.test_results[test_name]["details"].append("✓ SpellEffect DTO created correctly")
                    else:
                        self.test_results[test_name]["details"].append("✗ SpellEffect DTO not created properly")
                        self.test_results[test_name]["success"] = False
                else:
                    self.test_results[test_name]["details"].append("✗ No effects found in spell")
                    self.test_results[test_name]["success"] = False
            else:
                self.test_results[test_name]["success"] = False
                self.test_results[test_name]["details"].append("✗ Failed to create main spell DTO")
                
        except Exception as e:
            self.test_results[test_name]["success"] = False
            self.test_results[test_name]["details"].append(f"✗ Error testing nested objects: {e}")
    
    def test_inheritance_handling(self):
        """Test proper inheritance handling"""
        print("\n--- Test 4: Inheritance Handling ---")
        
        test_name = "inheritance"
        self.test_results[test_name] = {"success": True, "details": []}
        
        try:
            # Test TieredSpellTemplate inheritance from SpellTemplate
            tiered_file = self.reference_examples_dir / "3PFrostDragon_Trainable - T02 - A.json"
            with open(tiered_file, 'r', encoding='utf-8') as f:
                spell_data = json.load(f)
            
            spell_dto = self.factory.create_from_json_data(spell_data)
            
            if spell_dto:
                # Should be instance of TieredSpellTemplateDTO
                if isinstance(spell_dto, dtos.TieredSpellTemplateDTO):
                    self.test_results[test_name]["details"].append("✓ TieredSpellTemplateDTO created correctly")
                else:
                    self.test_results[test_name]["details"].append("✗ Wrong DTO type created")
                    self.test_results[test_name]["success"] = False
                
                # Should also be instance of base SpellTemplateDTO (inheritance)
                if isinstance(spell_dto, dtos.SpellTemplateDTO):
                    self.test_results[test_name]["details"].append("✓ Inheritance from SpellTemplateDTO works")
                else:
                    self.test_results[test_name]["details"].append("✗ Inheritance not working properly")
                    self.test_results[test_name]["success"] = False
                
                # Should have both base and derived properties
                if hasattr(spell_dto, 'm_name') and hasattr(spell_dto, 'm_nextTierSpells'):
                    self.test_results[test_name]["details"].append("✓ Both base and derived properties present")
                else:
                    self.test_results[test_name]["details"].append("✗ Missing base or derived properties")
                    self.test_results[test_name]["success"] = False
            else:
                self.test_results[test_name]["success"] = False
                self.test_results[test_name]["details"].append("✗ Failed to create tiered spell DTO")
                
        except Exception as e:
            self.test_results[test_name]["success"] = False
            self.test_results[test_name]["details"].append(f"✗ Error testing inheritance: {e}")
    
    def test_deep_nesting(self):
        """Test deep nesting with RandomSpellEffect"""
        print("\n--- Test 5: Deep Nesting (RandomSpellEffect) ---")
        
        test_name = "deep_nesting"
        self.test_results[test_name] = {"success": True, "details": []}
        
        try:
            # Test with FrostDragon which has RandomSpellEffect with effect list
            dragon_file = self.reference_examples_dir / "3PFrostDragon_Trainable - T02 - A.json"
            with open(dragon_file, 'r', encoding='utf-8') as f:
                spell_data = json.load(f)
            
            spell_dto = self.factory.create_from_json_data(spell_data)
            
            if spell_dto and spell_dto.m_effects:
                # Find the RandomSpellEffect
                random_effect = None
                for effect in spell_dto.m_effects:
                    if isinstance(effect, dtos.RandomSpellEffectDTO):
                        random_effect = effect
                        break
                
                if random_effect:
                    self.test_results[test_name]["details"].append("✓ RandomSpellEffect DTO found")
                    
                    # Check if it has the effect list
                    if hasattr(random_effect, 'm_effectList') and random_effect.m_effectList:
                        self.test_results[test_name]["details"].append("✓ RandomSpellEffect has effect list")
                        
                        # Check if effect list contains SpellEffect DTOs
                        first_nested_effect = random_effect.m_effectList[0]
                        if isinstance(first_nested_effect, dtos.SpellEffectDTO):
                            self.test_results[test_name]["details"].append("✓ Nested SpellEffect DTOs created correctly")
                        else:
                            self.test_results[test_name]["details"].append("✗ Nested effects not converted to DTOs")
                            self.test_results[test_name]["success"] = False
                    else:
                        self.test_results[test_name]["details"].append("✗ RandomSpellEffect missing effect list")
                        self.test_results[test_name]["success"] = False
                else:
                    self.test_results[test_name]["details"].append("✗ RandomSpellEffect not found")
                    self.test_results[test_name]["success"] = False
            else:
                self.test_results[test_name]["success"] = False
                self.test_results[test_name]["details"].append("✗ Failed to create spell DTO or no effects")
                
        except Exception as e:
            self.test_results[test_name]["success"] = False
            self.test_results[test_name]["details"].append(f"✗ Error testing deep nesting: {e}")
    
    def test_polymorphic_relationships(self):
        """Test polymorphic relationships and Union types"""
        print("\n--- Test 6: Polymorphic Relationships ---")
        
        test_name = "polymorphic"
        self.test_results[test_name] = {"success": True, "details": []}
        
        try:
            # Test different spell template types
            spell_types = [
                ("0P Minotaur - MOB.json", dtos.SpellTemplateDTO),
                ("3PFrostDragon_Trainable - T02 - A.json", dtos.TieredSpellTemplateDTO),
                ("AbominableWeaver.json", dtos.CastleMagicSpellTemplateDTO),
                ("Ant Lion TC FG.json", dtos.GardenSpellTemplateDTO),
                ("BanishSentinels1.json", dtos.FishingSpellTemplateDTO),
                ("CantripAirSomersault.json", dtos.CantripsSpellTemplateDTO),
                ("WhirlyBurlyF.json", dtos.WhirlyBurlySpellTemplateDTO)
            ]
            
            for filename, expected_type in spell_types:
                file_path = self.reference_examples_dir / filename
                with open(file_path, 'r', encoding='utf-8') as f:
                    spell_data = json.load(f)
                
                spell_dto = self.factory.create_from_json_data(spell_data)
                
                if spell_dto and isinstance(spell_dto, expected_type):
                    self.test_results[test_name]["details"].append(f"✓ {filename} -> {expected_type.__name__}")
                else:
                    self.test_results[test_name]["details"].append(f"✗ {filename} -> Wrong type")
                    self.test_results[test_name]["success"] = False
            
        except Exception as e:
            self.test_results[test_name]["success"] = False
            self.test_results[test_name]["details"].append(f"✗ Error testing polymorphic relationships: {e}")
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "=" * 60)
        print("FINAL VALIDATION REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
        
        # Print detailed results
        for test_name, result in self.test_results.items():
            status = "PASS" if result["success"] else "FAIL"
            print(f"\n{test_name.upper()}: {status}")
            for detail in result["details"]:
                print(f"  {detail}")
        
        # Final verdict
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! Enhanced DTOs are ready for combat simulation.")
            self.overall_success = True
        else:
            print(f"\n❌ {total_tests - passed_tests} test(s) failed. DTOs need fixes before use.")
            self.overall_success = False
        
        return self.overall_success


def main():
    """Main test function"""
    reference_examples_dir = "../Reference SpellClass Examples"
    
    if not Path(reference_examples_dir).exists():
        print(f"Error: Reference examples directory not found: {reference_examples_dir}")
        return 1
    
    # Run comprehensive validation
    validator = EnhancedDTOValidator(reference_examples_dir)
    success = validator.run_comprehensive_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())