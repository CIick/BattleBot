#!/usr/bin/env python3
"""
TemplateManifest DTOs
====================

Data Transfer Objects for TemplateManifest system.
Handles conversion between LazyObjects and structured Python objects.

These DTOs represent:
- TemplateManifestDTO: Main manifest containing all template locations
- TemplateLocationDTO: Individual template location mapping ID to filename

Key functionality:
- Template ID to deck filename lookup
- Deck categorization and analysis
- Batch processing and validation
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


@dataclass
class TemplateLocationDTO:
    """
    Represents a single template location mapping ID to filename.
    
    This is the core mapping that enables linking template IDs to file locations.
    Simple lookup without assumptions about what the files contain.
    """
    m_filename: str = ""
    m_id: int = 0
    
    # Simple derived fields
    file_name: str = ""
    file_type: str = ""
    file_directory: str = ""
    
    def __post_init__(self):
        """Process derived fields after initialization"""
        if self.m_filename:
            self.file_name = self._extract_file_name()
            self.file_type = self._determine_file_type()
            self.file_directory = self._extract_directory()
    
    def _extract_file_name(self) -> str:
        """Extract just the filename without path and extension"""
        if not self.m_filename:
            return ""
        
        # Extract filename without path and extension
        # e.g., "ObjectData/Decks/Mdeck-I-R9.xml" -> "Mdeck-I-R9"
        path = Path(self.m_filename)
        return path.stem
    
    def _determine_file_type(self) -> str:
        """Determine file type based on directory path"""
        if not self.m_filename:
            return "unknown"
        
        filename_lower = self.m_filename.lower()
        
        # Simple path-based classification
        if '/decks/' in filename_lower:
            return "deck"
        elif '/spells/' in filename_lower:
            return "spell"
        elif '/objects/' in filename_lower:
            return "object"
        elif '/creatures/' in filename_lower:
            return "creature"
        elif '/items/' in filename_lower:
            return "item"
        elif '/audio/' in filename_lower:
            return "audio"
        elif '/effects/' in filename_lower:
            return "effect"
        else:
            return "other"
    
    def _extract_directory(self) -> str:
        """Extract the directory path"""
        if not self.m_filename:
            return ""
        
        path = Path(self.m_filename)
        return str(path.parent)
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get template information"""
        return {
            'template_id': self.m_id,
            'filename': self.m_filename,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_directory': self.file_directory,
            'is_deck_file': self.file_type == "deck",
            'is_valid': self.m_id > 0 and bool(self.m_filename)
        }
    
    def __str__(self) -> str:
        return f"TemplateLocation(id={self.m_id}, file='{self.file_name}', type='{self.file_type}')"


@dataclass
class TemplateManifestDTO:
    """
    Represents the complete TemplateManifest containing all template locations.
    
    This is the main container that holds all template ID to filename mappings.
    Provides lookup and analysis capabilities for the entire manifest.
    """
    m_serializedTemplates: List[TemplateLocationDTO] = field(default_factory=list)
    
    # Metadata
    total_templates: int = 0
    file_types: Dict[str, int] = field(default_factory=dict)
    
    # Lookup optimization
    _id_to_location: Dict[int, TemplateLocationDTO] = field(default_factory=dict, init=False)
    _filename_to_location: Dict[str, TemplateLocationDTO] = field(default_factory=dict, init=False)
    
    def __post_init__(self):
        """Process derived fields and create lookup indexes"""
        self.total_templates = len(self.m_serializedTemplates)
        self._build_lookup_indexes()
        self._calculate_statistics()
    
    def _build_lookup_indexes(self):
        """Build lookup indexes for fast access"""
        self._id_to_location.clear()
        self._filename_to_location.clear()
        
        for location in self.m_serializedTemplates:
            self._id_to_location[location.m_id] = location
            self._filename_to_location[location.m_filename] = location
    
    def _calculate_statistics(self):
        """Calculate file type statistics"""
        self.file_types.clear()
        
        for location in self.m_serializedTemplates:
            file_type = location.file_type
            self.file_types[file_type] = self.file_types.get(file_type, 0) + 1
    
    def lookup_by_id(self, template_id: int) -> Optional[TemplateLocationDTO]:
        """
        Look up template location by ID.
        
        This is the primary use case - converting mob m_itemList IDs to deck filenames.
        """
        return self._id_to_location.get(template_id)
    
    def lookup_by_filename(self, filename: str) -> Optional[TemplateLocationDTO]:
        """Look up template location by filename"""
        return self._filename_to_location.get(filename)
    
    def get_filename(self, template_id: int) -> Optional[str]:
        """
        Get filename for a template ID.
        
        Args:
            template_id: Template ID to look up
            
        Returns:
            Filename or None if not found
        """
        location = self.lookup_by_id(template_id)
        return location.m_filename if location else None
    
    def get_file_name(self, template_id: int) -> Optional[str]:
        """
        Get file name (without path/extension) for a template ID.
        
        Args:
            template_id: Template ID to look up
            
        Returns:
            File name or None if not found
        """
        location = self.lookup_by_id(template_id)
        return location.file_name if location else None
    
    def get_templates_by_file_type(self, file_type: str) -> List[TemplateLocationDTO]:
        """Get all templates of a specific file type"""
        return [loc for loc in self.m_serializedTemplates if loc.file_type == file_type]
    
    def get_deck_templates(self) -> List[TemplateLocationDTO]:
        """Get all deck file templates"""
        return self.get_templates_by_file_type("deck")
    
    def get_spell_templates(self) -> List[TemplateLocationDTO]:
        """Get all spell file templates"""
        return self.get_templates_by_file_type("spell")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the manifest"""
        return {
            'total_templates': self.total_templates,
            'file_types': dict(self.file_types),
            'most_common_file_type': max(self.file_types.items(), key=lambda x: x[1])[0] if self.file_types else None,
            'valid_templates': sum(1 for loc in self.m_serializedTemplates if loc.m_id > 0 and loc.m_filename)
        }
    
    def validate_template_ids(self, template_ids: List[int]) -> Dict[str, Any]:
        """
        Validate a list of template IDs against the manifest.
        
        This is useful for validating mob m_itemList values.
        """
        found = []
        missing = []
        
        for template_id in template_ids:
            if template_id in self._id_to_location:
                found.append(template_id)
            else:
                missing.append(template_id)
        
        return {
            'total_checked': len(template_ids),
            'found': found,
            'missing': missing,
            'found_count': len(found),
            'missing_count': len(missing),
            'success_rate': len(found) / len(template_ids) if template_ids else 0.0
        }
    
    def __str__(self) -> str:
        return f"TemplateManifest(templates={self.total_templates}, types={len(self.template_types)})"
    
    def __len__(self) -> int:
        return self.total_templates