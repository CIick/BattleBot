#!/usr/bin/env python3
"""
TemplateManifest Database Schema
===============================

SQLite database schema definition for TemplateManifest system.
Provides normalized schema for storing template ID to filename mappings
with optimized indexes for fast lookups.

Key features:
- Fast template ID to filename lookups
- Deck type and category classification
- Comprehensive indexing strategy
- Analysis views for common queries
- Schema versioning and migration support
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

# Schema version for migration tracking
SCHEMA_VERSION = 1


class TemplateManifestDatabaseSchema:
    """Manages database schema for TemplateManifest system"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize schema manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        
        if db_path:
            self.connection = sqlite3.connect(str(db_path))
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
    
    def create_schema(self) -> bool:
        """
        Create complete database schema
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            # Create tables
            self._create_metadata_table(cursor)
            self._create_template_locations_table(cursor)
            self._create_template_statistics_table(cursor)
            
            # Create indexes
            self._create_indexes(cursor)
            
            # Create views
            self._create_views(cursor)
            
            # Set schema version
            self._set_schema_version(cursor)
            
            self.connection.commit()
            print(f"[OK] Database schema created successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to create schema: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def _create_metadata_table(self, cursor: sqlite3.Cursor):
        """Create metadata table for schema versioning"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_template_locations_table(self, cursor: sqlite3.Cursor):
        """Create main template locations table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL UNIQUE,
                filename TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_directory TEXT NOT NULL,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Validation flags
                is_valid BOOLEAN DEFAULT TRUE
            )
        """)
    
    def _create_template_statistics_table(self, cursor: sqlite3.Cursor):
        """Create template statistics summary table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Counts
                total_templates INTEGER NOT NULL DEFAULT 0,
                valid_templates INTEGER NOT NULL DEFAULT 0,
                invalid_templates INTEGER NOT NULL DEFAULT 0,
                
                -- File type distribution (stored as JSON)
                file_type_distribution TEXT,
                
                -- Quality metrics
                validation_success_rate REAL NOT NULL DEFAULT 0.0,
                
                -- Processing metadata
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_version TEXT,
                source_file TEXT DEFAULT 'TemplateManifest.xml'
            )
        """)
    
    
    def _create_indexes(self, cursor: sqlite3.Cursor):
        """Create database indexes for optimal performance"""
        
        # Primary lookup indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_id ON template_locations(template_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_filename ON template_locations(filename)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_name ON template_locations(file_name)")
        
        # File type classification indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_type ON template_locations(file_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_directory ON template_locations(file_directory)")
        
        # Validation indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_valid_templates ON template_locations(is_valid)")
    
    def _create_views(self, cursor: sqlite3.Cursor):
        """Create database views for common queries"""
        
        # Template lookup view (main query interface)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS template_lookup AS
            SELECT 
                template_id,
                filename,
                file_name,
                file_type,
                file_directory
            FROM template_locations
            WHERE is_valid = TRUE
        """)
        
        # File type summary view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS file_type_summary AS
            SELECT 
                file_type,
                COUNT(*) as template_count,
                COUNT(CASE WHEN is_valid THEN 1 END) as valid_count,
                ROUND(AVG(CASE WHEN is_valid THEN 1.0 ELSE 0.0 END) * 100, 2) as valid_percentage
            FROM template_locations
            GROUP BY file_type
            ORDER BY template_count DESC
        """)
        
        # Template validation summary view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS validation_summary AS
            SELECT 
                COUNT(*) as total_templates,
                COUNT(CASE WHEN is_valid THEN 1 END) as valid_templates,
                COUNT(CASE WHEN NOT is_valid THEN 1 END) as invalid_templates,
                ROUND(AVG(CASE WHEN is_valid THEN 1.0 ELSE 0.0 END) * 100, 2) as validation_success_rate
            FROM template_locations
        """)
        
        # Deck files only view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS deck_files AS
            SELECT 
                template_id,
                filename,
                file_name
            FROM template_locations
            WHERE file_type = 'deck' AND is_valid = TRUE
        """)
    
    def _set_schema_version(self, cursor: sqlite3.Cursor):
        """Set schema version in metadata table"""
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES ('schema_version', ?, CURRENT_TIMESTAMP)
        """, (str(SCHEMA_VERSION),))
    
    def get_schema_version(self) -> int:
        """Get current schema version"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = 'schema_version'")
            result = cursor.fetchone()
            return int(result[0]) if result else 0
        except Exception:
            return 0
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate database schema completeness"""
        try:
            cursor = self.connection.cursor()
            
            # Check tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    'metadata', 'template_locations', 'template_statistics'
                )
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Check views exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='view' AND name IN (
                    'template_lookup', 'file_type_summary', 'validation_summary', 'deck_files'
                )
            """)
            views = [row[0] for row in cursor.fetchall()]
            
            # Check indexes exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            return {
                'valid': len(tables) == 3 and len(views) == 4,
                'tables': tables,
                'views': views,
                'indexes': indexes,
                'table_count': len(tables),
                'view_count': len(views),
                'index_count': len(indexes),
                'schema_version': self.get_schema_version()
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'tables': [],
                'views': [],
                'indexes': []
            }
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get detailed table information"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            return [
                {
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default_value': col[4],
                    'primary_key': bool(col[5])
                }
                for col in columns
            ]
        except Exception as e:
            print(f"[ERROR] Failed to get table info for {table_name}: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


def create_database_schema(db_path: Path) -> TemplateManifestDatabaseSchema:
    """
    Create and initialize database schema
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Initialized TemplateManifestDatabaseSchema
    """
    schema = TemplateManifestDatabaseSchema(db_path)
    
    if not schema.create_schema():
        raise RuntimeError(f"Failed to create database schema at {db_path}")
    
    return schema


# Export main classes
__all__ = [
    'TemplateManifestDatabaseSchema',
    'create_database_schema',
    'SCHEMA_VERSION'
]