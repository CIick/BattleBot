"""
Decks Processors Module
=======================
Core processing logic for Wizard101 deck database creation.
"""

# Use try/except for flexible imports
try:
    from .DatabaseCreator import DatabaseCreator
    from .DatabaseSchema import DatabaseSchema
    from .WADProcessor import WADProcessor
except ImportError:
    # Fallback for direct execution
    from DatabaseCreator import DatabaseCreator
    from DatabaseSchema import DatabaseSchema
    from WADProcessor import WADProcessor