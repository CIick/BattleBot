#!/usr/bin/env python3
"""
Discover All Effect Types
========================
Comprehensive analysis of all 16,000+ WAD spell files to discover every effect type
used in m_effects. This will identify missing DTOs that need to be created.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Tuple
import traceback

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from processors import WADProcessor
from dtos import FixedSpellDTOFactory


class EffectTypeDiscoverer:
    """Discovers all effect types across the entire WAD archive"""
    
    def __init__(self):
        self.processor = None
        
        # Discovery data structures
        self.all_effect_types = set()
        self.effect_type_counts = Counter()
        self.effect_type_samples = defaultdict(list)  # Sample data for each type
        self.nested_types = set()  # Types found nested within effects
        self.failed_files = []
        self.processing_errors = []
        
        # Statistics
        self.total_files_processed = 0
        self.total_effects_found = 0
        self.files_with_effects = 0
        
        # Known types (already have DTOs)
        self.known_types = set(FixedSpellDTOFactory.get_supported_types())
        
    def initialize(self) -> bool:
        """Initialize the WAD processor"""
        print("Initializing Effect Type Discoverer...")
        
        self.processor = WADProcessor(types_path=Path("../types.json"))
        if not self.processor.initialize():
            print("Failed to initialize WAD processor")
            return False
        
        print("[OK] Effect Type Discoverer initialized")
        return True
    
    def discover_all_effect_types(self) -> bool:
        """Process all WAD files to discover effect types"""
        print("\nDiscovering All Effect Types in WAD Archive...")
        print("=" * 60)
        
        try:
            # Get all spell files
            spell_files = self.processor.get_all_spell_files()
            if not spell_files:
                print("No spell files found")
                return False
            
            total_files = len(spell_files)
            print(f"Processing {total_files} spell files...")
            
            # Process each file
            for i, file_path in enumerate(spell_files):
                self.total_files_processed += 1
                
                try:
                    self._process_single_file(file_path)
                except Exception as e:
                    error_info = {
                        "file": file_path,
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
                    self.processing_errors.append(error_info)
                    self.failed_files.append(file_path)
                
                # Progress update
                if self.total_files_processed % 1000 == 0:
                    progress = (self.total_files_processed / total_files) * 100
                    print(f"Progress: {self.total_files_processed}/{total_files} ({progress:.1f}%) - "
                          f"Found {len(self.all_effect_types)} unique effect types")
            
            print(f"\nProcessing complete!")
            return True
            
        except Exception as e:
            print(f"Error during discovery: {e}")
            traceback.print_exc()
            return False
    
    def _process_single_file(self, file_path: str):
        """Process a single spell file to extract effect types"""
        try:
            # Process the spell
            success, spell_dict, spell_dto, error_msg = self.processor.process_single_spell(file_path)
            
            if not success:
                self.failed_files.append(file_path)
                return
            
            # Extract effects from raw spell data
            if "m_effects" in spell_dict:
                effects = spell_dict["m_effects"]
                
                if effects and len(effects) > 0:
                    self.files_with_effects += 1
                    
                    for effect in effects:
                        self._analyze_effect(effect, file_path)
        
        except Exception as e:
            # Log but don't stop processing
            self.failed_files.append(file_path)
            raise  # Re-raise for error logging
    
    def _analyze_effect(self, effect: Any, source_file: str):
        """Analyze a single effect to extract type information"""
        self.total_effects_found += 1
        
        if isinstance(effect, dict) and "$__type" in effect:
            effect_type = effect["$__type"].replace("class ", "")
            
            # Track this effect type
            self.all_effect_types.add(effect_type)
            self.effect_type_counts[effect_type] += 1
            
            # Store sample data (limit to 3 samples per type)
            if len(self.effect_type_samples[effect_type]) < 3:
                sample_data = {
                    "source_file": source_file,
                    "sample_fields": list(effect.keys())[:10],  # First 10 fields
                    "field_count": len(effect.keys())
                }
                
                # Add some sample field values for analysis
                sample_values = {}
                for key in list(effect.keys())[:5]:  # First 5 field values
                    value = effect[key]
                    if isinstance(value, (str, int, float, bool)):
                        sample_values[key] = value
                    elif isinstance(value, list):
                        sample_values[key] = f"[list with {len(value)} items]"
                    elif isinstance(value, dict):
                        sample_values[key] = f"[dict with {len(value)} keys]"
                    else:
                        sample_values[key] = f"[{type(value).__name__}]"
                
                sample_data["sample_values"] = sample_values
                self.effect_type_samples[effect_type].append(sample_data)
            
            # Look for nested types within this effect
            self._analyze_nested_types(effect, effect_type)
    
    def _analyze_nested_types(self, effect: Dict[str, Any], parent_type: str):
        """Analyze nested types within an effect"""
        for key, value in effect.items():
            if isinstance(value, dict) and "$__type" in value:
                nested_type = value["$__type"].replace("class ", "")
                self.nested_types.add(f"{parent_type}.{key} -> {nested_type}")
            
            elif isinstance(value, list):
                # Check list items for nested types
                for i, item in enumerate(value):
                    if isinstance(item, dict) and "$__type" in item:
                        nested_type = item["$__type"].replace("class ", "")
                        self.nested_types.add(f"{parent_type}.{key}[{i}] -> {nested_type}")
                        
                        # Also analyze the nested item itself
                        self._analyze_effect(item, f"nested_in_{parent_type}")
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive report of findings"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE EFFECT TYPE DISCOVERY REPORT")
        print("=" * 80)
        
        # Summary statistics
        print(f"\nSUMMARY STATISTICS:")
        print(f"  Total files processed: {self.total_files_processed}")
        print(f"  Files with effects: {self.files_with_effects}")
        print(f"  Total effects analyzed: {self.total_effects_found}")
        print(f"  Unique effect types found: {len(self.all_effect_types)}")
        print(f"  Failed files: {len(self.failed_files)}")
        print(f"  Processing errors: {len(self.processing_errors)}")
        
        # Effect type analysis
        print(f"\nEFFECT TYPE BREAKDOWN:")
        
        # Categorize types
        known_types = []
        missing_types = []
        
        for effect_type in sorted(self.all_effect_types):
            dto_name = f"{effect_type}DTO"
            count = self.effect_type_counts[effect_type]
            
            if dto_name in self.known_types:
                known_types.append((effect_type, count))
            else:
                missing_types.append((effect_type, count))
        
        print(f"\n[OK] KNOWN TYPES (have DTOs): {len(known_types)}")
        for effect_type, count in sorted(known_types, key=lambda x: x[1], reverse=True):
            print(f"  {effect_type}: {count} occurrences")
        
        print(f"\n[MISSING] TYPES (need DTOs): {len(missing_types)}")
        for effect_type, count in sorted(missing_types, key=lambda x: x[1], reverse=True):
            print(f"  {effect_type}: {count} occurrences")
        
        # Detailed analysis of missing types
        print(f"\nDETAILED ANALYSIS OF MISSING TYPES:")
        print("=" * 50)
        
        for effect_type, count in sorted(missing_types, key=lambda x: x[1], reverse=True):
            print(f"\n{effect_type} ({count} occurrences):")
            
            samples = self.effect_type_samples[effect_type]
            if samples:
                sample = samples[0]  # Use first sample
                print(f"  Source files: {[s['source_file'] for s in samples[:3]]}")
                print(f"  Field count: {sample['field_count']}")
                print(f"  Sample fields: {sample['sample_fields']}")
                print(f"  Sample values:")
                for key, value in sample['sample_values'].items():
                    print(f"    {key}: {value}")
        
        # Nested types analysis
        if self.nested_types:
            print(f"\nNESTED TYPES FOUND: {len(self.nested_types)}")
            for nested_info in sorted(self.nested_types):
                print(f"  {nested_info}")
        
        # Create report data structure
        report_data = {
            "summary": {
                "total_files_processed": self.total_files_processed,
                "files_with_effects": self.files_with_effects,
                "total_effects_found": self.total_effects_found,
                "unique_effect_types": len(self.all_effect_types),
                "failed_files": len(self.failed_files),
                "processing_errors": len(self.processing_errors)
            },
            "known_types": {effect_type: count for effect_type, count in known_types},
            "missing_types": {effect_type: count for effect_type, count in missing_types},
            "missing_type_details": dict(self.effect_type_samples),
            "nested_types": list(self.nested_types),
            "failed_files": self.failed_files[:20],  # First 20 failed files
            "processing_errors": self.processing_errors[:10]  # First 10 errors
        }
        
        return report_data
    
    def save_report(self, report_data: Dict[str, Any]):
        """Save report to JSON file"""
        report_file = Path("../../Reports/Spell Reports/effect_types_discovery_report.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n[OK] Report saved to: {report_file}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.processor:
            self.processor.cleanup()


def main():
    """Main discovery function"""
    discoverer = EffectTypeDiscoverer()
    
    try:
        # Initialize
        if not discoverer.initialize():
            print("Failed to initialize discoverer")
            return 1
        
        # Discover all effect types
        if not discoverer.discover_all_effect_types():
            print("Effect type discovery failed")
            return 1
        
        # Generate and save report
        report_data = discoverer.generate_comprehensive_report()
        discoverer.save_report(report_data)
        
        # Summary for user
        missing_count = len(report_data["missing_types"])
        if missing_count > 0:
            print(f"\n[WARNING] FOUND {missing_count} MISSING EFFECT TYPES")
            print("Please provide class definitions from typedump for these types:")
            
            for effect_type, count in sorted(report_data["missing_types"].items(), 
                                           key=lambda x: x[1], reverse=True):
                print(f"  - {effect_type} ({count} occurrences)")
        else:
            print(f"\n[SUCCESS] ALL EFFECT TYPES HAVE DTOS!")
        
        return 0
        
    except Exception as e:
        print(f"Error during discovery: {e}")
        traceback.print_exc()
        return 1
        
    finally:
        discoverer.cleanup()


if __name__ == "__main__":
    sys.exit(main())