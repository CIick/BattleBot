"""
Mobs DTO Factory
===============
Factory class for creating mob DTOs from JSON data with proper type mapping
and behavior handling.
"""

import logging
from typing import Dict, Any, Optional, List, Type, Union
from dataclasses import fields

from .MobsDTO import (
    WizGameObjectTemplateDTO,
    BehaviorTemplateDTO,
    AnimationBehaviorDTO,
    WizardEquipmentBehaviorDTO,
    BasicObjectStateBehaviorDTO,
    PathBehaviorDTO,
    PathMovementBehaviorDTO,
    DuelistBehaviorDTO,
    NPCBehaviorDTO,
    CollisionBehaviorDTO,
    MobMonsterMagicBehaviorDTO
)


class MobsDTOFactory:
    """Factory for creating mob DTOs from JSON data"""
    
    # Type hash mappings for mob objects
    MOB_TYPE_MAPPINGS: Dict[int, Type] = {
        701229577: WizGameObjectTemplateDTO,  # WizGameObjectTemplate
    }
    
    # Type hash mappings for behavior objects
    BEHAVIOR_TYPE_MAPPINGS: Dict[int, Type] = {
        360231646: BehaviorTemplateDTO,          # BehaviorTemplate (base)
        101271634: AnimationBehaviorDTO,         # AnimationBehavior
        892480983: WizardEquipmentBehaviorDTO,   # WizardEquipmentBehavior
        1364452653: BasicObjectStateBehaviorDTO, # BasicObjectStateBehavior
        185541179: PathBehaviorDTO,              # PathBehavior
        1443896326: PathMovementBehaviorDTO,     # PathMovementBehavior
        290147688: DuelistBehaviorDTO,           # DuelistBehavior
        1701337223: NPCBehaviorDTO,              # NPCBehavior
        2052493990: CollisionBehaviorDTO,        # CollisionBehavior
        959047476: MobMonsterMagicBehaviorDTO,   # MobMonsterMagicBehavior
    }
    
    @classmethod
    def create_from_json_data(cls, data: Dict[str, Any]) -> Optional[WizGameObjectTemplateDTO]:
        """
        Create a mob DTO from JSON data
        
        Args:
            data: Dictionary containing mob data from WAD file
            
        Returns:
            WizGameObjectTemplateDTO instance or None if not a valid mob
        """
        if not isinstance(data, dict):
            return None
        
        # Check if this is a WizGameObjectTemplate
        type_hash = data.get('$__type')
        if type_hash != 701229577:
            return None
        
        try:
            # Create base mob DTO
            mob_dto = cls._create_dto_from_data(WizGameObjectTemplateDTO, data)
            
            # Process behaviors if present
            if 'm_behaviors' in data and isinstance(data['m_behaviors'], list):
                mob_dto.m_behaviors = cls._process_behaviors(data['m_behaviors'])
            
            return mob_dto
            
        except Exception as e:
            logging.warning(f"Failed to create mob DTO: {e}")
            return None
    
    @classmethod
    def _process_behaviors(cls, behaviors_data: List[Any]) -> List[Any]:
        """
        Process behavior list and convert to appropriate DTOs
        
        Args:
            behaviors_data: List of behavior objects from mob data
            
        Returns:
            List of behavior DTOs
        """
        processed_behaviors = []
        
        for behavior in behaviors_data:
            if behavior is None:
                processed_behaviors.append(None)
                continue
            
            if not isinstance(behavior, dict):
                processed_behaviors.append(behavior)
                continue
            
            # Get behavior type hash
            behavior_type = behavior.get('$__type')
            
            if behavior_type in cls.BEHAVIOR_TYPE_MAPPINGS:
                # Create appropriate behavior DTO
                behavior_class = cls.BEHAVIOR_TYPE_MAPPINGS[behavior_type]
                try:
                    behavior_dto = cls._create_dto_from_data(behavior_class, behavior)
                    processed_behaviors.append(behavior_dto)
                except Exception as e:
                    logging.warning(f"Failed to create behavior DTO for type {behavior_type}: {e}")
                    processed_behaviors.append(behavior)  # Keep original data
            else:
                # Unknown behavior type - keep original data
                logging.debug(f"Unknown behavior type: {behavior_type}")
                processed_behaviors.append(behavior)
        
        return processed_behaviors
    
    @classmethod
    def _create_dto_from_data(cls, dto_class: Type, data: Dict[str, Any]) -> Any:
        """
        Create a DTO instance from data dictionary
        
        Args:
            dto_class: The DTO class to instantiate
            data: Dictionary containing the data
            
        Returns:
            DTO instance with populated fields
        """
        # Get field names for the DTO class
        dto_fields = {f.name for f in fields(dto_class)}
        
        # Extract relevant data for this DTO
        dto_data = {}
        for key, value in data.items():
            if key in dto_fields:
                dto_data[key] = value
        
        # Create DTO instance
        return dto_class(**dto_data)
    
    @classmethod
    def get_supported_mob_types(cls) -> Dict[int, str]:
        """
        Get mapping of supported mob type hashes to class names
        
        Returns:
            Dictionary mapping type hash to class name
        """
        return {
            hash_value: dto_class.__name__ 
            for hash_value, dto_class in cls.MOB_TYPE_MAPPINGS.items()
        }
    
    @classmethod
    def get_supported_behavior_types(cls) -> Dict[int, str]:
        """
        Get mapping of supported behavior type hashes to class names
        
        Returns:
            Dictionary mapping type hash to class name
        """
        return {
            hash_value: dto_class.__name__ 
            for hash_value, dto_class in cls.BEHAVIOR_TYPE_MAPPINGS.items()
        }
    
    @classmethod
    def is_supported_mob_type(cls, type_hash: int) -> bool:
        """
        Check if a type hash is supported for mob creation
        
        Args:
            type_hash: The type hash to check
            
        Returns:
            True if supported, False otherwise
        """
        return type_hash in cls.MOB_TYPE_MAPPINGS
    
    @classmethod
    def is_supported_behavior_type(cls, type_hash: int) -> bool:
        """
        Check if a type hash is supported for behavior creation
        
        Args:
            type_hash: The type hash to check
            
        Returns:
            True if supported, False otherwise
        """
        return type_hash in cls.BEHAVIOR_TYPE_MAPPINGS