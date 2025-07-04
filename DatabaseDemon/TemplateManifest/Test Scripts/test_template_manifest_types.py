#!/usr/bin/env python3
"""
TemplateManifest Type Analysis Script
====================================

Validates that the required TemplateManifest and TemplateLocation types exist in types.json
and tests basic WAD processing capabilities.

This script:
1. Verifies type hashes exist in types.json
2. Tests basic WAD file opening
3. Validates TemplateManifest.xml accessibility
4. Tests katsuba serialization setup
"""

import json
import os
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directories to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

try:
    import katsuba
    from katsuba.wad import Archive
    from katsuba.op import LazyObject, LazyList, TypeList, Serializer, SerializerOptions
    print("[OK] Katsuba import successful")
except ImportError as e:
    print(f"[ERROR] Failed to import katsuba: {e}")
    sys.exit(1)


def get_platform_paths():
    """Get platform-specific paths for WAD and types files"""
    system = platform.system().lower()
    
    if system == "windows":
        wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    else:  # Linux/WSL
        wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    
    return wad_path, types_path


def test_type_definitions():
    """Test that required types exist in types.json"""
    print("\n=== Testing Type Definitions ===")
    
    wad_path, types_path = get_platform_paths()
    
    if not types_path.exists():
        print(f"[ERROR] types.json not found at {types_path}")
        return False
    
    try:
        with open(types_path, 'r') as f:
            types_data = json.load(f)
        print(f"[OK] Loaded types.json from {types_path}")
    except Exception as e:
        print(f"[ERROR] Failed to load types.json: {e}")
        return False
    
    # Check for required type hashes
    required_types = {
        "171021254": "class TemplateManifest",
        "1128060484": "class TemplateLocation"
    }
    
    classes = types_data.get("classes", {})
    
    for hash_str, expected_name in required_types.items():
        if hash_str in classes:
            actual_name = classes[hash_str]["name"]
            if actual_name == expected_name:
                print(f"[OK] Found {expected_name} (hash: {hash_str})")
            else:
                print(f"[ERROR] Hash {hash_str} found but name mismatch: expected '{expected_name}', got '{actual_name}'")
                return False
        else:
            print(f"[ERROR] Missing type hash {hash_str} ({expected_name})")
            return False
    
    # Print type details
    print("\n=== Type Details ===")
    for hash_str, expected_name in required_types.items():
        type_info = classes[hash_str]
        print(f"\n{expected_name}:")
        print(f"  Hash: {hash_str}")
        print(f"  Bases: {type_info.get('bases', [])}")
        print(f"  Properties:")
        for prop_name, prop_info in type_info.get('properties', {}).items():
            print(f"    {prop_name}: {prop_info.get('type', 'unknown')}")
            if prop_info.get('container') == 'Vector':
                print(f"      Container: Vector of {prop_info.get('type', 'unknown')}")
    
    return True


def test_wad_access():
    """Test basic WAD file access"""
    print("\n=== Testing WAD Access ===")
    
    wad_path, types_path = get_platform_paths()
    
    if not wad_path.exists():
        print(f"[ERROR] Root.wad not found at {wad_path}")
        return False
    
    try:
        # Try opening with memory mapping first
        try:
            archive = Archive.mmap(str(wad_path))
            print(f"[OK] Opened WAD archive (mmap): {wad_path}")
        except Exception:
            archive = Archive.heap(str(wad_path))
            print(f"[OK] Opened WAD archive (heap): {wad_path}")
        
        # Check if TemplateManifest.xml exists
        template_manifest_path = "TemplateManifest.xml"
        if template_manifest_path in archive:
            print(f"[OK] Found {template_manifest_path} in WAD archive")
            
            # Get file info
            file_info = archive[template_manifest_path]
            print(f"[OK] TemplateManifest.xml size: {len(file_info)} bytes")
            
            return True
        else:
            print(f"[ERROR] {template_manifest_path} not found in WAD archive")
            # List some files to debug
            print("Available files (first 20):")
            for i, filename in enumerate(archive.keys()):
                if i < 20:
                    print(f"  {filename}")
                else:
                    break
            return False
        
    except Exception as e:
        print(f"[ERROR] Failed to open WAD archive: {e}")
        return False


