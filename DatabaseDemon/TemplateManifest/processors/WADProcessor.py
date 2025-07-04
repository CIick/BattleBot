#!/usr/bin/env python3
"""
TemplateManifest WAD Processor
=============================

Class-based processor for extracting TemplateManifest data from Root.wad files.
Handles LazyObject conversion and DTO creation for template manifest data.

This processor follows the same patterns as Mobs and Spells processors,
providing dynamic processing of TemplateManifest.xml from Root.wad.
"""

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
sys.path.append(str(Path(__file__).parent.parent))         # TemplateManifest level

# Import centralized conversion utility
from utils.conversion_utils import convert_lazy_object_to_dict_with_hash_only

# Import TemplateManifest DTOs
from dtos import TemplateManifestDTOFactory, TemplateManifestDTO, TemplateLocationDTO
from dtos.TemplateManifestEnums import TypeHashes, TEMPLATE_MANIFEST_PATH


class TemplateManifestWADProcessor:
    """Class-based processor for TemplateManifest data extraction from WAD files"""
    
    def __init__(self, wad_path: Optional[Path] = None, types_path: Optional[Path] = None):
        """
        Initialize the TemplateManifest WAD processor
        
        Args:
            wad_path: Path to Root.wad file (auto-detected if None)
            types_path: Path to types.json file (auto-detected if None)
        """
        self.wad_path = wad_path
        self.types_path = types_path
        self.archive = None
        self.type_list = None
        self.serializer = None
        self.dto_factory = None
        
        # Statistics
        self.total_processed = 0
        self.total_success = 0
        self.total_failures = 0
        self.template_count = 0
        
        # Error tracking
        self.error_categories = {}
        self.processing_errors = []
        
        # Auto-detect paths if not provided
        if not self.wad_path or not self.types_path:
            detected_wad, detected_types = self._get_platform_paths()
            if not self.wad_path:
                self.wad_path = detected_wad
            if not self.types_path:
                self.types_path = detected_types
    
    def _get_platform_paths(self) -> Tuple[Path, Path]:
        """Get platform-specific paths for WAD and types files"""
        system = platform.system().lower()
        
        if system == "windows":
            wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            types_path = Path("../types.json")
        else:  # Linux/WSL
            wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            types_path = Path("../types.json")
        
        return wad_path, types_path
    
    def initialize(self) -> bool:
        """
        Initialize the processor with WAD file and type system
        
        Returns:
            True if initialization successful, False otherwise
        """
        print("Initializing TemplateManifest WAD Processor...")
        
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
        
        # Create DTO factory
        self.dto_factory = TemplateManifestDTOFactory(self.type_list)
        print("[OK] Created DTO factory")
        
        # Verify TemplateManifest.xml exists
        if TEMPLATE_MANIFEST_PATH not in self.archive:
            print(f"[ERROR] {TEMPLATE_MANIFEST_PATH} not found in WAD archive")
            return False
        
        print(f"[OK] Found {TEMPLATE_MANIFEST_PATH} in WAD archive")
        print("[OK] TemplateManifest WAD Processor initialized successfully")
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
    
    def process_template_manifest(self) -> Optional[TemplateManifestDTO]:
        """
        Process TemplateManifest.xml from WAD archive
        
        Returns:
            TemplateManifestDTO or None if processing fails
        """
        try:
            if not self.archive or not self.serializer or not self.dto_factory:
                print("[ERROR] Processor not initialized")
                return None
            
            print(f"[INFO] Processing {TEMPLATE_MANIFEST_PATH}...")
            
            # Deserialize using archive method (like Mobs system)
            lazy_object = self.archive.deserialize(TEMPLATE_MANIFEST_PATH, self.serializer)
            print(f"[OK] Deserialized {TEMPLATE_MANIFEST_PATH}")
            
            # Validate type
            if not isinstance(lazy_object, LazyObject):
                print(f"[ERROR] Expected LazyObject, got {type(lazy_object)}")
                return None
            
            if lazy_object.type_hash != TypeHashes.TEMPLATE_MANIFEST:
                print(f"[ERROR] Expected TemplateManifest hash {TypeHashes.TEMPLATE_MANIFEST}, got {lazy_object.type_hash}")
                return None
            
            print(f"[OK] Verified TemplateManifest type hash: {lazy_object.type_hash}")
            
            # Convert to DTO
            dto = self.dto_factory.create_template_manifest_dto(lazy_object)
            if not dto:
                print("[ERROR] Failed to create TemplateManifestDTO")
                return None
            
            print(f"[OK] Created TemplateManifestDTO with {len(dto.m_serializedTemplates)} templates")
            
            # Update statistics
            self.total_processed = 1
            self.total_success = 1
            self.template_count = len(dto.m_serializedTemplates)
            
            return dto
            
        except Exception as e:
            print(f"[ERROR] Failed to process TemplateManifest: {e}")
            traceback.print_exc()
            self.total_processed = 1
            self.total_failures = 1
            self._record_error("processing_error", str(e))
            return None
    
    def validate_template_manifest(self, dto: TemplateManifestDTO) -> Dict[str, Any]:
        """
        Validate TemplateManifest DTO
        
        Args:
            dto: TemplateManifestDTO to validate
            
        Returns:
            Validation results
        """
        try:
            validation_results = {
                'valid': True,
                'total_templates': len(dto.m_serializedTemplates),
                'issues': [],
                'statistics': dto.get_statistics()
            }
            
            # Check for empty manifest
            if not dto.m_serializedTemplates:
                validation_results['valid'] = False
                validation_results['issues'].append("TemplateManifest is empty")
                return validation_results
            
            # Validate individual templates
            missing_filenames = 0
            invalid_ids = 0
            duplicate_ids = set()
            seen_ids = set()
            
            for i, template in enumerate(dto.m_serializedTemplates):
                # Check for missing filename
                if not template.m_filename:
                    missing_filenames += 1
                
                # Check for invalid ID
                if template.m_id <= 0:
                    invalid_ids += 1
                
                # Check for duplicate ID
                if template.m_id in seen_ids:
                    duplicate_ids.add(template.m_id)
                seen_ids.add(template.m_id)
            
            # Report issues
            if missing_filenames > 0:
                validation_results['issues'].append(f"{missing_filenames} templates missing filenames")
            
            if invalid_ids > 0:
                validation_results['issues'].append(f"{invalid_ids} templates have invalid IDs")
            
            if duplicate_ids:
                validation_results['issues'].append(f"{len(duplicate_ids)} duplicate template IDs found")
            
            # Set overall validity
            validation_results['valid'] = len(validation_results['issues']) == 0
            
            # Add detailed statistics
            validation_results.update({
                'missing_filenames': missing_filenames,
                'invalid_ids': invalid_ids,
                'duplicate_ids': len(duplicate_ids),
                'unique_ids': len(seen_ids),
                'validation_success_rate': (len(dto.m_serializedTemplates) - missing_filenames - invalid_ids) / len(dto.m_serializedTemplates) if dto.m_serializedTemplates else 0
            })
            
            return validation_results
            
        except Exception as e:
            print(f"[ERROR] Validation failed: {e}")
            return {
                'valid': False,
                'issues': [f"Validation error: {str(e)}"],
                'total_templates': 0,
                'statistics': {}
            }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        stats = {
            'total_processed': self.total_processed,
            'total_success': self.total_success,
            'total_failures': self.total_failures,
            'template_count': self.template_count,
            'success_rate': (self.total_success / max(1, self.total_processed)) * 100,
            'error_categories': dict(self.error_categories),
            'processing_errors': self.processing_errors
        }
        
        # Add DTO factory statistics if available
        if self.dto_factory:
            stats['dto_factory_stats'] = self.dto_factory.get_conversion_stats()
        
        return stats
    
    def _record_error(self, category: str, error: str):
        """Record an error for statistics"""
        self.error_categories[category] = self.error_categories.get(category, 0) + 1
        self.processing_errors.append({
            'category': category,
            'error': error,
            'timestamp': str(Path(__file__).stat().st_mtime)  # Simple timestamp
        })
    
    def cleanup(self):
        """Clean up resources"""
        if self.archive:
            # Archive cleanup is handled by katsuba
            pass
        
        self.archive = None
        self.type_list = None
        self.serializer = None
        self.dto_factory = None
        print("[OK] Cleanup completed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


def create_template_manifest_processor(wad_path: Optional[Path] = None, types_path: Optional[Path] = None) -> TemplateManifestWADProcessor:
    """
    Factory function to create and initialize a TemplateManifest processor
    
    Args:
        wad_path: Path to Root.wad file (auto-detected if None)
        types_path: Path to types.json file (auto-detected if None)
        
    Returns:
        Initialized TemplateManifestWADProcessor
    """
    processor = TemplateManifestWADProcessor(wad_path, types_path)
    
    if not processor.initialize():
        raise RuntimeError("Failed to initialize TemplateManifest processor")
    
    return processor


# Export main classes
__all__ = [
    'TemplateManifestWADProcessor',
    'create_template_manifest_processor'
]