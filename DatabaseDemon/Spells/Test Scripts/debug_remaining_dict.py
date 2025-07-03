#!/usr/bin/env python3
"""
Debug Remaining Dict Effect
===========================
Debug the remaining dict effect in "Aeon of Atavus - Devour.xml"
"""

import sys
from pathlib import Path

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor
from dtos import FixedSpellDTOFactory


def debug_aeon_spell():
    """Debug the Aeon of Atavus spell specifically"""
    print("Debugging Aeon of Atavus - Devour.xml")
    print("=" * 50)
    
    # Initialize WAD processor
    processor = WADProcessor(types_path=Path("../types.json"))
    if not processor.initialize():
        print("Failed to initialize WAD processor")
        return
    
    test_file = "Spells/Aeon of Atavus - Devour.xml"
    
    try:
        # Process the spell
        success, spell_dict, spell_dto, error_msg = processor.process_single_spell(test_file)
        
        if not success:
            print(f"Failed to process: {error_msg}")
            return
        
        print(f"Spell DTO: {type(spell_dto).__name__}")
        
        # Examine raw effects
        print(f"\nRaw m_effects from WAD:")
        if "m_effects" in spell_dict:
            raw_effects = spell_dict["m_effects"]
            print(f"Count: {len(raw_effects)}")
            
            for i, effect in enumerate(raw_effects):
                print(f"  Effect {i}:")
                print(f"    Type: {type(effect)}")
                print(f"    $__type: {effect.get('$__type', 'MISSING')}")
                
                if "$__type" in effect:
                    # Try to create DTO for this effect
                    effect_dto = FixedSpellDTOFactory.create_from_json_data(effect)
                    if effect_dto:
                        print(f"    Factory result: {type(effect_dto).__name__}")
                    else:
                        print(f"    Factory FAILED")
                        
                        # Check if the type is in our mapping
                        type_name = effect["$__type"].replace("class ", "")
                        type_hash = FixedSpellDTOFactory.find_hash_for_type(type_name)
                        print(f"    Type name: {type_name}")
                        print(f"    Type hash: {type_hash}")
                        
                        if not type_hash:
                            print(f"    PROBLEM: No hash mapping for type {type_name}")
        
        # Examine DTO effects
        print(f"\nDTO m_effects:")
        if hasattr(spell_dto, "m_effects"):
            dto_effects = spell_dto.m_effects
            print(f"Count: {len(dto_effects) if dto_effects else 0}")
            
            if dto_effects:
                for i, effect in enumerate(dto_effects):
                    effect_type = type(effect).__name__
                    print(f"  DTO Effect {i}: {effect_type}")
                    
                    if isinstance(effect, dict):
                        print(f"    PROBLEM: DTO effect is still a dict!")
                        print(f"    Keys: {list(effect.keys())[:5]}...")
                        print(f"    $__type: {effect.get('$__type', 'MISSING')}")
                    
                    # Test database insertion logic
                    computed_type = type(effect).__name__
                    print(f"    Database would store as: '{computed_type}'")
        
        # Test the process_nested_objects method directly
        print(f"\nTesting process_nested_objects directly:")
        processed_data = FixedSpellDTOFactory.process_nested_objects(spell_dict)
        
        if "m_effects" in processed_data:
            processed_effects = processed_data["m_effects"]
            print(f"Processed effects count: {len(processed_effects)}")
            
            for i, effect in enumerate(processed_effects):
                print(f"  Processed Effect {i}: {type(effect).__name__}")
                
                if isinstance(effect, dict):
                    print(f"    PROBLEM: Processed effect is still a dict!")
    
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        processor.cleanup()


def check_factory_type_mapping():
    """Check what types are missing from the factory mapping"""
    print(f"\n" + "=" * 60)
    print("CHECKING FACTORY TYPE MAPPING")
    print("=" * 60)
    
    print("Current TYPE_MAPPING:")
    for type_hash, dto_class in FixedSpellDTOFactory.TYPE_MAPPING.items():
        print(f"  {type_hash}: {dto_class.__name__}")
    
    # Check supported types
    supported_types = FixedSpellDTOFactory.get_supported_types()
    print(f"\nSupported DTO types: {len(supported_types)}")
    for dto_type in supported_types:
        print(f"  {dto_type}")


def main():
    """Main debug function"""
    debug_aeon_spell()
    check_factory_type_mapping()


if __name__ == "__main__":
    main()