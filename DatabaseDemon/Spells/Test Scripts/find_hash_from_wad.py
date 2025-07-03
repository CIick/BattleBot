#!/usr/bin/env python3
"""
Find Hash from WAD
==================
Use the WAD processor to find the type hash for DelaySpellEffect.
"""

import sys
from pathlib import Path

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor


def find_delay_effect_hash_from_wad():
    """Find DelaySpellEffect hash from WAD processing"""
    print("Finding DelaySpellEffect hash from WAD...")
    
    # Initialize WAD processor
    processor = WADProcessor(types_path=Path("../types.json"))
    if not processor.initialize():
        print("Failed to initialize WAD processor")
        return
    
    test_file = "Spells/Aeon of Atavus - Devour.xml"
    
    try:
        # Get raw spell data
        spell_data = processor.archive.deserialize(test_file, processor.serializer)
        
        # Convert to dict
        spell_dict = processor.convert_lazy_object_to_dict(spell_data)
        
        print(f"Checking effects in {test_file}...")
        
        if "m_effects" in spell_dict:
            effects = spell_dict["m_effects"]
            
            for i, effect in enumerate(effects):
                if isinstance(effect, dict) and "$__type" in effect:
                    effect_type = effect["$__type"]
                    print(f"Effect {i}: {effect_type}")
                    
                    if "DelaySpellEffect" in effect_type:
                        print(f"Found DelaySpellEffect at effect {i}")
                        
                        # Try to find the hash from the LazyObject if possible
                        # Get the raw LazyObject for this effect
                        if hasattr(spell_data, "m_effects") and spell_data.m_effects:
                            raw_effects = list(spell_data.m_effects)
                            if i < len(raw_effects):
                                raw_effect = raw_effects[i]
                                if hasattr(raw_effect, "type_hash"):
                                    type_hash = raw_effect.type_hash
                                    print(f"DelaySpellEffect type hash: {type_hash}")
                                    
                                    # Verify with type list
                                    if processor.type_list:
                                        type_name = processor.type_list.name_for(type_hash)
                                        print(f"Verified type name: {type_name}")
                                    
                                    return type_hash
        
        print("DelaySpellEffect not found or hash not accessible")
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
    type_hash = find_delay_effect_hash_from_wad()
    
    if type_hash:
        print(f"\nDelaySpellEffect hash: {type_hash}")
        print(f"Add this to TYPE_MAPPING:")
        print(f"    {type_hash}: DelaySpellEffectDTO,")
    else:
        print("\nCould not find DelaySpellEffect hash")


if __name__ == "__main__":
    main()