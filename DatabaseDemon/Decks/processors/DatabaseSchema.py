"""
Wizard101 Decks Database Schema
===============================
SQLite database schema definition for Wizard101 deck data.

This module defines:
- Table schemas for deck storage
- Indexes for efficient querying
- Relationships to spell data via spell names
- Database versioning and migration support

Based on analysis of 3,556 deck files:
- Single DeckTemplate type (hash: 4737210)
- 4,167 unique spell names
- Rich metadata for analysis and ML training
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseSchema:
    """Manages database schema creation and versioning for deck data."""
    
    # Current schema version for migration tracking
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: Path):
        """Initialize schema manager with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def create_tables(self, connection: sqlite3.Connection):
        """Create all database tables with proper schema.
        
        Args:
            connection: SQLite database connection
        """
        cursor = connection.cursor()
        
        # Main decks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                -- Primary identification
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,  -- Source XML filename (PRIMARY KEY equivalent)
                deck_name TEXT NOT NULL,
                type_hash INTEGER NOT NULL,
                
                -- Spell composition
                spell_count INTEGER NOT NULL DEFAULT 0,
                unique_spell_count INTEGER NOT NULL DEFAULT 0,
                spell_names_json TEXT NOT NULL,  -- JSON array of spell names
                
                -- Categorization and analysis
                deck_type TEXT,  -- MOB, BOSS, POLYMORPH, etc.
                difficulty TEXT,  -- TUTORIAL, NORMAL, ELITE, BOSS
                primary_school TEXT,  -- Dominant spell school
                is_school_focused BOOLEAN DEFAULT FALSE,
                is_boss_deck BOOLEAN DEFAULT FALSE,
                
                -- Behavior information
                has_behaviors BOOLEAN DEFAULT FALSE,
                behavior_count INTEGER DEFAULT 0,
                behaviors_json TEXT,  -- JSON array of behaviors (currently empty)
                
                -- Metadata
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                data_version INTEGER NOT NULL DEFAULT 1,
                
                -- Raw data for future analysis
                raw_data_json TEXT  -- Complete original JSON data
            )
        """)
        
        # Spell references table for normalized spell analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deck_spells (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                spell_name TEXT NOT NULL,
                position INTEGER NOT NULL,  -- Position in deck (0-based)
                spell_count INTEGER NOT NULL DEFAULT 1,  -- How many copies in deck
                
                FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE,
                UNIQUE(deck_id, spell_name, position)
            )
        """)
        
        # Spell summary table for quick analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spell_summary (
                spell_name TEXT PRIMARY KEY,
                total_occurrences INTEGER NOT NULL DEFAULT 0,
                deck_count INTEGER NOT NULL DEFAULT 0,  -- How many decks contain this spell
                avg_copies_per_deck REAL NOT NULL DEFAULT 0.0,
                estimated_school TEXT,  -- Based on name patterns
                is_blade BOOLEAN DEFAULT FALSE,
                is_shield BOOLEAN DEFAULT FALSE,
                is_trap BOOLEAN DEFAULT FALSE,
                is_global BOOLEAN DEFAULT FALSE,
                
                first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # School analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deck_school_analysis (
                deck_id INTEGER NOT NULL,
                school_name TEXT NOT NULL,
                spell_count INTEGER NOT NULL DEFAULT 0,
                percentage REAL NOT NULL DEFAULT 0.0,
                
                PRIMARY KEY (deck_id, school_name),
                FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
            )
        """)
        
        # Database metadata and versioning
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS database_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert initial metadata
        cursor.execute("""
            INSERT OR REPLACE INTO database_metadata (key, value, updated_at)
            VALUES 
                ('schema_version', ?, CURRENT_TIMESTAMP),
                ('created_by', 'DatabaseDemon Decks System', CURRENT_TIMESTAMP),
                ('database_type', 'wizard101_decks', CURRENT_TIMESTAMP)
        """, (str(self.SCHEMA_VERSION),))
        
        connection.commit()
        print("Database tables created successfully")
    
    def create_indexes(self, connection: sqlite3.Connection):
        """Create database indexes for efficient querying.
        
        Args:
            connection: SQLite database connection
        """
        cursor = connection.cursor()
        
        # Primary lookup indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_filename ON decks(filename)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_name ON decks(deck_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_type ON decks(deck_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_school ON decks(primary_school)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_difficulty ON decks(difficulty)")
        
        # Analysis indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_boss ON decks(is_boss_deck)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_focused ON decks(is_school_focused)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_spell_count ON decks(spell_count)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_behaviors ON decks(has_behaviors)")
        
        # Spell reference indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_spells_deck ON deck_spells(deck_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_spells_name ON deck_spells(spell_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_spells_position ON deck_spells(position)")
        
        # Spell summary indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_spell_summary_occurrences ON spell_summary(total_occurrences DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_spell_summary_deck_count ON spell_summary(deck_count DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_spell_summary_school ON spell_summary(estimated_school)")
        
        # School analysis indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_school_analysis_deck ON deck_school_analysis(deck_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_school_analysis_school ON deck_school_analysis(school_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_school_analysis_count ON deck_school_analysis(spell_count DESC)")
        
        connection.commit()
        print("Database indexes created successfully")
    
    def create_views(self, connection: sqlite3.Connection):
        """Create database views for common queries.
        
        Args:
            connection: SQLite database connection
        """
        cursor = connection.cursor()
        
        # Comprehensive deck summary view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS deck_summary AS
            SELECT 
                d.id,
                d.filename,
                d.deck_name,
                d.deck_type,
                d.difficulty,
                d.primary_school,
                d.spell_count,
                d.unique_spell_count,
                d.is_boss_deck,
                d.is_school_focused,
                d.has_behaviors,
                ROUND(CAST(d.unique_spell_count AS FLOAT) / d.spell_count * 100, 2) as diversity_percentage,
                d.created_at
            FROM decks d
            ORDER BY d.spell_count DESC
        """)
        
        # Top spells across all decks
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS top_spells AS
            SELECT 
                spell_name,
                total_occurrences,
                deck_count,
                ROUND(CAST(total_occurrences AS FLOAT) / deck_count, 2) as avg_copies_per_deck,
                estimated_school,
                ROUND(CAST(deck_count AS FLOAT) / (SELECT COUNT(*) FROM decks) * 100, 2) as deck_penetration_percent
            FROM spell_summary
            ORDER BY total_occurrences DESC
        """)
        
        # School distribution summary
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS school_distribution AS
            SELECT 
                school_name,
                COUNT(DISTINCT deck_id) as deck_count,
                SUM(spell_count) as total_spells,
                ROUND(AVG(spell_count), 2) as avg_spells_per_deck,
                ROUND(AVG(percentage), 2) as avg_percentage
            FROM deck_school_analysis
            WHERE spell_count > 0
            GROUP BY school_name
            ORDER BY deck_count DESC
        """)
        
        # Boss deck analysis
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS boss_deck_analysis AS
            SELECT 
                d.deck_name,
                d.primary_school,
                d.spell_count,
                d.unique_spell_count,
                GROUP_CONCAT(ds.spell_name, ', ') as top_5_spells
            FROM decks d
            LEFT JOIN (
                SELECT 
                    deck_id, 
                    spell_name,
                    ROW_NUMBER() OVER (PARTITION BY deck_id ORDER BY spell_count DESC) as rn
                FROM deck_spells
            ) ds ON d.id = ds.deck_id AND ds.rn <= 5
            WHERE d.is_boss_deck = TRUE
            GROUP BY d.id, d.deck_name, d.primary_school, d.spell_count, d.unique_spell_count
            ORDER BY d.spell_count DESC
        """)
        
        # Deck type summary
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS deck_type_summary AS
            SELECT 
                deck_type,
                COUNT(*) as deck_count,
                ROUND(AVG(spell_count), 2) as avg_spell_count,
                ROUND(AVG(unique_spell_count), 2) as avg_unique_spells,
                COUNT(CASE WHEN is_boss_deck THEN 1 END) as boss_decks,
                COUNT(CASE WHEN is_school_focused THEN 1 END) as school_focused_decks
            FROM decks
            WHERE deck_type IS NOT NULL
            GROUP BY deck_type
            ORDER BY deck_count DESC
        """)
        
        connection.commit()
        print("Database views created successfully")
    
    def setup_database(self) -> sqlite3.Connection:
        """Complete database setup with tables, indexes, and views.
        
        Returns:
            SQLite database connection
        """
        print(f"Setting up database: {self.db_path}")
        
        connection = sqlite3.connect(str(self.db_path))
        
        # Enable foreign key constraints
        connection.execute("PRAGMA foreign_keys = ON")
        
        # Set performance optimizations
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute("PRAGMA cache_size = -64000")  # 64MB cache
        connection.execute("PRAGMA temp_store = MEMORY")
        
        # Create schema components
        self.create_tables(connection)
        self.create_indexes(connection)
        self.create_views(connection)
        
        # Update metadata
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO database_metadata (key, value, updated_at)
            VALUES ('last_schema_update', ?, CURRENT_TIMESTAMP)
        """, (datetime.now().isoformat(),))
        connection.commit()
        
        print("Database setup complete")
        return connection
    
    def get_schema_version(self, connection: sqlite3.Connection) -> int:
        """Get current database schema version.
        
        Args:
            connection: SQLite database connection
            
        Returns:
            Schema version number
        """
        cursor = connection.cursor()
        cursor.execute("""
            SELECT value FROM database_metadata 
            WHERE key = 'schema_version'
        """)
        result = cursor.fetchone()
        return int(result[0]) if result else 0
    
    def needs_migration(self, connection: sqlite3.Connection) -> bool:
        """Check if database needs schema migration.
        
        Args:
            connection: SQLite database connection
            
        Returns:
            True if migration is needed
        """
        try:
            current_version = self.get_schema_version(connection)
            return current_version < self.SCHEMA_VERSION
        except:
            return True  # Assume migration needed if we can't determine version
    
    def get_table_info(self, connection: sqlite3.Connection) -> Dict[str, List[Dict[str, Any]]]:
        """Get detailed information about all tables.
        
        Args:
            connection: SQLite database connection
            
        Returns:
            Dictionary mapping table names to column information
        """
        cursor = connection.cursor()
        
        # Get all table names
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        table_info = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': bool(row[3]),
                    'default_value': row[4],
                    'pk': bool(row[5])
                })
            table_info[table] = columns
        
        return table_info
    
    def get_database_stats(self, connection: sqlite3.Connection) -> Dict[str, Any]:
        """Get comprehensive database statistics.
        
        Args:
            connection: SQLite database connection
            
        Returns:
            Dictionary containing database statistics
        """
        cursor = connection.cursor()
        
        stats = {}
        
        # Table row counts
        cursor.execute("SELECT COUNT(*) FROM decks")
        stats['total_decks'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM deck_spells")
        stats['total_spell_references'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM spell_summary")
        stats['unique_spells'] = cursor.fetchone()[0]
        
        # Deck statistics
        cursor.execute("SELECT AVG(spell_count), MIN(spell_count), MAX(spell_count) FROM decks")
        avg_spells, min_spells, max_spells = cursor.fetchone()
        stats['spell_count_stats'] = {
            'average': round(avg_spells, 2) if avg_spells else 0,
            'minimum': min_spells or 0,
            'maximum': max_spells or 0
        }
        
        # School distribution
        cursor.execute("""
            SELECT primary_school, COUNT(*) 
            FROM decks 
            WHERE primary_school IS NOT NULL 
            GROUP BY primary_school 
            ORDER BY COUNT(*) DESC
        """)
        stats['school_distribution'] = dict(cursor.fetchall())
        
        # Deck type distribution
        cursor.execute("""
            SELECT deck_type, COUNT(*) 
            FROM decks 
            WHERE deck_type IS NOT NULL 
            GROUP BY deck_type 
            ORDER BY COUNT(*) DESC
        """)
        stats['deck_type_distribution'] = dict(cursor.fetchall())
        
        # Database file size
        stats['database_size_bytes'] = self.db_path.stat().st_size if self.db_path.exists() else 0
        stats['database_size_mb'] = round(stats['database_size_bytes'] / (1024 * 1024), 2)
        
        return stats


def create_database(db_path: Path) -> sqlite3.Connection:
    """Convenience function to create a complete deck database.
    
    Args:
        db_path: Path where to create the database
        
    Returns:
        SQLite database connection
    """
    schema = DatabaseSchema(db_path)
    return schema.setup_database()


def get_database_info(db_path: Path) -> Dict[str, Any]:
    """Get comprehensive information about an existing database.
    
    Args:
        db_path: Path to existing database
        
    Returns:
        Dictionary containing database information
    """
    if not db_path.exists():
        return {'error': 'Database file does not exist'}
    
    try:
        schema = DatabaseSchema(db_path)
        connection = sqlite3.connect(str(db_path))
        
        info = {
            'schema_version': schema.get_schema_version(connection),
            'needs_migration': schema.needs_migration(connection),
            'table_info': schema.get_table_info(connection),
            'statistics': schema.get_database_stats(connection)
        }
        
        connection.close()
        return info
        
    except Exception as e:
        return {'error': f'Failed to read database info: {e}'}


if __name__ == "__main__":
    # Test database creation
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db = Path(temp_dir) / "test_decks.db"
        print(f"Creating test database: {test_db}")
        
        connection = create_database(test_db)
        
        # Test database info
        info = get_database_info(test_db)
        print(f"Database info: {info['statistics']}")
        
        connection.close()
        print("Test completed successfully")