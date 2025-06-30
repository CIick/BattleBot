#!/usr/bin/env python3
"""
Wizard101 Dynamic Spell DTO Generator
=====================================
Standalone tool that dynamically discovers and generates Python DTO classes
for ALL Wizard101 spell template types from any wiztype dump.

Usage:
    python class_generator.py [types_json_path]
    
Features:
    - Auto-discovers new spell template types (future-proof)
    - Generates proper inheritance hierarchy
    - Creates type-safe dataclasses with proper annotations
    - Handles enums, containers, and pointer types
    - Outputs working Python module with all DTOs
"""

import json
import re
from typing import Dict, List, Set, Any, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sys


@dataclass
class SpellTemplateInfo:
    """Information about a discovered spell template class"""
    hash_value: int
    name: str
    class_name: str  # Clean class name without 'class ' prefix
    bases: List[str]
    properties: Dict[str, Dict[str, Any]]
    
    
@dataclass
class PropertyInfo:
    """Information about a spell template property"""
    name: str
    cpp_type: str
    python_type: str
    container: str
    is_pointer: bool
    is_dynamic: bool
    enum_options: Optional[Dict[str, Any]]
    

class SpellTemplateDiscovery:
    """Dynamic discovery and analysis of spell template types"""
    
    def __init__(self, types_json_path: str):
        self.types_json_path = Path(types_json_path)
        self.types_data = self.load_types_json()
        self.discovered_templates: Dict[int, SpellTemplateInfo] = {}
        self.inheritance_tree: Dict[str, List[str]] = {}
        self.all_properties: Dict[str, PropertyInfo] = {}
        self.shared_properties: Set[str] = set()
        self.enum_definitions: Dict[str, Dict[str, int]] = {}
        self.core_templates: Dict[int, SpellTemplateInfo] = {}  # Only core templates (not pointers/pairs)
        
    def load_types_json(self) -> Dict[str, Any]:
        """Load and parse the types JSON file"""
        try:
            with open(self.types_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded types JSON from {self.types_json_path}")
            return data
        except Exception as e:
            print(f"Error loading types JSON: {e}")
            sys.exit(1)
    
    def extract_class_name(self, full_name: str) -> str:
        """Extract clean class name from full C++ class name"""
        # Remove "class " prefix and any pointer indicators
        clean_name = full_name.replace("class ", "").replace("*", "").strip()
        return clean_name
    
    def discover_all_spell_templates(self) -> Dict[int, SpellTemplateInfo]:
        """Main discovery method - finds ALL spell template types"""
        print("Discovering spell template types...")
        
        discovered_count = 0
        
        for hash_str, class_info in self.types_data.get("classes", {}).items():
            class_name = class_info.get("name", "")
            
            # Look for any class containing "SpellTemplate"
            if "SpellTemplate" in class_name and "class " in class_name:
                hash_value = int(hash_str)
                clean_name = self.extract_class_name(class_name)
                
                template_info = SpellTemplateInfo(
                    hash_value=hash_value,
                    name=class_name,
                    class_name=clean_name,
                    bases=class_info.get("bases", []),
                    properties=class_info.get("properties", {})
                )
                
                self.discovered_templates[hash_value] = template_info
                discovered_count += 1
                
                # Filter for core templates (exclude pointers, pairs, etc.)
                if self.is_core_template(clean_name):
                    self.core_templates[hash_value] = template_info
                    print(f"  Found: {clean_name} (hash: {hash_value}) [CORE]")
                else:
                    print(f"  Found: {clean_name} (hash: {hash_value}) [HELPER]")
        
        print(f"Discovered {discovered_count} spell template types ({len(self.core_templates)} core templates)")
        return self.discovered_templates
    
    def is_core_template(self, class_name: str) -> bool:
        """Check if this is a core template (not a helper like SharedPointer or pair)"""
        # Exclude helper types
        if any(helper in class_name for helper in ["SharedPointer", "std::pair", "struct "]):
            return False
        # Only include direct spell template classes
        return "SpellTemplate" in class_name
    
    def analyze_inheritance_hierarchy(self):
        """Analyze base classes to build proper inheritance tree"""
        print("Analyzing inheritance hierarchy...")
        
        # Find the root SpellTemplate (one that doesn't inherit from another SpellTemplate)
        root_template = None
        for template in self.discovered_templates.values():
            has_spell_template_parent = any("SpellTemplate" in base for base in template.bases)
            if not has_spell_template_parent and "SpellTemplate" in template.class_name:
                root_template = template
                break
        
        if root_template:
            print(f"  Root template: {root_template.class_name}")
            self.inheritance_tree[root_template.class_name] = []
        
        # Build inheritance relationships
        for template in self.discovered_templates.values():
            if template.class_name == root_template.class_name:
                continue
                
            # Find which spell template this inherits from
            spell_template_parents = [base for base in template.bases if base in [t.class_name for t in self.discovered_templates.values()]]
            
            if spell_template_parents:
                parent = spell_template_parents[0]  # Take first spell template parent
                if parent not in self.inheritance_tree:
                    self.inheritance_tree[parent] = []
                self.inheritance_tree[parent].append(template.class_name)
                print(f"  {template.class_name} inherits from {parent}")
            else:
                # Inherits from root template
                if root_template.class_name not in self.inheritance_tree:
                    self.inheritance_tree[root_template.class_name] = []
                self.inheritance_tree[root_template.class_name].append(template.class_name)
                print(f"  {template.class_name} inherits from {root_template.class_name} (root)")
    
    def analyze_properties(self):
        """Analyze ALL properties across ALL discovered spell templates"""
        print("Analyzing spell template properties...")
        
        property_counts: Dict[str, int] = {}
        
        # Collect all properties and count occurrences
        for template in self.discovered_templates.values():
            for prop_name, prop_data in template.properties.items():
                if prop_name not in property_counts:
                    property_counts[prop_name] = 0
                property_counts[prop_name] += 1
                
                # Store property info if not already stored
                if prop_name not in self.all_properties:
                    self.all_properties[prop_name] = self.analyze_property(prop_name, prop_data)
        
        # Determine shared properties (appear in multiple templates)
        template_count = len(self.discovered_templates)
        for prop_name, count in property_counts.items():
            if count > 1:  # Shared if appears in more than one template
                self.shared_properties.add(prop_name)
        
        print(f"  Found {len(self.all_properties)} unique properties")
        print(f"  {len(self.shared_properties)} properties are shared across templates")
        
        # Collect enum definitions
        self.collect_enum_definitions()
    
    def analyze_property(self, prop_name: str, prop_data: Dict[str, Any]) -> PropertyInfo:
        """Analyze a single property and convert types"""
        cpp_type = prop_data.get("type", "unknown")
        container = prop_data.get("container", "Static")
        is_pointer = prop_data.get("pointer", False)
        is_dynamic = prop_data.get("dynamic", False)
        enum_options = prop_data.get("enum_options")
        
        # Convert C++ type to Python type
        python_type = self.convert_cpp_type_to_python(cpp_type, container, is_pointer, enum_options)
        
        return PropertyInfo(
            name=prop_name,
            cpp_type=cpp_type,
            python_type=python_type,
            container=container,
            is_pointer=is_pointer,
            is_dynamic=is_dynamic,
            enum_options=enum_options
        )
    
    def convert_cpp_type_to_python(self, cpp_type: str, container: str, is_pointer: bool, enum_options: Optional[Dict]) -> str:
        """Convert C++ type to Python type annotation"""
        # Handle enums
        if cpp_type.startswith("enum "):
            enum_name = self.extract_enum_name(cpp_type)
            base_type = enum_name
        else:
            # Basic type mapping
            type_mapping = {
                "std::string": "str",
                "int": "int",
                "unsigned int": "int", 
                "bool": "bool",
                "float": "float",
                "double": "float"
            }
            
            base_type = type_mapping.get(cpp_type, "Any")
            
            # Handle class types
            if cpp_type.startswith("class "):
                if "SharedPointer" in cpp_type:
                    # Extract inner type from SharedPointer<class Type>
                    inner_match = re.search(r"SharedPointer<class (.+?)>", cpp_type)
                    if inner_match:
                        inner_type = inner_match.group(1).replace("*", "").strip()
                        base_type = f"Optional[Any]"  # Use Any for unknown types
                    else:
                        base_type = "Any"
                else:
                    # Regular class type - use Any for unknown types
                    base_type = "Any"
        
        # Handle containers
        if container == "Vector" or container == "List":
            return f"List[{base_type}]"
        elif is_pointer and not container in ["Vector", "List"]:
            return f"Optional[{base_type}]"
        else:
            return base_type
    
    def extract_enum_name(self, enum_type: str) -> str:
        """Extract enum name from enum type string"""
        # e.g., "enum SpellTemplate::kSpellSourceType" -> "SpellSourceType"  
        if "::" in enum_type:
            return enum_type.split("::")[-1]
        else:
            # e.g., "enum LootInfo::LOOT_TYPE" -> "LOOT_TYPE"
            parts = enum_type.replace("enum ", "").split("::")
            return parts[-1] if parts else "UnknownEnum"
    
    def collect_enum_definitions(self):
        """Collect all enum definitions from properties"""
        print("Collecting enum definitions...")
        
        for prop_info in self.all_properties.values():
            if prop_info.enum_options and "__BASECLASS" not in prop_info.enum_options:
                enum_name = self.extract_enum_name(prop_info.cpp_type)
                if enum_name not in self.enum_definitions:
                    self.enum_definitions[enum_name] = prop_info.enum_options
                    print(f"  Found enum: {enum_name} with {len(prop_info.enum_options)} values")
    
    def run_discovery(self):
        """Run the complete discovery process"""
        print("Starting Wizard101 Spell Template Discovery...")
        print("=" * 50)
        
        self.discover_all_spell_templates()
        self.analyze_inheritance_hierarchy() 
        self.analyze_properties()
        
        print("=" * 50)
        print("Discovery complete!")
        print(f"Templates found: {len(self.discovered_templates)}")
        print(f"Core templates: {len(self.core_templates)}")
        print(f"Properties found: {len(self.all_properties)}")
        print(f"Enums found: {len(self.enum_definitions)}")


class DynamicClassGenerator:
    """Generates Python dataclass code dynamically"""
    
    def __init__(self, discovery: SpellTemplateDiscovery):
        self.discovery = discovery
        
    def generate_complete_module(self) -> str:
        """Generate complete Python module with all DTO classes"""
        lines = []
        
        # Module header
        lines.extend(self.generate_module_header())
        
        # Import statements
        lines.extend(self.generate_imports())
        
        # Enum classes
        lines.extend(self.generate_all_enums())
        
        # DTO classes
        lines.extend(self.generate_all_dto_classes())
        
        # Factory class
        lines.extend(self.generate_factory_class())
        
        return "\n".join(lines)
    
    def generate_module_header(self) -> List[str]:
        """Generate module header and docstring"""
        return [
            '"""',
            'Wizard101 Spell Template DTOs',
            '==============================',
            'Auto-generated Data Transfer Objects for Wizard101 spell templates.',
            '',
            'This module contains:',
            f'- {len(self.discovery.core_templates)} spell template DTO classes',
            f'- {len(self.discovery.enum_definitions)} enum definitions',
            '- Factory class for creating DTOs from spell data',
            '',
            'Generated automatically by class_generator.py',
            '"""',
            '',
        ]
    
    def generate_imports(self) -> List[str]:
        """Generate all necessary import statements"""
        return [
            'from dataclasses import dataclass, field',
            'from typing import Dict, List, Optional, Any, Union, Type',
            'from enum import Enum',
            '',
        ]
    
    def generate_all_enums(self) -> List[str]:
        """Generate all enum classes"""
        lines = ['# ===== ENUM DEFINITIONS =====', '']
        
        for enum_name, enum_values in self.discovery.enum_definitions.items():
            if enum_name == "float":  # Skip invalid enum
                continue
                
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
            if value_name == "__DEFAULT":  # Skip default values
                continue
            # Clean up enum value names
            clean_name = value_name.replace("::", "_").replace(".", "_")
            lines.append(f'    {clean_name} = {value_int}')
        
        if len(lines) == 1:  # No valid values added
            lines.append('    pass')
            
        return lines
    
    def generate_all_dto_classes(self) -> List[str]:
        """Generate all DTO classes with proper inheritance"""
        lines = ['# ===== DTO CLASSES =====', '']
        
        # Find root template
        root_template = self.find_root_template()
        if root_template:
            # Generate base class first
            lines.extend(self.generate_dto_class(root_template, is_base=True))
            lines.append('')
            
            # Generate derived classes
            for template in self.discovery.core_templates.values():
                if template.hash_value != root_template.hash_value:
                    lines.extend(self.generate_dto_class(template, is_base=False))
                    lines.append('')
        
        return lines
    
    def find_root_template(self) -> Optional[SpellTemplateInfo]:
        """Find the root SpellTemplate class"""
        for template in self.discovery.core_templates.values():
            # Root template doesn't inherit from another SpellTemplate
            has_spell_template_parent = any("SpellTemplate" in base for base in template.bases)
            if not has_spell_template_parent and template.class_name == "SpellTemplate":
                return template
        return None
    
    def generate_dto_class(self, template: SpellTemplateInfo, is_base: bool = False) -> List[str]:
        """Generate a single DTO class"""
        lines = []
        
        # Class decorator and definition
        lines.append('@dataclass')
        
        if is_base:
            class_def = f'class {template.class_name}DTO:'
            lines.append(f'class {template.class_name}DTO:')
            lines.append(f'    """Base DTO for {template.class_name} with all core properties"""')
        else:
            lines.append(f'class {template.class_name}DTO(SpellTemplateDTO):')
            lines.append(f'    """DTO for {template.class_name} - specialized spell template"""')
        
        # Generate properties
        property_lines = self.generate_class_properties(template, is_base)
        if property_lines:
            lines.extend(property_lines)
        else:
            lines.append('    pass')
        
        return lines
    
    def generate_class_properties(self, template: SpellTemplateInfo, is_base: bool) -> List[str]:
        """Generate property definitions for a class"""
        lines = []
        
        if is_base:
            # Base class gets all shared properties
            properties_to_include = self.discovery.shared_properties
        else:
            # Derived class gets only unique properties
            template_properties = set(template.properties.keys())
            properties_to_include = template_properties - self.discovery.shared_properties
        
        for prop_name in sorted(properties_to_include):
            if prop_name in self.discovery.all_properties:
                prop_info = self.discovery.all_properties[prop_name]
                lines.append(f'    {prop_name}: {prop_info.python_type}')
        
        return lines
    
    def generate_factory_class(self) -> List[str]:
        """Generate factory class for creating DTOs"""
        lines = [
            '# ===== FACTORY CLASS =====',
            '',
            'class SpellTemplateDTOFactory:',
            '    """Factory for creating appropriate DTO instances from spell data"""',
            '    ',
            '    # Hash to DTO class mapping',
            '    TYPE_MAPPING: Dict[int, Type] = {'
        ]
        
        # Add mapping for each core template
        for template in self.discovery.core_templates.values():
            lines.append(f'        {template.hash_value}: {template.class_name}DTO,')
        
        lines.extend([
            '    }',
            '    ',
            '    @classmethod',
            '    def create_dto(cls, type_hash: int, spell_data: Dict[str, Any]) -> Optional[Any]:',
            '        """Create appropriate DTO instance based on type hash"""',
            '        dto_class = cls.TYPE_MAPPING.get(type_hash)',
            '        if dto_class:',
            '            try:',
            '                # Filter spell_data to only include fields that exist in the DTO',
            '                filtered_data = cls.filter_data_for_dto(dto_class, spell_data)',
            '                return dto_class(**filtered_data)',
            '            except Exception as e:',
            '                print(f"Error creating DTO for hash {type_hash}: {e}")',
            '                return None',
            '        else:',
            '            print(f"No DTO class found for hash {type_hash}")',
            '            return None',
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
        ])
        
        return lines
    
    def save_generated_module(self, output_path: str = "wizard101_spell_dtos.py"):
        """Save generated module to file"""
        module_code = self.generate_complete_module()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(module_code)
        
        print(f"Generated DTO module saved to: {output_path}")
        return output_path


def main():
    """Standalone execution - auto-discover and generate DTOs"""
    # Get types JSON path from command line or default
    types_path = sys.argv[1] if len(sys.argv) > 1 else "r777820_Wizard_1_580_0_Live.json"
    
    if not Path(types_path).exists():
        print(f"Error: Types file not found: {types_path}")
        print("Usage: python class_generator.py [types_json_path]")
        sys.exit(1)
    
    # Discover spell templates
    discovery = SpellTemplateDiscovery(types_path)
    discovery.run_discovery()
    
    # Generate DTO classes
    print("\nGenerating DTO classes...")
    generator = DynamicClassGenerator(discovery)
    output_file = generator.save_generated_module("wizard101_spell_dtos.py")
    
    # Print summary
    print("\n" + "=" * 50)
    print("GENERATION SUMMARY")
    print("=" * 50)
    
    print(f"\nCore Spell Template Types ({len(discovery.core_templates)}):")
    for template in discovery.core_templates.values():
        print(f"  {template.class_name} (hash: {template.hash_value})")
    
    print(f"\nShared Properties ({len(discovery.shared_properties)}):")
    shared_list = list(sorted(discovery.shared_properties))[:10]  # Show first 10
    for prop_name in shared_list:
        prop_info = discovery.all_properties[prop_name]
        print(f"  {prop_name}: {prop_info.python_type}")
    if len(discovery.shared_properties) > 10:
        print(f"  ... and {len(discovery.shared_properties) - 10} more")
    
    print(f"\nEnum Definitions ({len(discovery.enum_definitions)}):")
    for enum_name, enum_values in discovery.enum_definitions.items():
        if enum_name != "float":  # Skip invalid enum
            print(f"  {enum_name}: {len(enum_values)} values")
    
    print(f"\nOutput: {output_file}")
    print("[SUCCESS] DTO generation complete!")


if __name__ == "__main__":
    main()