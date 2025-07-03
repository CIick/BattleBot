"""
DatabaseDemon.Spells - Wizard101 Spell Database Creation Module
==============================================================
Creates SQLite database from Wizard101 Root.wad spell data.

Components:
- processors/: Core database creation logic (DatabaseCreator, WADProcessor, etc.)
- dtos/: Data Transfer Objects for spell data structures
- database_creator.py: Main entry point script

Usage:
    cd DatabaseDemon/Spells
    python database_creator.py

Requirements:
    - types.json file in parent DatabaseDemon directory
    - Wizard101 installed with accessible Root.wad file
"""

__version__ = "2.0.0"
__author__ = "Claude Code"
__description__ = "Wizard101 Spell Database Creation Module"