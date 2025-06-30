# DatabaseDemon - Wizard101 Spell Database Creator

Automated system for creating SQLite databases from Wizard101 Root.wad spell data. Designed for ML training and combat analysis.

## Features

- **Automatic Revision Detection**: Detects current Wizard101 revision from `revision.dat`
- **Duplicate Prevention**: Uses filename as PRIMARY KEY to prevent duplicates
- **Comprehensive Error Logging**: Failed spells logged to `failed_spells/` directory
- **SQL Server Compatible**: Schema designed for easy migration to SQL Server
- **Raw Data Storage**: No premature feature engineering - stores complete spell data
- **LazyList/LazyObject Handling**: Properly converts katsuba objects to JSON structures

## Prerequisites

1. **Wizard101 Installation**: Must have access to Root.wad file
2. **Types File**: Correct `types.json` file for your Wizard101 revision
3. **Python Packages**: `katsuba` library installed

## Quick Start

1. **Copy types.json**: Place the correct types.json file in the DatabaseDemon directory
2. **Run database creator**:
   ```bash
   cd DatabaseDemon
   python database_creator.py
   ```

## File Structure

```
DatabaseDemon/
├── dtos/                           # Data Transfer Objects
│   ├── SpellsEnums.py             # Enum definitions
│   ├── SpellsDTO.py               # DTO class definitions  
│   └── SpellsDTOFactory.py        # Factory and processing logic
├── processors/                     # Core processing logic
│   ├── WADProcessor.py            # WAD file processing
│   ├── DatabaseCreator.py         # Database creation and population
│   ├── DatabaseSchema.py          # Database schema definition
│   └── RevisionDetector.py        # Revision detection utilities
├── database/                       # Generated databases
│   └── r{revision}_spells.db      # SQLite database (created)
├── failed_spells/                  # Error analysis
│   ├── duplicate_*.json           # Duplicate collision analysis
│   └── failed_*.json              # Processing failure details
├── database_creator.py             # Main entry point
├── types.json                      # Types file (user provided)
└── README.md                       # This file
```

## Database Schema

### Main Tables
- **spell_cards**: Main spell data (filename as PRIMARY KEY)
- **spell_effects**: Spell effects (one-to-many)
- **spell_ranks**: Pip costs and requirements
- **random_spell_effects**: Nested effects for RandomSpellEffect DTOs

### Type-Specific Tables
- **tiered_spell_data**: TieredSpellTemplate specific fields
- **cantrips_spell_data**: CantripsSpellTemplate specific fields
- **castle_magic_spell_data**: CastleMagicSpellTemplate specific fields
- And more...

### Metadata Tables
- **processing_metadata**: Processing statistics and revision info
- **duplicate_log**: Duplicate detection results

## Error Handling

### Duplicate Detection
If duplicate filenames are found:
- Database insertion prevented by PRIMARY KEY constraint
- Full spell data comparison logged to `failed_spells/duplicate_*.json`
- Summary shows total duplicate count

### Processing Failures
Failed spell processing logged with:
- Full error messages and stack traces
- Complete spell data for analysis
- Categorized by failure type

## Types File Requirements

The `types.json` file must match your Wizard101 revision:
- Get from QuestWhiz types dump
- Filename should contain revision number (e.g., `r777820_Wizard_1_580_0_Live.json`)
- Rename to `types.json` and place in DatabaseDemon directory

**Error Message**: If types don't match, you'll see:
```
Check if the type dump (types.json) is the correct version for this revision
```

## Output

### Successful Run
```
Database: database/r777820_spells.db
Total processed: 16,405
Successful: 16,200
Failed: 205
Duplicates: 0
Success rate: 98.8%
```

### Warning Signs
- **Duplicates > 0**: Filename is not unique, need different primary key strategy
- **High failure rate**: Types file version mismatch or WAD corruption

## Next Steps

After database creation:
1. **Validate Data**: Query database to ensure spell data looks correct
2. **Add Mob Data**: Integrate with mob data for complete combat simulation
3. **Feature Engineering**: Add computed columns for ML training
4. **SQL Server Migration**: Migrate to SQL Server for advanced analytics

## SQL Server Migration

Schema is designed for easy migration:
```sql
-- Example queries work in both SQLite and SQL Server
SELECT m_name, m_sMagicSchoolName, m_accuracy 
FROM spell_cards 
WHERE m_sTypeName = 'Damage'
ORDER BY m_accuracy DESC;
```

## Troubleshooting

### Common Issues

**"Types file not found"**
- Copy correct types.json to DatabaseDemon directory

**"No spell files found"**
- Check WAD file path in auto-detection
- Ensure Wizard101 is installed correctly

**"High duplicate count"**
- Indicates filename PRIMARY KEY strategy may not work
- Check duplicate analysis in failed_spells/ directory

**"Database creation failed"**
- Check disk space for database directory
- Ensure write permissions to DatabaseDemon folder