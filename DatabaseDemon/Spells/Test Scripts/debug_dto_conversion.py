#!/usr/bin/env python3
"""
Debug DTO Conversion
===================
Debug the exact point where DTO conversion fails for spell effects.
"""

import json
import sys
from pathlib import Path

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor
from dtos import FixedSpellDTOFactory


def debug_dto_conversion():
    """Debug DTO conversion step by step"""
    print("Debugging DTO Conversion Process")
    print("=" * 50)
    
    # Initialize WAD processor
    processor = WADProcessor(types_path=Path("../types.json"))
    if not processor.initialize():
        print("Failed to initialize WAD processor")
        return
    
    # Test with known problematic file
    test_file = "Spells/0P Minotaur - MOB.xml"
    print(f"Testing file: {test_file}")
    
    try:
        # Step 1: Get raw spell data
        print("\n1. Getting raw spell data from WAD...")
        success, spell_dict, spell_dto, error_msg = processor.process_single_spell(test_file)
        
        if not success:
            print(f"Failed to process: {error_msg}")
            return
        
        print(f"Raw spell data type: {type(spell_dict)}")
        print(f"Spell DTO type: {type(spell_dto)}")
        
        # Step 2: Examine raw m_effects
        print("\n2. Examining raw m_effects...")
        if "m_effects" in spell_dict:
            raw_effects = spell_dict["m_effects"]
            print(f"Raw m_effects type: {type(raw_effects)}")
            print(f"Raw m_effects length: {len(raw_effects)}")
            
            for i, effect in enumerate(raw_effects):
                print(f"  Raw Effect {i}: {type(effect)} - {effect.get('$__type', 'NO TYPE')}")
        
        # Step 3: Examine DTO m_effects
        print("\n3. Examining DTO m_effects...")
        if hasattr(spell_dto, "m_effects"):
            dto_effects = spell_dto.m_effects
            print(f"DTO m_effects type: {type(dto_effects)}")
            print(f"DTO m_effects length: {len(dto_effects) if dto_effects else 0}")
            
            if dto_effects:
                for i, effect in enumerate(dto_effects):
                    print(f"  DTO Effect {i}: {type(effect)}")
                    
                    # Check if it's actually a dict
                    if isinstance(effect, dict):
                        print(f"    WARNING: DTO effect is still a dict!")
                        print(f"    Dict keys: {list(effect.keys())[:5]}...")
                        print(f"    $__type: {effect.get('$__type', 'MISSING')}")
                    else:
                        print(f"    DTO attributes: {list(effect.__dict__.keys())[:5] if hasattr(effect, '__dict__') else 'N/A'}...")
        
        # Step 4: Test DTO factory directly on effects
        print("\n4. Testing DTO factory directly on effects...")
        if "m_effects" in spell_dict:
            for i, raw_effect in enumerate(spell_dict["m_effects"]):
                print(f"\n  Testing raw effect {i}:")
                print(f"    Type: {type(raw_effect)}")
                print(f"    $__type: {raw_effect.get('$__type', 'MISSING')}")
                
                # Try to create DTO directly
                effect_dto = FixedSpellDTOFactory.create_from_json_data(raw_effect)
                if effect_dto:
                    print(f"    Factory result: {type(effect_dto).__name__}")
                else:
                    print(f"    Factory FAILED to create DTO")
        
        # Step 5: Test complete spell DTO creation
        print("\n5. Testing complete spell DTO creation...")
        spell_dto_direct = FixedSpellDTOFactory.create_from_json_data(spell_dict)
        
        if spell_dto_direct:
            print(f"Direct DTO creation: {type(spell_dto_direct).__name__}")
            
            if hasattr(spell_dto_direct, "m_effects"):
                direct_effects = spell_dto_direct.m_effects
                print(f"Direct DTO m_effects: {len(direct_effects) if direct_effects else 0}")
                
                if direct_effects:
                    for i, effect in enumerate(direct_effects):
                        print(f"  Direct Effect {i}: {type(effect)}")
                        if isinstance(effect, dict):
                            print(f"    PROBLEM: Still a dict!")
        else:
            print("Direct DTO creation FAILED")
        
        # Step 6: Compare WAD processor vs direct factory
        print("\n6. Comparing WAD processor vs direct factory...")
        
        if hasattr(spell_dto, "m_effects") and hasattr(spell_dto_direct, "m_effects"):
            wad_effects = spell_dto.m_effects
            direct_effects = spell_dto_direct.m_effects
            
            print(f"WAD processor effects: {len(wad_effects) if wad_effects else 0}")
            print(f"Direct factory effects: {len(direct_effects) if direct_effects else 0}")
            
            if wad_effects and direct_effects:
                for i in range(min(len(wad_effects), len(direct_effects))):
                    wad_type = type(wad_effects[i]).__name__
                    direct_type = type(direct_effects[i]).__name__
                    
                    if wad_type != direct_type:
                        print(f"  Effect {i}: WAD={wad_type}, Direct={direct_type} - MISMATCH!")
                    else:
                        print(f"  Effect {i}: Both={wad_type} - OK")
    
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        processor.cleanup()


def debug_factory_process_nested():
    """Debug the process_nested_objects method specifically"""
    print("\n" + "=" * 60)
    print("DEBUGGING FACTORY PROCESS_NESTED_OBJECTS")
    print("=" * 60)
    
    # Load reference data
    reference_file = Path("../../Reference SpellClass Examples/3PFrostDragon_Trainable - T02 - A.json")
    if not reference_file.exists():
        print(f"Reference file not found: {reference_file}")
        return
    
    with open(reference_file, 'r') as f:
        reference_data = json.load(f)
    
    print("Testing process_nested_objects on reference data...")
    
    # Test the process_nested_objects method directly
    processed_data = FixedSpellDTOFactory.process_nested_objects(reference_data)
    
    print(f"Original m_effects type: {type(reference_data.get('m_effects', []))}")
    print(f"Processed m_effects type: {type(processed_data.get('m_effects', []))}")
    
    original_effects = reference_data.get("m_effects", [])
    processed_effects = processed_data.get("m_effects", [])
    
    print(f"Original effects count: {len(original_effects)}")
    print(f"Processed effects count: {len(processed_effects)}")
    
    for i in range(min(len(original_effects), len(processed_effects))):
        orig = original_effects[i]
        proc = processed_effects[i]
        
        print(f"\nEffect {i}:")
        print(f"  Original: {type(orig)} - {orig.get('$__type', 'NO TYPE')}")
        print(f"  Processed: {type(proc)}")
        
        if isinstance(proc, dict):
            print(f"    PROBLEM: Processed effect is still a dict!")
            print(f"    Keys: {list(proc.keys())[:5]}...")
        else:
            print(f"    OK: Converted to {type(proc).__name__}")
            
            # Check for RandomSpellEffect
            if hasattr(proc, "m_effectList"):
                effect_list = proc.m_effectList
                print(f"    RandomSpellEffect with {len(effect_list) if effect_list else 0} sub-effects")


def main():
    """Main debug function"""
    debug_dto_conversion()
    debug_factory_process_nested()


if __name__ == "__main__":
    main()