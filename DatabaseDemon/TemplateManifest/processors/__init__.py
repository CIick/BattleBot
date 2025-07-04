"""
TemplateManifest Processors
==========================

Processing components for TemplateManifest system.
Handles WAD file processing, database creation, and schema management.

Components:
- WADProcessor: Processes TemplateManifest.xml from Root.wad
- DatabaseCreator: Creates and populates SQLite database
- DatabaseSchema: SQLite schema management and migrations
"""

try:
    from .WADProcessor import *
    from .DatabaseCreator import *
    from .DatabaseSchema import *
except ImportError:
    # Fallback for direct execution
    from WADProcessor import *
    from DatabaseCreator import *
    from DatabaseSchema import *