#!/usr/bin/env python3
"""
Debug Inheritance Issue
======================
Debug why TieredSpellTemplateDTO is not getting m_effects from parent class.
"""

import json
import sys
from pathlib import Path

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from dtos import FixedSpellDTOFactory, TieredSpellTemplateDTO, SpellTemplateDTO


def debug_inheritance():
    """Debug inheritance in DTO creation"""
    print("Debugging DTO Inheritance Issue")
    print("=" * 50)
    
    # Load 3PFrostDragon reference data
    reference_file = Path("../../Reference SpellClass Examples/3PFrostDragon_Trainable - T02 - A.json")
    
    if not reference_file.exists():
        print(f"Reference file not found: {reference_file}")
        return
    
    with open(reference_file, 'r') as f:
        reference_data = json.load(f)
    
    print(f"Reference data type: {reference_data.get('$__type')}")
    print(f"Reference m_effects count: {len(reference_data.get('m_effects', []))}")
    
    # Check TieredSpellTemplateDTO class annotations
    print(f"\nTieredSpellTemplateDTO annotations:")
    for field_name in TieredSpellTemplateDTO.__annotations__:
        print(f"  {field_name}")
    
    print(f"\nSpellTemplateDTO annotations:")
    spell_template_fields = []
    for field_name in SpellTemplateDTO.__annotations__:
        spell_template_fields.append(field_name)
        if field_name == "m_effects":
            print(f"  {field_name} ← FOUND!")
        else:
            print(f"  {field_name}")
    
    # Test the factory processing
    print(f"\nTesting DTO factory processing...")
    
    # Step 1: Test process_nested_objects
    processed_data = FixedSpellDTOFactory.process_nested_objects(reference_data)
    
    print(f"Processed m_effects count: {len(processed_data.get('m_effects', []))}")
    
    if "m_effects" in processed_data:
        for i, effect in enumerate(processed_data["m_effects"]):
            print(f"  Effect {i}: {type(effect).__name__}")
    
    # Step 2: Test DTO creation
    dto = FixedSpellDTOFactory.create_from_json_data(reference_data)
    
    if dto:
        print(f"\nCreated DTO: {type(dto).__name__}")
        print(f"DTO has m_effects: {hasattr(dto, 'm_effects')}")
        
        if hasattr(dto, "m_effects"):
            effects = dto.m_effects
            print(f"DTO m_effects: {effects}")
            print(f"DTO m_effects type: {type(effects)}")
            print(f"DTO m_effects length: {len(effects) if effects else 0}")
        
        # Check all attributes
        print(f"\nDTO attributes:")
        if hasattr(dto, "__dict__"):
            for attr_name, attr_value in dto.__dict__.items():
                if attr_name == "m_effects":
                    print(f"  {attr_name}: {attr_value} ← EFFECTS!")
                elif isinstance(attr_value, list) and len(attr_value) > 0:
                    print(f"  {attr_name}: [list with {len(attr_value)} items]")
                else:
                    print(f"  {attr_name}: {attr_value}")
    
    # Step 3: Test manual DTO creation
    print(f"\nTesting manual DTO creation...")
    
    # Create kwargs manually
    kwargs = {}
    for field_name in TieredSpellTemplateDTO.__annotations__.keys():
        if field_name in processed_data:
            kwargs[field_name] = processed_data[field_name]
            if field_name == "m_effects":
                print(f"  Added m_effects to kwargs: {len(kwargs[field_name])} effects")
    
    # Also check parent class fields
    print(f"\nChecking parent class fields in processed data...")
    for field_name in SpellTemplateDTO.__annotations__.keys():
        if field_name in processed_data:
            if field_name not in kwargs:  # Only add if not already from child class
                kwargs[field_name] = processed_data[field_name]
                if field_name == "m_effects":
                    print(f"  Added parent m_effects to kwargs: {len(kwargs[field_name])} effects")
    
    print(f"Total kwargs: {len(kwargs)}")
    print(f"m_effects in kwargs: {'m_effects' in kwargs}")
    
    # Create DTO manually
    try:
        manual_dto = TieredSpellTemplateDTO(**kwargs)
        print(f"Manual DTO created: {type(manual_dto).__name__}")
        print(f"Manual DTO m_effects: {len(manual_dto.m_effects) if manual_dto.m_effects else 0}")
    except Exception as e:
        print(f"Manual DTO creation failed: {e}")


def test_factory_create_dto():
    """Test the factory create_dto method specifically"""
    print(f"\n" + "=" * 60)
    print("TESTING FACTORY CREATE_DTO METHOD")
    print("=" * 60)
    
    # Load reference data
    reference_file = Path("../../Reference SpellClass Examples/3PFrostDragon_Trainable - T02 - A.json")
    
    with open(reference_file, 'r') as f:
        reference_data = json.load(f)
    
    # Find the type hash for TieredSpellTemplateDTO
    type_hash = None
    for hash_val, dto_class in FixedSpellDTOFactory.TYPE_MAPPING.items():
        if dto_class == TieredSpellTemplateDTO:
            type_hash = hash_val
            break
    
    print(f"TieredSpellTemplateDTO type hash: {type_hash}")
    
    if type_hash:
        # Test create_dto directly
        dto = FixedSpellDTOFactory.create_dto(type_hash, reference_data)
        
        if dto:
            print(f"Direct create_dto result: {type(dto).__name__}")
            print(f"Has m_effects: {hasattr(dto, 'm_effects')}")
            
            if hasattr(dto, "m_effects"):
                print(f"m_effects: {len(dto.m_effects) if dto.m_effects else 0}")
        else:
            print("Direct create_dto failed")


def main():
    """Main debug function"""
    debug_inheritance()
    test_factory_create_dto()


if __name__ == "__main__":
    main()