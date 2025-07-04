"""
TemplateManifest DTOs
====================

Data Transfer Objects for TemplateManifest system.
Handles conversion between LazyObjects and structured Python objects.

Components:
- TemplateManifestDTO: Main manifest with template locations
- TemplateLocationDTO: Individual template location with ID and filename
- TemplateManifestDTOFactory: Factory for creating DTOs from raw data
- TemplateManifestEnums: Enumerated values and constants
"""

try:
    from .TemplateManifestDTO import *
    from .TemplateManifestDTOFactory import *
    from .TemplateManifestEnums import *
except ImportError:
    # Fallback for direct execution
    from TemplateManifestDTO import *
    from TemplateManifestDTOFactory import *
    from TemplateManifestEnums import *