#!/usr/bin/env python3
"""
Comprehensive WAD Spell Processing with Recursive DTO Testing
============================================================
Processes all 16,405+ spell XML files from Root.wad and tests our enhanced DTOs
with detailed tracking of recursive nested object creation.

Outputs:
- all_spells_partX.txt (100MB chunks) with full XML data
- spell_failures.txt with detailed failure analysis
- Console progress with success/failure tracking
"""

import json
import os
import platform
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import traceback

import katsuba
from katsuba.wad import Archive
from katsuba.op import LazyObject, LazyList, TypeList, Serializer, SerializerOptions

# Import our fixed DTOs
try:
    import fixed_wizard101_spell_dtos as dtos
    print("[OK] Successfully imported fixed DTOs")
except ImportError as e:
    print(f"[FAIL] Failed to import fixed DTOs: {e}")
    sys.exit(1)


class SpellProcessingManager:
    """Manages the processing of all spells with file splitting and detailed logging"""
    
    def __init__(self, max_file_size_mb: int = 100):
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.current_file_num = 1
        self.current_file_size = 0
        self.current_file_handle = None
        
        # Statistics
        self.total_processed = 0
        self.total_success = 0
        self.total_failures = 0
        self.nested_dto_successes = 0
        self.max_recursion_depth = 0
        
        # Error tracking
        self.error_categories = {}
        self.failure_log_handle = None
        
    def start_processing(self):
        """Initialize the processing"""
        self.open_next_output_file()
        self.failure_log_handle = open("../Reports/Spell Reports/spell_failures.txt", 'w', encoding='utf-8')
        self.failure_log_handle.write("Wizard101 Spell DTO Failure Analysis\n")
        self.failure_log_handle.write("=" * 50 + "\n\n")
    
    def open_next_output_file(self):
        """Open the next output file in the sequence"""
        if self.current_file_handle:
            self.current_file_handle.close()
        
        filename = f"all_spells_part{self.current_file_num}.txt"
        self.current_file_handle = open(filename, 'w', encoding='utf-8')
        self.current_file_handle.write(f"Wizard101 Spell Data - Part {self.current_file_num}\n")
        self.current_file_handle.write("=" * 50 + "\n\n")
        self.current_file_size = 0
        print(f"[INFO] Started writing to {filename}")
    
    def check_file_size_and_rotate(self):
        """Check if current file exceeds size limit and rotate if needed"""
        if self.current_file_size >= self.max_file_size:
            self.current_file_num += 1
            self.open_next_output_file()
    
    def write_to_output(self, content: str):
        """Write content to current output file and track size"""
        self.current_file_handle.write(content)
        self.current_file_size += len(content.encode('utf-8'))
        self.check_file_size_and_rotate()
    
    def analyze_nested_dtos(self, dto_obj: Any, path: str = "", depth: int = 0) -> Tuple[List[str], int]:
        """Recursively analyze created DTOs to show nesting structure"""
        nested_dtos = []
        max_depth = depth
        
        if hasattr(dto_obj, '__dict__'):
            for attr_name, attr_value in dto_obj.__dict__.items():
                current_path = f"{path}.{attr_name}" if path else attr_name
                
                # Check if this is a DTO object
                if hasattr(attr_value, '__class__') and attr_value.__class__.__name__.endswith('DTO'):
                    nested_dtos.append(f"  - {current_path}: {attr_value.__class__.__name__} ✓")
                    # Recurse into this DTO
                    sub_dtos, sub_depth = self.analyze_nested_dtos(attr_value, current_path, depth + 1)
                    nested_dtos.extend(sub_dtos)
                    max_depth = max(max_depth, sub_depth)
                
                elif isinstance(attr_value, list):
                    # Handle lists that might contain DTOs
                    for i, item in enumerate(attr_value):
                        if hasattr(item, '__class__') and item.__class__.__name__.endswith('DTO'):
                            list_path = f"{current_path}[{i}]"
                            nested_dtos.append(f"  - {list_path}: {item.__class__.__name__} ✓")
                            # Recurse into list item DTO
                            sub_dtos, sub_depth = self.analyze_nested_dtos(item, list_path, depth + 1)
                            nested_dtos.extend(sub_dtos)
                            max_depth = max(max_depth, sub_depth)
        
        return nested_dtos, max_depth
    
    def process_spell_success(self, file_path: str, spell_dict: Dict[str, Any], spell_dto: Any):
        """Process a successful spell conversion"""
        self.total_success += 1
        
        # Analyze nested DTOs
        nested_dtos, recursion_depth = self.analyze_nested_dtos(spell_dto)
        self.max_recursion_depth = max(self.max_recursion_depth, recursion_depth)
        
        if nested_dtos:
            self.nested_dto_successes += 1
        
        # Check inheritance
        inheritance_info = ""
        dto_type = type(spell_dto).__name__
        if hasattr(spell_dto.__class__, '__bases__'):
            bases = [base.__name__ for base in spell_dto.__class__.__bases__]
            if len(bases) > 1 or bases[0] != 'object':  # Has real inheritance
                inheritance_info = f"INHERITANCE: {dto_type} → {' → '.join(bases)} ✓\n"
        
        # Format output
        output = f"=== SUCCESS: {file_path} ===\n"
        output += f"DTO_TYPE: {dto_type}\n"
        output += f"SPELL_NAME: {getattr(spell_dto, 'm_name', 'N/A')}\n"
        
        if nested_dtos:
            output += f"NESTED_DTOS_CREATED:\n"
            output += "\n".join(nested_dtos) + "\n"
            output += f"RECURSION_DEPTH: {recursion_depth} levels\n"
        
        if inheritance_info:
            output += inheritance_info
        
        output += f"FULL_XML_DATA:\n"
        output += json.dumps(spell_dict, indent=2, default=str) + "\n\n"
        
        self.write_to_output(output)
        
        # Console update
        if self.total_processed % 500 == 0:
            print(f"[PROGRESS] {self.total_processed} processed, {self.total_success} success, {self.total_failures} failed")
    
    def process_spell_failure(self, file_path: str, spell_dict: Dict[str, Any], error: Exception, failed_at: str = ""):
        """Process a failed spell conversion"""
        self.total_failures += 1
        
        error_type = type(error).__name__
        self.error_categories[error_type] = self.error_categories.get(error_type, 0) + 1
        
        # Write to main output
        output = f"=== FAILURE: {file_path} ===\n"
        output += f"ERROR_TYPE: {error_type}\n"
        output += f"ERROR_MSG: {str(error)}\n"
        if failed_at:
            output += f"FAILED_AT: {failed_at}\n"
        output += f"FULL_XML_DATA:\n"
        output += json.dumps(spell_dict, indent=2, default=str) + "\n\n"
        
        self.write_to_output(output)
        
        # Write detailed failure analysis
        self.failure_log_handle.write(f"FAILURE: {file_path}\n")
        self.failure_log_handle.write(f"Error Type: {error_type}\n")
        self.failure_log_handle.write(f"Error Message: {str(error)}\n")
        self.failure_log_handle.write(f"Spell Type: {spell_dict.get('$__type', 'unknown')}\n")
        self.failure_log_handle.write(f"Traceback:\n{traceback.format_exc()}\n")
        self.failure_log_handle.write("-" * 50 + "\n\n")
    
    def finish_processing(self):
        """Complete the processing and generate final summary"""
        if self.current_file_handle:
            self.current_file_handle.close()
        
        if self.failure_log_handle:
            # Write error summary to failure log
            self.failure_log_handle.write("\nERROR SUMMARY:\n")
            self.failure_log_handle.write("=" * 30 + "\n")
            for error_type, count in sorted(self.error_categories.items(), key=lambda x: x[1], reverse=True):
                self.failure_log_handle.write(f"{error_type}: {count}\n")
            self.failure_log_handle.close()
        
        # Print final statistics
        print(f"\n" + "=" * 60)
        print("COMPREHENSIVE SPELL PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"Total processed: {self.total_processed}")
        print(f"Successful DTOs: {self.total_success}")
        print(f"Failed conversions: {self.total_failures}")
        print(f"Success rate: {(self.total_success/self.total_processed*100):.1f}%")
        print(f"Spells with nested DTOs: {self.nested_dto_successes}")
        print(f"Maximum recursion depth: {self.max_recursion_depth}")
        print(f"Output files: all_spells_part1.txt through all_spells_part{self.current_file_num}.txt")
        print(f"Failure analysis: spell_failures.txt")


def get_platform_paths():
    """Get platform-specific paths for WAD and types files"""
    system = platform.system().lower()
    
    if system == "windows":
        wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("C:/Github Repos Python/QuestWhiz/types/r777820_Wizard_1_580_0_Live.json")
    else:  # Linux or other
        wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("/mnt/c/Github Repos Python/QuestWhiz/types/r777820_Wizard_1_580_0_Live.json")
    
    return wad_path, types_path


def load_type_list(types_path: Path) -> Optional[TypeList]:
    """Load TypeList from the QuestWhiz types JSON file"""
    try:
        if not types_path.exists():
            print(f"Warning: Types file not found at {types_path}")
            return None
            
        type_list = TypeList.open(str(types_path))
        print(f"[OK] Loaded type definitions from {types_path}")
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
            print(f"[OK] Opened WAD archive (mmap): {wad_path}")
        except Exception:
            archive = Archive.heap(str(wad_path))
            print(f"[OK] Opened WAD archive (heap): {wad_path}")
            
        return archive
        
    except Exception as e:
        print(f"Error opening WAD archive: {e}")
        return None


def convert_lazy_object_to_dict(obj: Any, type_list: Optional[TypeList]) -> Dict[str, Any]:
    """Convert LazyObject/LazyList to dictionary with type information"""
    # Handle LazyList objects
    if isinstance(obj, LazyList) and type_list:
        try:
            # Convert LazyList to a list of converted items
            result = []
            for item in obj:
                if isinstance(item, (LazyObject, LazyList)):
                    # Recursively convert nested LazyObjects/LazyLists
                    result.append(convert_lazy_object_to_dict(item, type_list))
                else:
                    result.append(item)
            return result
        except Exception as e:
            return {"error": f"LazyList conversion failed: {e}"}
    
    # Handle LazyObject objects
    if isinstance(obj, LazyObject) and type_list:
        try:
            # Convert LazyObject to dictionary
            result = {}
            for key, value in obj.items(type_list):
                if isinstance(value, (LazyObject, LazyList)):
                    # Recursively convert nested LazyObjects/LazyLists
                    result[key] = convert_lazy_object_to_dict(value, type_list)
                elif isinstance(value, list):
                    # Handle lists that might contain LazyObjects/LazyLists
                    result[key] = [convert_lazy_object_to_dict(item, type_list) if isinstance(item, (LazyObject, LazyList)) else item for item in value]
                else:
                    result[key] = value
            
            # Add type information
            type_name = type_list.name_for(obj.type_hash)
            result["$__type"] = type_name
            
            return result
        except Exception as e:
            return {"error": f"LazyObject conversion failed: {e}", "type_hash": getattr(obj, 'type_hash', 'unknown')}
    
    return obj


def process_all_spells(archive: Archive, type_list: Optional[TypeList]):
    """Process all spells in the archive with comprehensive DTO testing"""
    
    factory = dtos.FixedSpellDTOFactory
    manager = SpellProcessingManager(max_file_size_mb=100)
    manager.start_processing()
    
    print("Processing all spell files from WAD archive...")
    
    try:
        # Find all files in the spells folder
        spell_files = list(archive.iter_glob("Spells/*"))
        total_files = len(spell_files)
        print(f"Found {total_files} files in Spells folder")
        
        # Filter for XML files
        xml_files = [file for file in spell_files if file.lower().endswith(('.xml', '.spell'))]
        if not xml_files:
            xml_files = spell_files  # Use all files if no .xml files found
            
        print(f"Processing {len(xml_files)} spell files...")
        
        # Create serializer if we have type list
        serializer = None
        if type_list:
            options = SerializerOptions()
            serializer = Serializer(options, type_list)
        
        for i, file_path in enumerate(xml_files):
            manager.total_processed += 1
            
            try:
                # Deserialize the spell data
                if serializer:
                    spell_data = archive.deserialize(file_path, serializer)
                else:
                    spell_data = archive[file_path]
                
                # Convert to dictionary format
                if isinstance(spell_data, LazyObject):
                    spell_dict = convert_lazy_object_to_dict(spell_data, type_list)
                else:
                    spell_dict = spell_data
                
                # Check for conversion errors
                if isinstance(spell_dict, dict) and "error" in spell_dict:
                    manager.process_spell_failure(file_path, spell_dict, Exception(spell_dict["error"]), "conversion")
                    continue
                
                # Try to create DTO
                try:
                    spell_dto = factory.create_from_json_data(spell_dict)
                    
                    if spell_dto:
                        manager.process_spell_success(file_path, spell_dict, spell_dto)
                    else:
                        manager.process_spell_failure(file_path, spell_dict, Exception("No DTO created - unknown spell type"), "dto_creation")
                
                except Exception as e:
                    manager.process_spell_failure(file_path, spell_dict, e, "dto_creation")
            
            except Exception as e:
                # Even if we can't process the spell, try to get basic info
                error_dict = {"file_path": file_path, "processing_error": str(e)}
                manager.process_spell_failure(file_path, error_dict, e, "file_processing")
    
    except Exception as e:
        print(f"Fatal error during processing: {e}")
        traceback.print_exc()
    
    finally:
        manager.finish_processing()


def main():
    """Main function to test all WAD spells with comprehensive DTO analysis"""
    print("Comprehensive WAD Spell Processing with Recursive DTO Testing")
    print("=" * 60)
    
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
    
    # Process all spells
    print(f"\nProcessing all spells with comprehensive DTO testing...")
    process_all_spells(archive, type_list)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())