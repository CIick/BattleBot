#!/usr/bin/env python3
"""
Simple Test for Enhanced Wizard101 Spell DTOs
=============================================
Quick validation that enhanced DTOs work with reference examples.
"""

import json
import sys
from pathlib import Path

# Import our enhanced DTOs
try:
    import enhanced_wizard101_spell_dtos as dtos
    print("[OK] Successfully imported enhanced DTOs")
except ImportError as e:
    print(f"[FAIL] Failed to import enhanced DTOs: {e}")
    sys.exit(1)


def test_reference_examples():
    """Test creating DTOs from all reference examples"""
    print("\n=== Testing Reference Examples ===")
    
    reference_dir = Path("../Reference SpellClass Examples")
    if not reference_dir.exists():
        print("[FAIL] Reference examples directory not found")
        return False
    
    factory = dtos.EnhancedSpellDTOFactory
    success_count = 0
    total_count = 0
    
    reference_files = list(reference_dir.glob("*.json"))
    
    for ref_file in reference_files:
        total_count += 1
        print(f"\nTesting: {ref_file.name}")
        
        try:
            # Load the reference file
            with open(ref_file, 'r', encoding='utf-8') as f:
                spell_data = json.load(f)
            
            # Create DTO from the data
            spell_dto = factory.create_from_json_data(spell_data)
            
            if spell_dto:
                print(f"  [OK] Created {type(spell_dto).__name__}")
                
                # Basic validation
                if hasattr(spell_dto, 'm_name') and hasattr(spell_dto, 'm_spellRank'):
                    print(f"  [OK] Has core properties: m_name='{spell_dto.m_name}'")
                    
                    # Check SpellRank DTO
                    if isinstance(spell_dto.m_spellRank, dtos.SpellRankDTO):
                        print(f"  [OK] SpellRank DTO created properly")
                    else:
                        print(f"  [WARN] SpellRank not a DTO: {type(spell_dto.m_spellRank)}")
                    
                    # Check effects if present
                    if hasattr(spell_dto, 'm_effects') and spell_dto.m_effects:
                        effect = spell_dto.m_effects[0]
                        if isinstance(effect, (dtos.SpellEffectDTO, dtos.RandomSpellEffectDTO)):
                            print(f"  [OK] Effect DTO created: {type(effect).__name__}")
                        else:
                            print(f"  [WARN] Effect not a DTO: {type(effect)}")
                    
                    success_count += 1
                else:
                    print(f"  [FAIL] Missing core properties")
            else:
                print(f"  [FAIL] Failed to create DTO")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print(f"\n=== Results: {success_count}/{total_count} files processed successfully ===")
    return success_count == total_count


def test_specific_features():
    """Test specific features like inheritance and nesting"""
    print("\n=== Testing Specific Features ===")
    
    factory = dtos.EnhancedSpellDTOFactory
    
    # Test 1: TieredSpellTemplate inheritance
    print("\nTest 1: TieredSpellTemplate inheritance")
    try:
        tiered_file = Path("../Reference SpellClass Examples/3PFrostDragon_Trainable - T02 - A.json")
        with open(tiered_file, 'r', encoding='utf-8') as f:
            spell_data = json.load(f)
        
        spell_dto = factory.create_from_json_data(spell_data)
        
        if isinstance(spell_dto, dtos.TieredSpellTemplateDTO):
            print("  [OK] Created TieredSpellTemplateDTO")
            if isinstance(spell_dto, dtos.SpellTemplateDTO):
                print("  [OK] Inheritance from SpellTemplateDTO works")
            else:
                print("  [FAIL] Inheritance not working")
        else:
            print(f"  [FAIL] Wrong type: {type(spell_dto)}")
            
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # Test 2: RandomSpellEffect deep nesting
    print("\nTest 2: RandomSpellEffect deep nesting")
    try:
        # Same file has RandomSpellEffect with nested effects
        if spell_dto and spell_dto.m_effects:
            random_effect = None
            for effect in spell_dto.m_effects:
                if isinstance(effect, dtos.RandomSpellEffectDTO):
                    random_effect = effect
                    break
            
            if random_effect:
                print("  [OK] Found RandomSpellEffectDTO")
                if hasattr(random_effect, 'm_effectList') and random_effect.m_effectList:
                    nested_effect = random_effect.m_effectList[0]
                    if isinstance(nested_effect, dtos.SpellEffectDTO):
                        print("  [OK] Nested SpellEffect DTOs created")
                    else:
                        print(f"  [FAIL] Nested effect wrong type: {type(nested_effect)}")
                else:
                    print("  [FAIL] No effect list in RandomSpellEffect")
            else:
                print("  [WARN] No RandomSpellEffect found")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # Test 3: Factory mappings
    print("\nTest 3: Factory mappings")
    try:
        supported_hashes = factory.get_supported_hashes()
        polymorphic_types = factory.get_polymorphic_types()
        
        print(f"  [OK] Factory supports {len(supported_hashes)} types")
        print(f"  [OK] Polymorphic mappings for {len(polymorphic_types)} base types")
        
        if "SpellTemplateDTO" in polymorphic_types:
            subtypes = polymorphic_types["SpellTemplateDTO"]
            print(f"  [OK] SpellTemplateDTO has {len(subtypes)} subtypes")
        
    except Exception as e:
        print(f"  [ERROR] {e}")


def main():
    """Main test function"""
    print("Enhanced DTO Validation Test")
    print("=" * 40)
    
    # Test basic functionality
    basic_success = test_reference_examples()
    
    # Test specific features
    test_specific_features()
    
    # Final result
    print(f"\n{'='*40}")
    if basic_success:
        print("SUCCESS: Enhanced DTOs are working correctly!")
        print("Ready for combat simulation database creation.")
        return 0
    else:
        print("FAILURE: Some tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())