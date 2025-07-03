#!/usr/bin/env python3
"""
Focused Nested Type Analyzer for Combat-Relevant Spell Data
==========================================================
Analyzes only the nested types that actually appear in our reference examples
to create focused DTOs for combat simulation.

This analyzer:
1. Scans reference examples for actual $__type usage
2. Maps property structures for each nested type
3. Identifies inheritance relationships between nested types
4. Creates specifications for DTO generation
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
import re


class FocusedNestedAnalyzer:
    """Analyzer focused on combat-relevant nested types"""
    
    def __init__(self, reference_examples_dir: str, types_json_path: str):
        self.reference_examples_dir = Path(reference_examples_dir)
        self.types_json_path = Path(types_json_path)
        
        # Core results
        self.used_nested_types: Dict[str, Dict[str, Any]] = {}
        self.type_definitions: Dict[str, Dict[str, Any]] = {}
        self.inheritance_map: Dict[str, str] = {}  # child -> parent
        self.property_analysis: Dict[str, Dict[str, Any]] = {}
        
        # Load type definitions
        self.types_data = self.load_types_json()
        
    def load_types_json(self) -> Dict[str, Any]:
        """Load the types JSON file"""
        try:
            with open(self.types_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded types JSON from {self.types_json_path}")
            return data
        except Exception as e:
            print(f"Error loading types JSON: {e}")
            return {}
    
    def analyze_reference_examples(self):
        """Analyze reference examples to find actually used nested types"""
        print("Analyzing reference examples for used nested types...")
        
        reference_files = list(self.reference_examples_dir.glob("*.json"))
        print(f"Found {len(reference_files)} reference files")
        
        for ref_file in reference_files:
            print(f"  Analyzing: {ref_file.name}")
            self.extract_nested_types_from_file(ref_file)
        
        print(f"Found {len(self.used_nested_types)} actually used nested types")
    
    def extract_nested_types_from_file(self, file_path: Path):
        """Extract nested types from a single reference file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Recursively find all $__type entries
            self.find_types_recursive(data, file_path.name)
            
        except Exception as e:
            print(f"    Error analyzing {file_path}: {e}")
    
    def find_types_recursive(self, obj: Any, source_file: str, path: str = ""):
        """Recursively find all $__type entries and their properties"""
        if isinstance(obj, dict):
            # Check if this object has a type
            if "$__type" in obj:
                type_name = obj["$__type"]
                clean_type = self.clean_type_name(type_name)
                
                # Initialize type info if not seen before
                if clean_type not in self.used_nested_types:
                    self.used_nested_types[clean_type] = {
                        "full_name": type_name,
                        "clean_name": clean_type,
                        "properties": {},
                        "found_in_files": [],
                        "example_data": {},
                        "nested_types": set()
                    }
                
                # Record where we found it
                if source_file not in self.used_nested_types[clean_type]["found_in_files"]:
                    self.used_nested_types[clean_type]["found_in_files"].append(source_file)
                
                # Store an example of the data
                if not self.used_nested_types[clean_type]["example_data"]:
                    self.used_nested_types[clean_type]["example_data"] = dict(obj)
                
                # Analyze all properties of this type
                for key, value in obj.items():
                    if key != "$__type":
                        # Record property type and example value
                        prop_info = self.analyze_property_type(key, value)
                        self.used_nested_types[clean_type]["properties"][key] = prop_info
                        
                        # Recurse into nested objects
                        nested_type = self.find_types_recursive(value, source_file, f"{path}.{key}")
                        if nested_type:
                            self.used_nested_types[clean_type]["nested_types"].add(nested_type)
                
                return clean_type
            else:
                # Object without type - recurse into properties
                for key, value in obj.items():
                    self.find_types_recursive(value, source_file, f"{path}.{key}")
        
        elif isinstance(obj, list):
            # Recurse into list items
            for i, item in enumerate(obj):
                self.find_types_recursive(item, source_file, f"{path}[{i}]")
        
        return None
    
    def clean_type_name(self, type_name: str) -> str:
        """Clean type name by removing 'class ' prefix"""
        return type_name.replace("class ", "").strip()
    
    def analyze_property_type(self, prop_name: str, prop_value: Any) -> Dict[str, Any]:
        """Analyze a property to determine its type and characteristics"""
        prop_info = {
            "python_type": None,
            "is_list": False,
            "is_optional": False,
            "nested_type": None,
            "example_value": prop_value
        }
        
        if prop_value is None:
            prop_info["python_type"] = "Optional[Any]"
            prop_info["is_optional"] = True
        
        elif isinstance(prop_value, bool):
            prop_info["python_type"] = "bool"
        
        elif isinstance(prop_value, int):
            prop_info["python_type"] = "int"
        
        elif isinstance(prop_value, float):
            prop_info["python_type"] = "float"
        
        elif isinstance(prop_value, str):
            prop_info["python_type"] = "str"
        
        elif isinstance(prop_value, list):
            prop_info["is_list"] = True
            if len(prop_value) > 0:
                # Analyze first item to determine list type
                first_item = prop_value[0]
                if isinstance(first_item, dict) and "$__type" in first_item:
                    nested_type = self.clean_type_name(first_item["$__type"])
                    prop_info["nested_type"] = nested_type
                    prop_info["python_type"] = f"List[{nested_type}DTO]"
                else:
                    item_type = type(first_item).__name__
                    type_map = {"str": "str", "int": "int", "float": "float", "bool": "bool"}
                    mapped_type = type_map.get(item_type, "Any")
                    prop_info["python_type"] = f"List[{mapped_type}]"
            else:
                prop_info["python_type"] = "List[Any]"
        
        elif isinstance(prop_value, dict):
            if "$__type" in prop_value:
                nested_type = self.clean_type_name(prop_value["$__type"])
                prop_info["nested_type"] = nested_type
                prop_info["python_type"] = f"{nested_type}DTO"
            else:
                prop_info["python_type"] = "Dict[str, Any]"
        
        else:
            prop_info["python_type"] = "Any"
        
        return prop_info
    
    def load_type_definitions(self):
        """Load full type definitions for the used nested types"""
        print("Loading type definitions for used nested types...")
        
        classes = self.types_data.get("classes", {})
        
        for type_name in self.used_nested_types.keys():
            # Find the type definition in the types JSON
            for hash_str, class_info in classes.items():
                class_name = class_info.get("name", "")
                clean_name = self.clean_type_name(class_name)
                
                if clean_name == type_name:
                    self.type_definitions[type_name] = {
                        "hash": int(hash_str),
                        "full_name": class_name,
                        "bases": class_info.get("bases", []),
                        "properties": class_info.get("properties", {}),
                        "class_info": class_info
                    }
                    
                    # Check for inheritance
                    bases = class_info.get("bases", [])
                    for base in bases:
                        clean_base = self.clean_type_name(base)
                        if clean_base in self.used_nested_types:
                            self.inheritance_map[type_name] = clean_base
                            print(f"  Found inheritance: {type_name} inherits from {clean_base}")
                    
                    print(f"  Loaded definition for: {type_name}")
                    break
    
    def enhance_property_analysis(self):
        """Enhance property analysis with type definition data"""
        print("Enhancing property analysis with type definitions...")
        
        for type_name, type_info in self.used_nested_types.items():
            if type_name in self.type_definitions:
                type_def = self.type_definitions[type_name]
                
                # Merge properties from type definition
                for prop_name, prop_def in type_def["properties"].items():
                    if prop_name not in type_info["properties"]:
                        # Property exists in definition but not in our examples
                        # Add it with type information
                        cpp_type = prop_def.get("type", "unknown")
                        python_type = self.convert_cpp_to_python_type(cpp_type, prop_def)
                        
                        type_info["properties"][prop_name] = {
                            "python_type": python_type,
                            "is_list": prop_def.get("container") in ["Vector", "List"],
                            "is_optional": prop_def.get("pointer", False),
                            "nested_type": None,
                            "example_value": None,
                            "from_definition": True
                        }
    
    def convert_cpp_to_python_type(self, cpp_type: str, prop_def: Dict[str, Any]) -> str:
        """Convert C++ type to Python type"""
        container = prop_def.get("container", "Static")
        is_pointer = prop_def.get("pointer", False)
        
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
        
        # Handle containers
        if container in ["Vector", "List"]:
            return f"List[{base_type}]"
        elif is_pointer:
            return f"Optional[{base_type}]"
        else:
            return base_type
    
    def generate_dto_specifications(self) -> Dict[str, Dict[str, Any]]:
        """Generate specifications for DTO creation"""
        print("Generating DTO specifications...")
        
        dto_specs = {}
        
        for type_name, type_info in self.used_nested_types.items():
            dto_specs[type_name] = {
                "class_name": f"{type_name}DTO",
                "base_class": None,
                "properties": {},
                "hash_value": None,
                "is_polymorphic": False,
                "subtypes": []
            }
            
            # Check for inheritance
            if type_name in self.inheritance_map:
                parent = self.inheritance_map[type_name]
                dto_specs[type_name]["base_class"] = f"{parent}DTO"
            
            # Add properties
            for prop_name, prop_info in type_info["properties"].items():
                dto_specs[type_name]["properties"][prop_name] = prop_info["python_type"]
            
            # Add hash value if available
            if type_name in self.type_definitions:
                dto_specs[type_name]["hash_value"] = self.type_definitions[type_name]["hash"]
            
            print(f"  Generated spec for: {type_name}")
        
        # Identify polymorphic relationships
        for child, parent in self.inheritance_map.items():
            if parent in dto_specs:
                dto_specs[parent]["is_polymorphic"] = True
                dto_specs[parent]["subtypes"].append(child)
        
        return dto_specs
    
    def generate_analysis_report(self) -> str:
        """Generate focused analysis report"""
        lines = []
        
        lines.append("Combat-Focused Nested Type Analysis Report")
        lines.append("=" * 50)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY:")
        lines.append(f"- Used nested types: {len(self.used_nested_types)}")
        lines.append(f"- Types with definitions: {len(self.type_definitions)}")
        lines.append(f"- Inheritance relationships: {len(self.inheritance_map)}")
        lines.append("")
        
        # Used nested types
        lines.append("USED NESTED TYPES:")
        lines.append("-" * 30)
        for type_name in sorted(self.used_nested_types.keys()):
            type_info = self.used_nested_types[type_name]
            lines.append(f"\n{type_name}:")
            lines.append(f"  Found in: {', '.join(type_info['found_in_files'])}")
            lines.append(f"  Properties: {len(type_info['properties'])}")
            lines.append(f"  Nested types: {', '.join(sorted(type_info['nested_types'])) if type_info['nested_types'] else 'None'}")
            
            # Show key properties
            key_props = list(type_info["properties"].keys())[:5]
            if key_props:
                lines.append(f"  Key properties: {', '.join(key_props)}")
                if len(type_info["properties"]) > 5:
                    lines.append(f"    ... and {len(type_info['properties']) - 5} more")
        
        lines.append("")
        
        # Inheritance relationships
        if self.inheritance_map:
            lines.append("INHERITANCE RELATIONSHIPS:")
            lines.append("-" * 30)
            for child, parent in self.inheritance_map.items():
                lines.append(f"{child} inherits from {parent}")
            lines.append("")
        
        # Property analysis summary
        lines.append("PROPERTY TYPE ANALYSIS:")
        lines.append("-" * 30)
        all_prop_types = set()
        for type_info in self.used_nested_types.values():
            for prop_info in type_info["properties"].values():
                all_prop_types.add(prop_info["python_type"])
        
        lines.append(f"Unique property types found: {len(all_prop_types)}")
        for prop_type in sorted(all_prop_types):
            lines.append(f"  - {prop_type}")
        
        return "\n".join(lines)
    
    def run_focused_analysis(self):
        """Run the complete focused analysis"""
        print("Starting focused nested type analysis for combat simulation...")
        print("=" * 60)
        
        # Phase 1: Extract types from reference examples
        self.analyze_reference_examples()
        
        # Phase 2: Load type definitions
        self.load_type_definitions()
        
        # Phase 3: Enhance property analysis
        self.enhance_property_analysis()
        
        print("=" * 60)
        print("Focused analysis complete!")
        print(f"Found {len(self.used_nested_types)} combat-relevant nested types")
        
        return self.generate_analysis_report(), self.generate_dto_specifications()


