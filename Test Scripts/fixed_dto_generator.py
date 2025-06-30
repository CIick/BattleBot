#!/usr/bin/env python3
"""
Fixed DTO Generator for Wizard101 Spell Data
============================================
Generates DTOs with proper default values to handle missing properties gracefully.
All fields are optional with sensible defaults to ensure DTOs can be created from
incomplete data.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field


class FixedDTOGenerator:
    """Fixed generator that creates DTOs with proper defaults"""
    
    def __init__(self, dto_specs_path: str):
        self.dto_specs_path = Path(dto_specs_path)
        self.dto_specs = {}
        self.load_dto_specifications()
        
    def load_dto_specifications(self):
        """Load DTO specifications from JSON file"""
        try:
            with open(self.dto_specs_path, 'r', encoding='utf-8') as f:
                self.dto_specs = json.load(f)
            print(f"Loaded {len(self.dto_specs)} DTO specifications")
        except Exception as e:
            print(f"Error loading DTO specifications: {e}")
            raise
    
    def get_default_value_for_type(self, python_type: str) -> str:
        """Get default value for a Python type"""
        type_defaults = {
            "bool": "False",
            "int": "0",
            "float": "0.0",
            "str": '""',
            "Optional[Any]": "None",
            "Any": "None"
        }
        
        # Handle List types
        if python_type.startswith("List["):
            return "field(default_factory=list)"
        
        # Handle specific DTO types
        if python_type.endswith("DTO"):
            return "None"
        
        # Handle Optional types
        if python_type.startswith("Optional["):
            return "None"
        
        return type_defaults.get(python_type, "None")
    
    def generate_complete_module(self) -> str:
        """Generate the complete fixed DTO module"""
        lines = []
        
        # Module header
        lines.extend([
            '"""',
            'Fixed Wizard101 Spell Template DTOs',
            '===================================',
            'DTOs with proper default values for handling incomplete spell data.',
            '',
            'All fields have sensible defaults to ensure DTOs can be created',
            'even when some properties are missing from the source data.',
            '"""',
            '',
            'from dataclasses import dataclass, field',
            'from typing import Dict, List, Optional, Any, Union, Type',
            'from enum import Enum',
            '',
        ])
        
        # Enums
        lines.extend(self.generate_enums())
        
        # Base DTOs first
        base_types = [name for name, spec in self.dto_specs.items() 
                     if spec.get("base_class") is None]
        
        lines.extend(['# ===== BASE DTO CLASSES =====', ''])
        for type_name in sorted(base_types):
            lines.extend(self.generate_dto_class(type_name))
            lines.append('')
        
        # Derived DTOs
        derived_types = [name for name, spec in self.dto_specs.items() 
                        if spec.get("base_class") is not None]
        
        lines.extend(['# ===== DERIVED DTO CLASSES =====', ''])
        for type_name in sorted(derived_types):
            lines.extend(self.generate_dto_class(type_name))
            lines.append('')
        
        # Enhanced factory
        lines.extend(self.generate_enhanced_factory())
        
        return "\n".join(lines)
    
    def generate_enums(self) -> List[str]:
        """Generate enum definitions"""
        return [
            '# ===== ENUM DEFINITIONS =====',
            '',
            'class kSpellSourceType(Enum):',
            '    kCaster = 0',
            '    kPet = 1',
            '    kShadowCreature = 2',
            '    kWeapon = 3',
            '    kEquipment = 4',
            '',
            'class GardenSpellType(Enum):',
            '    GS_SoilPreparation = 0',
            '    GS_Growing = 1',
            '    GS_InsectFighting = 2',
            '    GS_PlantProtection = 3',
            '    GS_PlantUtility = 4',
            '',
            'class FishingSpellType(Enum):',
            '    FS_Catching = 0',
            '    FS_Utility = 1',
            '    FS_PredatorBanishment = 2',
            '',
            'class CantripsSpellType(Enum):',
            '    CS_Teleportation = 0',
            '    CS_Incantation = 1',
            '    CS_Beneficial = 2',
            '    CS_Ritual = 3',
            '    CS_Sigil = 4',
            '',
            'class CantripsSpellEffect(Enum):',
            '    CSE_None = 0',
            '    CSE_PlayEffect = 1',
            '    CSE_Mark = 2',
            '    CSE_Recall = 3',
            '    CSE_Heal = 4',
            '',
        ]
    
    def generate_dto_class(self, type_name: str) -> List[str]:
        """Generate a single DTO class with proper defaults"""
        spec = self.dto_specs[type_name]
        lines = []
        
        # Class decorator and definition
        lines.append('@dataclass')
        
        if spec.get("base_class"):
            lines.append(f'class {spec["class_name"]}({spec["base_class"]}):')
            lines.append(f'    """DTO for {type_name} - inherits from {spec["base_class"]}"""')
        else:
            lines.append(f'class {spec["class_name"]}:')
            lines.append(f'    """Base DTO for {type_name}"""')
        
        # Properties with defaults
        properties = spec.get("properties", {})
        
        if spec.get("base_class"):
            # For derived classes, only include unique properties
            base_type = spec["base_class"].replace("DTO", "")
            if base_type in self.dto_specs:
                base_props = set(self.dto_specs[base_type].get("properties", {}).keys())
                unique_props = {k: v for k, v in properties.items() if k not in base_props}
                properties = unique_props
        
        if properties:
            for prop_name in sorted(properties.keys()):
                prop_type = properties[prop_name]
                default_value = self.get_default_value_for_type(prop_type)
                
                # Make all properties optional with defaults
                if default_value == "field(default_factory=list)":
                    lines.append(f'    {prop_name}: {prop_type} = {default_value}')
                else:
                    # Make the type optional and provide default
                    if not prop_type.startswith("Optional[") and prop_type != "Any":
                        prop_type = f"Optional[{prop_type}]"
                    lines.append(f'    {prop_name}: {prop_type} = {default_value}')
        else:
            lines.append('    pass')
        
        return lines
    
    def generate_enhanced_factory(self) -> List[str]:
        """Generate enhanced factory with better error handling"""
        lines = [
            '# ===== ENHANCED FACTORY =====',
            '',
            'class FixedSpellDTOFactory:',
            '    """Fixed factory for creating spell DTOs with graceful error handling"""',
            '    ',
            '    # Hash to DTO class mapping',
            '    TYPE_MAPPING: Dict[int, Type] = {'
        ]
        
        # Add type mappings
        for type_name, spec in self.dto_specs.items():
            if spec.get("hash_value"):
                lines.append(f'        {spec["hash_value"]}: {spec["class_name"]},')
        
        lines.extend([
            '    }',
            '    ',
            '    @classmethod',
            '    def create_dto(cls, type_hash: int, spell_data: Dict[str, Any]) -> Optional[Any]:',
            '        """Create appropriate DTO instance based on type hash"""',
            '        dto_class = cls.TYPE_MAPPING.get(type_hash)',
            '        if dto_class:',
            '            try:',
            '                # Process nested objects recursively',
            '                processed_data = cls.process_nested_objects(spell_data)',
            '                ',
            '                # Create kwargs with only the fields that exist in both data and DTO',
            '                kwargs = {}',
            '                if hasattr(dto_class, "__annotations__"):',
            '                    for field_name in dto_class.__annotations__.keys():',
            '                        if field_name in processed_data:',
            '                            kwargs[field_name] = processed_data[field_name]',
            '                ',
            '                # Create the DTO instance (missing fields will use defaults)',
            '                return dto_class(**kwargs)',
            '            except Exception as e:',
            '                print(f"Error creating DTO for hash {type_hash}: {e}")',
            '                return None',
            '        else:',
            '            print(f"No DTO class found for hash {type_hash}")',
            '            return None',
            '    ',
            '    @classmethod',
            '    def process_nested_objects(cls, data: Dict[str, Any]) -> Dict[str, Any]:',
            '        """Recursively process nested objects to create DTOs"""',
            '        if not isinstance(data, dict):',
            '            return data',
            '        ',
            '        processed = {}',
            '        ',
            '        for key, value in data.items():',
            '            if isinstance(value, dict) and "$__type" in value:',
            '                # This is a nested typed object',
            '                nested_type = value["$__type"].replace("class ", "")',
            '                nested_hash = cls.find_hash_for_type(nested_type)',
            '                if nested_hash:',
            '                    processed[key] = cls.create_dto(nested_hash, value)',
            '                else:',
            '                    processed[key] = value',
            '            ',
            '            elif isinstance(value, list):',
            '                # Process list items',
            '                processed_list = []',
            '                for item in value:',
            '                    if isinstance(item, dict) and "$__type" in item:',
            '                        nested_type = item["$__type"].replace("class ", "")',
            '                        nested_hash = cls.find_hash_for_type(nested_type)',
            '                        if nested_hash:',
            '                            processed_list.append(cls.create_dto(nested_hash, item))',
            '                        else:',
            '                            processed_list.append(item)',
            '                    else:',
            '                        processed_list.append(item)',
            '                processed[key] = processed_list',
            '            ',
            '            else:',
            '                processed[key] = value',
            '        ',
            '        return processed',
            '    ',
            '    @classmethod',
            '    def find_hash_for_type(cls, type_name: str) -> Optional[int]:',
            '        """Find hash value for a given type name"""',
            '        for hash_val, dto_class in cls.TYPE_MAPPING.items():',
            '            if dto_class.__name__ == f"{type_name}DTO":',
            '                return hash_val',
            '        return None',
            '    ',
            '    @classmethod',
            '    def create_from_json_data(cls, json_data: Dict[str, Any]) -> Optional[Any]:',
            '        """Create DTO from raw JSON data (with $__type field)"""',
            '        if "$__type" not in json_data:',
            '            print("No $__type field found in JSON data")',
            '            return None',
            '        ',
            '        type_name = json_data["$__type"].replace("class ", "")',
            '        type_hash = cls.find_hash_for_type(type_name)',
            '        ',
            '        if type_hash:',
            '            return cls.create_dto(type_hash, json_data)',
            '        else:',
            '            print(f"No hash found for type: {type_name}")',
            '            return None',
            '    ',
            '    @classmethod',
            '    def get_supported_hashes(cls) -> List[int]:',
            '        """Get list of all supported type hashes"""',
            '        return list(cls.TYPE_MAPPING.keys())'
        ])
        
        return lines
    
    def save_generated_module(self, output_path: str = "fixed_wizard101_spell_dtos.py"):
        """Save the generated fixed module to file"""
        module_code = self.generate_complete_module()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(module_code)
        
        print(f"Fixed DTO module saved to: {output_path}")
        return output_path


def main():
    """Main function to generate fixed DTOs"""
    dto_specs_path = "../dto_specifications.json"
    
    if not Path(dto_specs_path).exists():
        print(f"Error: DTO specifications file not found: {dto_specs_path}")
        return 1
    
    # Generate fixed DTOs
    generator = FixedDTOGenerator(dto_specs_path)
    output_file = generator.save_generated_module("fixed_wizard101_spell_dtos.py")
    
    print(f"\nFixed DTO module generated: {output_file}")
    print("All fields have proper defaults to handle missing properties gracefully.")
    
    return 0


if __name__ == "__main__":
    exit(main())