def test_katsuba_setup():
    """Test katsuba serialization setup"""
    print("\n=== Testing Katsuba Setup ===")
    
    wad_path, types_path = get_platform_paths()
    
    try:
        # Load types
        with open(types_path, 'r') as f:
            types_data = json.load(f)
        
        type_list = TypeList(types_data)
        print(f"[OK] Created TypeList with {len(types_data.get('classes', {}))} classes")
        
        # Create serializer with recommended options
        options = SerializerOptions()
        options.shallow = False  # Required for skip_unknown_types
        options.skip_unknown_types = True  # Ignore server-side types
        
        serializer = Serializer(options, type_list)
        print("[OK] Created Serializer with recommended options")
        print(f"     - shallow: {options.shallow}")
        print(f"     - skip_unknown_types: {options.skip_unknown_types}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to setup katsuba: {e}")
        return False


def test_template_manifest_processing():
    """Test actual TemplateManifest processing"""
    print("\n=== Testing TemplateManifest Processing ===")
    
    wad_path, types_path = get_platform_paths()
    
    try:
        # Setup
        with open(types_path, 'r') as f:
            types_data = json.load(f)
        
        type_list = TypeList(types_data)
        options = SerializerOptions()
        options.shallow = False
        options.skip_unknown_types = True
        serializer = Serializer(options, type_list)
        
        # Open archive
        try:
            archive = Archive.mmap(str(wad_path))
        except Exception:
            archive = Archive.heap(str(wad_path))
        
        # Process TemplateManifest.xml
        template_manifest_data = archive["TemplateManifest.xml"]
        lazy_object = serializer.deserialize(template_manifest_data)
        
        print(f"[OK] Deserialized TemplateManifest.xml")
        print(f"     Type: {type(lazy_object)}")
        
        # Check if it's a LazyObject
        if isinstance(lazy_object, LazyObject):
            print(f"     Type hash: {lazy_object.type_hash}")
            print(f"     Expected hash: 171021254")
            
            if lazy_object.type_hash == 171021254:
                print("[OK] TemplateManifest type hash matches expected")
                
                # Try to access properties
                if hasattr(lazy_object, 'm_serializedTemplates'):
                    templates = lazy_object.m_serializedTemplates
                    print(f"[OK] Found m_serializedTemplates: {type(templates)}")
                    
                    if isinstance(templates, LazyList):
                        print(f"[OK] m_serializedTemplates is LazyList with {len(templates)} items")
                        
                        # Check first few items
                        for i, template in enumerate(templates[:3]):
                            if isinstance(template, LazyObject):
                                print(f"[OK] Template {i}: type_hash={template.type_hash}")
                                if hasattr(template, 'm_filename') and hasattr(template, 'm_id'):
                                    print(f"     Filename: {template.m_filename}")
                                    print(f"     ID: {template.m_id}")
                                else:
                                    print(f"     Missing expected properties")
                            else:
                                print(f"[ERROR] Template {i} is not LazyObject: {type(template)}")
                        
                        return True
                    else:
                        print(f"[ERROR] m_serializedTemplates is not LazyList: {type(templates)}")
                        return False
                else:
                    print("[ERROR] m_serializedTemplates property not found")
                    return False
            else:
                print(f"[ERROR] Type hash mismatch: expected 171021254, got {lazy_object.type_hash}")
                return False
        else:
            print(f"[ERROR] Deserialized object is not LazyObject: {type(lazy_object)}")
            return False
        
    except Exception as e:
        print(f"[ERROR] Failed to process TemplateManifest: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("TemplateManifest Type Analysis Script")
    print("=" * 50)
    
    tests = [
        ("Type Definitions", test_type_definitions),
        ("WAD Access", test_wad_access),
        ("Katsuba Setup", test_katsuba_setup),
        ("TemplateManifest Processing", test_template_manifest_processing)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n[SUCCESS] All tests passed! TemplateManifest processing is ready.")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())