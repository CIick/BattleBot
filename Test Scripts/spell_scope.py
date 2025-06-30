#!/usr/bin/env python3
"""
Spell Analysis Script for Wizard101
Analyzes all spell XML files in Root.wad to understand parameter structure variations
"""

import json
import os
import platform
import sys
from pathlib import Path
from typing import Set, Dict, Any, Optional
from collections import defaultdict

import katsuba
from katsuba.wad import Archive
from katsuba.op import LazyObject, TypeList, Serializer, SerializerOptions


def get_platform_paths():
    """Get platform-specific paths for WAD and types files"""
    system = platform.system().lower()
    
    if system == "windows":
        wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("C:/Github Repos Python/QuestWhiz/types/r777820_Wizard_1_580_0_Live.json")
    else:  # Linux or other
        # For Linux (Claude environment), we'll need to handle missing files gracefully
        wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("/mnt/c/Github Repos Python/QuestWhiz/types/r777820_Wizard_1_580_0_Live.json")
    
    return wad_path, types_path


def load_type_list(types_path: Path) -> Optional[TypeList]:
    """Load TypeList from the QuestWhiz types JSON file"""
    try:
        if not types_path.exists():
            print(f"Warning: Types file not found at {types_path}")
            return None
            
        # Use TypeList.open() to load from file path
        type_list = TypeList.open(str(types_path))
        print(f"Loaded type definitions from {types_path}")
        return type_list
        
    except Exception as e:
        print(f"Error loading types file: {e}")
        return None


def open_wad_archive(wad_path: Path) -> Optional[Archive]:
    """Open the WAD archive file"""
    try:
        if not wad_path.exists():
            print(f"Error: WAD file not found at {wad_path}")
            return None
            
        # Try memory mapping first, fall back to heap if needed
        try:
            archive = Archive.mmap(str(wad_path))
            print(f"Opened WAD archive (mmap): {wad_path}")
        except Exception:
            archive = Archive.heap(str(wad_path))
            print(f"Opened WAD archive (heap): {wad_path}")
            
        return archive
        
    except Exception as e:
        print(f"Error opening WAD archive: {e}")
        return None


def extract_parameters_recursive(obj: Any, type_list: Optional[TypeList], path: str = "") -> Set[str]:
    """Recursively extract all parameter names from an object"""
    parameters = set()
    
    try:
        if isinstance(obj, LazyObject):
            # Handle LazyObject with type conversion
            if type_list:
                try:
                    lazy_dict = {k: v for k, v in obj.items(type_list)}
                    type_name = type_list.name_for(obj.type_hash)
                    lazy_dict["$__type"] = type_name
                    
                    # Add the type parameter
                    parameters.add("$__type")
                    
                    # Recursively process the converted dictionary
                    for key, value in lazy_dict.items():
                        if key != "$__type":  # Don't recurse on our added type field
                            parameters.add(key)
                            sub_params = extract_parameters_recursive(value, type_list, f"{path}.{key}")
                            parameters.update(sub_params)
                except Exception as e:
                    print(f"Warning: Could not process LazyObject at {path}: {e}")
                    # Fall back to basic iteration
                    for key in obj:
                        parameters.add(key)
        
        elif isinstance(obj, dict):
            # Handle regular dictionaries
            for key, value in obj.items():
                parameters.add(key)
                sub_params = extract_parameters_recursive(value, type_list, f"{path}.{key}")
                parameters.update(sub_params)
                
        elif isinstance(obj, (list, tuple)):
            # Handle lists/tuples
            for i, item in enumerate(obj):
                sub_params = extract_parameters_recursive(item, type_list, f"{path}[{i}]")
                parameters.update(sub_params)
                
        elif hasattr(obj, '__dict__'):
            # Handle objects with attributes
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):  # Skip private attributes
                    parameters.add(key)
                    sub_params = extract_parameters_recursive(value, type_list, f"{path}.{key}")
                    parameters.update(sub_params)
    
    except Exception as e:
        print(f"Warning: Error processing object at {path}: {e}")
    
    return parameters


