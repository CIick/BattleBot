#!/usr/bin/env python3
"""
Mob WAD Processor for Wizard101 Mob Data
========================================
Class-based processor for extracting and converting mob data from Root.wad files.
Handles LazyObject/LazyList conversion and DTO creation for mobs.
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

# Add parent directories to Python path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))  # DatabaseDemon level
sys.path.append(str(Path(__file__).parent.parent))         # Mobs level

# Import centralized conversion utility
from utils.conversion_utils import convert_lazy_object_to_dict_with_hash_only

# Import mob DTOs
from dtos import MobsDTOFactory


class MobWADProcessor:
    """Class-based processor for mob data extraction from WAD files"""
    
    def __init__(self, wad_path: Optional[Path] = None, types_path: Optional[Path] = None):
        """
        Initialize the mob WAD processor
        
        Args:
            wad_path: Path to Root.wad file (auto-detected if None)
            types_path: Path to types.json file (auto-detected if None)
        """
        self.wad_path = wad_path
        self.types_path = types_path
        self.archive = None
        self.type_list = None
        self.serializer = None
        
        # Auto-detect paths if not provided
        if not self.wad_path or not self.types_path:
            self._auto_detect_paths()
    
    def _auto_detect_paths(self):
        """Auto-detect WAD and types paths based on platform"""
        system = platform.system().lower()
        
        if system == "windows":
            if not self.wad_path:
                self.wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            if not self.types_path:
                self.types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json")
        else:  # Linux or other
            if not self.wad_path:
                self.wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            if not self.types_path:
                self.types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    
    def initialize(self) -> bool:
        """
        Initialize the WAD processor
        
        Returns:
            True if initialization successful, False otherwise
        """
        print("Initializing Mob WAD Processor...")
        
        # Load type definitions
        if not self._load_type_list():
            print("Failed to load type definitions")
            return False
        
        # Open WAD archive
        if not self._open_wad_archive():
            print("Failed to open WAD archive")
            return False
        
        # Create serializer
        if self.type_list:
            options = SerializerOptions()
            options.shallow = False  # Allow deep serialization (required for skip_unknown_types)
            options.skip_unknown_types = True  # Equivalent to CLI --ignore-unknown-types
            self.serializer = Serializer(options, self.type_list)
            print("[OK] Created serializer with deep serialization and skip_unknown_types enabled")
        
        print("[OK] Mob WAD Processor initialized successfully")
        return True
    
    def _load_type_list(self) -> bool:
        """Load TypeList from the types JSON file"""
        try:
            if not self.types_path.exists():
                print(f"Error: Types file not found at {self.types_path}")
                return False
                
            self.type_list = TypeList.open(str(self.types_path))
            print(f"[OK] Loaded type definitions from {self.types_path}")
            return True
            
        except Exception as e:
            print(f"Error loading types file: {e}")
            return False
    
    def _open_wad_archive(self) -> bool:
        """Open the WAD archive file"""
        try:
            if not self.wad_path.exists():
                print(f"Error: WAD file not found at {self.wad_path}")
                return False
                
            # Try memory mapping first, fall back to heap if needed
            try:
                self.archive = Archive.mmap(str(self.wad_path))
                print(f"[OK] Opened WAD archive (mmap): {self.wad_path}")
            except Exception:
                self.archive = Archive.heap(str(self.wad_path))
                print(f"[OK] Opened WAD archive (heap): {self.wad_path}")
                
            return True
            
        except Exception as e:
            print(f"Error opening WAD archive: {e}")
            return False
    
    def process_single_mob(self, file_path: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Any], Optional[str]]:
        """
        Process a single mob file and return results
        
        Returns:
            (success, mob_dict, mob_dto, error_message)
        """
        try:
            # Deserialize the mob data
            if self.serializer:
                mob_data = self.archive.deserialize(file_path, self.serializer)
            else:
                mob_data = self.archive[file_path]
            
            # Convert to dictionary format (use hash-only to preserve integer type hashes)
            if isinstance(mob_data, LazyObject):
                mob_dict = convert_lazy_object_to_dict_with_hash_only(mob_data, self.type_list)
            else:
                mob_dict = mob_data
            
            # Check for conversion errors
            if isinstance(mob_dict, dict) and "error" in mob_dict:
                return False, mob_dict, None, mob_dict["error"]
            
            # Check if this is a WizGameObjectTemplate (mob)
            obj_type = mob_dict.get('$__type')
            if obj_type != 701229577:
                return False, mob_dict, None, f"Not a WizGameObjectTemplate (type: {obj_type})"
            
            # Try to create DTO
            try:
                mob_dto = MobsDTOFactory.create_from_json_data(mob_dict)
                
                if mob_dto:
                    return True, mob_dict, mob_dto, None
                else:
                    return False, mob_dict, None, "No DTO created - unknown mob type"
            
            except Exception as e:
                return False, mob_dict, None, f"DTO creation failed: {e}"
        
        except Exception as e:
            # Even if we can't process the mob, try to get basic info
            error_dict = {"file_path": file_path, "processing_error": str(e)}
            return False, error_dict, None, f"File processing failed: {e}"
    
    def get_all_object_files(self) -> List[str]:
        """
        Get list of all ObjectData XML files
        
        Returns:
            List of file paths in ObjectData
        """
        try:
            object_files = list(self.archive.iter_glob("ObjectData/**/*.xml"))
            print(f"Found {len(object_files)} XML files in ObjectData")
            return object_files
        except Exception as e:
            print(f"Error getting ObjectData files: {e}")
            return []
    
    def get_mob_files_only(self) -> List[str]:
        """
        Get list of ObjectData files that are actually mobs (WizGameObjectTemplate)
        
        Returns:
            List of file paths that contain mobs
        """
        mob_files = []
        object_files = self.get_all_object_files()
        
        print(f"Filtering {len(object_files)} files for mobs...")
        
        for i, file_path in enumerate(object_files):
            try:
                success, mob_dict, mob_dto, error = self.process_single_mob(file_path)
                if success and mob_dto:
                    mob_files.append(file_path)
                
                # Progress reporting
                if (i + 1) % 10000 == 0:
                    print(f"[PROGRESS] Checked {i + 1}/{len(object_files)} files, found {len(mob_files)} mobs")
                    
            except Exception as e:
                continue  # Skip files that can't be processed
        
        print(f"Found {len(mob_files)} mob files out of {len(object_files)} total files")
        return mob_files
    
    def process_all_mobs(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process all mob files and return results
        
        Returns:
            (successful_mobs, failed_mobs)
        """
        successful_mobs = []
        failed_mobs = []
        
        object_files = self.get_all_object_files()
        total_files = len(object_files)
        
        print(f"Processing {total_files} ObjectData files for mobs...")
        
        for i, file_path in enumerate(object_files):
            try:
                success, mob_dict, mob_dto, error = self.process_single_mob(file_path)
                
                if success and mob_dto:
                    successful_mobs.append({
                        "file_path": file_path,
                        "mob_dict": mob_dict,
                        "mob_dto": mob_dto
                    })
                elif error and "Not a WizGameObjectTemplate" not in error:
                    # Only log actual failures, not non-mob files
                    failed_mobs.append({
                        "file_path": file_path,
                        "error": error,
                        "mob_dict": mob_dict
                    })
                
                # Progress reporting
                if (i + 1) % 5000 == 0:
                    print(f"[PROGRESS] {i + 1}/{total_files} processed, "
                          f"{len(successful_mobs)} mobs, {len(failed_mobs)} failures")
                    
            except Exception as e:
                failed_mobs.append({
                    "file_path": file_path,
                    "error": f"Exception: {e}",
                    "mob_dict": {}
                })
        
        print(f"Mob processing complete: {len(successful_mobs)} successful, {len(failed_mobs)} failed")
        return successful_mobs, failed_mobs
    
    def export_mob_data(self, output_path: Path, format: str = "json") -> bool:
        """
        Export all mob data to file
        
        Args:
            output_path: Path for output file
            format: Export format ("json" or "csv")
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            successful_mobs, failed_mobs = self.process_all_mobs()
            
            if format.lower() == "json":
                export_data = {
                    "successful_mobs": len(successful_mobs),
                    "failed_mobs": len(failed_mobs),
                    "mobs": []
                }
                
                for mob_data in successful_mobs:
                    export_data["mobs"].append({
                        "file_path": mob_data["file_path"],
                        "mob_data": mob_data["mob_dict"],
                        "dto_data": mob_data["mob_dto"].__dict__ if hasattr(mob_data["mob_dto"], '__dict__') else str(mob_data["mob_dto"])
                    })
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                print(f"Exported mob data to: {output_path}")
                return True
            
            else:
                print(f"Unsupported export format: {format}")
                return False
                
        except Exception as e:
            print(f"Error exporting mob data: {e}")
            return False
    
    def close(self):
        """Close resources"""
        # WAD archive and type list are automatically managed by katsuba
        print("[OK] Mob WAD Processor resources closed")


# Compatibility functions for existing code
def load_type_list(types_path: Path) -> Optional[TypeList]:
    """Compatibility function for existing code"""
    processor = MobWADProcessor(types_path=types_path)
    if processor._load_type_list():
        return processor.type_list
    return None


def open_wad_archive(wad_path: Path) -> Optional[Archive]:
    """Compatibility function for existing code"""
    processor = MobWADProcessor(wad_path=wad_path)
    if processor._open_wad_archive():
        return processor.archive
    return None