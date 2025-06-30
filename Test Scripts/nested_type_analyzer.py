#!/usr/bin/env python3
"""
Nested Type Analyzer for Wizard101 Spell Data
=============================================
Comprehensive analysis tool to identify all nested class types and their relationships
within Wizard101 spell data. Goes deeper than spell_scope.py to map full object hierarchy.

This tool:
1. Analyzes all reference examples to identify nested $__type entries
2. Maps relationships and inheritance between nested classes
3. Documents nesting depth and complexity
4. Prepares data for enhanced DTO generation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict, deque
import re


class NestedTypeAnalyzer:
    """Comprehensive analyzer for nested class types in spell data"""
    
    def __init__(self, types_json_path: str, reference_examples_dir: str):
        self.types_json_path = Path(types_json_path)
        self.reference_examples_dir = Path(reference_examples_dir)
        
        # Analysis results
        self.nested_types: Dict[str, Dict[str, Any]] = {}  # type_name -> type_info
        self.type_relationships: Dict[str, List[str]] = defaultdict(list)  # parent -> children
        self.type_properties: Dict[str, Set[str]] = defaultdict(set)  # type -> properties
        self.nesting_depth: Dict[str, int] = {}  # type -> max depth found
        self.polymorphic_types: Dict[str, Set[str]] = defaultdict(set)  # base_type -> subtypes
        
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
    
    def analyze_all_reference_examples(self):
        """Analyze all reference examples to identify nested types"""
        print("Analyzing reference examples for nested types...")
        
        reference_files = list(self.reference_examples_dir.glob("*.json"))
        print(f"Found {len(reference_files)} reference files")
        
        for ref_file in reference_files:
            print(f"  Analyzing: {ref_file.name}")
            self.analyze_single_file(ref_file)
    
    def analyze_single_file(self, file_path: Path):
        """Analyze a single JSON file for nested types"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Start recursive analysis from root
            self.analyze_object_recursive(data, depth=0, path="root")
            
        except Exception as e:
            print(f"    Error analyzing {file_path}: {e}")
    
    def analyze_object_recursive(self, obj: Any, depth: int = 0, path: str = "") -> Optional[str]:
        """Recursively analyze an object to find nested types"""
        current_type = None
        
        if isinstance(obj, dict):
            # Check if this object has a type
            if "$__type" in obj:
                current_type = obj["$__type"]
                
                # Extract clean type name
                clean_type = self.extract_clean_type_name(current_type)
                
                # Record this type
                if clean_type not in self.nested_types:
                    self.nested_types[clean_type] = {
                        "full_name": current_type,
                        "clean_name": clean_type,
                        "properties": set(),
                        "max_depth": depth,
                        "found_in": [],
                        "contains_types": set()
                    }
                
                # Update depth
                if depth > self.nested_types[clean_type]["max_depth"]:
                    self.nested_types[clean_type]["max_depth"] = depth
                
                # Record where we found it
                if path not in self.nested_types[clean_type]["found_in"]:
                    self.nested_types[clean_type]["found_in"].append(path)
            
            # Analyze all properties
            for key, value in obj.items():
                if key != "$__type":  # Skip the type field itself
                    
                    # Record property for current type
                    if current_type:
                        clean_type = self.extract_clean_type_name(current_type)
                        self.nested_types[clean_type]["properties"].add(key)
                    
                    # Recurse into the value
                    child_type = self.analyze_object_recursive(
                        value, 
                        depth + 1, 
                        f"{path}.{key}"
                    )
                    
                    # Record relationship
                    if current_type and child_type:
                        clean_current = self.extract_clean_type_name(current_type)
                        clean_child = self.extract_clean_type_name(child_type)
                        self.nested_types[clean_current]["contains_types"].add(clean_child)
                        self.type_relationships[clean_current].append(clean_child)
        
        elif isinstance(obj, list):
            # Analyze list items
            for i, item in enumerate(obj):
                child_type = self.analyze_object_recursive(
                    item, 
                    depth + 1, 
                    f"{path}[{i}]"
                )
                
                # Record relationship if we're in a typed object
                if current_type and child_type:
                    clean_current = self.extract_clean_type_name(current_type)
                    clean_child = self.extract_clean_type_name(child_type)
                    self.nested_types[clean_current]["contains_types"].add(clean_child)
        
        return current_type
    
    def extract_clean_type_name(self, full_type_name: str) -> str:
        """Extract clean class name from full type name"""
        # Remove "class " prefix and any extra whitespace
        clean = full_type_name.replace("class ", "").strip()
        return clean
    
    def analyze_type_definitions(self):
        """Analyze the types JSON to find additional nested types"""
        print("Analyzing type definitions for additional nested types...")
        
        classes = self.types_data.get("classes", {})
        
        # Look for any class that might be used in spell data
        spell_related_keywords = [
            "Spell", "Effect", "Requirement", "Req", "Magic", "Combat", 
            "Damage", "Heal", "Buff", "Debuff", "Rank", "School", "Pip"
        ]
        
        for hash_str, class_info in classes.items():
            class_name = class_info.get("name", "")
            
            # Check if this might be a nested type used in spells
            if any(keyword in class_name for keyword in spell_related_keywords):
                clean_name = self.extract_clean_type_name(class_name)
                
                # Skip spell template classes (we handle those separately)
                if "SpellTemplate" in clean_name:
                    continue
                
                # Add to our nested types if not already found
                if clean_name not in self.nested_types:
                    self.nested_types[clean_name] = {
                        "full_name": class_name,
                        "clean_name": clean_name,
                        "properties": set(),
                        "max_depth": 0,
                        "found_in": ["types_definition"],
                        "contains_types": set()
                    }
                
                # Add properties from type definition
                properties = class_info.get("properties", {})
                for prop_name in properties.keys():
                    self.nested_types[clean_name]["properties"].add(prop_name)
                
                print(f"  Found potential nested type: {clean_name}")
    
    def identify_polymorphic_relationships(self):
        """Identify polymorphic inheritance relationships"""
        print("Identifying polymorphic relationships...")
        
        classes = self.types_data.get("classes", {})
        
        # Build inheritance map
        inheritance_map = {}  # child -> parent
        
        for hash_str, class_info in classes.items():
            class_name = self.extract_clean_type_name(class_info.get("name", ""))
            bases = class_info.get("bases", [])
            
            if class_name in self.nested_types:
                for base in bases:
                    clean_base = self.extract_clean_type_name(base)
                    if clean_base in self.nested_types:
                        inheritance_map[class_name] = clean_base
                        self.polymorphic_types[clean_base].add(class_name)
                        print(f"  {class_name} inherits from {clean_base}")
    
    def generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report"""
        lines = []
        
        lines.append("Wizard101 Nested Type Analysis Report")
        lines.append("=" * 50)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY:")
        lines.append(f"- Nested types found: {len(self.nested_types)}")
        lines.append(f"- Polymorphic relationships: {len(self.polymorphic_types)}")
        lines.append(f"- Maximum nesting depth: {max((info['max_depth'] for info in self.nested_types.values()), default=0)}")
        lines.append("")
        
        # Nested types by depth
        lines.append("NESTED TYPES BY DEPTH:")
        lines.append("-" * 30)
        
        types_by_depth = defaultdict(list)
        for type_name, info in self.nested_types.items():
            types_by_depth[info["max_depth"]].append(type_name)
        
        for depth in sorted(types_by_depth.keys()):
            lines.append(f"Depth {depth}: {', '.join(sorted(types_by_depth[depth]))}")
        lines.append("")
        
        # Detailed type information
        lines.append("DETAILED TYPE INFORMATION:")
        lines.append("-" * 30)
        
        for type_name in sorted(self.nested_types.keys()):
            info = self.nested_types[type_name]
            lines.append(f"\n{type_name}:")
            lines.append(f"  Full name: {info['full_name']}")
            lines.append(f"  Max depth: {info['max_depth']}")
            lines.append(f"  Properties ({len(info['properties'])}): {', '.join(sorted(info['properties']))}")
            if info['contains_types']:
                lines.append(f"  Contains types: {', '.join(sorted(info['contains_types']))}")
            lines.append(f"  Found in: {', '.join(info['found_in'])}")
        
        lines.append("")
        
        # Polymorphic relationships
        if self.polymorphic_types:
            lines.append("POLYMORPHIC RELATIONSHIPS:")
            lines.append("-" * 30)
            for base_type, subtypes in self.polymorphic_types.items():
                lines.append(f"{base_type} -> {', '.join(sorted(subtypes))}")
            lines.append("")
        
        # Type relationships (containment)
        lines.append("CONTAINMENT RELATIONSHIPS:")
        lines.append("-" * 30)
        for parent, children in self.type_relationships.items():
            if children:
                unique_children = sorted(set(children))
                lines.append(f"{parent} contains: {', '.join(unique_children)}")
        
        return "\n".join(lines)
    
    def run_complete_analysis(self):
        """Run the complete nested type analysis"""
        print("Starting comprehensive nested type analysis...")
        print("=" * 50)
        
        # Phase 1: Analyze reference examples
        self.analyze_all_reference_examples()
        
        # Phase 2: Analyze type definitions
        self.analyze_type_definitions()
        
        # Phase 3: Identify polymorphic relationships
        self.identify_polymorphic_relationships()
        
        print("=" * 50)
        print("Analysis complete!")
        print(f"Found {len(self.nested_types)} nested types")
        print(f"Found {len(self.polymorphic_types)} polymorphic base types")
        
        return self.generate_analysis_report()


def main():
    """Main function to run the nested type analysis"""
    # Paths
    types_json_path = "../r777820_Wizard_1_580_0_Live.json"
    reference_examples_dir = "../Reference SpellClass Examples"
    
    # Check paths exist
    if not Path(types_json_path).exists():
        print(f"Error: Types JSON file not found: {types_json_path}")
        return 1
    
    if not Path(reference_examples_dir).exists():
        print(f"Error: Reference examples directory not found: {reference_examples_dir}")
        return 1
    
    # Run analysis
    analyzer = NestedTypeAnalyzer(types_json_path, reference_examples_dir)
    report = analyzer.run_complete_analysis()
    
    # Save report
    output_file = "../Reports/nested_type_analysis_report.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nAnalysis report saved to: {output_file}")
    
    # Print key findings
    print("\n" + "=" * 50)
    print("KEY FINDINGS:")
    print("=" * 50)
    
    # Top-level nested types
    top_level_types = [name for name, info in analyzer.nested_types.items() 
                      if info["max_depth"] <= 1]
    print(f"\nTop-level nested types ({len(top_level_types)}):")
    for type_name in sorted(top_level_types):
        print(f"  - {type_name}")
    
    # Most complex types (contain other types)
    complex_types = [(name, len(info["contains_types"])) 
                    for name, info in analyzer.nested_types.items() 
                    if info["contains_types"]]
    complex_types.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nMost complex types (contain other types):")
    for type_name, count in complex_types[:5]:
        print(f"  - {type_name}: contains {count} different types")
    
    return 0


if __name__ == "__main__":
    exit(main())