def analyze_spells(archive: Archive, type_list: Optional[TypeList]) -> Dict[str, Any]:
    """Analyze all spells in the archive and return parameter analysis"""
    
    # Data collection structures
    all_parameters = set()
    parameter_first_seen = {}  # parameter -> first file it was seen in
    type_classes = set()
    type_class_first_seen = {}  # type class -> first file it was seen in
    processed_files = 0
    failed_files = 0
    
    print("Searching for spell files in the archive...")
    
    try:
        # Find all files in the spells folder (note: capital S)
        spell_files = list(archive.iter_glob("Spells/*"))
        print(f"Found {len(spell_files)} files in Spells folder")
        
        # Filter for XML files (assuming they have certain extensions)
        xml_files = [f for f in spell_files if f.lower().endswith(('.xml', '.spell'))]
        if not xml_files:
            # If no .xml files, try all files
            xml_files = spell_files
            
        print(f"Processing {len(xml_files)} spell files...")
        
        # Create serializer if we have type list
        serializer = None
        if type_list:
            options = SerializerOptions()
            serializer = Serializer(options, type_list)
        
        for file_path in xml_files:
            try:
                print(f"Processing: {file_path}")
                
                if serializer:
                    # Deserialize with type information
                    spell_data = archive.deserialize(file_path, serializer)
                else:
                    # Try basic deserialization without types
                    spell_data = archive[file_path]
                
                # Extract parameters from this spell
                file_parameters = extract_parameters_recursive(spell_data, type_list)
                
                # Track new parameters
                for param in file_parameters:
                    if param not in all_parameters:
                        parameter_first_seen[param] = file_path
                    all_parameters.add(param)
                
                # Extract type information if available
                if isinstance(spell_data, LazyObject) and type_list:
                    try:
                        type_name = type_list.name_for(spell_data.type_hash)
                        if type_name not in type_classes:
                            type_class_first_seen[type_name] = file_path
                        type_classes.add(type_name)
                    except Exception:
                        pass
                
                processed_files += 1
                
                if processed_files % 10 == 0:
                    print(f"Processed {processed_files} files, found {len(all_parameters)} unique parameters so far...")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                failed_files += 1
                continue
    
    except Exception as e:
        print(f"Error during spell analysis: {e}")
    
    return {
        'all_parameters': all_parameters,
        'parameter_first_seen': parameter_first_seen,
        'type_classes': type_classes,
        'type_class_first_seen': type_class_first_seen,
        'processed_files': processed_files,
        'failed_files': failed_files
    }


def write_analysis_report(analysis_data: Dict[str, Any], output_file: str):
    """Write the analysis results to a log file"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Wizard101 Spell Parameter Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Summary:\n")
        f.write(f"- Processed files: {analysis_data['processed_files']}\n")
        f.write(f"- Failed files: {analysis_data['failed_files']}\n")
        f.write(f"- Unique parameters found: {len(analysis_data['all_parameters'])}\n")
        f.write(f"- Unique type classes found: {len(analysis_data['type_classes'])}\n\n")
        
        # Write type classes
        f.write("Type Classes Found:\n")
        f.write("-" * 20 + "\n")
        for type_class in sorted(analysis_data['type_classes']):
            first_file = analysis_data['type_class_first_seen'][type_class]
            f.write(f"{type_class} | {first_file}\n")
        f.write("\n")
        
        # Write all parameters
        f.write("All Parameters Found:\n")
        f.write("-" * 20 + "\n")
        for param in sorted(analysis_data['all_parameters']):
            first_file = analysis_data['parameter_first_seen'][param]
            f.write(f"{param} | {first_file}\n")
        
    print(f"Analysis report written to: {output_file}")


def main():
    """Main function to run the spell analysis"""
    print("Wizard101 Spell Parameter Analysis")
    print("=" * 40)
    
    # Get platform-specific paths
    wad_path, types_path = get_platform_paths()
    print(f"WAD Path: {wad_path}")
    print(f"Types Path: {types_path}")
    
    # Load type definitions
    print("\nLoading type definitions...")
    type_list = load_type_list(types_path)
    
    # Open WAD archive
    print("\nOpening WAD archive...")
    archive = open_wad_archive(wad_path)
    if not archive:
        print("Failed to open WAD archive. Exiting.")
        return 1
    
    # Analyze spells
    print("\nAnalyzing spell files...")
    analysis_data = analyze_spells(archive, type_list)
    
    # Write report
    output_file = "../Reports/spell_analysis_report.txt"
    print(f"\nWriting analysis report...")
    write_analysis_report(analysis_data, output_file)
    
    # Print summary
    print(f"\nAnalysis Complete!")
    print(f"Processed: {analysis_data['processed_files']} files")
    print(f"Failed: {analysis_data['failed_files']} files") 
    print(f"Unique parameters: {len(analysis_data['all_parameters'])}")
    print(f"Unique type classes: {len(analysis_data['type_classes'])}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())