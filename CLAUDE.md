# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation project for Wizard101 combat using the wizwalker library. The project contains a single main script that implements an automated combat handler called `LostSoulDestroyer` which casts "thunder snake" spells on Lost Soul monsters.

## Dependencies

The project uses wizwalker, a Python library for Wizard101 automation:
- **Installation**: `pip install git+https://codeberg.org/notfaj/wizwalker@development`
- **Note**: The PyPI version (`pip install wizwalker`) is outdated and no longer maintained. Always use the Codeberg repository version.

## Development Environment

- **Python Version**: Python 3.12.3 (use `python3` command)
- **Virtual Environment**: Windows-style venv located at `.venv/`
- **Activation**: Use `.venv/Scripts/python.exe` for running scripts
- **Package Management**: Use `.venv/Scripts/python.exe -m pip` for installing packages

## Running the Application

```bash
# Run the main script
.venv/Scripts/python.exe main.py
```

**Note**: The application requires an active Wizard101 client to function. It will fail with "IndexError: list index out of range" if no clients are detected.

## Architecture

### Core Components

- **main.py**: Single entry point containing:
  - `LostSoulDestroyer` class: Extends `CombatHandler` from wizwalker
  - `main()` function: Sets up client connection and combat handling
  - Combat logic: Automatically casts "thunder snake" on the first monster (assumed to be Lost Soul)

### Key Classes

- `LostSoulDestroyer(CombatHandler)`: Main combat automation class
  - `handle_round()`: Core combat logic executed each round
  - Searches for "thunder snake" card in hand
  - Targets first monster in monster list
  - Handles card not found scenarios gracefully

## Development Workflow

1. Ensure Wizard101 client is running
2. Use virtual environment Python executable for all operations
3. The script runs continuously until combat ends or client disconnects
4. Monitor console output for debugging information

## Common Tasks

- **Install dependencies**: `.venv/Scripts/python.exe -m pip install git+https://codeberg.org/notfaj/wizwalker@development`
- **Run script**: `.venv/Scripts/python.exe main.py`
- **Update wizwalker**: Re-run the pip install command above

---

## DatabaseDemon - Wizard101 Data Processing System

The repository also contains **DatabaseDemon**, a comprehensive system for extracting and processing Wizard101 game data from WAD files into structured databases.

### DatabaseDemon Structure

```
DatabaseDemon/
├── types.json              # Master type definitions for all object types
├── Spells/                 # Spell database creation system
│   ├── processors/         # Core processing logic
│   ├── dtos/              # Data Transfer Objects
│   └── Test Scripts/      # Validation and testing scripts
└── Mobs/                  # Mob database creation system
    └── Test Scripts/      # Mob validation scripts
```

### Katsuba Library Best Practices

When creating new object type processors (Items, NPCs, etc.), always follow these patterns:

#### SerializerOptions Configuration
**ALWAYS** configure SerializerOptions with these recommended settings:

```python
from katsuba.op import SerializerOptions, Serializer

# Standard configuration for all Wizard101 data processing
options = SerializerOptions()
options.shallow = False  # Allow deep serialization (required for skip_unknown_types)
options.skip_unknown_types = True  # Equivalent to CLI --ignore-unknown-types
serializer = Serializer(options, type_list)
```

**Why these specific options?**
- `shallow = False`: Enables deep serialization of nested objects (required for skip_unknown_types)
- `skip_unknown_types = True`: Ignores server-side types not in client type dumps
- Prevents 18,000+ failures from unknown server types
- Allows partial data extraction rather than complete failures
- Essential for processing data across different game versions

**Critical Note**: You CANNOT use `skip_unknown_types = True` with `shallow = True` (default). Katsuba will throw: "cannot skip unknown types in shallow mode".

#### Platform-Specific Paths
```python
def get_platform_paths():
    system = platform.system().lower()
    if system == "windows":
        wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    else:  # Linux/WSL
        wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    return wad_path, types_path
```

#### WAD Archive Opening Pattern
```python
def open_wad_archive(wad_path: Path) -> Optional[Archive]:
    try:
        # Try memory mapping first, fall back to heap if needed
        try:
            archive = Archive.mmap(str(wad_path))
            print(f"[OK] Opened WAD archive (mmap): {wad_path}")
        except Exception:
            archive = Archive.heap(str(wad_path))
            print(f"[OK] Opened WAD archive (heap): {wad_path}")
        return archive
    except Exception as e:
        print(f"Error opening WAD archive: {e}")
        return None
```

#### Object Processing Pattern
```python
# Filter by type hash for specific object types
obj_type = obj_dict.get('$__type')
if obj_type == TARGET_TYPE_HASH:  # e.g., 701229577 for WizGameObjectTemplate
    process_target_object(file_path, obj_dict)
else:
    process_non_target_object(file_path, obj_dict)
```

### Creating New Object Type Processors

When adding support for new object types (Items, NPCs, Housing, etc.):

1. **Create directory structure**: `DatabaseDemon/{ObjectType}/`
2. **Add Test Scripts**: Start with validation script like `test_all_root_wad_{objecttype}.py`
3. **Use types.json**: Reference central type definitions in main directory
4. **Follow chunk size standards**: 50MB for most objects, 100MB for very large datasets
5. **Output to Reports**: Save validation reports to `Reports/{ObjectType} Reports/`
6. **Standard imports**: Always include katsuba SerializerOptions configuration

### Type Hash Reference

Common Wizard101 object type hashes:
- **701229577**: WizGameObjectTemplate (Mobs)
- **Spells**: Multiple types, see Spells/dtos/SpellsDTOFactory.py for complete mapping

### Centralized Conversion Utilities

**Always use the centralized conversion utility** for processing LazyObjects:

```python
from utils.conversion_utils import convert_lazy_object_to_dict

# Convert LazyObject with proper byte string decoding
obj_dict = convert_lazy_object_to_dict(lazy_object, type_list)
```

**Why use the centralized utility?**
- **Fixes byte string artifacts**: Prevents `b'string'` from appearing in output
- **Proper UTF-8 decoding**: Converts bytes objects to readable strings
- **Fallback encoding**: Handles edge cases with latin-1 and string representation
- **Consistent behavior**: Same conversion logic across all object types
- **Future maintenance**: Single location for conversion improvements

**Available Functions:**
- `convert_lazy_object_to_dict()`: Standard conversion with type name resolution
- `convert_lazy_object_to_dict_with_hash_only()`: Alternative using only type hashes
- `decode_bytes_to_string()`: Utility for individual byte string conversion

### Error Handling

- Use `skip_unknown_types = True` to handle server-side types gracefully
- Implement comprehensive logging for skipped elements
- Separate successful processing from failures with detailed error analysis
- Output failures to dedicated log files for debugging
- **Always use centralized conversion utilities** to prevent encoding issues
```

## Project Memories and Notes

### DatabaseDemon Project Structure and Templating
- With the plan created, establish a template for database creation that can be consistently used across the DatabaseDemon project
- Aim to create a standardized approach for processing different object types with similar structural patterns