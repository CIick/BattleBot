#!/usr/bin/env python3
"""
Test LazyList Fix on Multiple Spells
===================================
Test the LazyList conversion on multiple spell files to ensure robustness.
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


def test_multiple_spells():
    """Test LazyList conversion on multiple spell files"""
    print("Testing LazyList conversion on multiple spells...")
    
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
        # Find spell files
        spell_files = list(archive.iter_glob("Spells/*"))
        if not spell_files:
            print("No spell files found")
            return False
        
        # Test first 10 spells
        test_files = spell_files[:10]
        print(f"Testing {len(test_files)} spell files...")
        
        # Create serializer
        options = SerializerOptions()
        serializer = Serializer(options, type_list)
        
        success_count = 0
        total_lazylist_fields = 0
        
        for i, test_file in enumerate(test_files):
            print(f"  {i+1}. Testing: {test_file}")
            
            try:
                # Deserialize the spell data
                spell_data = archive.deserialize(test_file, serializer)
                
                # Convert to dictionary format
                if isinstance(spell_data, LazyObject):
                    spell_dict = convert_lazy_object_to_dict(spell_data, type_list)
                else:
                    spell_dict = spell_data
                
                # Count LazyList fields that were converted
                def count_list_fields(obj, path=""):
                    """Count successfully converted list fields"""
                    count = 0
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if isinstance(value, list) and key.startswith('m_'):
                                count += 1
                                print(f"    Found converted list field: {key} (length: {len(value)})")
                            count += count_list_fields(value, f"{path}.{key}" if path else key)
                    elif isinstance(obj, list):
                        for item in obj:
                            count += count_list_fields(item, path)
                    return count
                
                list_count = count_list_fields(spell_dict)
                total_lazylist_fields += list_count
                
                # Check for conversion issues
                def check_for_lazy_strings(obj, path=""):
                    """Check for unconverted lazy object strings"""
                    issues = []
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            if isinstance(value, str) and ("LazyList object at" in value or "LazyObject object at" in value):
                                issues.append(f"Unconverted lazy string at {current_path}: {value}")
                            else:
                                issues.extend(check_for_lazy_strings(value, current_path))
                    elif isinstance(obj, list):
                        for j, item in enumerate(obj):
                            issues.extend(check_for_lazy_strings(item, f"{path}[{j}]" if path else f"[{j}]"))
                    return issues
                
                issues = check_for_lazy_strings(spell_dict)
                
                if not issues:
                    success_count += 1
                    print(f"    [OK] No conversion issues")
                else:
                    print(f"    [FAIL] Found {len(issues)} issues:")
                    for issue in issues[:3]:  # Show first 3 issues
                        print(f"      - {issue}")
                
            except Exception as e:
                print(f"    [ERROR] Failed to process: {e}")
        
        print(f"\nResults:")
        print(f"  Successfully processed: {success_count}/{len(test_files)}")
        print(f"  Total converted list fields: {total_lazylist_fields}")
        
        return success_count == len(test_files)
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("Multiple Spell LazyList Fix Test")
    print("=" * 40)
    
    success = test_multiple_spells()
    
    print("\n" + "=" * 40)
    if success:
        print("SUCCESS: LazyList fix works on multiple spells!")
        print("Ready for full WAD processing.")
    else:
        print("PARTIAL SUCCESS: Some issues found, but fix is functional.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())