# DatabaseDemon/Mobs - Wizard101 Mob Database Creation

**Status: Future Development**

This module will create comprehensive SQLite database from Wizard101 mob data following the same patterns as the Spells module.

## Planned Features

- Extract mob data from Wizard101 WAD files
- Create normalized database with mob statistics, behaviors, and attributes
- Support for different mob types (enemies, NPCs, bosses, etc.)
- Comprehensive error handling and logging

## Future Architecture

```
Mobs/
├── processors/           # Core processing logic
│   ├── DatabaseCreator.py   # Main database creation
│   ├── DatabaseSchema.py    # Table definitions  
│   ├── WADProcessor.py      # WAD file processing
│   └── RevisionDetector.py  # Auto-revision detection
├── dtos/                # Data Transfer Objects
│   ├── MobsDTO.py           # All mob DTOs
│   ├── MobsDTOFactory.py    # Type hash mappings
│   └── MobsEnums.py         # Enumerations
└── database_creator.py  # Main entry point
```

## Shared Resources

- Uses `../types.json` from parent DatabaseDemon directory
- Follows same revision detection patterns as Spells module
- Inherits error handling and logging infrastructure

## Development Notes

When implementing this module:
1. Copy and adapt the Spells module structure
2. Update DTOs for mob-specific data structures
3. Create appropriate database schema for mob data
4. Implement WAD processing for mob files
5. Add comprehensive testing and validation

## Usage (Future)

```bash
cd DatabaseDemon/Mobs
python database_creator.py
```