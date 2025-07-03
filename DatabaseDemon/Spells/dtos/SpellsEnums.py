"""
Wizard101 Spell Enums
=====================
Enum definitions for Wizard101 spell data structures.
"""

from enum import Enum


class kSpellSourceType(Enum):
    kCaster = 0
    kPet = 1
    kShadowCreature = 2
    kWeapon = 3
    kEquipment = 4


class GardenSpellType(Enum):
    GS_SoilPreparation = 0
    GS_Growing = 1
    GS_InsectFighting = 2
    GS_PlantProtection = 3
    GS_PlantUtility = 4


class FishingSpellType(Enum):
    FS_Catching = 0
    FS_Utility = 1
    FS_PredatorBanishment = 2


class CantripsSpellType(Enum):
    CS_Teleportation = 0
    CS_Incantation = 1
    CS_Beneficial = 2
    CS_Ritual = 3
    CS_Sigil = 4


class CantripsSpellEffect(Enum):
    CSE_None = 0
    CSE_PlayEffect = 1
    CSE_Mark = 2
    CSE_Recall = 3
    CSE_Heal = 4