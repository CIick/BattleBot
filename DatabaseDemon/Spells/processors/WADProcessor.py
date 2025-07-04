#!/usr/bin/env python3
"""
WAD Processor for Wizard101 Spell Data
======================================
Class-based processor for extracting and converting spell data from Root.wad files.
Handles LazyObject/LazyList conversion and DTO creation.
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
sys.path.append(str(Path(__file__).parent.parent.parent))  # DatabaseDemon level
sys.path.append(str(Path(__file__).parent.parent))         # Spells level

# Import centralized conversion utility
from utils.conversion_utils import convert_lazy_object_to_dict

# Import our DTOs
from dtos import FixedSpellDTOFactory


class WADProcessor:
    """Class-based processor for handling WAD file processing and spell data extraction"""
    
    def __init__(self, wad_path: Optional[Path] = None, types_path: Optional[Path] = None):
        """Initialize the WAD processor with paths"""
        self.wad_path = wad_path
        self.types_path = types_path
        self.archive = None
        self.type_list = None
        self.serializer = None
        
        # Statistics
        self.total_processed = 0
        self.total_success = 0
        self.total_failures = 0
        self.nested_dto_successes = 0
        self.max_recursion_depth = 0
        
        # Error tracking
        self.error_categories = {}
        
        # Auto-detect paths if not provided
        if not self.wad_path or not self.types_path:
            self._auto_detect_paths()
    
    def _auto_detect_paths(self):
        """Auto-detect platform-specific paths for WAD and types files"""
        system = platform.system().lower()
        
        if system == "windows":
            if not self.wad_path:
                self.wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            if not self.types_path:
                self.types_path = Path("../types.json")  # Look in DatabaseDemon folder
        else:  # Linux or other
            if not self.wad_path:
                self.wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            if not self.types_path:
                self.types_path = Path("../types.json")  # Look in DatabaseDemon folder
    
    def initialize(self) -> bool:
        """Initialize the processor by loading type list and opening WAD archive"""
        print("Initializing WAD Processor...")
        
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
        
        print("[OK] WAD Processor initialized successfully")
        return True
    
    def _load_type_list(self) -> bool:
        """Load TypeList from the types JSON file"""
        try:
            if not self.types_path.exists():
                print(f"Error: Types file not found at {self.types_path}")
                print("Check if the type dump (types.json) is the correct version for this revision")
                return False
                
            self.type_list = TypeList.open(str(self.types_path))
            print(f"[OK] Loaded type definitions from {self.types_path}")
            return True
            
        except Exception as e:
            print(f"Error loading types file: {e}")
            print("Check if the type dump (types.json) is the correct version for this revision")
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
    
    
    def process_single_spell(self, file_path: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Any], Optional[str]]:
        """
        Process a single spell file and return results
        
        Returns:
            (success, spell_dict, spell_dto, error_message)
        """
        try:
            # Deserialize the spell data
            if self.serializer:
                spell_data = self.archive.deserialize(file_path, self.serializer)
            else:
                spell_data = self.archive[file_path]
            
            # Convert to dictionary format
            if isinstance(spell_data, LazyObject):
                spell_dict = convert_lazy_object_to_dict(spell_data, self.type_list)
            else:
                spell_dict = spell_data
            
            # Check for conversion errors
            if isinstance(spell_dict, dict) and "error" in spell_dict:
                return False, spell_dict, None, spell_dict["error"]
            
            # Try to create DTO
            try:
                spell_dto = FixedSpellDTOFactory.create_from_json_data(spell_dict)
                
                if spell_dto:
                    return True, spell_dict, spell_dto, None
                else:
                    return False, spell_dict, None, "No DTO created - unknown spell type"
            
            except Exception as e:
                return False, spell_dict, None, f"DTO creation failed: {e}"
        
        except Exception as e:
            # Even if we can't process the spell, try to get basic info
            error_dict = {"file_path": file_path, "processing_error": str(e)}
            return False, error_dict, None, f"File processing failed: {e}"
    
    def analyze_nested_dtos(self, dto_obj: Any, path: str = "", depth: int = 0) -> Tuple[List[str], int]:
        """Recursively analyze created DTOs to show nesting structure"""
        nested_dtos = []
        max_depth = depth
        
        if hasattr(dto_obj, '__dict__'):
            for attr_name, attr_value in dto_obj.__dict__.items():
                current_path = f"{path}.{attr_name}" if path else attr_name
                
                # Check if this is a DTO object
                if hasattr(attr_value, '__class__') and attr_value.__class__.__name__.endswith('DTO'):
                    nested_dtos.append(f"  - {current_path}: {attr_value.__class__.__name__}")
                    # Recurse into this DTO
                    sub_dtos, sub_depth = self.analyze_nested_dtos(attr_value, current_path, depth + 1)
                    nested_dtos.extend(sub_dtos)
                    max_depth = max(max_depth, sub_depth)
                
                elif isinstance(attr_value, list):
                    # Handle lists that might contain DTOs
                    for i, item in enumerate(attr_value):
                        if hasattr(item, '__class__') and item.__class__.__name__.endswith('DTO'):
                            list_path = f"{current_path}[{i}]"
                            nested_dtos.append(f"  - {list_path}: {item.__class__.__name__}")
                            # Recurse into list item DTO
                            sub_dtos, sub_depth = self.analyze_nested_dtos(item, list_path, depth + 1)
                            nested_dtos.extend(sub_dtos)
                            max_depth = max(max_depth, sub_depth)
        
        return nested_dtos, max_depth
    
    def get_all_spell_files(self) -> List[str]:
        """Get all spell files from the WAD archive"""
        if not self.archive:
            return []
        
        try:
            # Find all files in the spells folder
            spell_files = list(self.archive.iter_glob("Spells/*"))
            print(f"Found {len(spell_files)} files in Spells folder")
            
            # Filter for XML files
            xml_files = [file for file in spell_files if file.lower().endswith(('.xml', '.spell'))]
            if not xml_files:
                xml_files = spell_files  # Use all files if no .xml files found
                
            print(f"Processing {len(xml_files)} spell files...")
            return xml_files
            
        except Exception as e:
            print(f"Error getting spell files: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources"""
        self.archive = None
        self.type_list = None
        self.serializer = None
        print("[OK] WAD Processor cleaned up")


# Compatibility functions for existing code
def get_platform_paths():
    """Compatibility function for existing code"""
    processor = WADProcessor()
    return processor.wad_path, processor.types_path


def load_type_list(types_path: Path) -> Optional[TypeList]:
    """Compatibility function for existing code"""
    processor = WADProcessor(types_path=types_path)
    if processor._load_type_list():
        return processor.type_list
    return None


def open_wad_archive(wad_path: Path) -> Optional[Archive]:
    """Compatibility function for existing code"""
    processor = WADProcessor(wad_path=wad_path)
    if processor._open_wad_archive():
        return processor.archive
    return None


