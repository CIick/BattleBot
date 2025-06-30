"""
Wizard101 Spell DTO Factory
===========================
Factory and processing logic for creating spell DTOs with graceful error handling.
"""

from typing import Dict, List, Optional, Any, Type
from .SpellsDTO import *


class FixedSpellDTOFactory:
    """Fixed factory for creating spell DTOs with graceful error handling"""
    
    # Hash to DTO class mapping
    TYPE_MAPPING: Dict[int, Type] = {
        1864220976: SpellTemplateDTO,
        1225309305: SpellEffectDTO,
        853452777: SpellRankDTO,
        1015536062: TieredSpellTemplateDTO,
        1906855338: RandomSpellEffectDTO,
        1558190673: RequirementListDTO,
        258825572: ReqMagicLevelDTO,
        1087768358: CastleMagicSpellTemplateDTO,
        108720390: GardenSpellTemplateDTO,
        710415701: ReqGardeningLevelDTO,
        2095072282: FishingSpellTemplateDTO,
        443110133: CantripsSpellTemplateDTO,
        1914767513: ReqHasBadgeDTO,
        1093865471: WhirlyBurlySpellTemplateDTO,
        1928119170: DelaySpellEffectDTO,  # Added DelaySpellEffect
        1004451249: SpellDTO,  # Added Spell (root spell object)
        
        # All missing effect types from discovery
        1601626199: ConditionalSpellElementDTO,  # ConditionalSpellElement
        1545841998: ConditionalSpellEffectDTO,  # ConditionalSpellEffect
        1965311493: VariableSpellEffectDTO,  # VariableSpellEffect
        1760816619: EffectListSpellEffectDTO,  # EffectListSpellEffect
        1007398909: TargetCountSpellEffectDTO,  # TargetCountSpellEffect
        1531258114: HangingConversionSpellEffectDTO,  # HangingConversionSpellEffect
        1017660130: ShadowSpellEffectDTO,  # ShadowSpellEffect
        1256117554: RandomPerTargetSpellEffectDTO,  # RandomPerTargetSpellEffect
        61741842: CountBasedSpellEffectDTO,  # CountBasedSpellEffect
        
        # All missing requirement types from error analysis
        566693623: ReqHangingCharmDTO,  # ReqHangingCharm
        1161498678: ReqCombatHealthDTO,  # ReqCombatHealth  
        1670595781: ReqPipCountDTO,  # ReqPipCount
        1558190673: RequirementListDTO,  # RequirementList (already existed)
        808508263: ReqHangingOverTimeDTO,  # ReqHangingOverTime
        859401725: ReqMinionDTO,  # ReqMinion
        1523922554: ReqCombatStatusDTO,  # ReqCombatStatus
        1321510422: ReqHangingEffectTypeDTO,  # ReqHangingEffectType
        37594247: ReqHasEntryDTO,  # ReqHasEntry
        488394038: ReqShadowPipCountDTO,  # ReqShadowPipCount
        1827867182: ReqHangingWardDTO,  # ReqHangingWard
        392858099: ReqSchoolOfFocusDTO,  # ReqSchoolOfFocus
        295368144: ReqHangingAuraDTO,  # ReqHangingAura
        1501176517: ReqPvPCombatDTO,  # ReqPvPCombat
        1382050381: ReqIsSchoolDTO,  # ReqIsSchool
    }
    
    @classmethod
    def create_dto(cls, type_hash: int, spell_data: Dict[str, Any]) -> Optional[Any]:
        """Create appropriate DTO instance based on type hash"""
        dto_class = cls.TYPE_MAPPING.get(type_hash)
        if dto_class:
            try:
                # Process nested objects recursively
                processed_data = cls.process_nested_objects(spell_data)
                
                # Create kwargs with only the fields that exist in both data and DTO
                # Get all fields including inherited ones from parent classes
                kwargs = {}
                all_fields = set()
                
                # Collect annotations from the class and all parent classes
                for cls in dto_class.__mro__:  # Method Resolution Order includes all parent classes
                    if hasattr(cls, "__annotations__"):
                        all_fields.update(cls.__annotations__.keys())
                
                # Add fields that exist in both processed data and DTO class
                for field_name in all_fields:
                    if field_name in processed_data:
                        kwargs[field_name] = processed_data[field_name]
                
                # Create the DTO instance (missing fields will use defaults)
                return dto_class(**kwargs)
            except Exception as e:
                print(f"Error creating DTO for hash {type_hash}: {e}")
                return None
        else:
            print(f"No DTO class found for hash {type_hash}")
            return None
    
    @classmethod
    def process_nested_objects(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively process nested objects to create DTOs"""
        if not isinstance(data, dict):
            return data
        
        processed = {}
        
        for key, value in data.items():
            if isinstance(value, dict) and "$__type" in value:
                # This is a nested typed object
                nested_type = value["$__type"].replace("class ", "")
                nested_hash = cls.find_hash_for_type(nested_type)
                if nested_hash:
                    processed[key] = cls.create_dto(nested_hash, value)
                else:
                    processed[key] = value
            
            elif isinstance(value, list):
                # Process list items
                processed_list = []
                for item in value:
                    if isinstance(item, dict) and "$__type" in item:
                        nested_type = item["$__type"].replace("class ", "")
                        nested_hash = cls.find_hash_for_type(nested_type)
                        if nested_hash:
                            processed_dto = cls.create_dto(nested_hash, item)
                            if processed_dto is not None:
                                processed_list.append(processed_dto)
                            else:
                                print(f"WARNING: Failed to create DTO for type {nested_type} (hash: {nested_hash})")
                                processed_list.append(item)
                        else:
                            print(f"WARNING: No hash mapping found for type {nested_type}")
                            processed_list.append(item)
                    elif isinstance(item, dict):
                        # Recursively process nested dicts that might contain $__type
                        processed_item = cls.process_nested_objects(item)
                        processed_list.append(processed_item)
                    else:
                        processed_list.append(item)
                processed[key] = processed_list
            
            else:
                processed[key] = value
        
        return processed
    
    @classmethod
    def find_hash_for_type(cls, type_name: str) -> Optional[int]:
        """Find hash value for a given type name"""
        for hash_val, dto_class in cls.TYPE_MAPPING.items():
            if dto_class.__name__ == f"{type_name}DTO":
                return hash_val
        return None
    
    @classmethod
    def create_from_json_data(cls, json_data: Dict[str, Any]) -> Optional[Any]:
        """Create DTO from raw JSON data (with $__type field)"""
        if "$__type" not in json_data:
            print("No $__type field found in JSON data")
            return None
        
        type_name = json_data["$__type"].replace("class ", "")
        type_hash = cls.find_hash_for_type(type_name)
        
        if type_hash:
            return cls.create_dto(type_hash, json_data)
        else:
            print(f"No hash found for type: {type_name}")
            return None
    
    @classmethod
    def get_supported_hashes(cls) -> List[int]:
        """Get list of all supported type hashes"""
        return list(cls.TYPE_MAPPING.keys())
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of all supported DTO class names"""
        return [dto_class.__name__ for dto_class in cls.TYPE_MAPPING.values()]