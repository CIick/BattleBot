#!/usr/bin/env python3
"""
Wizard101 Database Creator - Main Entry Point
=============================================
Creates SQLite database from Wizard101 Root.wad spell data.

This script:
1. Auto-detects Wizard101 revision from revision.dat
2. Validates types.json compatibility
3. Processes all spell XML files from Root.wad
4. Creates normalized database with filename PRIMARY KEY
5. Handles duplicate detection and comprehensive error logging
6. Stores raw data for future ML feature engineering

Usage:
    python database_creator.py

Requirements:
    - types.json file in DatabaseDemon directory (correct revision)
    - Wizard101 installed with accessible Root.wad file
    - Python packages: katsuba, sqlite3 (built-in)

Output:
    - database/r{revision}_spells.db - SQLite database
    - failed_spells/ - Duplicate analysis and failed records
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from processors import DatabaseCreator, RevisionDetector, get_current_revision


def check_prerequisites():
    """Check that all prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check for types.json file
    types_path = Path("types.json")
    if not types_path.exists():
        print("ERROR: types.json file not found in DatabaseDemon directory")
        print("Please copy the correct types.json file for your Wizard101 revision")
        print("Check if the type dump (types.json) is the correct version for this revision")
        return False
    
    print(f"[OK] Found types.json at {types_path}")
    
    # Check revision detection
    revision = get_current_revision()
    if not revision:
        print("WARNING: Could not detect Wizard101 revision")
        print("Database will be named with 'unknown' revision")
    else:
        print(f"[OK] Detected revision: {revision}")
    
    # Check types file compatibility
    detector = RevisionDetector()
    if not detector.validate_types_compatibility(types_path):
        print("WARNING: Types file may not match current revision")
    
    return True


def main():
    """Main function to create the Wizard101 spell database"""
    print("Wizard101 Spell Database Creator")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPrerequisites not met. Exiting.")
        return 1
    
    # Initialize database creator
    print("\nInitializing database creator...")
    creator = DatabaseCreator()
    
    try:
        # Initialize (loads WAD, types, creates schema)
        if not creator.initialize():
            print("Failed to initialize database creator")
            return 1
        
        print(f"\nDatabase will be created at: {creator.database_path}")
        print(f"Failed spells will be logged to: {creator.failed_spells_dir}")
        
        # Confirm before processing
        response = input("\nProceed with database creation? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Database creation cancelled.")
            return 0
        
        # Process all spells
        print("\nStarting spell processing...")
        if not creator.process_all_spells():
            print("Spell processing failed")
            return 1
        
        # Print summary
        creator.print_summary()
        
        # Check for issues
        if creator.duplicate_count > 0:
            print(f"\nWARNING: Found {creator.duplicate_count} duplicate filenames!")
            print("This means filename is not a reliable unique identifier.")
            print("Check failed_spells/ directory for duplicate analysis.")
            print("You may need to use a different primary key strategy.")
        
        if creator.total_failures > 0:
            print(f"\nWARNING: {creator.total_failures} spells failed to process")
            print("Check failed_spells/ directory for detailed error analysis.")
        
        if creator.duplicate_count == 0 and creator.total_failures < (creator.total_processed * 0.05):
            print("\n🎉 Database creation completed successfully!")
            print("Database is ready for ML training and combat analysis.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nDatabase creation interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Clean up resources
        creator.cleanup()


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