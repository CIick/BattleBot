#!/usr/bin/env python3
"""
Deck Type Analysis Script
========================
Analyzes all deck XML files to identify required types from types.json files.

This script:
1. Scans all XML files in MobDecks directory
2. Extracts type hashes from the JSON data
3. Maps them to type definitions from types.json and deck_types.json
4. Generates comprehensive type requirements report
5. Validates against mobdeckbehaviortypes.json

Usage:
    python analyze_deck_types.py

Output:
    - Console report of type analysis
    - type_requirements_report.txt with detailed findings
"""

import json
import os
import platform
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any

def get_platform_paths():
    """Get platform-specific paths for deck and type files."""
    system = platform.system().lower()
    if system == "windows":
        deck_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/Decks/MobDecks")
        types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json")
        deck_types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/deck_types.json")
        mob_deck_types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/mobdeckbehaviortypes.json")
    else:  # Linux/WSL
        deck_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/Decks/MobDecks")
        types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
        deck_types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/deck_types.json")
        mob_deck_types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/mobdeckbehaviortypes.json")
    
    return deck_path, types_path, deck_types_path, mob_deck_types_path

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and return JSON file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def analyze_deck_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single deck XML file and extract type information."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Parse the JSON content from the XML file
        deck_data = json.loads(content)
        
        analysis = {
            'filename': file_path.name,
            'type_hash': deck_data.get('$__type'),
            'has_behaviors': len(deck_data.get('m_behaviors', [])) > 0,
            'behavior_count': len(deck_data.get('m_behaviors', [])),
            'has_name': bool(deck_data.get('m_name')),
            'name': deck_data.get('m_name', ''),
            'has_spell_list': bool(deck_data.get('m_spellNameList')),
            'spell_count': len(deck_data.get('m_spellNameList', [])),
            'spell_names': deck_data.get('m_spellNameList', []),
            'behaviors': deck_data.get('m_behaviors', []),
            'raw_data': deck_data
        }
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {
            'filename': file_path.name,
            'error': str(e),
            'type_hash': None
        }

def find_type_definition(type_hash: str, types_data: Dict, deck_types_data: Dict) -> Dict[str, Any]:
    """Find type definition in either types.json or deck_types.json."""
    # Check main types.json first
    if 'classes' in types_data and type_hash in types_data['classes']:
        return {
            'source': 'types.json',
            'definition': types_data['classes'][type_hash]
        }
    
    # Check deck_types.json
    if 'classes' in deck_types_data and type_hash in deck_types_data['classes']:
        return {
            'source': 'deck_types.json', 
            'definition': deck_types_data['classes'][type_hash]
        }
    
    return {
        'source': 'not_found',
        'definition': None
    }

