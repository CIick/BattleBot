#!/usr/bin/env python3
"""
Wizard101 Items WAD Processor
============================
Processes ObjectData files from Root.wad to extract WizItemTemplate objects
with comprehensive handling of all nested types including pets, mounts, housing, etc.
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import traceback

import katsuba
from katsuba.wad import Archive
from katsuba.op import LazyObject, LazyList, TypeList, Serializer, SerializerOptions

# Add DatabaseDemon to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.conversion_utils import convert_lazy_object_to_dict

# Import item DTOs
from ..dtos import ItemsDTOFactory
from ..dtos.ItemsDTO import WizItemTemplateDTO


class ItemsWADProcessor:
    """Processes WAD files to extract and convert WizItemTemplate objects"""
    
    # WizItemTemplate type hash
    WIZITEMTEMPLATE_HASH = 991922385
    
    def __init__(self, types_path: Optional[Path] = None, max_file_size_mb: int = 100):
        """
        Initialize the WAD processor
        
        Args:
            types_path: Path to types.json file (auto-detected if None)
            max_file_size_mb: Maximum file size for processing chunks
        """
        self.types_path = types_path
        self.max_file_size = max_file_size_mb * 1024 * 1024
        
        # WAD processing components
        self.wad_path = None
        self.archive = None
        self.type_list = None
        self.serializer = None
        
        # Statistics
        self.total_files_processed = 0
        self.total_items_found = 0
        self.total_non_items = 0
        self.processing_errors = []
        self.failed_files = []
        
        # Processing results
        self.successful_items = []
        self.failed_items = []
        
        # Auto-detect paths
        self._auto_detect_paths()
    
    def _auto_detect_paths(self):
        """Auto-detect platform-specific paths for WAD and types files"""
        system = platform.system().lower()
        
        if system == "windows":
            self.wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            if self.types_path is None:
                self.types_path = self._detect_types_json_path()
        else:  # Linux/WSL
            self.wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            if self.types_path is None:
                self.types_path = self._detect_types_json_path()
    
    def _detect_types_json_path(self) -> Path:
        """Auto-detect correct path to types.json based on working directory context"""
        import os
        
        # Get current working directory
        cwd = Path(os.getcwd())
        cwd_name = cwd.name
        
        # Check if we're in Test Scripts subdirectory
        if cwd_name == "Test Scripts":
            # From Test Scripts, types.json is up 2 levels: Test Scripts -> Items -> DatabaseDemon
            types_path = Path("../../types.json")
        else:
            # From Items directory or processors, types.json is up 1 level: Items -> DatabaseDemon
            types_path = Path("../types.json")
        
        # Verify the path exists, if not try alternative paths
        if types_path.exists():
            return types_path
        else:
            # Try alternative paths as fallback
            alternatives = [
                Path("../../types.json"),  # Test Scripts context
                Path("../types.json"),     # Items context  
                Path("types.json"),        # DatabaseDemon context
                Path("../../DatabaseDemon/types.json"),  # If running from somewhere else
            ]
            
            for alt_path in alternatives:
                if alt_path.exists():
                    return alt_path
            
            # If none found, return the most likely path and let it fail with proper error
            return Path("../types.json")
    
    def initialize(self) -> bool:
        """Initialize WAD processor and type system"""
        print("Initializing Items WAD Processor...")
        print("=" * 50)
        
        # Load type list
        if not self._load_type_list():
            return False
        
        # Open WAD archive
        if not self._open_wad_archive():
            return False
        
        # Create serializer
        if not self._create_serializer():
            return False
        
        print("[OK] Items WAD Processor initialized successfully")
        print(f"WAD Path: {self.wad_path}")
        print(f"Types Path: {self.types_path}")
        return True
    
    def _load_type_list(self) -> bool:
        """Load TypeList from types.json"""
        try:
            if not self.types_path.exists():
                print(f"[ERROR] Types file not found: {self.types_path}")
                return False
            
            self.type_list = TypeList.open(str(self.types_path))
            print(f"[OK] Loaded type definitions from {self.types_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load type list: {e}")
            return False
    
    def _open_wad_archive(self) -> bool:
        """Open WAD archive file"""
        try:
            if not self.wad_path.exists():
                print(f"[ERROR] WAD file not found: {self.wad_path}")
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
            print(f"[ERROR] Failed to open WAD archive: {e}")
            return False
    
    def _create_serializer(self) -> bool:
        """Create serializer with proper options"""
        try:
            options = SerializerOptions()
            options.shallow = False  # Allow deep serialization (required for skip_unknown_types)
            options.skip_unknown_types = True  # Equivalent to CLI --ignore-unknown-types
            self.serializer = Serializer(options, self.type_list)
            print("[OK] Created serializer with deep serialization and skip_unknown_types enabled")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create serializer: {e}")
            return False
    
    def get_all_item_files(self) -> List[str]:
        """Get all XML files in ObjectData that could contain items"""
        try:
            # Get all files in ObjectData recursively
            item_files = list(self.archive.iter_glob("ObjectData/**/*.xml"))
            print(f"[INFO] Found {len(item_files)} XML files in ObjectData")
            return item_files
        except Exception as e:
            print(f"[ERROR] Failed to get item files: {e}")
            return []
    
    def process_single_item(self, file_path: str) -> Tuple[bool, Dict[str, Any], Optional[WizItemTemplateDTO], str]:
        """
        Process a single item file
        
        Args:
            file_path: Path to the item file in the WAD
            
        Returns:
            Tuple of (success, raw_dict, item_dto, error_message)
        """
        try:
            # Deserialize the object data
            if self.serializer:
                object_data = self.archive.deserialize(file_path, self.serializer)
            else:
                object_data = self.archive[file_path]
            
            # Convert to dictionary format
            if isinstance(object_data, LazyObject):
                obj_dict = convert_lazy_object_to_dict(object_data, self.type_list)
            else:
                obj_dict = object_data
            
            # Check if this is a WizItemTemplate
            obj_type = obj_dict.get('$__type')
            if obj_type != 'class WizItemTemplate':
                return False, obj_dict, None, f"Not a WizItemTemplate (type: {obj_type})"
            
            # Create DTO using factory
            item_dto = ItemsDTOFactory.create_from_json_data(obj_dict)
            if item_dto is None:
                return False, obj_dict, None, "Failed to create WizItemTemplate DTO"
            
            return True, obj_dict, item_dto, ""
            
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            return False, {}, None, error_msg
    
    def process_all_items(self, progress_callback=None) -> bool:
        """
        Process all item files in ObjectData
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            True if processing completed successfully
        """
        print("\nProcessing All Items from ObjectData...")
        print("=" * 50)
        
        try:
            # Get all item files
            item_files = self.get_all_item_files()
            if not item_files:
                print("[ERROR] No item files found")
                return False
            
            total_files = len(item_files)
            print(f"Processing {total_files} files...")
            
            # Process each file
            for i, file_path in enumerate(item_files):
                self.total_files_processed += 1
                
                try:
                    success, raw_dict, item_dto, error_msg = self.process_single_item(file_path)
                    
                    if success:
                        self.total_items_found += 1
                        self.successful_items.append({
                            'file_path': file_path,
                            'raw_dict': raw_dict,
                            'item_dto': item_dto
                        })
                    else:
                        self.total_non_items += 1
                        if "Not a WizItemTemplate" not in error_msg:
                            # This was a processing error, not just a non-item
                            self.failed_files.append(file_path)
                            self.failed_items.append({
                                'file_path': file_path,
                                'error': error_msg,
                                'raw_dict': raw_dict
                            })
                
                except Exception as e:
                    self.failed_files.append(file_path)
                    self.processing_errors.append({
                        'file_path': file_path,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    })
                
                # Progress reporting
                if self.total_files_processed % 1000 == 0 or i == total_files - 1:
                    progress = (self.total_files_processed / total_files) * 100
                    print(f"[PROGRESS] {self.total_files_processed}/{total_files} ({progress:.1f}%) - "
                          f"Found {self.total_items_found} items, {self.total_non_items} non-items, "
                          f"{len(self.failed_files)} failed")
                    
                    if progress_callback:
                        progress_callback(self.total_files_processed, total_files, 
                                       self.total_items_found, len(self.failed_files))
            
            print(f"\n[COMPLETE] Processing finished!")
            print(f"Total files processed: {self.total_files_processed}")
            print(f"WizItemTemplates found: {self.total_items_found}")
            print(f"Non-item objects: {self.total_non_items}")
            print(f"Processing errors: {len(self.processing_errors)}")
            print(f"Failed files: {len(self.failed_files)}")
            
            if self.total_items_found > 0:
                success_rate = (self.total_items_found / self.total_files_processed) * 100
                print(f"Item discovery rate: {success_rate:.2f}%")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Processing failed: {e}")
            traceback.print_exc()
            return False
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return {
            "total_files_processed": self.total_files_processed,
            "total_items_found": self.total_items_found,
            "total_non_items": self.total_non_items,
            "processing_errors": len(self.processing_errors),
            "failed_files": len(self.failed_files),
            "success_rate": (self.total_items_found / max(1, self.total_files_processed)) * 100,
            "successful_items": len(self.successful_items),
            "failed_items": len(self.failed_items)
        }
    
    def get_successful_items(self) -> List[Dict[str, Any]]:
        """Get all successfully processed items"""
        return self.successful_items
    
    def get_failed_items(self) -> List[Dict[str, Any]]:
        """Get all failed item processing attempts"""
        return self.failed_items
    
    def get_processing_errors(self) -> List[Dict[str, Any]]:
        """Get all processing errors"""
        return self.processing_errors
    
    def save_processing_report(self, output_path: Path) -> bool:
        """
        Save comprehensive processing report
        
        Args:
            output_path: Path to save the report
            
        Returns:
            True if report saved successfully
        """
        try:
            report = {
                "processing_statistics": self.get_processing_statistics(),
                "successful_items_sample": self.successful_items[:10],  # First 10 successful items
                "failed_items": self.failed_items,
                "processing_errors": self.processing_errors
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"[OK] Processing report saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save processing report: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.archive:
            # Archive cleanup is handled by katsuba
            pass
        
        self.archive = None
        self.type_list = None
        self.serializer = None
        print("[OK] Items WAD Processor cleanup completed")