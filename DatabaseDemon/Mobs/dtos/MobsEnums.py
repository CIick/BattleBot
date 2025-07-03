"""
Mobs Enumerations
================
Enumeration classes for Wizard101 mob constants and lookup values.
"""

from enum import Enum, IntEnum
from typing import Dict, Any


class MobTitle(IntEnum):
    """Mob title enumeration"""
    UNKNOWN = 0
    MINION = 1
    NORMAL = 2
    ELITE = 3
    BOSS = 4


class SchoolType(Enum):
    """Magic school enumeration"""
    FIRE = "Fire"
    ICE = "Ice" 
    STORM = "Storm"
    MYTH = "Myth"
    LIFE = "Life"
    DEATH = "Death"
    BALANCE = "Balance"
    STAR = "Star"
    SUN = "Sun"
    MOON = "Moon"
    SHADOW = "Shadow"


class ObjectType(IntEnum):
    """Game object type enumeration"""
    UNKNOWN = 0
    MOB = 1
    NPC = 2
    ITEM = 3


class LightType(IntEnum):
    """Lighting type enumeration"""
    NONE = 0
    POINT = 1
    DIRECTIONAL = 2
    SPOT = 3


class PathDirection(IntEnum):
    """Path direction enumeration"""
    FORWARD = 1
    REVERSE = -1


class PathType(IntEnum):
    """Path type enumeration"""
    LINEAR = 0
    LOOP = 1
    PING_PONG = 2