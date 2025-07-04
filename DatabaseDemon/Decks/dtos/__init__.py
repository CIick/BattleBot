"""
Decks DTOs Module
=================
Data Transfer Object classes for Wizard101 deck data structures.
"""

# Use try/except for flexible imports
try:
    from .DecksDTO import *
    from .DecksDTOFactory import DecksDTOFactory
    from .DecksEnums import *
except ImportError:
    # Fallback for direct execution
    from DecksDTO import *
    from DecksDTOFactory import DecksDTOFactory 
    from DecksEnums import *