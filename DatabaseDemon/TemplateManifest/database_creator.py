#!/usr/bin/env python3
"""
TemplateManifest Database Creator - Main Entry Point
===================================================

Creates SQLite database from Wizard101 Root.wad TemplateManifest.xml file.
Provides template ID to deck filename mapping for linking mob item lists to deck data.

This script:
1. Processes TemplateManifest.xml from Root.wad using katsuba
2. Creates normalized database with comprehensive template mapping
3. Handles platform detection and comprehensive error logging
4. Stores template data with categorization and analysis
5. Enables fast lookup of template IDs to deck filenames

Usage:
    python database_creator.py [--output-dir PATH] [--skip-validation]

Requirements:
    - types.json file in parent DatabaseDemon directory
    - Wizard101 installed with accessible Root.wad file
    - Python packages: katsuba, sqlite3 (built-in)

Output:
    - database/template_manifest_{timestamp}.db - SQLite database
    - Reports/TemplateManifest Reports/ - Analysis and statistics reports

Key Use Case:
    Mob m_itemList contains template IDs like [211553, 4589, 324086]
    -> Look up template ID 211553 in database
    -> Get deck filename "ObjectData/Decks/Mdeck-I-R9.xml"
    -> Load corresponding deck data for mob analysis
"""

import sys
import os
import argparse
from pathlib import Path
import platform
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from processors import TemplateManifestDatabaseCreator


def get_platform_paths():
    """Get platform-specific paths for WAD and types files"""
    system = platform.system().lower()
    
    if system == "windows":
        wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("../types.json")
    else:  # Linux/WSL
        wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("../types.json")
    
    return wad_path, types_path


def check_prerequisites():
    """Check that all prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check for types.json file
    wad_path, types_path = get_platform_paths()
    
    if not types_path.exists():
        print("ERROR: types.json file not found in DatabaseDemon directory")
        print(f"Expected location: {types_path.absolute()}")
        print("Please copy the correct types.json file for your Wizard101 revision")
        return False
    
    print(f"[OK] Found types.json at {types_path}")
    
    # Check for Root.wad file
    if not wad_path.exists():
        print("ERROR: Root.wad file not found")
        print(f"Expected location: {wad_path}")
        print("Please ensure Wizard101 is installed and accessible")
        return False
    
    print(f"[OK] Found Root.wad at {wad_path}")
    
    # Check katsuba availability
    try:
        import katsuba
        print("[OK] Katsuba library available")
    except ImportError:
        print("ERROR: katsuba library not found")
        print("Please install katsuba: pip install katsuba")
        return False
    
    print("[OK] All prerequisites met")
    return True


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Create TemplateManifest database from Wizard101 Root.wad",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python database_creator.py
    python database_creator.py --output-dir /custom/path
    python database_creator.py --skip-validation

Output:
    Database will be created with template ID to deck filename mappings.
    Use this database to resolve mob m_itemList values to deck files.
        """
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('.'),
        help='Output directory for database and reports (default: current directory)'
    )
    
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip validation for faster processing'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force database creation even if validation fails'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def print_usage_examples():
    """Print usage examples for the created database"""
    print("\n" + "=" * 60)
    print("DATABASE USAGE EXAMPLES")
    print("=" * 60)
    print("""
After creating the database, you can use it to look up template IDs:

Python Example:
    import sqlite3
    conn = sqlite3.connect('database/template_manifest_YYYYMMDD_HHMMSS.db')
    cursor = conn.cursor()
    
    # Look up deck filename for template ID 211553
    cursor.execute("SELECT filename, deck_name FROM template_locations WHERE template_id = ?", (211553,))
    result = cursor.fetchone()
    if result:
        print(f"Template 211553 -> {result[0]} ({result[1]})")

SQL Examples:
    -- Find all mob decks
    SELECT template_id, deck_name FROM template_locations WHERE is_mob_deck = TRUE;
    
    -- Find deck for specific template ID
    SELECT * FROM template_lookup WHERE template_id = 211553;
    
    -- Get all Fire school decks
    SELECT * FROM template_locations WHERE deck_category = 'fire';

Common Use Case:
    If mob has m_itemList = [211553, 4589, 324086]:
    1. Look up each template ID in database
    2. Get corresponding deck filenames
    3. Load deck data to analyze mob's spell capabilities
    """)


def main():
    """Main entry point"""
    print("Wizard101 TemplateManifest Database Creator")
    print("=" * 50)
    print(f"Platform: {platform.system()}")
    print(f"Started: {datetime.now()}")
    print()
    
    # Parse arguments
    args = parse_arguments()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPrerequisites not met. Please fix the issues above.")
        return 1
    
    try:
        # Create output directory
        args.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {args.output_dir.absolute()}")
        
        # Create database
        print("\nStarting TemplateManifest database creation...")
        creator = TemplateManifestDatabaseCreator(args.output_dir)
        
        success = creator.create_database(skip_validation=args.skip_validation)
        
        if success:
            print("\n" + "=" * 50)
            print("SUCCESS: TemplateManifest database created!")
            print("=" * 50)
            
            # Get statistics
            stats = creator.get_processing_statistics()
            print(f"Templates processed: {stats.get('templates_processed', 0)}")
            print(f"Templates inserted: {stats.get('templates_inserted', 0)}")
            print(f"Processing time: {stats.get('duration', 0):.2f} seconds")
            
            if 'template_manifest_stats' in stats:
                manifest_stats = stats['template_manifest_stats']
                print(f"Template types: {len(manifest_stats.get('template_types', {}))}")
                print(f"Template categories: {len(manifest_stats.get('template_categories', {}))}")
            
            # Print database location
            if hasattr(creator, 'db_path') and creator.db_path:
                print(f"\nDatabase created: {creator.db_path}")
                print(f"Reports directory: {creator.reports_dir}")
            
            # Print usage examples
            if args.verbose:
                print_usage_examples()
            
            return 0
        else:
            print("\n" + "=" * 50)
            print("FAILURE: Database creation failed!")
            print("=" * 50)
            print("Please check the error messages above.")
            
            if not args.force:
                return 1
            else:
                print("Continuing due to --force flag...")
                return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())