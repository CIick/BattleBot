#!/usr/bin/env python3
"""
Debug Database Insertion
========================
Debug the exact database insertion process to see where DTOs become "dict".
"""

import sqlite3
import sys
from pathlib import Path

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor, DatabaseCreator
from dtos import FixedSpellDTOFactory


def debug_database_insertion():
    """Debug database insertion step by step"""
    print("Debugging Database Insertion Process")
    print("=" * 50)
    
    # Initialize WAD processor
    processor = WADProcessor(types_path=Path("../types.json"))
    if not processor.initialize():
        print("Failed to initialize WAD processor")
        return
    
    # Test with known file
    test_file = "Spells/0P Minotaur - MOB.xml"
    print(f"Testing file: {test_file}")
    
    try:
        # Step 1: Get spell data and DTO
        print("\n1. Getting spell data and DTO...")
        success, spell_dict, spell_dto, error_msg = processor.process_single_spell(test_file)
        
        if not success:
            print(f"Failed to process: {error_msg}")
            return
        
        print(f"Spell DTO type: {type(spell_dto).__name__}")
        
        # Step 2: Examine effects before database insertion
        print("\n2. Examining effects before database insertion...")
        if hasattr(spell_dto, "m_effects"):
            effects = spell_dto.m_effects
            print(f"Effects count: {len(effects)}")
            
            for i, effect in enumerate(effects):
                print(f"  Effect {i}:")
                print(f"    Type: {type(effect)}")
                print(f"    Type name: {type(effect).__name__}")
                print(f"    Is DTO: {hasattr(effect, '__dict__')}")
                print(f"    Is dict: {isinstance(effect, dict)}")
                
                # Test the safe_effect_get function logic
                def safe_effect_get(attr, default=None):
                    if hasattr(effect, attr):
                        value = getattr(effect, attr)
                        if isinstance(value, bool):
                            return 1 if value else 0
                        return value
                    return default
                
                print(f"    m_effectType: {safe_effect_get('m_effectType')}")
                print(f"    m_effectParam: {safe_effect_get('m_effectParam')}")
                print(f"    m_sDamageType: {safe_effect_get('m_sDamageType')}")
        
        # Step 3: Test individual effect insertion logic
        print("\n3. Testing effect insertion logic...")
        
        # Create a temporary in-memory database for testing
        test_db = sqlite3.connect(":memory:")
        test_cursor = test_db.cursor()
        
        # Create spell_effects table
        test_cursor.execute("""
            CREATE TABLE spell_effects (
                filename TEXT,
                effect_order INTEGER,
                effect_type TEXT,
                m_act INTEGER,
                m_actNum INTEGER,
                m_effectType INTEGER,
                m_effectParam INTEGER,
                m_sDamageType TEXT,
                PRIMARY KEY (filename, effect_order)
            )
        """)
        
        # Test inserting effects
        if hasattr(spell_dto, "m_effects"):
            for effect_order, effect in enumerate(spell_dto.m_effects):
                print(f"\n  Inserting effect {effect_order}:")
                print(f"    Effect object: {effect}")
                print(f"    Effect type: {type(effect)}")
                print(f"    Effect type name: {type(effect).__name__}")
                
                # Simulate the exact insertion logic from DatabaseCreator
                def safe_effect_get(attr, default=None):
                    if hasattr(effect, attr):
                        value = getattr(effect, attr)
                        if isinstance(value, bool):
                            return 1 if value else 0
                        return value
                    return default
                
                effect_type = type(effect).__name__
                
                print(f"    Computed effect_type: '{effect_type}'")
                
                # Insert into test database
                test_cursor.execute("""
                    INSERT INTO spell_effects (
                        filename, effect_order, effect_type, m_act, m_actNum,
                        m_effectType, m_effectParam, m_sDamageType
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_file, effect_order, effect_type,
                    safe_effect_get("m_act"), safe_effect_get("m_actNum"),
                    safe_effect_get("m_effectType"), safe_effect_get("m_effectParam"),
                    safe_effect_get("m_sDamageType")
                ))
                
                print(f"    [OK] Inserted with effect_type: '{effect_type}'")
        
        # Step 4: Query the test database to see what was inserted
        print("\n4. Querying test database to verify insertion...")
        test_cursor.execute("SELECT filename, effect_order, effect_type FROM spell_effects")
        results = test_cursor.fetchall()
        
        for filename, effect_order, effect_type in results:
            print(f"  DB Effect {effect_order}: type='{effect_type}'")
            
            if effect_type == "dict":
                print(f"    PROBLEM: Effect stored as 'dict'!")
            else:
                print(f"    OK: Effect stored as '{effect_type}'")
        
        test_db.close()
        
        # Step 5: Compare with actual database
        print("\n5. Comparing with actual database...")
        actual_db_path = Path("../database/r777820.Wizard_1_580_0_Live_spells - Backup.db")
        
        if actual_db_path.exists():
            actual_db = sqlite3.connect(str(actual_db_path))
            actual_cursor = actual_db.cursor()
            
            actual_cursor.execute("""
                SELECT effect_order, effect_type, m_effectType, m_effectParam, m_sDamageType 
                FROM spell_effects 
                WHERE filename = ?
                ORDER BY effect_order
            """, (test_file,))
            
            actual_results = actual_cursor.fetchall()
            print(f"  Actual database has {len(actual_results)} effects for this file:")
            
            for effect_order, effect_type, m_effectType, m_effectParam, m_sDamageType in actual_results:
                print(f"    Effect {effect_order}: type='{effect_type}', effectType={m_effectType}, param={m_effectParam}")
                
                if effect_type == "dict":
                    print(f"      PROBLEM: Stored as 'dict' in actual database!")
            
            actual_db.close()
        else:
            print("  Actual database not found")
    
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        processor.cleanup()


def test_problematic_files():
    """Test files that are known to have dict effects in the database"""
    print("\n" + "=" * 60)
    print("TESTING PROBLEMATIC FILES")
    print("=" * 60)
    
    # Files that were shown to have dict effects in the analysis
    problematic_files = [
        "Spells/4P Supernova - Amulet.xml",
        "Spells/Accursed Ground - MOB ONLY.xml",
        "Spells/Aeon of Atavus - Devour - Late.xml"
    ]
    
    # Initialize WAD processor
    processor = WADProcessor(types_path=Path("../types.json"))
    if not processor.initialize():
        print("Failed to initialize WAD processor")
        return
    
    try:
        for test_file in problematic_files:
            print(f"\nTesting problematic file: {test_file}")
            
            # Try to process the file
            success, spell_dict, spell_dto, error_msg = processor.process_single_spell(test_file)
            
            if success:
                print(f"  [OK] Successfully processed")
                print(f"  Spell DTO: {type(spell_dto).__name__}")
                
                if hasattr(spell_dto, "m_effects"):
                    effects = spell_dto.m_effects
                    print(f"  Effects: {len(effects)}")
                    
                    for i, effect in enumerate(effects):
                        effect_type_name = type(effect).__name__
                        print(f"    Effect {i}: {effect_type_name}")
                        
                        if effect_type_name == "dict":
                            print(f"      PROBLEM: Effect is a dict!")
                        elif isinstance(effect, dict):
                            print(f"      WEIRD: Effect isinstance dict but type name is {effect_type_name}")
                else:
                    print(f"  No m_effects attribute")
            else:
                print(f"  [FAIL] Failed to process: {error_msg}")
    
    finally:
        processor.cleanup()


def main():
    """Main debug function"""
    debug_database_insertion()
    test_problematic_files()


if __name__ == "__main__":
    main()