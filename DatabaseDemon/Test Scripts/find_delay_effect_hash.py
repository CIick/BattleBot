#!/usr/bin/env python3
"""
Find DelaySpellEffect Hash
=========================
Find the type hash for DelaySpellEffect from the types.json file.
"""

import json
from pathlib import Path


def find_delay_effect_hash():
    """Find the hash for DelaySpellEffect"""
    types_path = Path("../types.json")
    
    if not types_path.exists():
        print(f"Types file not found: {types_path}")
        return
    
    with open(types_path, 'r') as f:
        types_data = json.load(f)
    
    print("Searching for DelaySpellEffect...")
    
    # Types data structure is usually a list of type definitions
    for type_info in types_data:
        if isinstance(type_info, dict):
            # Look for the type name
            if "name" in type_info and "DelaySpellEffect" in type_info["name"]:
                print(f"Found DelaySpellEffect:")
                print(f"  Name: {type_info.get('name')}")
                print(f"  Hash: {type_info.get('hash')}")
                print(f"  Full info: {type_info}")
                return type_info.get('hash')
            
            # Some types files have different structures
            for key, value in type_info.items():
                if isinstance(value, str) and "DelaySpellEffect" in value:
                    print(f"Found DelaySpellEffect in {key}: {value}")
                    if "hash" in type_info:
                        print(f"  Hash: {type_info['hash']}")
                        return type_info['hash']
    
    print("DelaySpellEffect not found in types file")
    return None


if __name__ == "__main__":
    find_delay_effect_hash()