def main():
    """Main function"""
    reference_examples_dir = "../Reference Material/Spells/Reference Spells Examples"
    types_json_path = "../r777820_Wizard_1_580_0_Live.json"
    
    # Check paths
    if not Path(reference_examples_dir).exists():
        print(f"Error: Reference examples directory not found: {reference_examples_dir}")
        return 1
    
    if not Path(types_json_path).exists():
        print(f"Error: Types JSON file not found: {types_json_path}")
        return 1
    
    # Run analysis
    analyzer = FocusedNestedAnalyzer(reference_examples_dir, types_json_path)
    report, dto_specs = analyzer.run_focused_analysis()
    
    # Save report
    with open("../Reports/Spell Reports/focused_nested_analysis_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save DTO specifications
    with open("../dto_specifications.json", 'w', encoding='utf-8') as f:
        json.dump(dto_specs, f, indent=2, default=str)
    
    print(f"\nReport saved to: focused_nested_analysis_report.txt")
    print(f"DTO specs saved to: dto_specifications.json")
    
    # Print key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS FOR COMBAT SIMULATION:")
    print("=" * 60)
    
    print(f"\nCombat-relevant nested types ({len(analyzer.used_nested_types)}):")
    for type_name in sorted(analyzer.used_nested_types.keys()):
        files = analyzer.used_nested_types[type_name]["found_in_files"]
        print(f"  - {type_name} (found in: {', '.join(files)})")
    
    if analyzer.inheritance_map:
        print(f"\nInheritance relationships:")
        for child, parent in analyzer.inheritance_map.items():
            print(f"  - {child} → {parent}")
    
    return 0


if __name__ == "__main__":
    exit(main())