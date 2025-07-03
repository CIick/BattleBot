# DatabaseDemon/Spells - Wizard101 Spell Database Creation

Creates comprehensive SQLite database from Wizard101 Root.wad spell data with full DTO mapping and error handling.

## Quick Start

```bash
cd DatabaseDemon/Spells
python database_creator.py
```

## Requirements

- **types.json**: Must exist in parent DatabaseDemon directory (correct revision)
- **Wizard101**: Installed with accessible Root.wad file
- **Python packages**: katsuba, sqlite3 (built-in)

## Output

- `database/r{revision}_spells.db` - SQLite database with normalized spell data
- `failed_spells/` - Error analysis and skipped element reports

## Database Schema

### Core Tables
- **spell_cards**: Main spell templates (filename as PRIMARY KEY)
- **spell_effects**: All spell effect types with inheritance support
- **requirement_lists**: Spell casting requirements
- **req_***: Individual requirement types (ReqIsSchool, ReqMagicLevel, etc.)

### Features
- **Duplicate Prevention**: Filename-based PRIMARY KEY prevents duplicates
- **Error Logging**: Comprehensive tracking of skipped elements and failures
- **Type Coverage**: Support for 60+ spell and requirement types
- **Normalization**: Proper foreign key relationships

## Recent Updates

- ✅ Fixed ReqMagicLevelDTO handler (788 errors resolved)
- ✅ Added missing requirement DTOs and database tables
- ✅ Comprehensive skipped element logging
- ✅ Support for nested RequirementLists

## Architecture

```
Spells/
├── processors/           # Core processing logic
│   ├── DatabaseCreator.py   # Main database creation
│   ├── DatabaseSchema.py    # Table definitions
│   ├── WADProcessor.py      # WAD file processing
│   └── RevisionDetector.py  # Auto-revision detection
├── dtos/                # Data Transfer Objects
│   ├── SpellsDTO.py         # All spell/requirement DTOs
│   ├── SpellsDTOFactory.py  # Type hash mappings
│   └── SpellsEnums.py       # Enumerations
└── database_creator.py  # Main entry point
```