def analyze_all_decks():
    """Main analysis function."""
    print("Deck Type Analysis Starting...")
    print("=" * 50)
    
    # Get platform-specific paths
    deck_path, types_path, deck_types_path, mob_deck_types_path = get_platform_paths()
    
    # Validate paths exist
    if not deck_path.exists():
        print(f"ERROR: Deck directory not found: {deck_path}")
        return
    
    if not types_path.exists():
        print(f"ERROR: Types file not found: {types_path}")
        return
        
    print(f"Deck directory: {deck_path}")
    print(f"Types file: {types_path}")
    print(f"Deck types file: {deck_types_path}")
    print(f"Mob deck behavior types file: {mob_deck_types_path}")
    print()
    
    # Load type definition files
    print("Loading type definition files...")
    types_data = load_json_file(types_path)
    deck_types_data = load_json_file(deck_types_path) if deck_types_path.exists() else {}
    mob_deck_types_data = load_json_file(mob_deck_types_path) if mob_deck_types_path.exists() else {}
    
    print(f"Main types loaded: {len(types_data.get('classes', {})):,}")
    print(f"Deck types loaded: {len(deck_types_data.get('classes', {})):,}")
    print(f"Mob deck behavior types loaded: {len(mob_deck_types_data.get('classes', {}))}")
    print()
    
    # Find all XML files in MobDecks directory
    xml_files = list(deck_path.glob("*.xml"))
    print(f"Found {len(xml_files)} XML files to analyze")
    print()
    
    # Analyze each file
    analyses = []
    type_hash_counter = Counter()
    successful_parses = 0
    failed_parses = 0
    
    print("Analyzing deck files...")
    for i, xml_file in enumerate(xml_files):
        if i % 100 == 0:
            print(f"Progress: {i:,}/{len(xml_files):,} files processed")
            
        analysis = analyze_deck_file(xml_file)
        analyses.append(analysis)
        
        if 'error' in analysis:
            failed_parses += 1
        else:
            successful_parses += 1
            if analysis['type_hash']:
                type_hash_counter[str(analysis['type_hash'])] += 1
    
    print(f"Analysis complete!")
    print(f"Successful parses: {successful_parses:,}")
    print(f"Failed parses: {failed_parses:,}")
    print()
    
    # Analyze type usage
    print("Type Hash Analysis:")
    print("-" * 30)
    required_types = {}
    
    for type_hash, count in type_hash_counter.most_common():
        type_def = find_type_definition(type_hash, types_data, deck_types_data)
        class_name = type_def['definition']['name'] if type_def['definition'] else 'UNKNOWN'
        
        print(f"Hash {type_hash}: {count:,} files - {class_name} [{type_def['source']}]")
        required_types[type_hash] = {
            'count': count,
            'class_name': class_name,
            'source': type_def['source'],
            'definition': type_def['definition']
        }
    
    print()
    
    # Analyze behavior usage
    behaviors_found = []
    for analysis in analyses:
        if not analysis.get('error') and analysis.get('behaviors'):
            behaviors_found.extend(analysis['behaviors'])
    
    print(f"Behaviors found in {len([a for a in analyses if a.get('behavior_count', 0) > 0])} decks")
    print(f"Total behavior instances: {len(behaviors_found)}")
    print()
    
    # Analyze spell name patterns
    all_spell_names = []
    for analysis in analyses:
        if not analysis.get('error') and analysis.get('spell_names'):
            all_spell_names.extend(analysis['spell_names'])
    
    spell_name_counter = Counter(all_spell_names)
    print(f"Unique spell names found: {len(spell_name_counter)}")
    print(f"Total spell references: {len(all_spell_names):,}")
    print()
    
    print("Most common spells:")
    for spell_name, count in spell_name_counter.most_common(10):
        print(f"  {spell_name}: {count:,}")
    print()
    
    # Generate detailed report
    report_path = deck_path.parent / "type_requirements_report.txt"
    print(f"Generating detailed report: {report_path}")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Deck Type Requirements Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Analysis Date: {__import__('datetime').datetime.now()}\n")
        f.write(f"Files Analyzed: {len(xml_files):,}\n")
        f.write(f"Successful Parses: {successful_parses:,}\n")
        f.write(f"Failed Parses: {failed_parses:,}\n\n")
        
        f.write("REQUIRED TYPE DEFINITIONS\n")
        f.write("-" * 30 + "\n")
        for type_hash, info in required_types.items():
            f.write(f"Type Hash: {type_hash}\n")
            f.write(f"  Class Name: {info['class_name']}\n")
            f.write(f"  Source: {info['source']}\n")
            f.write(f"  Usage Count: {info['count']:,}\n")
            if info['definition']:
                f.write(f"  Properties: {list(info['definition'].get('properties', {}).keys())}\n")
            f.write("\n")
        
        f.write("SPELL NAME ANALYSIS\n")
        f.write("-" * 20 + "\n")
        f.write(f"Unique spell names: {len(spell_name_counter)}\n")
        f.write(f"Total spell references: {len(all_spell_names):,}\n\n")
        
        f.write("Top 20 Most Common Spells:\n")
        for spell_name, count in spell_name_counter.most_common(20):
            f.write(f"  {spell_name}: {count:,}\n")
        
        f.write("\nBEHAVIOR ANALYSIS\n")
        f.write("-" * 17 + "\n")
        f.write(f"Decks with behaviors: {len([a for a in analyses if a.get('behavior_count', 0) > 0])}\n")
        f.write(f"Total behavior instances: {len(behaviors_found)}\n")
        
        if failed_parses > 0:
            f.write("\nFAILED PARSES\n")
            f.write("-" * 13 + "\n")
            for analysis in analyses:
                if 'error' in analysis:
                    f.write(f"{analysis['filename']}: {analysis['error']}\n")
    
    print("Analysis complete! Check the report file for detailed findings.")
    print()
    print("SUMMARY FOR DTO CREATION:")
    print("=" * 30)
    print("Required DTO classes based on analysis:")
    for type_hash, info in required_types.items():
        print(f"- {info['class_name']}DTO (hash: {type_hash})")
    
    return analyses, required_types

if __name__ == "__main__":
    analyze_all_decks()