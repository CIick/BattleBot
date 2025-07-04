"""
TemplateManifest Database System
===============================

Wizard101 TemplateManifest processing system for creating databases from Root.wad TemplateManifest.xml files.
Provides template ID to deck filename mapping for linking mob item lists to deck data.

Key components:
- DTOs: Data Transfer Objects for TemplateManifest and TemplateLocation
- Processors: WAD processing, database creation, and schema management
- Testing: Comprehensive validation and testing framework

Usage:
    python database_creator.py

This system enables lookup of template IDs (e.g., 211553) to deck filenames (e.g., "Mdeck-I-R9.xml")
for linking mob m_itemList values to their corresponding deck data.
"""

__version__ = "1.0.0"
__author__ = "DatabaseDemon"