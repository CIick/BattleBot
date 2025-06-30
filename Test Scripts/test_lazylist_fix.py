#!/usr/bin/env python3
"""
Test LazyList Fix
================
Quick test to verify that LazyList objects are properly converted to JSON structures.
"""

import json
import os
import platform
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import katsuba
from katsuba.wad import Archive
from katsuba.op import LazyObject, LazyList, TypeList, Serializer, SerializerOptions

# Import the fixed conversion function
from test_all_root_wad_spells import convert_lazy_object_to_dict, get_platform_paths, load_type_list, open_wad_archive


def test_single_spell_lazylist_conversion():
    """Test LazyList conversion on a single spell"""
    print("Testing LazyList conversion fix...")
    
    # Get platform-specific paths
    wad_path, types_path = get_platform_paths()
    
    # Load type definitions
    type_list = load_type_list(types_path)
    if not type_list:
        print("Failed to load type list")
        return False
    
    # Open WAD archive
    archive = open_wad_archive(wad_path)
    if not archive:
        print("Failed to open WAD archive")
        return False
    
    try:
        # Find and process one spell file
        spell_files = list(archive.iter_glob("Spells/*"))
        if not spell_files:
            print("No spell files found")
            return False
            
        # Take the first spell file
        test_file = spell_files[0]
        print(f"Testing file: {test_file}")
        
        # Create serializer
        options = SerializerOptions()
        serializer = Serializer(options, type_list)
        
        # Deserialize the spell data
        spell_data = archive.deserialize(test_file, serializer)
        
        # Convert to dictionary format
        if isinstance(spell_data, LazyObject):
            spell_dict = convert_lazy_object_to_dict(spell_data, type_list)
        else:
            spell_dict = spell_data
        
        # Check for LazyList conversion issues
        def check_for_lazy_objects(obj, path=""):
            """Recursively check for unconverted lazy objects"""
            issues = []
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (LazyObject, LazyList)):
                        issues.append(f"Unconverted lazy object at {current_path}: {type(value)}")
                    elif isinstance(value, str) and "LazyList object at" in value:
                        issues.append(f"String representation of LazyList at {current_path}: {value}")
                    elif isinstance(value, str) and "LazyObject object at" in value:
                        issues.append(f"String representation of LazyObject at {current_path}: {value}")
                    else:
                        issues.extend(check_for_lazy_objects(value, current_path))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    if isinstance(item, (LazyObject, LazyList)):
                        issues.append(f"Unconverted lazy object at {current_path}: {type(item)}")
                    elif isinstance(item, str) and ("LazyList object at" in item or "LazyObject object at" in item):
                        issues.append(f"String representation of lazy object at {current_path}: {item}")
                    else:
                        issues.extend(check_for_lazy_objects(item, current_path))
            
            return issues
        
        # Check for issues
        issues = check_for_lazy_objects(spell_dict)
        
        if issues:
            print("ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("SUCCESS: No LazyList/LazyObject conversion issues found!")
            
            # Show some sample data to verify proper conversion
            print("\nSample converted data:")
            if "m_effects" in spell_dict and spell_dict["m_effects"]:
                print(f"m_effects type: {type(spell_dict['m_effects'])}")
                print(f"m_effects length: {len(spell_dict['m_effects'])}")
                if len(spell_dict["m_effects"]) > 0:
                    effect = spell_dict["m_effects"][0]
                    print(f"First effect type: {type(effect)}")
                    if isinstance(effect, dict) and "$__type" in effect:
                        print(f"First effect $__type: {effect['$__type']}")
            
            return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("LazyList Fix Validation Test")
    print("=" * 40)
    
    success = test_single_spell_lazylist_conversion()
    
    print("\n" + "=" * 40)
    if success:
        print("SUCCESS: LazyList fix is working correctly!")
        print("Ready to process all WAD spells.")
    else:
        print("FAILURE: LazyList fix needs more work.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())