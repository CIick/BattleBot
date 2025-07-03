#!/usr/bin/env python3
"""
Enhanced DTO Generator for Wizard101 Spell Data
===============================================
Generates comprehensive DTOs for combat simulation, including:
- Proper inheritance hierarchy for spell templates
- Nested class DTOs (SpellEffect, RequirementList, etc.)
- Polymorphic factory support for complex object creation
- Complete type safety for all 14 combat-relevant types

Uses the focused analysis results to generate exactly what we need for combat simulation.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass


@dataclass
class DTOSpecification:
    """Specification for generating a DTO class"""
    class_name: str
    base_class: Optional[str]
    properties: Dict[str, str]
    hash_value: Optional[int]
    is_polymorphic: bool
    subtypes: List[str]


class EnhancedDTOGenerator:
    """Enhanced generator for comprehensive spell DTOs"""
    
    def __init__(self, dto_specs_path: str):
        self.dto_specs_path = Path(dto_specs_path)
        self.dto_specs: Dict[str, DTOSpecification] = {}
        self.inheritance_tree: Dict[str, List[str]] = {}
        self.enum_definitions: Dict[str, Dict[str, int]] = {}
        
        # Load specifications
        self.load_dto_specifications()
        self.build_inheritance_tree()
        self.load_enum_definitions()
    
    def load_dto_specifications(self):
        """Load DTO specifications from JSON file"""
        try:
            with open(self.dto_specs_path, 'r', encoding='utf-8') as f:
                specs_data = json.load(f)
            
            for type_name, spec_data in specs_data.items():
                self.dto_specs[type_name] = DTOSpecification(
                    class_name=spec_data["class_name"],
                    base_class=spec_data["base_class"],
                    properties=spec_data["properties"],
                    hash_value=spec_data["hash_value"],
                    is_polymorphic=spec_data["is_polymorphic"],
                    subtypes=spec_data["subtypes"]
                )
            
            print(f"Loaded {len(self.dto_specs)} DTO specifications")
            
        except Exception as e:
            print(f"Error loading DTO specifications: {e}")
            raise
    
    def build_inheritance_tree(self):
        """Build inheritance tree from specifications"""
        for type_name, spec in self.dto_specs.items():
            if spec.base_class:
                # Find the base type name
                base_type = spec.base_class.replace("DTO", "")
                if base_type not in self.inheritance_tree:
                    self.inheritance_tree[base_type] = []
                self.inheritance_tree[base_type].append(type_name)
            else:
                # This is a root type
                if type_name not in self.inheritance_tree:
                    self.inheritance_tree[type_name] = []
        
        print(f"Built inheritance tree with {len(self.inheritance_tree)} nodes")
    
    def load_enum_definitions(self):
        """Load enum definitions from the types JSON"""
        # For now, we'll use the enums from the existing wizard101_spell_dtos.py
        # In a more complete implementation, we'd extract these from the types JSON
        self.enum_definitions = {
            "kSpellSourceType": {
                "kCaster": 0,
                "kPet": 1,
                "kShadowCreature": 2,
                "kWeapon": 3,
                "kEquipment": 4
            },
            "kDelayOrder": {
                "SpellEffect_kAnyOrder": 0,
                "SpellEffect_kFirst": 1,
                "SpellEffect_kSecond": 2
            },
            "GardenSpellType": {
                "GS_SoilPreparation": 0,
                "GS_Growing": 1,
                "GS_InsectFighting": 2,
                "GS_PlantProtection": 3,
                "GS_PlantUtility": 4
            },
            "UtilitySpellType": {
                "US_None": 0,
                "US_Zap": 1,
                "US_Revive": 2,
                "US_Inspect": 3,
                "US_Stasis": 4,
                "US_PlowAll": 5,
                "US_PlantAll": 6,
                "US_HarvestNow": 7
            },
            "CastleMagicSpellType": {
                "CM_Action": 0,
                "CM_Effect": 1,
                "CM_Utility": 2,
                "CM_Logic": 3
            },
            "CastleMagicSpellEffect": {
                "CM_None": 0,
                "CM_MakeInvisible": 1,
                "CM_MakeVisible": 2,
                "CM_PlaySpellEffect": 3,
                "CM_PlaySoundEffect": 4
            },
            "FishingSpellType": {
                "FS_Catching": 0,
                "FS_Utility": 1,
                "FS_PredatorBanishment": 2
            },
            "CantripsSpellType": {
                "CS_Teleportation": 0,
                "CS_Incantation": 1,
                "CS_Beneficial": 2,
                "CS_Ritual": 3,
                "CS_Sigil": 4
            },
            "CantripsSpellEffect": {
                "CSE_None": 0,
                "CSE_PlayEffect": 1,
                "CSE_Mark": 2,
                "CSE_Recall": 3,
                "CSE_Heal": 4
            }
        }
    
    def generate_complete_module(self) -> str:
        """Generate the complete enhanced DTO module"""
        lines = []
        
        # Module header
        lines.extend(self.generate_module_header())
        
        # Imports
        lines.extend(self.generate_imports())
        
        # Enums
        lines.extend(self.generate_all_enums())
        
        # Base DTOs (no inheritance)
        lines.extend(self.generate_base_dtos())
        
        # Derived DTOs (with inheritance)
        lines.extend(self.generate_derived_dtos())
        
        # Enhanced factory
        lines.extend(self.generate_enhanced_factory())
        
        return "\n".join(lines)
    
    def generate_module_header(self) -> List[str]:
        """Generate enhanced module header"""
        return [
            '"""',
            'Enhanced Wizard101 Spell Template DTOs',
            '=====================================',
            'Comprehensive Data Transfer Objects for Wizard101 spell templates and nested types.',
            '',
            'This module contains:',
            f'- {len(self.dto_specs)} DTO classes with proper inheritance',
            f'- {len(self.enum_definitions)} enum definitions',
            '- Enhanced factory with polymorphic support',
            '- Full nested object creation capabilities',
            '',
            'Generated by enhanced_dto_generator.py for combat simulation',
            '"""',
            '',
        ]
    
    def generate_imports(self) -> List[str]:
        """Generate import statements"""
        return [
            'from dataclasses import dataclass',
            'from typing import Dict, List, Optional, Any, Union, Type',
            'from enum import Enum',
            '',
        ]
    
    def generate_all_enums(self) -> List[str]:
        """Generate all enum classes"""
        lines = ['# ===== ENUM DEFINITIONS =====', '']
        
        for enum_name, enum_values in self.enum_definitions.items():
            lines.extend(self.generate_enum_class(enum_name, enum_values))
            lines.append('')
        
        return lines
    
    def generate_enum_class(self, enum_name: str, enum_values: Dict[str, int]) -> List[str]:
        """Generate a single enum class"""
        lines = [f'class {enum_name}(Enum):']
        
        if not enum_values:
            lines.append('    pass')
            return lines
        
        for value_name, value_int in enum_values.items():
            lines.append(f'    {value_name} = {value_int}')
        
        return lines
    
    def generate_base_dtos(self) -> List[str]:
        """Generate base DTO classes (those without inheritance)"""
        lines = ['# ===== BASE DTO CLASSES =====', '']
        
        base_types = [name for name, spec in self.dto_specs.items() 
                     if spec.base_class is None]
        
        # Sort to ensure base classes come before derived ones
        base_types.sort()
        
        for type_name in base_types:
            spec = self.dto_specs[type_name]
            lines.extend(self.generate_dto_class(type_name, spec))
            lines.append('')
        
        return lines
    
    def generate_derived_dtos(self) -> List[str]:
        """Generate derived DTO classes (those with inheritance)"""
        lines = ['# ===== DERIVED DTO CLASSES =====', '']
        
        derived_types = [name for name, spec in self.dto_specs.items() 
                        if spec.base_class is not None]
        
        # Sort to ensure proper inheritance order
        derived_types.sort()
        
        for type_name in derived_types:
            spec = self.dto_specs[type_name]
            lines.extend(self.generate_dto_class(type_name, spec))
            lines.append('')
        
        return lines
    
    def generate_dto_class(self, type_name: str, spec: DTOSpecification) -> List[str]:
        """Generate a single DTO class"""
        lines = []
        
        # Class decorator
        lines.append('@dataclass')
        
        # Class definition
        if spec.base_class:
            lines.append(f'class {spec.class_name}({spec.base_class}):')
            lines.append(f'    """DTO for {type_name} - inherits from {spec.base_class}"""')
        else:
            lines.append(f'class {spec.class_name}:')
            lines.append(f'    """Base DTO for {type_name}"""')
        
        # Properties
        property_lines = self.generate_class_properties(type_name, spec)
        if property_lines:
            lines.extend(property_lines)
        else:
            lines.append('    pass')
        
        return lines
    
    def generate_class_properties(self, type_name: str, spec: DTOSpecification) -> List[str]:
        """Generate property definitions for a class"""
        lines = []
        
        if spec.base_class:
            # For derived classes, only include properties not in base class
            base_type = spec.base_class.replace("DTO", "")
            if base_type in self.dto_specs:
                base_spec = self.dto_specs[base_type]
                base_properties = set(base_spec.properties.keys())
                
                # Only include properties unique to this class
                unique_properties = set(spec.properties.keys()) - base_properties
                
                for prop_name in sorted(unique_properties):
                    prop_type = spec.properties[prop_name]
                    lines.append(f'    {prop_name}: {prop_type}')
        else:
            # For base classes, include all properties
            for prop_name in sorted(spec.properties.keys()):
                prop_type = spec.properties[prop_name]
                lines.append(f'    {prop_name}: {prop_type}')
        
        return lines
    
    def generate_enhanced_factory(self) -> List[str]:
        """Generate enhanced factory with polymorphic support"""
        lines = [
            '# ===== ENHANCED FACTORY =====',
            '',
            'class EnhancedSpellDTOFactory:',
            '    """Enhanced factory for creating spell DTOs with full polymorphic support"""',
            '    ',
            '    # Hash to DTO class mapping',
            '    TYPE_MAPPING: Dict[int, Type] = {'
        ]
        
        # Add type mappings
        for type_name, spec in self.dto_specs.items():
            if spec.hash_value:
                lines.append(f'        {spec.hash_value}: {spec.class_name},')
        
        lines.extend([
            '    }',
            '    ',
            '    # Polymorphic type mapping (for Union types)',
            '    POLYMORPHIC_MAPPING: Dict[str, List[Type]] = {'
        ])
        
        # Add polymorphic mappings
        for type_name, spec in self.dto_specs.items():
            if spec.is_polymorphic and spec.subtypes:
                subtype_classes = [f'{subtype}DTO' for subtype in spec.subtypes]
                lines.append(f'        "{spec.class_name}": [{", ".join(subtype_classes)}],')
        
        lines.extend([
            '    }',
            '    ',
            '    @classmethod',
            '    def create_dto(cls, type_hash: int, spell_data: Dict[str, Any]) -> Optional[Any]:',
            '        """Create appropriate DTO instance based on type hash"""',
            '        dto_class = cls.TYPE_MAPPING.get(type_hash)',
            '        if dto_class:',
            '            try:',
            '                # Convert nested objects recursively',
            '                processed_data = cls.process_nested_objects(spell_data)',
            '                ',
            '                # Filter data to only include fields that exist in the DTO',
            '                filtered_data = cls.filter_data_for_dto(dto_class, processed_data)',
            '                ',
            '                # Create the DTO instance',
            '                return dto_class(**filtered_data)',
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
            '                # This is a nested typed object - find its hash and create DTO',
            '                nested_type = value["$__type"].replace("class ", "")',
            '                ',
            '                # Find the hash for this type',
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
            '    def filter_data_for_dto(cls, dto_class: Type, data: Dict[str, Any]) -> Dict[str, Any]:',
            '        """Filter data to only include fields that exist in the DTO class"""',
            '        if hasattr(dto_class, "__annotations__"):',
            '            valid_fields = set(dto_class.__annotations__.keys())',
            '            return {k: v for k, v in data.items() if k in valid_fields}',
            '        return data',
            '    ',
            '    @classmethod',
            '    def get_supported_hashes(cls) -> List[int]:',
            '        """Get list of all supported type hashes"""',
            '        return list(cls.TYPE_MAPPING.keys())',
            '    ',
            '    @classmethod',
            '    def get_polymorphic_types(cls) -> Dict[str, List[Type]]:',
            '        """Get polymorphic type mappings"""',
            '        return cls.POLYMORPHIC_MAPPING.copy()',
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
            '            return None'
        ])
        
        return lines
    
    def save_generated_module(self, output_path: str = "enhanced_wizard101_spell_dtos.py"):
        """Save the generated enhanced module to file"""
        module_code = self.generate_complete_module()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(module_code)
        
        print(f"Enhanced DTO module saved to: {output_path}")
        return output_path
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of what was generated"""
        lines = []
        
        lines.append("Enhanced DTO Generation Summary")
        lines.append("=" * 40)
        lines.append("")
        
        # Count different types
        base_types = [name for name, spec in self.dto_specs.items() if spec.base_class is None]
        derived_types = [name for name, spec in self.dto_specs.items() if spec.base_class is not None]
        polymorphic_types = [name for name, spec in self.dto_specs.items() if spec.is_polymorphic]
        
        lines.append(f"Base DTO classes: {len(base_types)}")
        for type_name in sorted(base_types):
            lines.append(f"  - {type_name}DTO")
        
        lines.append("")
        lines.append(f"Derived DTO classes: {len(derived_types)}")
        for type_name in sorted(derived_types):
            spec = self.dto_specs[type_name]
            lines.append(f"  - {type_name}DTO (inherits from {spec.base_class})")
        
        lines.append("")
        lines.append(f"Polymorphic types: {len(polymorphic_types)}")
        for type_name in sorted(polymorphic_types):
            spec = self.dto_specs[type_name]
            lines.append(f"  - {type_name}DTO has subtypes: {', '.join(spec.subtypes)}")
        
        lines.append("")
        lines.append(f"Enum definitions: {len(self.enum_definitions)}")
        for enum_name in sorted(self.enum_definitions.keys()):
            lines.append(f"  - {enum_name}")
        
        lines.append("")
        lines.append("Features:")
        lines.append("  - Proper inheritance hierarchy")
        lines.append("  - Recursive nested object creation")
        lines.append("  - Polymorphic factory support")
        lines.append("  - Type-safe property definitions")
        lines.append("  - Hash-based DTO creation")
        lines.append("  - JSON data processing")
        
        return "\n".join(lines)


def main():
    """Main function to generate enhanced DTOs"""
    dto_specs_path = "../dto_specifications.json"
    
    if not Path(dto_specs_path).exists():
        print(f"Error: DTO specifications file not found: {dto_specs_path}")
        print("Please run focused_nested_analyzer.py first to generate specifications.")
        return 1
    
    # Generate enhanced DTOs
    generator = EnhancedDTOGenerator(dto_specs_path)
    output_file = generator.save_generated_module("enhanced_wizard101_spell_dtos.py")
    
    # Generate summary report
    summary = generator.generate_summary_report()
    with open("../Reports/Spell Reports/enhanced_dto_summary.txt", 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("\n" + "=" * 50)
    print("ENHANCED DTO GENERATION COMPLETE")
    print("=" * 50)
    print(summary)
    print(f"\nOutput files:")
    print(f"  - {output_file}")
    print(f"  - enhanced_dto_summary.txt")
    
    return 0


if __name__ == "__main__":
    exit(main())