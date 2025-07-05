#!/usr/bin/env python3
"""
Wizard101 Items Database Creator
===============================
Main script to create complete Items database by processing entire ObjectData
for WizItemTemplate objects with comprehensive nested type support.
"""

import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from Items.processors.DatabaseCreator import ItemsDatabaseCreator


def main():
    """Main function to create Items database"""
    print("Wizard101 Items Database Creator")
    print("=" * 50)
    print("Creating comprehensive database of all WizItemTemplate objects")
    print("with support for 117+ nested types including pets, mounts, housing, etc.")
    print()
    
    # Initialize database creator
    creator = ItemsDatabaseCreator()
    
    try:
        print("Initializing database schema...")
        if not creator.initialize_database():
            print("[ERROR] Failed to initialize database")
            return 1
        
        print("Processing all items from WAD archive...")
        if not creator.process_all_items_from_wad():
            print("[ERROR] Failed to process items from WAD")
            return 1
        
        print("\n" + "=" * 60)
        print("DATABASE CREATION COMPLETE!")
        print("=" * 60)
        print(f"Database file: {creator.database_path}")
        print(f"Total items processed: {creator.total_processed}")
        print(f"Successfully inserted: {creator.total_success}")
        print(f"Failed insertions: {creator.total_failed}")
        print(f"Behaviors processed: {creator.total_behaviors}")
        print(f"Effects processed: {creator.total_effects}")
        print(f"Requirements processed: {creator.total_requirements}")
        print(f"Pet items: {creator.total_pet_items}")
        print(f"Mount items: {creator.total_mount_items}")
        print(f"Housing items: {creator.total_housing_items}")
        print(f"Equipment items: {creator.total_equipment_items}")
        
        if creator.total_success > 0:
            success_rate = (creator.total_success / creator.total_processed) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        if creator.start_time and creator.end_time:
            duration = creator.end_time - creator.start_time
            print(f"Processing time: {duration}")
        
        print(f"\nDatabase is ready for use!")
        print(f"Location: {creator.database_path.absolute()}")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Database creation failed: {e}")
        traceback.print_exc()
        return 1
        
    finally:
        creator.cleanup()


if __name__ == "__main__":
    sys.exit(main())