#!/usr/bin/env python3
"""
Comprehensive WAD Mob Processing and Validation
===============================================
Processes all mob XML files from ObjectData/**/*.xml in Root.wad and validates
WizGameObjectTemplate objects with detailed tracking.

Outputs:
- all_mobs_partX.txt (50MB chunks) with full XML data
- mob_failures.txt with detailed failure analysis
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

# Import centralized conversion utility
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.conversion_utils import convert_lazy_object_to_dict_with_hash_only


class MobProcessingManager:
    """Manages the processing of all mobs with file splitting and detailed logging"""
    
    def __init__(self, max_file_size_mb: int = 50):
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.current_file_num = 1
        self.current_file_size = 0
        self.current_file_handle = None
        
        # Statistics
        self.total_processed = 0
        self.total_success = 0
        self.total_failures = 0
        self.total_non_mobs = 0  # Objects that aren't WizGameObjectTemplate
        self.behavior_types_found = set()
        
        # Error tracking
        self.error_categories = {}
        self.failure_log_handle = None
        
    def start_processing(self):
        """Initialize the processing"""
        # Ensure Reports/Mob Reports directory exists
        reports_dir = Path("../../Reports/Mob Reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.open_next_output_file()
        self.failure_log_handle = open("../../Reports/Mob Reports/mob_failures.txt", 'w', encoding='utf-8')
        self.failure_log_handle.write("Wizard101 Mob Validation Failure Analysis\n")
        self.failure_log_handle.write("=" * 50 + "\n\n")
    
    def open_next_output_file(self):
        """Open the next output file in the sequence"""
        if self.current_file_handle:
            self.current_file_handle.close()
        
        # Output to Reports/Mob Reports directory
        reports_dir = Path("../../Reports/Mob Reports")
        filename = reports_dir / f"all_mobs_part{self.current_file_num}.txt"
        self.current_file_handle = open(filename, 'w', encoding='utf-8')
        self.current_file_handle.write(f"Wizard101 Mob Data - Part {self.current_file_num}\n")
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
    
    def analyze_mob_behaviors(self, mob_dict: Dict[str, Any]) -> List[str]:
        """Analyze mob behaviors and extract useful information"""
        behaviors_info = []
        
        if 'm_behaviors' in mob_dict and isinstance(mob_dict['m_behaviors'], list):
            for i, behavior in enumerate(mob_dict['m_behaviors']):
                if behavior is None:
                    behaviors_info.append(f"  - behaviors[{i}]: null")
                    continue
                    
                if isinstance(behavior, dict) and 'm_behaviorName' in behavior:
                    behavior_name = behavior['m_behaviorName']
                    behavior_type = behavior.get('$__type', 'unknown')
                    self.behavior_types_found.add(behavior_name)
                    
                    # Extract key information based on behavior type
                    extra_info = ""
                    if behavior_name == "NPCBehavior":
                        level = behavior.get('m_nLevel', 'N/A')
                        health = behavior.get('m_nStartingHealth', 'N/A')
                        school = behavior.get('m_schoolOfFocus', 'N/A')
                        extra_info = f" (Level: {level}, Health: {health}, School: {school})"
                    elif behavior_name == "AnimationBehavior":
                        asset = behavior.get('m_assetName', 'N/A')
                        extra_info = f" (Asset: {asset})"
                    elif behavior_name == "WizardEquipmentBehavior":
                        items = behavior.get('m_itemList', [])
                        extra_info = f" (Items: {len(items)})"
                    
                    behaviors_info.append(f"  - behaviors[{i}]: {behavior_name} (type: {behavior_type}){extra_info}")
                else:
                    behaviors_info.append(f"  - behaviors[{i}]: Unknown behavior structure")
        
        return behaviors_info
    
    def process_mob_success(self, file_path: str, mob_dict: Dict[str, Any]):
        """Process a successful mob validation"""
        self.total_success += 1
        
        # Analyze behaviors
        behaviors_info = self.analyze_mob_behaviors(mob_dict)
        
        # Extract key mob information
        mob_name = mob_dict.get('m_objectName', 'N/A')
        display_name = mob_dict.get('m_displayName', 'N/A')
        template_id = mob_dict.get('m_templateID', 'N/A')
        primary_school = mob_dict.get('m_primarySchoolName', 'N/A')
        
        # Format output
        output = f"=== SUCCESS: {file_path} ===\n"
        output += f"MOB_NAME: {mob_name}\n"
        output += f"DISPLAY_NAME: {display_name}\n"
        output += f"TEMPLATE_ID: {template_id}\n"
        output += f"PRIMARY_SCHOOL: {primary_school}\n"
        
        if behaviors_info:
            output += f"BEHAVIORS_FOUND:\n"
            output += "\n".join(behaviors_info) + "\n"
        
        output += f"FULL_XML_DATA:\n"
        output += json.dumps(mob_dict, indent=2, default=str) + "\n\n"
        
        self.write_to_output(output)
        
        # Console update
        if self.total_processed % 100 == 0:
            print(f"[PROGRESS] {self.total_processed} processed, {self.total_success} mobs, {self.total_non_mobs} non-mobs, {self.total_failures} failed")
    
    def process_mob_failure(self, file_path: str, mob_dict: Dict[str, Any], error: Exception, failed_at: str = ""):
        """Process a failed mob validation"""
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
        output += json.dumps(mob_dict, indent=2, default=str) + "\n\n"
        
        self.write_to_output(output)
        
        # Write detailed failure analysis
        self.failure_log_handle.write(f"FAILURE: {file_path}\n")
        self.failure_log_handle.write(f"Error Type: {error_type}\n")
        self.failure_log_handle.write(f"Error Message: {str(error)}\n")
        self.failure_log_handle.write(f"Object Type: {mob_dict.get('$__type', 'unknown')}\n")
        self.failure_log_handle.write(f"Traceback:\n{traceback.format_exc()}\n")
        self.failure_log_handle.write("-" * 50 + "\n\n")
    
    def process_non_mob(self, file_path: str, obj_dict: Dict[str, Any]):
        """Process objects that aren't WizGameObjectTemplate"""
        self.total_non_mobs += 1
        # We don't output these to keep the files focused on actual mobs
    
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
            
            # Write behavior types summary
            self.failure_log_handle.write("\nBEHAVIOR TYPES FOUND:\n")
            self.failure_log_handle.write("=" * 30 + "\n")
            for behavior_type in sorted(self.behavior_types_found):
                self.failure_log_handle.write(f"{behavior_type}\n")
            
            self.failure_log_handle.close()
        
        # Print final statistics
        print(f"\n" + "=" * 60)
        print("COMPREHENSIVE MOB PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"Total files processed: {self.total_processed}")
        print(f"Valid mobs found: {self.total_success}")
        print(f"Non-mob objects: {self.total_non_mobs}")
        print(f"Failed conversions: {self.total_failures}")
        if self.total_success > 0:
            print(f"Mob success rate: {(self.total_success/(self.total_success + self.total_failures)*100):.1f}%")
        print(f"Behavior types found: {len(self.behavior_types_found)}")
        print(f"Output files: all_mobs_part1.txt through all_mobs_part{self.current_file_num}.txt")
        print(f"Failure analysis: mob_failures.txt")
        print(f"Reports saved to: Reports/Mob Reports/")


def get_platform_paths():
    """Get platform-specific paths for WAD and types files"""
    system = platform.system().lower()
    
    if system == "windows":
        wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    else:  # Linux or other
        wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    
    return wad_path, types_path


def load_type_list(types_path: Path) -> Optional[TypeList]:
    """Load TypeList from the types JSON file"""
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




def process_all_mobs(archive: Archive, type_list: Optional[TypeList]):
    """Process all ObjectData files in the archive and validate WizGameObjectTemplate objects"""
    
    manager = MobProcessingManager(max_file_size_mb=50)
    manager.start_processing()
    
    print("Processing all ObjectData files from WAD archive...")
    
    try:
        # Find all files in the ObjectData folder recursively
        object_files = list(archive.iter_glob("ObjectData/**/*.xml"))
        total_files = len(object_files)
        print(f"Found {total_files} XML files in ObjectData")
        
        if not object_files:
            print("No XML files found in ObjectData. Checking for other file types...")
            object_files = list(archive.iter_glob("ObjectData/**/*"))
            print(f"Found {len(object_files)} total files in ObjectData")
        
        print(f"Processing {len(object_files)} files...")
        
        # Create serializer if we have type list
        serializer = None
        if type_list:
            options = SerializerOptions()
            options.shallow = False  # Allow deep serialization (required for skip_unknown_types)
            options.skip_unknown_types = True  # Equivalent to CLI --ignore-unknown-types
            serializer = Serializer(options, type_list)
            print("[INFO] Enabled deep serialization with skip_unknown_types - will ignore server-side types not in type dump")
        
        for i, file_path in enumerate(object_files):
            manager.total_processed += 1
            
            try:
                # Deserialize the object data
                if serializer:
                    object_data = archive.deserialize(file_path, serializer)
                else:
                    object_data = archive[file_path]
                
                # Convert to dictionary format (use hash-only to preserve integer type hashes)
                if isinstance(object_data, LazyObject):
                    obj_dict = convert_lazy_object_to_dict_with_hash_only(object_data, type_list)
                else:
                    obj_dict = object_data
                
                # Check for conversion errors
                if isinstance(obj_dict, dict) and "error" in obj_dict:
                    manager.process_mob_failure(file_path, obj_dict, Exception(obj_dict["error"]), "conversion")
                    continue
                
                # Check if this is a WizGameObjectTemplate (mob)
                obj_type = obj_dict.get('$__type')
                if obj_type == 701229577:  # WizGameObjectTemplate hash
                    # This is a mob - process it
                    try:
                        manager.process_mob_success(file_path, obj_dict)
                    except Exception as e:
                        manager.process_mob_failure(file_path, obj_dict, e, "mob_processing")
                else:
                    # Not a mob - just count it
                    manager.process_non_mob(file_path, obj_dict)
            
            except Exception as e:
                # Even if we can't process the object, try to get basic info
                error_dict = {"file_path": file_path, "processing_error": str(e)}
                manager.process_mob_failure(file_path, error_dict, e, "file_processing")
    
    except Exception as e:
        print(f"Fatal error during processing: {e}")
        traceback.print_exc()
    
    finally:
        manager.finish_processing()


def main():
    """Main function to test all WAD ObjectData files and find mobs"""
    print("Comprehensive WAD Mob Processing and Validation")
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
    
    # Process all ObjectData files
    print(f"\nProcessing all ObjectData files for mobs...")
    process_all_mobs(archive, type_list)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())