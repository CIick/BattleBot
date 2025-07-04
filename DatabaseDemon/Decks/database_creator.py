#!/usr/bin/env python3
"""
Wizard101 Deck Database Creator - Main Entry Point
==================================================
Creates SQLite database from Wizard101 deck XML files.

This script:
1. Processes all deck XML files from MobDecks directory
2. Converts deck data to structured DTOs using DecksDTOFactory
3. Creates normalized SQLite database with comprehensive schema
4. Performs spell analysis and categorization
5. Generates detailed reports and statistics

Based on analysis of 3,556 deck files with 84,827 spell references.

Usage:
    python database_creator.py [--output-dir PATH] [--skip-validation]

Requirements:
    - Deck XML files in MobDecks directory
    - types.json file in parent DatabaseDemon directory
    - Python packages: sqlite3 (built-in), json (built-in)

Output:
    - database/wizard101_decks.db - Main SQLite database
    - Reports/Deck Reports/ - Analysis reports and statistics
"""

import argparse
import sys
import platform
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "processors"))
sys.path.insert(0, str(current_dir / "dtos"))

try:
    from DatabaseCreator import DatabaseCreator, create_deck_database
    from WADProcessor import WADProcessor, process_deck_directory
    from DecksDTOFactory import DecksDTOFactory
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the correct directory")
    sys.exit(1)


def get_platform_paths():
    """Get platform-specific default paths."""
    system = platform.system().lower()
    if system == "windows":
        base_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon")
    else:  # Linux/WSL
        base_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon")
    
    return {
        'base': base_path,
        'decks': base_path / "Decks",
        'mobdecks': base_path / "Decks" / "MobDecks",
        'database': base_path / "Decks" / "database",
        'reports': base_path / "Reports" / "Deck Reports",
        'types': base_path / "types.json"
    }


def validate_prerequisites(paths: dict) -> bool:
    """Validate that all required files and directories exist."""
    print("Validating prerequisites...")
    
    required_paths = ['mobdecks', 'types']
    missing_paths = []
    
    for path_name in required_paths:
        if not paths[path_name].exists():
            missing_paths.append(f"{path_name}: {paths[path_name]}")
    
    if missing_paths:
        print("ERROR: Missing required files/directories:")
        for path in missing_paths:
            print(f"  - {path}")
        return False
    
    # Check for XML files
    xml_files = list(paths['mobdecks'].glob("*.xml"))
    if not xml_files:
        print(f"ERROR: No XML files found in {paths['mobdecks']}")
        return False
    
    print(f"✓ Found {len(xml_files)} XML files in MobDecks directory")
    print(f"✓ Types file exists: {paths['types']}")
    
    return True


def setup_output_directories(paths: dict):
    """Create output directories if they don't exist."""
    output_dirs = ['database', 'reports']
    
    for dir_name in output_dirs:
        paths[dir_name].mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory ready: {paths[dir_name]}")


def run_validation_tests(args) -> bool:
    """Run validation tests if requested."""
    if args.skip_validation:
        print("Skipping validation tests (--skip-validation)")
        return True
    
    print("Running validation tests...")
    
    try:
        # Import and run validator
        # Import validation module with proper path setup
        validation_script_dir = current_dir / "Test Scripts"
        sys.path.insert(0, str(validation_script_dir))
        from validate_deck_processing import DeckProcessingValidator
        
        validator = DeckProcessingValidator()
        
        # Run just the critical tests
        print("Testing DTO conversion...")
        dto_test = validator.test_dto_conversion()
        
        print("Testing database schema...")
        schema_test = validator.test_database_schema()
        
        validator.cleanup()
        
        if dto_test and schema_test:
            print("✓ Critical validation tests passed")
            return True
        else:
            print("✗ Validation tests failed")
            if not args.force:
                print("Use --force to proceed anyway, or --skip-validation to skip tests")
                return False
            else:
                print("Proceeding anyway due to --force flag")
                return True
                
    except ImportError:
        print("Warning: Validation module not available, skipping tests")
        return True
    except Exception as e:
        print(f"Warning: Validation failed with error: {e}")
        if args.force:
            print("Proceeding anyway due to --force flag")
            return True
        else:
            print("Use --force to proceed anyway")
            return False


def create_database_with_progress(db_path: Path, args) -> bool:
    """Create database with progress reporting."""
    print(f"\nCreating deck database: {db_path}")
    print("=" * 50)
    
    try:
        # Create database creator
        creator = DatabaseCreator(db_path)
        
        # Process decks and create database
        success = creator.create_full_database()
        
        if success:
            print(f"\n✓ Database created successfully: {db_path}")
            
            # Show database statistics
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                print(f"✓ Database size: {size_mb:.2f} MB")
            
            return True
        else:
            print(f"\n✗ Database creation failed")
            return False
            
    except Exception as e:
        print(f"\n✗ Database creation failed with error: {e}")
        return False


def print_completion_summary(db_path: Path, paths: dict):
    """Print completion summary and next steps."""
    print("\n" + "=" * 60)
    print("DECK DATABASE CREATION COMPLETE")
    print("=" * 60)
    
    print(f"Database file: {db_path}")
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"Database size: {size_mb:.2f} MB")
    
    print(f"Reports directory: {paths['reports']}")
    
    print("\nGenerated files:")
    
    # Check for database
    if db_path.exists():
        print(f"  ✓ {db_path.name}")
    
    # Check for reports
    if paths['reports'].exists():
        report_files = list(paths['reports'].glob("*.txt"))
        for report in report_files:
            print(f"  ✓ {report.name}")
    
    print("\nNext steps:")
    print("  1. Examine reports in the Reports/Deck Reports directory")
    print("  2. Use SQLite tools to query the database")
    print("  3. Run analysis queries using the provided views")
    
    print("\nExample queries:")
    print("  SELECT * FROM deck_summary LIMIT 10;")
    print("  SELECT * FROM top_spells LIMIT 20;")
    print("  SELECT * FROM school_distribution;")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create Wizard101 deck database from XML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python database_creator.py
  python database_creator.py --output-dir /custom/path
  python database_creator.py --skip-validation --force
        """
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Custom output directory for database and reports'
    )
    
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip validation tests before database creation'
    )
    
    parser.add_argument(
        '--force',
        action='store_true', 
        help='Proceed even if validation tests fail'
    )
    
    parser.add_argument(
        '--database-name',
        default='wizard101_decks.db',
        help='Name for the output database file'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("Wizard101 Deck Database Creator")
    print("=" * 40)
    print(f"Started: {datetime.now()}")
    print()
    
    # Get paths
    paths = get_platform_paths()
    
    # Override output directory if specified
    if args.output_dir:
        paths['database'] = args.output_dir / "database"
        paths['reports'] = args.output_dir / "reports"
        print(f"Using custom output directory: {args.output_dir}")
    
    # Validate prerequisites
    if not validate_prerequisites(paths):
        print("\nPrerequisite validation failed. Please check your setup.")
        return 1
    
    # Setup output directories
    setup_output_directories(paths)
    
    # Run validation if requested
    if not run_validation_tests(args):
        print("\nValidation failed. Database creation aborted.")
        return 1
    
    # Create database
    db_path = paths['database'] / args.database_name
    success = create_database_with_progress(db_path, args)
    
    if success:
        print_completion_summary(db_path, paths)
        return 0
    else:
        print("\nDatabase creation failed. Check error messages above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)