#!/usr/bin/env python3
"""
Wizard101 Mob Database Creator - Main Entry Point
================================================
Creates SQLite database from Wizard101 Root.wad mob data (ObjectData files).

This script:
1. Processes all ObjectData/**/*.xml files from Root.wad
2. Filters for WizGameObjectTemplate objects (mobs)
3. Creates normalized database with comprehensive behavior tracking
4. Handles duplicate detection and comprehensive error logging
5. Stores mob data with full behavior relationships

Usage:
    python database_creator.py

Requirements:
    - types.json file in parent DatabaseDemon directory
    - Wizard101 installed with accessible Root.wad file
    - Python packages: katsuba, sqlite3 (built-in)

Output:
    - database/mob_templates_{timestamp}.db - SQLite database
    - failed_mobs/ - Error analysis and failed records
"""

import sys
import os
from pathlib import Path
import platform
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from processors import MobDatabaseCreator


def get_platform_paths():
    """Get platform-specific paths for WAD and types files"""
    system = platform.system().lower()
    
    if system == "windows":
        wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("../types.json")
    else:  # Linux or other
        wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("../types.json")
    
    return wad_path, types_path


def check_prerequisites():
    """Check that all prerequisites are met"""
    print("Checking prerequisites...")
    
    # Get platform-specific paths
    wad_path, types_path = get_platform_paths()
    
    # Check for types.json file
    if not types_path.exists():
        print("ERROR: types.json file not found in DatabaseDemon directory")
        print("Please copy the correct types.json file for your Wizard101 revision")
        return False
    
    print(f"[OK] Found types.json at {types_path}")
    
    # Check for WAD file
    if not wad_path.exists():
        print(f"ERROR: Root.wad file not found at {wad_path}")
        print("Please ensure Wizard101 is installed and accessible")
        return False
    
    print(f"[OK] Found Root.wad at {wad_path}")
    
    return True


def main():
    """Main function to create the Wizard101 mob database"""
    print("Wizard101 Mob Database Creator")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPrerequisites not met. Exiting.")
        return 1
    
    # Get paths
    wad_path, types_path = get_platform_paths()
    
    # Initialize database creator
    print("\nInitializing mob database creator...")
    creator = MobDatabaseCreator()
    
    try:
        # Initialize
        if not creator.initialize():
            print("Failed to initialize mob database creator")
            return 1
        
        # Create database schema
        if not creator.create_database():
            print("Failed to create mob database schema")
            return 1
        
        print(f"\nDatabase will be created at: {creator.database_path}")
        print(f"Failed mobs will be logged to: {creator.failed_mobs_dir}")
        
        # Confirm before processing
        response = input("\nProceed with mob database creation? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Mob database creation cancelled.")
            return 0
        
        # Process all mobs
        print("\nStarting mob processing from ObjectData files...")
        print("This may take a while as we process ~95k ObjectData files...")
        if not creator.process_all_mobs(wad_path, types_path):
            print("Mob processing failed")
            return 1
        
        # Check for issues and provide feedback
        if creator.duplicate_count > 0:
            print(f"\nINFO: Found {creator.duplicate_count} duplicate mobs (skipped)")
            print("Duplicates are normal and were handled correctly.")
        
        if creator.total_failures > 0:
            print(f"\nWARNING: {creator.total_failures} objects failed to process")
            print("Most failures are likely non-mob ObjectData files - this is expected.")
            print("Check failed_mobs/ directory for detailed error analysis.")
        
        success_rate = (creator.total_success / creator.total_processed * 100) if creator.total_processed > 0 else 0
        
        if creator.total_success > 0:
            print(f"\n🎉 Mob database creation completed successfully!")
            print(f"Successfully processed {creator.total_success} mobs")
            print(f"Database is ready for analysis and combat planning.")
        else:
            print(f"\n⚠️ No mobs were successfully processed!")
            print("This may indicate an issue with data processing or filtering.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nMob database creation interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Clean up resources
        if creator.connection:
            creator.close()


def show_help():
    """Show help information"""
    print(__doc__)


if __name__ == "__main__":
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        sys.exit(0)
    
    # Run main function
    sys.exit(main())