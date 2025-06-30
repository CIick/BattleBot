#!/usr/bin/env python3
"""
Quick Validation
===============
Quick test to verify DelaySpellEffect fix works in database creation.
"""

import sqlite3
import sys
import random
from pathlib import Path

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor, DatabaseCreator


def quick_validation_test():
    """Quick validation test with new database name"""
    print("Quick Validation Test - DelaySpellEffect Fix")
    print("=" * 50)
    
    # Create test database with random name to avoid conflicts
    test_db_name = f"test_validation_{random.randint(1000, 9999)}.db"
    test_db_path = Path(f"../database/{test_db_name}")
    test_db_path.parent.mkdir(exist_ok=True)
    
    # Initialize database creator
    creator = DatabaseCreator(database_path=test_db_path)
    creator.wad_processor.types_path = Path("../types.json")
    
    if not creator.initialize():
        print("Failed to initialize database creator")
        return False
    
    try:
        # Test with the Aeon spell that had DelaySpellEffect
        test_file = "Spells/Aeon of Atavus - Devour.xml"
        
        print(f"Processing: {test_file}")
        
        # Process spell
        success, spell_dict, spell_dto, error_msg = creator.wad_processor.process_single_spell(test_file)
        
        if success and spell_dto:
            # Insert into database
            if creator.insert_spell_data(test_file, spell_dict, spell_dto):
                print(f"  [OK] Successfully inserted")
            else:
                print(f"  [FAIL] Failed to insert")
                return False
        else:
            print(f"  [FAIL] Failed to process: {error_msg}")
            return False
        
        # Commit changes
        creator.connection.commit()
        
        # Check the database for effect types
        print(f"\nValidating database...")
        
        cursor = creator.cursor
        cursor.execute("SELECT effect_type, COUNT(*) FROM spell_effects GROUP BY effect_type")
        effect_types = cursor.fetchall()
        
        print("Effect types found:")
        dict_count = 0
        for effect_type, count in effect_types:
            print(f"  {effect_type}: {count}")
            if effect_type == "dict":
                dict_count += count
        
        # Test result
        if dict_count == 0:
            print(f"\n[SUCCESS] No dict effects found! DelaySpellEffect fix works!")
            return True
        else:
            print(f"\n[PROBLEM] Found {dict_count} dict effects")
            return False
    
    finally:
        creator.cleanup()
        # Clean up test database
        try:
            if test_db_path.exists():
                test_db_path.unlink()
        except:
            pass  # Ignore cleanup errors


def main():
    """Main test function"""
    success = quick_validation_test()
    
    if success:
        print("\n🎉 DelaySpellEffect fix validated successfully!")
        print("Ready to proceed with comprehensive type discovery.")
    else:
        print("\n❌ Still have issues to resolve.")
    
    return success


if __name__ == "__main__":
    main()