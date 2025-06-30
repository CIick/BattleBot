#!/usr/bin/env python3
"""
Find Hash Direct
================
Directly analyze the LazyObject to get DelaySpellEffect hash.
"""

import sys
from pathlib import Path

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor
from katsuba.op import LazyObject


def find_delay_effect_hash_direct():
    """Find DelaySpellEffect hash by examining LazyObjects directly"""
    print("Finding DelaySpellEffect hash from LazyObjects...")
    
    # Initialize WAD processor
    processor = WADProcessor(types_path=Path("../types.json"))
    if not processor.initialize():
        print("Failed to initialize WAD processor")
        return
    
    test_file = "Spells/Aeon of Atavus - Devour.xml"
    
    try:
        # Get raw LazyObject (before conversion)
        raw_spell_data = processor.archive.deserialize(test_file, processor.serializer)
        
        print(f"Raw spell data type: {type(raw_spell_data)}")
        
        if isinstance(raw_spell_data, LazyObject) and hasattr(raw_spell_data, "m_effects"):
            effects_lazy = raw_spell_data.m_effects
            print(f"Effects LazyList: {type(effects_lazy)}")
            
            # Iterate through LazyList
            for i, effect_lazy in enumerate(effects_lazy):
                print(f"\nEffect {i}:")
                print(f"  Type: {type(effect_lazy)}")
                
                if isinstance(effect_lazy, LazyObject):
                    print(f"  Type hash: {effect_lazy.type_hash}")
                    
                    # Get type name from hash
                    if processor.type_list:
                        type_name = processor.type_list.name_for(effect_lazy.type_hash)
                        print(f"  Type name: {type_name}")
                        
                        if "DelaySpellEffect" in type_name:
                            print(f"  FOUND DelaySpellEffect!")
                            print(f"  Hash: {effect_lazy.type_hash}")
                            return effect_lazy.type_hash
        
        print("DelaySpellEffect not found")
        return None
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        processor.cleanup()


def main():
    """Main function"""
    type_hash = find_delay_effect_hash_direct()
    
    if type_hash:
        print(f"\nDelaySpellEffect hash found: {type_hash}")
        print(f"Add this to TYPE_MAPPING in SpellsDTOFactory.py:")
        print(f"    {type_hash}: DelaySpellEffectDTO,")
    else:
        print("\nCould not find DelaySpellEffect hash")


if __name__ == "__main__":
    main()