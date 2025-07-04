#!/usr/bin/env python3
"""
TemplateManifest DTO Factory
===========================

Factory class for creating TemplateManifest DTOs from LazyObjects.
Handles conversion between katsuba LazyObjects and structured Python objects.

Key functionality:
- Type hash mapping for TemplateManifest and TemplateLocation
- Batch conversion of LazyObjects to DTOs
- Error handling and validation
- Statistics and reporting
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import traceback

# Add parent directories to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from katsuba.op import LazyObject, LazyList
from utils.conversion_utils import convert_lazy_object_to_dict

try:
    from .TemplateManifestDTO import TemplateManifestDTO, TemplateLocationDTO
    from .TemplateManifestEnums import TypeHashes
except ImportError:
    from TemplateManifestDTO import TemplateManifestDTO, TemplateLocationDTO
    from TemplateManifestEnums import TypeHashes


class TemplateManifestDTOFactory:
    """Factory for creating TemplateManifest DTOs from LazyObjects"""
    
    # Type hash mappings
    TYPE_HASH_TO_DTO = {
        TypeHashes.TEMPLATE_MANIFEST: TemplateManifestDTO,
        TypeHashes.TEMPLATE_LOCATION: TemplateLocationDTO,
    }
    
    def __init__(self, type_list=None):
        """
        Initialize the factory
        
        Args:
            type_list: katsuba TypeList for type resolution
        """
        self.type_list = type_list
        self.conversion_stats = {
            'total_processed': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'skipped_conversions': 0,
            'type_counts': {}
        }
        self.failed_conversions = []
    
    def create_template_location_dto(self, lazy_object: LazyObject) -> Optional[TemplateLocationDTO]:
        """
        Create TemplateLocationDTO from LazyObject
        
        Args:
            lazy_object: LazyObject representing TemplateLocation
            
        Returns:
            TemplateLocationDTO or None if conversion fails
        """
        try:
            if lazy_object.type_hash != TypeHashes.TEMPLATE_LOCATION:
                return None
            
            # Convert to dict using centralized utility
            obj_dict = convert_lazy_object_to_dict(lazy_object, self.type_list)
            
            # Create DTO
            dto = TemplateLocationDTO(
                m_filename=obj_dict.get('m_filename', ''),
                m_id=obj_dict.get('m_id', 0)
            )
            
            self.conversion_stats['successful_conversions'] += 1
            return dto
            
        except Exception as e:
            self.conversion_stats['failed_conversions'] += 1
            self.failed_conversions.append({
                'type': 'TemplateLocation',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            return None
    
    def create_template_manifest_dto(self, lazy_object: LazyObject) -> Optional[TemplateManifestDTO]:
        """
        Create TemplateManifestDTO from LazyObject
        
        Args:
            lazy_object: LazyObject representing TemplateManifest
            
        Returns:
            TemplateManifestDTO or None if conversion fails
        """
        try:
            if lazy_object.type_hash != TypeHashes.TEMPLATE_MANIFEST:
                return None
            
            # Convert to dict using centralized utility
            obj_dict = convert_lazy_object_to_dict(lazy_object, self.type_list)
            
            # Process template locations
            template_locations = []
            serialized_templates = obj_dict.get('m_serializedTemplates', [])
            
            if isinstance(serialized_templates, list):
                for template_data in serialized_templates:
                    if isinstance(template_data, dict):
                        # Create DTO directly from dict
                        location_dto = TemplateLocationDTO(
                            m_filename=template_data.get('m_filename', ''),
                            m_id=template_data.get('m_id', 0)
                        )
                        template_locations.append(location_dto)
                    elif isinstance(template_data, LazyObject):
                        # Convert LazyObject to DTO
                        location_dto = self.create_template_location_dto(template_data)
                        if location_dto:
                            template_locations.append(location_dto)
            
            # Create main DTO
            dto = TemplateManifestDTO(
                m_serializedTemplates=template_locations
            )
            
            self.conversion_stats['successful_conversions'] += 1
            return dto
            
        except Exception as e:
            self.conversion_stats['failed_conversions'] += 1
            self.failed_conversions.append({
                'type': 'TemplateManifest',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            return None
    
    def create_dto_from_lazy_object(self, lazy_object: LazyObject) -> Optional[Union[TemplateManifestDTO, TemplateLocationDTO]]:
        """
        Create appropriate DTO from LazyObject based on type hash
        
        Args:
            lazy_object: LazyObject to convert
            
        Returns:
            Appropriate DTO or None if conversion fails
        """
        self.conversion_stats['total_processed'] += 1
        
        # Update type counts
        type_hash = lazy_object.type_hash
        self.conversion_stats['type_counts'][type_hash] = self.conversion_stats['type_counts'].get(type_hash, 0) + 1
        
        if type_hash == TypeHashes.TEMPLATE_MANIFEST:
            return self.create_template_manifest_dto(lazy_object)
        elif type_hash == TypeHashes.TEMPLATE_LOCATION:
            return self.create_template_location_dto(lazy_object)
        else:
            self.conversion_stats['skipped_conversions'] += 1
            return None
    
    def create_dto_from_dict(self, obj_dict: Dict[str, Any], type_hash: int) -> Optional[Union[TemplateManifestDTO, TemplateLocationDTO]]:
        """
        Create DTO from dictionary representation
        
        Args:
            obj_dict: Dictionary representation of object
            type_hash: Type hash of the object
            
        Returns:
            Appropriate DTO or None if conversion fails
        """
        try:
            if type_hash == TypeHashes.TEMPLATE_MANIFEST:
                # Process template locations
                template_locations = []
                serialized_templates = obj_dict.get('m_serializedTemplates', [])
                
                for template_data in serialized_templates:
                    if isinstance(template_data, dict):
                        location_dto = TemplateLocationDTO(
                            m_filename=template_data.get('m_filename', ''),
                            m_id=template_data.get('m_id', 0)
                        )
                        template_locations.append(location_dto)
                
                return TemplateManifestDTO(m_serializedTemplates=template_locations)
                
            elif type_hash == TypeHashes.TEMPLATE_LOCATION:
                return TemplateLocationDTO(
                    m_filename=obj_dict.get('m_filename', ''),
                    m_id=obj_dict.get('m_id', 0)
                )
            
            return None
            
        except Exception as e:
            self.conversion_stats['failed_conversions'] += 1
            self.failed_conversions.append({
                'type': f'Dict conversion (hash: {type_hash})',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            return None
    
    def batch_convert_template_locations(self, lazy_objects: List[LazyObject]) -> List[TemplateLocationDTO]:
        """
        Convert multiple LazyObjects to TemplateLocationDTOs
        
        Args:
            lazy_objects: List of LazyObjects to convert
            
        Returns:
            List of successfully converted DTOs
        """
        results = []
        
        for lazy_object in lazy_objects:
            dto = self.create_template_location_dto(lazy_object)
            if dto:
                results.append(dto)
        
        return results
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        return {
            'total_processed': self.conversion_stats['total_processed'],
            'successful_conversions': self.conversion_stats['successful_conversions'],
            'failed_conversions': self.conversion_stats['failed_conversions'],
            'skipped_conversions': self.conversion_stats['skipped_conversions'],
            'success_rate': (self.conversion_stats['successful_conversions'] / 
                           max(1, self.conversion_stats['total_processed'])) * 100,
            'type_counts': dict(self.conversion_stats['type_counts']),
            'failed_conversion_examples': self.failed_conversions[:5]  # First 5 failures
        }
    
    def get_failed_conversions(self) -> List[Dict[str, Any]]:
        """Get detailed failed conversion information"""
        return self.failed_conversions
    
    def reset_stats(self):
        """Reset conversion statistics"""
        self.conversion_stats = {
            'total_processed': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'skipped_conversions': 0,
            'type_counts': {}
        }
        self.failed_conversions = []
    
    def validate_dto(self, dto: Union[TemplateManifestDTO, TemplateLocationDTO]) -> Dict[str, Any]:
        """
        Validate a DTO for completeness and correctness
        
        Args:
            dto: DTO to validate
            
        Returns:
            Validation results
        """
        issues = []
        
        if isinstance(dto, TemplateLocationDTO):
            if not dto.m_filename:
                issues.append("Missing filename")
            if dto.m_id <= 0:
                issues.append("Invalid or missing ID")
            if not dto.deck_name:
                issues.append("Could not extract deck name")
        
        elif isinstance(dto, TemplateManifestDTO):
            if not dto.m_serializedTemplates:
                issues.append("No template locations found")
            if dto.total_templates <= 0:
                issues.append("Invalid template count")
            
            # Check for duplicate IDs
            ids = [loc.m_id for loc in dto.m_serializedTemplates]
            if len(ids) != len(set(ids)):
                issues.append("Duplicate template IDs found")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'issue_count': len(issues)
        }
    
    @staticmethod
    def get_supported_types() -> List[int]:
        """Get list of supported type hashes"""
        return list(TemplateManifestDTOFactory.TYPE_HASH_TO_DTO.keys())
    
    @staticmethod
    def is_supported_type(type_hash: int) -> bool:
        """Check if type hash is supported"""
        return type_hash in TemplateManifestDTOFactory.TYPE_HASH_TO_DTO