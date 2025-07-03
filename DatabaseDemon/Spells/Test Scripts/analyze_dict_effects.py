#!/usr/bin/env python3
"""
Analyze Dict Effects Issue
==========================
Diagnostic script to analyze the 4289 spell effects stored as "dict" type
instead of proper DTO objects. Identifies root cause of DTO conversion failures.
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor


def analyze_dict_effects_in_database():
    """Analyze all spell effects with type 'dict' in the database"""
    print("Analyzing Dict Effects in Database")
    print("=" * 50)
    
    # Connect to backup database
    db_path = Path("../database/r777820.Wizard_1_580_0_Live_spells - Backup.db")
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Query all dict effects
        cursor.execute("SELECT filename, effect_order, effect_type FROM spell_effects WHERE effect_type = 'dict'")
        dict_effects = cursor.fetchall()
        
        print(f"Found {len(dict_effects)} spell effects with type 'dict'")
        
        if not dict_effects:
            print("No dict effects found!")
            return
        
        # Group by filename to see which spells are affected
        affected_files = {}
        for filename, effect_order, effect_type in dict_effects:
            if filename not in affected_files:
                affected_files[filename] = []
            affected_files[filename].append(effect_order)
        
        print(f"Affected spell files: {len(affected_files)}")
        print("\nSample affected files:")
        for i, (filename, effect_orders) in enumerate(list(affected_files.items())[:10]):
            print(f"  {i+1:2d}. {filename} - effects {effect_orders}")
        
        # Analyze a few specific examples
        print("\n" + "=" * 50)
        print("DETAILED ANALYSIS OF SAMPLE FILES")
        print("=" * 50)
        
        # Analyze first 5 affected files
        sample_files = list(affected_files.keys())[:5]
        
        for filename in sample_files:
            print(f"\nAnalyzing: {filename}")
            print("-" * 40)
            
            # Get all effects for this file
            cursor.execute("""
                SELECT effect_order, effect_type, m_effectType, m_effectParam, m_sDamageType 
                FROM spell_effects 
                WHERE filename = ? 
                ORDER BY effect_order
            """, (filename,))
            
            effects = cursor.fetchall()
            print(f"Total effects: {len(effects)}")
            
            for effect_order, effect_type, m_effectType, m_effectParam, m_sDamageType in effects:
                if effect_type == 'dict':
                    print(f"  Effect {effect_order}: TYPE=dict, m_effectType={m_effectType}, "
                          f"m_effectParam={m_effectParam}, m_sDamageType={m_sDamageType}")
                else:
                    print(f"  Effect {effect_order}: TYPE={effect_type}")
        
        return affected_files
        
    finally:
        conn.close()


def analyze_raw_spell_data_for_dict_effects():
    """Analyze raw spell data from WAD to understand why effects become 'dict'"""
    print("\n" + "=" * 60)
    print("ANALYZING RAW SPELL DATA FROM WAD")
    print("=" * 60)
    
    # Initialize WAD processor
    processor = WADProcessor(types_path=Path("../types.json"))
    if not processor.initialize():
        print("Failed to initialize WAD processor")
        return
    
    try:
        # Test with known problematic files
        test_files = [
            "Spells/0P Minotaur - MOB.xml",
            "Spells/3PFrostDragon_Trainable - T02 - A.xml",
            "Spells/1P Guiding Light - Amulet.xml"
        ]
        
        for file_path in test_files:
            print(f"\nAnalyzing raw data: {file_path}")
            print("-" * 50)
            
            try:
                # Process the spell
                success, spell_dict, spell_dto, error_msg = processor.process_single_spell(file_path)
                
                if not success:
                    print(f"  Failed to process: {error_msg}")
                    continue
                
                # Examine m_effects structure
                if "m_effects" in spell_dict:
                    effects = spell_dict["m_effects"]
                    print(f"  m_effects type: {type(effects)}")
                    print(f"  m_effects length: {len(effects) if isinstance(effects, list) else 'N/A'}")
                    
                    if isinstance(effects, list):
                        for i, effect in enumerate(effects):
                            print(f"    Effect {i}:")
                            print(f"      Type: {type(effect)}")
                            if isinstance(effect, dict):
                                print(f"      $__type: {effect.get('$__type', 'MISSING')}")
                                print(f"      Keys: {list(effect.keys())[:10]}...")  # First 10 keys
                            print()
                
                # Examine DTO effects
                if spell_dto and hasattr(spell_dto, "m_effects"):
                    dto_effects = spell_dto.m_effects
                    print(f"  DTO m_effects type: {type(dto_effects)}")
                    print(f"  DTO m_effects length: {len(dto_effects) if dto_effects else 0}")
                    
                    if dto_effects:
                        for i, effect in enumerate(dto_effects):
                            print(f"    DTO Effect {i}: {type(effect).__name__}")
                            if hasattr(effect, "__dict__"):
                                # Check if it's actually a dict disguised as DTO
                                if isinstance(effect, dict):
                                    print(f"      WARNING: DTO effect is actually a dict!")
                                    print(f"      Keys: {list(effect.keys())[:5]}...")
                
            except Exception as e:
                print(f"  Error processing {file_path}: {e}")
                import traceback
                traceback.print_exc()
    
    finally:
        processor.cleanup()


def check_dto_factory_processing():
    """Test DTO factory processing on spell effects specifically"""
    print("\n" + "=" * 60) 
    print("TESTING DTO FACTORY PROCESSING")
    print("=" * 60)
    
    from dtos import FixedSpellDTOFactory
    
    # Load reference example to test DTO factory
    reference_file = Path("../../Reference SpellClass Examples/3PFrostDragon_Trainable - T02 - A.json")
    if not reference_file.exists():
        print(f"Reference file not found: {reference_file}")
        return
    
    with open(reference_file, 'r') as f:
        reference_data = json.load(f)
    
    print("Testing DTO creation from reference data...")
    
    # Test creating DTO from reference data
    spell_dto = FixedSpellDTOFactory.create_from_json_data(reference_data)
    
    if spell_dto:
        print(f"[OK] Successfully created DTO: {type(spell_dto).__name__}")
        
        if hasattr(spell_dto, "m_effects"):
            effects = spell_dto.m_effects
            print(f"  m_effects type: {type(effects)}")
            print(f"  m_effects length: {len(effects) if effects else 0}")
            
            if effects:
                for i, effect in enumerate(effects):
                    print(f"    Effect {i}: {type(effect).__name__}")
                    
                    # Check for RandomSpellEffect
                    if hasattr(effect, "m_effectList"):
                        effect_list = effect.m_effectList
                        print(f"      Has m_effectList: {len(effect_list) if effect_list else 0} items")
                        if effect_list:
                            for j, sub_effect in enumerate(effect_list):
                                print(f"        Sub-effect {j}: {type(sub_effect).__name__}")
    else:
        print("[FAIL] Failed to create DTO from reference data")
    
    print("\nTesting individual effect creation...")
    
    # Test creating individual effects
    if "m_effects" in reference_data:
        for i, effect_data in enumerate(reference_data["m_effects"]):
            print(f"\nTesting effect {i}:")
            print(f"  Raw type: {effect_data.get('$__type', 'MISSING')}")
            
            # Try to create DTO for this effect
            effect_dto = FixedSpellDTOFactory.create_from_json_data(effect_data)
            if effect_dto:
                print(f"  [OK] Created DTO: {type(effect_dto).__name__}")
                
                # Check RandomSpellEffect processing
                if hasattr(effect_dto, "m_effectList"):
                    effect_list = effect_dto.m_effectList
                    print(f"    m_effectList: {len(effect_list) if effect_list else 0} items")
            else:
                print(f"  [FAIL] Failed to create DTO")


def generate_summary_report():
    """Generate summary report of findings"""
    print("\n" + "=" * 60)
    print("SUMMARY REPORT")
    print("=" * 60)
    
    # Connect to database for final stats
    db_path = Path("../database/r777820.Wizard_1_580_0_Live_spells - Backup.db")
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        try:
            # Get effect type distribution
            cursor.execute("SELECT effect_type, COUNT(*) FROM spell_effects GROUP BY effect_type ORDER BY COUNT(*) DESC")
            effect_types = cursor.fetchall()
            
            print("Effect Type Distribution:")
            for effect_type, count in effect_types:
                print(f"  {effect_type}: {count}")
            
            # Check random spell effects
            cursor.execute("SELECT COUNT(*) FROM random_spell_effects")
            random_count = cursor.fetchone()[0]
            print(f"\nRandom spell effects entries: {random_count}")
            
            # Check 3PFrostDragon_Trainable specifically
            cursor.execute("SELECT COUNT(*) FROM random_spell_effects WHERE filename LIKE '%3PFrostDragon_Trainable - T02 - A%'")
            frost_dragon_count = cursor.fetchone()[0]
            print(f"3PFrostDragon_Trainable random effects: {frost_dragon_count} (expected: 5)")
            
        finally:
            conn.close()
    
    print("\nNext Steps:")
    print("1. Fix DTO factory to properly convert spell effects")
    print("2. Fix database insertion to detect DTO types correctly")
    print("3. Ensure RandomSpellEffect.m_effectList gets processed")
    print("4. Regenerate database and validate")


def main():
    """Main analysis function"""
    print("Dict Effects Analysis")
    print("Database:", "../database/r777820.Wizard_1_580_0_Live_spells - Backup.db")
    print("=" * 60)
    
    try:
        # Analyze database
        affected_files = analyze_dict_effects_in_database()
        
        # Analyze raw data
        analyze_raw_spell_data_for_dict_effects()
        
        # Test DTO factory
        check_dto_factory_processing()
        
        # Generate summary
        generate_summary_report()
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()