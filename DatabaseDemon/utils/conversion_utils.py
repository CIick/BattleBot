"""
Conversion Utilities for Wizard101 Data Processing
=================================================
Centralized utilities for converting katsuba LazyObjects to dictionaries
with proper byte string decoding and type handling.
"""

from typing import Dict, Any, Optional, List
from katsuba.op import LazyObject, LazyList, TypeList, Vec3, Quaternion, Matrix, Euler, PointInt, PointFloat, SizeInt, RectInt, RectFloat, Color


def decode_bytes_to_string(value: Any) -> Any:
    """
    Decode bytes objects to UTF-8 strings and convert katsuba objects to readable strings.
    
    Args:
        value: Any value that might be a bytes object or katsuba geometric/color object
        
    Returns:
        Decoded/converted string if input was bytes or katsuba object, otherwise original value
    """
    # Handle katsuba geometric and color objects
    if isinstance(value, Vec3):
        return f"(x={value.x}, y={value.y}, z={value.z})"
    
    elif isinstance(value, Quaternion):
        return f"(x={value.x}, y={value.y}, z={value.z}, w={value.w})"
    
    elif isinstance(value, Matrix):
        return f"[{value.i}, {value.j}, {value.k}]"
    
    elif isinstance(value, Euler):
        return f"(pitch={value.pitch}, yaw={value.yaw}, roll={value.roll})"
    
    elif isinstance(value, (PointInt, PointFloat)):
        return f"(x={value.x}, y={value.y})"
    
    elif isinstance(value, SizeInt):
        return f"({value.width}, {value.height})"
    
    elif isinstance(value, (RectInt, RectFloat)):
        return f"(left={value.left}, top={value.top}, right={value.right}, bottom={value.bottom})"
    
    elif isinstance(value, Color):
        return f"(r={value.r}, g={value.g}, b={value.b}, a={value.a})"
    
    # Handle bytes objects
    elif isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            # If UTF-8 fails, try latin-1 as fallback
            try:
                return value.decode('latin-1')
            except UnicodeDecodeError:
                # If all decoding fails, return as string representation
                return str(value)
    
    return value


def convert_lazy_object_to_dict(obj: Any, type_list: Optional[TypeList] = None) -> Dict[str, Any]:
    """
    Convert LazyObject/LazyList to dictionary with type information and proper byte decoding.
    
    This function handles:
    - LazyList conversion with recursive processing
    - LazyObject conversion with nested object support
    - Byte string decoding to prevent b'string' artifacts
    - Type hash resolution and naming
    
    Args:
        obj: LazyObject, LazyList, or other object to convert
        type_list: Optional TypeList for resolving type names
        
    Returns:
        Dictionary representation with decoded strings and type information
    """
    # Handle LazyList objects
    if isinstance(obj, LazyList) and type_list:
        try:
            # Convert LazyList to a list of converted items
            result = []
            for item in obj:
                if isinstance(item, (LazyObject, LazyList)):
                    # Recursively convert nested LazyObjects/LazyLists
                    result.append(convert_lazy_object_to_dict(item, type_list))
                else:
                    # Decode bytes to strings for primitive values
                    result.append(decode_bytes_to_string(item))
            return result
        except Exception as e:
            return {"error": f"LazyList conversion failed: {e}"}
    
    # Handle LazyObject objects
    if isinstance(obj, LazyObject) and type_list:
        try:
            # Convert LazyObject to dictionary
            result = {}
            for key, value in obj.items(type_list):
                # Ensure key is also decoded if it's bytes
                decoded_key = decode_bytes_to_string(key)
                
                if isinstance(value, (LazyObject, LazyList)):
                    # Recursively convert nested LazyObjects/LazyLists
                    result[decoded_key] = convert_lazy_object_to_dict(value, type_list)
                elif isinstance(value, list):
                    # Handle lists that might contain LazyObjects/LazyLists or bytes
                    converted_list = []
                    for item in value:
                        if isinstance(item, (LazyObject, LazyList)):
                            converted_list.append(convert_lazy_object_to_dict(item, type_list))
                        else:
                            converted_list.append(decode_bytes_to_string(item))
                    result[decoded_key] = converted_list
                else:
                    # Handle primitive values (including bytes)
                    result[decoded_key] = decode_bytes_to_string(value)
            
            # Add type information
            try:
                type_name = type_list.name_for(obj.type_hash)
                result["$__type"] = type_name
            except:
                # If type name resolution fails, use hash
                result["$__type"] = obj.type_hash
            
            return result
        except Exception as e:
            return {"error": f"LazyObject conversion failed: {e}", "type_hash": getattr(obj, 'type_hash', 'unknown')}
    
    # Handle primitive types that might be bytes
    return decode_bytes_to_string(obj)


def convert_lazy_object_to_dict_with_hash_only(obj: Any, type_list: Optional[TypeList] = None) -> Dict[str, Any]:
    """
    Alternative conversion that uses type hash instead of type name.
    Useful when type name resolution is unreliable or not needed.
    
    Args:
        obj: LazyObject, LazyList, or other object to convert
        type_list: Optional TypeList for object iteration
        
    Returns:
        Dictionary representation with type hashes and decoded strings
    """
    # Handle LazyList objects
    if isinstance(obj, LazyList) and type_list:
        try:
            result = []
            for item in obj:
                if isinstance(item, (LazyObject, LazyList)):
                    result.append(convert_lazy_object_to_dict_with_hash_only(item, type_list))
                else:
                    result.append(decode_bytes_to_string(item))
            return result
        except Exception as e:
            return {"error": f"LazyList conversion failed: {e}"}
    
    # Handle LazyObject objects
    if isinstance(obj, LazyObject) and type_list:
        try:
            result = {}
            for key, value in obj.items(type_list):
                decoded_key = decode_bytes_to_string(key)
                
                if isinstance(value, (LazyObject, LazyList)):
                    result[decoded_key] = convert_lazy_object_to_dict_with_hash_only(value, type_list)
                elif isinstance(value, list):
                    converted_list = []
                    for item in value:
                        if isinstance(item, (LazyObject, LazyList)):
                            converted_list.append(convert_lazy_object_to_dict_with_hash_only(item, type_list))
                        else:
                            converted_list.append(decode_bytes_to_string(item))
                    result[decoded_key] = converted_list
                else:
                    result[decoded_key] = decode_bytes_to_string(value)
            
            # Use type hash directly (no name resolution)
            result["$__type"] = obj.type_hash
            
            return result
        except Exception as e:
            return {"error": f"LazyObject conversion failed: {e}", "type_hash": getattr(obj, 'type_hash', 'unknown')}
    
    return decode_bytes_to_string(obj)