# Wizard101 TemplateManifest Database System

Comprehensive system for processing Wizard101 TemplateManifest data from Root.wad files, creating structured SQLite databases for template ID to deck filename mapping.

## Overview

This system processes the TemplateManifest.xml file from Wizard101's Root.wad to create a database that enables lookup of template IDs to their corresponding deck filenames. This is essential for linking mob `m_itemList` values to actual deck data.

**Key Use Case**: When a mob has `m_itemList: [211553, 4589, 324086]`, you can look up template ID `211553` to find it maps to `"ObjectData/Decks/Mdeck-I-R9.xml"`, allowing you to load the corresponding deck data.

## Features

- **Dynamic WAD Processing**: Processes TemplateManifest.xml directly from Root.wad
- **Fast Template Lookup**: Optimized database schema for instant ID-to-filename mapping
- **Comprehensive Categorization**: Automatic deck type and category classification
- **Future-Proof Design**: Handles manifest changes across game patches
- **Complete Analysis**: Detailed statistics and reporting capabilities
- **Robust Validation**: Comprehensive testing and error handling

## Quick Start

### Basic Usage

```bash
# Create complete TemplateManifest database
python database_creator.py

# Custom output directory
python database_creator.py --output-dir /custom/path

# Skip validation for faster processing
python database_creator.py --skip-validation
```

### Validation

```bash
# Run comprehensive validation tests
cd "Test Scripts"
python test_template_manifest_processing.py

# Run type validation only
python test_template_manifest_types.py
```

## System Architecture

### Core Components

```
DatabaseDemon/TemplateManifest/
├── dtos/                           # Data Transfer Objects
│   ├── TemplateManifestDTO.py     # Main DTO classes
│   ├── TemplateManifestDTOFactory.py # Conversion factory
│   └── TemplateManifestEnums.py   # Enums and constants
├── processors/                     # Core processing logic
│   ├── WADProcessor.py            # TemplateManifest.xml processing
│   ├── DatabaseSchema.py          # SQLite schema management
│   └── DatabaseCreator.py         # Database population logic
├── Test Scripts/                   # Validation and testing
│   ├── test_template_manifest_processing.py # Complete validation
│   └── test_template_manifest_types.py # Type validation
└── database_creator.py            # Main entry point
```

### Data Flow

1. **Root.wad/TemplateManifest.xml** → WADProcessor → **LazyObjects**
2. **LazyObjects** → DTOFactory → **DTOs**
3. **DTOs** → DatabaseCreator → **SQLite Database**
4. **Database** → Analysis Views → **Reports**

## Database Schema

### Main Tables

- **`template_locations`**: Primary template mapping with full categorization
- **`template_statistics`**: Processing and validation statistics
- **`deck_analysis`**: Advanced deck analysis and pattern matching

### Analysis Views

- **`template_lookup`**: Fast template ID to filename lookup
- **`deck_type_summary`**: Template distribution by deck type
- **`deck_category_summary`**: Template distribution by category
- **`validation_summary`**: Data quality metrics

### Key Indexes

- Primary lookup: `template_id`, `filename`, `deck_name`
- Classification: `deck_type`, `deck_category`
- Fast filtering: `is_mob_deck`, `is_boss_deck`, `is_polymorph_deck`

## Data Transfer Objects

### TemplateManifestDTO

Main container for all template locations:

```python
@dataclass
class TemplateManifestDTO:
    m_serializedTemplates: List[TemplateLocationDTO]
    
    # Key methods
    def lookup_by_id(self, template_id: int) -> TemplateLocationDTO
    def get_deck_filename(self, template_id: int) -> str
    def get_deck_name(self, template_id: int) -> str
    def validate_template_ids(self, ids: List[int]) -> dict
```

### TemplateLocationDTO

Individual template mapping:

```python
@dataclass
class TemplateLocationDTO:
    m_filename: str        # Full deck filename
    m_id: int             # Template ID
    deck_name: str        # Extracted deck name
    deck_type: str        # mob/boss/polymorph/etc.
    deck_category: str    # fire/ice/storm/etc.
```

## Usage Examples

### Python API

```python
import sqlite3

# Open database
conn = sqlite3.connect('database/template_manifest_20250704_123456.db')
cursor = conn.cursor()

# Look up template ID from mob m_itemList
template_id = 211553
cursor.execute("SELECT filename, deck_name FROM template_locations WHERE template_id = ?", (template_id,))
result = cursor.fetchone()

if result:
    filename, deck_name = result
    print(f"Template {template_id} -> {filename} ({deck_name})")
    # Now load deck data using filename
```

### SQL Queries

```sql
-- Find deck for specific template ID
SELECT * FROM template_lookup WHERE template_id = 211553;

-- Get all mob decks
SELECT template_id, deck_name FROM template_locations WHERE is_mob_deck = TRUE;

-- Find Fire school decks
SELECT * FROM template_locations WHERE deck_category = 'fire';

-- Get deck type distribution
SELECT * FROM deck_type_summary ORDER BY template_count DESC;
```

