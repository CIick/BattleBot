#!/usr/bin/env python3
"""
Validate Fixes
==============
Test that current DTO processing and database creation works correctly.
Creates a small test database to validate the fixes.
"""

import sqlite3
import sys
from pathlib import Path

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor, DatabaseCreator
from dtos import FixedSpellDTOFactory


def test_small_database_creation():
    """Test creating a small database with a few spells to validate fixes"""
    print("Testing Small Database Creation")
    print("=" * 50)
    
    # Create test database
    test_db_path = Path("../database/test_validation.db")
    test_db_path.parent.mkdir(exist_ok=True)
    
    # Remove existing test database
    if test_db_path.exists():
        test_db_path.unlink()
    
    # Initialize database creator
    creator = DatabaseCreator(database_path=test_db_path)
    creator.wad_processor.types_path = Path("../types.json")
    
    if not creator.initialize():
        print("Failed to initialize database creator")
        return False
    
    try:
        # Test with a small set of known files
        test_files = [
            "Spells/0P Minotaur - MOB.xml",
            "Spells/1P Guiding Light - Amulet.xml",
            "Spells/Aeon of Atavus - Devour.xml"  # This had mixed dict/DTO effects
        ]
        
        print(f"Testing {len(test_files)} spell files...")
        
        for test_file in test_files:
            print(f"\nProcessing: {test_file}")
            
            # Process spell
            success, spell_dict, spell_dto, error_msg = creator.wad_processor.process_single_spell(test_file)
            
            if success and spell_dto:
                # Insert into database
                if creator.insert_spell_data(test_file, spell_dict, spell_dto):
                    print(f"  [OK] Successfully inserted")
                else:
                    print(f"  [FAIL] Failed to insert")
            else:
                print(f"  [FAIL] Failed to process: {error_msg}")
        
        # Commit changes
        creator.connection.commit()
        
        # Validate the database
        return validate_test_database(test_db_path)
    
    finally:
        creator.cleanup()


def validate_test_database(db_path: Path) -> bool:
    """Validate the test database has correct data"""
    print(f"\nValidating test database: {db_path}")
    print("-" * 40)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check spell_cards table
        cursor.execute("SELECT COUNT(*) FROM spell_cards")
        spell_count = cursor.fetchone()[0]
        print(f"Spell cards: {spell_count}")
        
        # Check spell_effects table and effect types
        cursor.execute("SELECT effect_type, COUNT(*) FROM spell_effects GROUP BY effect_type")
        effect_types = cursor.fetchall()
        
        print("Effect types:")
        dict_count = 0
        dto_count = 0
        
        for effect_type, count in effect_types:
            print(f"  {effect_type}: {count}")
            
            if effect_type == "dict":
                dict_count += count
            else:
                dto_count += count
        
        # Check random spell effects
        cursor.execute("SELECT COUNT(*) FROM random_spell_effects")
        random_effects_count = cursor.fetchone()[0]
        print(f"Random spell effects: {random_effects_count}")
        
        # Validation results
        print(f"\nValidation Results:")
        print(f"  Dict effects: {dict_count}")
        print(f"  DTO effects: {dto_count}")
        
        if dict_count == 0:
            print(f"  [SUCCESS] No dict effects found!")
            success = True
        else:
            print(f"  [PROBLEM] Found {dict_count} dict effects")
            success = False
        
        # Show specific examples
        print(f"\nSample effect data:")
        cursor.execute("""
            SELECT filename, effect_order, effect_type, m_effectType, m_effectParam, m_sDamageType 
            FROM spell_effects 
            LIMIT 5
        """)
        
        sample_effects = cursor.fetchall()
        for filename, effect_order, effect_type, m_effectType, m_effectParam, m_sDamageType in sample_effects:
            print(f"  {filename.split('/')[-1]}: {effect_type}, effectType={m_effectType}, param={m_effectParam}")
        
        return success
    
    finally:
        conn.close()


def test_reference_examples():
    """Test that reference examples work correctly with current DTO processing"""
    print(f"\n" + "=" * 60)
    print("TESTING REFERENCE EXAMPLES")
    print("=" * 60)
    
    reference_examples = [
        "0P Minotaur - MOB.json",
        "3PFrostDragon_Trainable - T02 - A.json"
    ]
    
    success_count = 0
    
    for example_name in reference_examples:
        reference_file = Path(f"../../Reference SpellClass Examples/{example_name}")
        
        if not reference_file.exists():
            print(f"Reference file not found: {reference_file}")
            continue
        
        print(f"\nTesting: {example_name}")
        
        try:
            import json
            with open(reference_file, 'r') as f:
                reference_data = json.load(f)
            
            # Test DTO creation
            spell_dto = FixedSpellDTOFactory.create_from_json_data(reference_data)
            
            if spell_dto:
                print(f"  [OK] Created DTO: {type(spell_dto).__name__}")
                
                # Check effects
                if hasattr(spell_dto, "m_effects"):
                    effects = spell_dto.m_effects
                    print(f"  Effects: {len(effects) if effects else 0}")
                    
                    all_dto = True
                    random_effects = 0
                    
                    if effects:
                        for i, effect in enumerate(effects):
                            effect_type = type(effect).__name__
                            print(f"    Effect {i}: {effect_type}")
                            
                            if isinstance(effect, dict):
                                all_dto = False
                                print(f"      [PROBLEM] Effect is still a dict!")
                            
                            # Check for RandomSpellEffect
                            if hasattr(effect, "m_effectList"):
                                sub_effects = effect.m_effectList
                                random_effects += len(sub_effects) if sub_effects else 0
                                print(f"      RandomSpellEffect with {len(sub_effects) if sub_effects else 0} sub-effects")
                    
                    if all_dto:
                        print(f"  [SUCCESS] All effects are proper DTOs")
                        success_count += 1
                    else:
                        print(f"  [PROBLEM] Some effects are still dicts")
                    
                    if "3PFrostDragon_Trainable" in example_name and random_effects == 5:
                        print(f"  [SUCCESS] 3PFrostDragon has correct 5 random effects")
                    elif "3PFrostDragon_Trainable" in example_name:
                        print(f"  [PROBLEM] 3PFrostDragon has {random_effects} random effects, expected 5")
                
            else:
                print(f"  [FAIL] Failed to create DTO")
        
        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
    
    print(f"\nReference Examples Results: {success_count}/{len(reference_examples)} successful")
    return success_count == len(reference_examples)


def main():
    """Main validation function"""
    print("Validation of DTO Processing Fixes")
    print("=" * 60)
    
    # Test 1: Reference examples
    ref_success = test_reference_examples()
    
    # Test 2: Small database creation
    db_success = test_small_database_creation()
    
    print(f"\n" + "=" * 60)
    print("FINAL VALIDATION RESULTS")
    print("=" * 60)
    print(f"Reference examples: {'PASS' if ref_success else 'FAIL'}")
    print(f"Database creation: {'PASS' if db_success else 'FAIL'}")
    
    if ref_success and db_success:
        print(f"\n[SUCCESS] All fixes validated! Ready to regenerate full database.")
        print(f"The DTO processing is working correctly.")
        print(f"The original database had dict effects because it was created with broken code.")
    else:
        print(f"\n[PROBLEM] Some issues remain to be fixed.")
    
    return ref_success and db_success


if __name__ == "__main__":
    main()