### Mob Item List Integration

```python
# Example: Process mob m_itemList
mob_item_list = [211553, 4589, 324086, 225697]

deck_filenames = []
for template_id in mob_item_list:
    cursor.execute("SELECT filename FROM template_locations WHERE template_id = ?", (template_id,))
    result = cursor.fetchone()
    if result:
        deck_filenames.append(result[0])

print(f"Mob uses decks: {deck_filenames}")
# Load each deck file for complete mob analysis
```

## Configuration

### Platform Support

The system automatically detects Windows vs Linux/WSL environments:

- **Windows**: `C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad`
- **Linux/WSL**: `/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad`

### Type System

Uses centralized type definitions from `../types.json`:
- **TemplateManifest**: Hash `171021254`
- **TemplateLocation**: Hash `1128060484`

### Output Locations

- **Database**: `database/template_manifest_{timestamp}.db`
- **Reports**: `Reports/TemplateManifest Reports/`

## Validation & Testing

### Comprehensive Testing

The validation system tests:
- Type system compatibility
- WAD file processing
- DTO conversion accuracy
- Database creation and population
- Template lookup functionality
- Performance benchmarks

### Quality Metrics

Expected performance:
- **100% Processing Success**: All templates processed without errors
- **Fast Lookups**: 1000+ lookups per second
- **High Validation Rate**: 95%+ template validation success
- **Complete Coverage**: All template types categorized

## Performance

### Processing Speed

Typical performance on modern hardware:
- **Template Processing**: Instant (single XML file)
- **Database Creation**: 1-2 seconds
- **Lookup Performance**: 1000+ lookups/second

### Database Efficiency

- **Optimized Schema**: Comprehensive indexing strategy
- **Compact Storage**: Normalized design minimizes redundancy
- **Fast Queries**: Sub-millisecond lookups with proper indexes

## Integration

### With Existing Systems

This system follows the same patterns as Mobs and Spells systems:
- **Consistent Architecture**: Same DTO/Processor pattern
- **Shared Utilities**: Uses centralized conversion utilities
- **Compatible Reporting**: Similar report formats

### For Mob Analysis

Perfect integration point for mob data analysis:
1. **Mob Processing**: Extract mob `m_itemList` values
2. **Template Lookup**: Convert template IDs to deck filenames
3. **Deck Loading**: Load corresponding deck data
4. **Complete Analysis**: Analyze mob's spell capabilities

## Troubleshooting

### Common Issues

1. **Type Hash Errors**: Ensure types.json is correct version for your Wizard101 revision
2. **WAD Access Issues**: Verify Wizard101 is installed and Root.wad is accessible
3. **Performance Issues**: Check database indexes and query optimization

### Debug Mode

```bash
# Run with verbose output
python database_creator.py --verbose

# Force creation despite validation issues
python database_creator.py --force

# Run complete validation suite
python "Test Scripts/test_template_manifest_processing.py"
```

## Development

### Adding New Features

1. **DTOs**: Extend DTOs in `dtos/TemplateManifestDTO.py`
2. **Analysis**: Add functions to `TemplateManifestDTOFactory.py`
3. **Database**: Modify schema in `DatabaseSchema.py`
4. **Processing**: Update logic in `DatabaseCreator.py`

### Testing

Always run validation after changes:

```bash
cd "Test Scripts"
python test_template_manifest_processing.py
```

## Technical Details

### Katsuba Integration

Follows recommended patterns for Wizard101 data processing:

```python
# Standard SerializerOptions configuration
options = SerializerOptions()
options.shallow = False              # Enable deep serialization
options.skip_unknown_types = True   # Ignore server-side types
```

### Error Handling

Comprehensive error handling at all levels:
- **WAD Processing**: Graceful handling of missing files
- **Type Conversion**: Robust LazyObject to DTO conversion
- **Database Operations**: Transaction safety and rollback
- **Validation**: Detailed error reporting and categorization

### Memory Management

Efficient memory usage:
- **Single File Processing**: Only TemplateManifest.xml loaded
- **Batch Operations**: Optimized database insertions
- **Resource Cleanup**: Proper cleanup of WAD archives and connections

## Output Statistics

### Typical Results

Based on current Wizard101 version:
- **Total Templates**: 5000+ template locations
- **Processing Time**: 1-2 seconds
- **Database Size**: 1-2 MB
- **Validation Rate**: 99%+ success

### Template Distribution

Common template type distribution:
- **Mob Decks**: 60-70% of templates
- **Boss Decks**: 15-20% of templates
- **Polymorph Decks**: 10-15% of templates
- **Other Types**: 5-10% of templates

This comprehensive system provides the foundation for linking Wizard101 mob data to deck information, enabling complete mob behavior analysis and strategic planning.