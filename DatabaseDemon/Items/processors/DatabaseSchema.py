#!/usr/bin/env python3
"""
Wizard101 Items Database Schema Definition
==========================================
Database schema for Wizard101 item data with SQL Server compatibility.
Uses filename as PRIMARY KEY to prevent duplicates, with comprehensive
support for all nested item types including pets, mounts, housing, etc.
"""

from typing import Dict, List, Any


class ItemsDatabaseSchema:
    """Database schema definition for Wizard101 item data"""
    
    # SQLite schema (compatible with SQL Server migration)
    SCHEMA_SQL = {
        # Main item templates table - filename as PRIMARY KEY
        "item_templates": """
            CREATE TABLE item_templates (
                filename TEXT PRIMARY KEY,              -- "Helephant.xml"
                item_type TEXT NOT NULL,               -- "WizItemTemplate"
                m_templateID INTEGER,                  -- Unique item template ID
                m_objectName TEXT,                     -- Internal object name
                m_displayName TEXT,                    -- Display name for UI
                m_description TEXT,                    -- Item description
                m_visualID INTEGER,                    -- Visual appearance ID
                m_nObjectType INTEGER,                 -- Object type enumeration
                m_school TEXT,                         -- Magic school (Fire, Ice, etc.)
                m_rarity INTEGER,                      -- Rarity level (0-6)
                m_rank INTEGER,                        -- Item rank/level
                m_baseCost REAL,                       -- Base gold cost
                m_creditsCost REAL,                    -- Crowns cost
                m_arenaPointCost INTEGER,              -- Arena point cost
                m_pvpCurrencyCost INTEGER,             -- PvP currency cost
                m_pvpTourneyCurrencyCost INTEGER,      -- PvP tournament currency cost
                m_sIcon TEXT,                          -- Icon filename
                m_boyIconIndex INTEGER,                -- Boy character icon index
                m_girlIconIndex INTEGER,               -- Girl character icon index
                m_holidayFlag TEXT,                    -- Holiday restriction flag
                m_itemLimit INTEGER,                   -- Stack/inventory limit
                m_itemSetBonusTemplateID INTEGER,      -- Set bonus template ID
                m_exemptFromAOI INTEGER,               -- Boolean: exempt from AOI
                m_numPatterns INTEGER,                 -- Number of pattern options
                m_numPrimaryColors INTEGER,            -- Number of primary color options
                m_numSecondaryColors INTEGER,          -- Number of secondary color options
                m_adjectiveList TEXT,                  -- JSON array of adjectives
                m_avatarFlags TEXT,                    -- JSON array of avatar flags
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        
        # Item behaviors table - stores all behavior types
        "item_behaviors": """
            CREATE TABLE item_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                behavior_index INTEGER NOT NULL,      -- Order in the behaviors list
                behavior_type TEXT NOT NULL,          -- Type of behavior (RenderBehavior, etc.)
                behavior_name TEXT,                   -- m_behaviorName field
                behavior_data TEXT,                   -- JSON of all behavior-specific data
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Item equipment effects table - StatisticEffectInfo data
        "item_equip_effects": """
            CREATE TABLE item_equip_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                effect_index INTEGER NOT NULL,        -- Order in the equipEffects list
                m_effectName TEXT,                    -- Effect name (e.g., "CanonicalFireDamage")
                m_lookupIndex INTEGER,                -- Lookup index for effect
                m_effectValue REAL,                   -- Numeric effect value
                m_effectPercent REAL,                 -- Percentage effect value
                m_schoolName TEXT,                    -- School restriction for effect
                m_effectType INTEGER,                 -- Effect type enumeration
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Avatar customization options
        "item_avatar_options": """
            CREATE TABLE item_avatar_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                option_index INTEGER NOT NULL,        -- Order in the options list
                m_mesh TEXT,                          -- Mesh filename
                m_noMesh INTEGER,                     -- Boolean: no mesh flag
                m_geometry TEXT,                      -- Geometry specification
                m_conditionFlags TEXT,                -- JSON array of condition flags
                m_assetName TEXT,                     -- Asset name
                m_materialName TEXT,                  -- Material name
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Avatar texture options
        "item_avatar_textures": """
            CREATE TABLE item_avatar_textures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                texture_index INTEGER NOT NULL,       -- Order in the textureOptions list
                m_conditionFlags TEXT,                -- JSON array of condition flags (MALE/FEMALE)
                m_decals TEXT,                        -- JSON array of decal names
                m_decals2 TEXT,                       -- JSON array of secondary decals
                m_materialName TEXT,                  -- Material name
                m_textures TEXT,                      -- JSON array of texture paths
                m_tintColorNames TEXT,                -- JSON array of tint color names
                m_tintColors TEXT,                    -- JSON array of tint color values
                m_useTintColor INTEGER,               -- Boolean: use tint color
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Equipment requirements
        "item_requirements": """
            CREATE TABLE item_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                requirement_type TEXT NOT NULL,       -- Type of requirement (equip/purchase)
                requirement_index INTEGER NOT NULL,   -- Order in the requirements list
                req_class TEXT,                       -- Requirement class name
                m_applyNOT INTEGER,                   -- Boolean: apply NOT logic
                m_operator INTEGER,                   -- Operator type
                requirement_data TEXT,                -- JSON of requirement-specific data
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Pet-specific data
        "item_pet_data": """
            CREATE TABLE item_pet_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                m_conversionLevel INTEGER,            -- Pet conversion level
                m_conversionXP INTEGER,               -- Conversion XP requirement
                m_eGender INTEGER,                    -- Pet gender
                m_eRace INTEGER,                      -- Pet race
                m_eggColor INTEGER,                   -- Egg color
                m_eggName TEXT,                       -- Egg name
                m_excludeFromHatchOfTheDay INTEGER,   -- Boolean: exclude from hatch of day
                m_exclusivePet INTEGER,               -- Boolean: exclusive pet
                m_fScale REAL,                        -- Pet scale factor
                m_favoriteSnackCategories TEXT,       -- JSON array of snack categories
                m_flyingOffset REAL,                  -- Flying animation offset
                m_hatchesAsID INTEGER,                -- Hatches as template ID
                m_hatchmakingInitalCooldownTime INTEGER, -- Initial cooldown time
                m_hatchmakingMaximumHatches INTEGER,  -- Maximum hatches allowed
                m_hideName INTEGER,                   -- Boolean: hide pet name
                m_houseGuestOpacity REAL,             -- House guest opacity
                m_sHatchRate TEXT,                    -- Hatch rate string
                m_wowFactor INTEGER,                  -- Pet wow factor
                m_duckSound TEXT,                     -- Duck sound effect
                m_jumpSound TEXT,                     -- Jump sound effect
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Pet level progression
        "item_pet_levels": """
            CREATE TABLE item_pet_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                m_level INTEGER NOT NULL,             -- Pet level
                m_lootTable TEXT,                     -- JSON array of loot table names
                m_powerCardCount INTEGER,             -- Number of power cards
                m_powerCardName TEXT,                 -- Primary power card name
                m_powerCardName2 TEXT,                -- Secondary power card name
                m_powerCardName3 TEXT,                -- Tertiary power card name
                m_requiredXP INTEGER,                 -- XP required for this level
                m_template INTEGER,                   -- Template type
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Pet statistics (start, max, conversion stats)
        "item_pet_stats": """
            CREATE TABLE item_pet_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                stat_type TEXT NOT NULL,              -- Type: start/max/conversion
                m_name TEXT,                          -- Stat name (Strength, Will, etc.)
                m_statID INTEGER,                     -- Stat ID
                m_value INTEGER,                      -- Stat value
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Pet talents and derby talents
        "item_pet_talents": """
            CREATE TABLE item_pet_talents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                talent_type TEXT NOT NULL,            -- Type: talent/derby/guaranteed/conversion
                talent_name TEXT,                     -- Talent name
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Pet morphing exceptions
        "item_pet_morphing": """
            CREATE TABLE item_pet_morphing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                m_eggTemplateID INTEGER,              -- Egg template ID
                m_probability REAL,                   -- Morphing probability
                m_secondPetTemplateID INTEGER,        -- Second pet template ID
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Pet dye to texture mappings
        "item_pet_dyes": """
            CREATE TABLE item_pet_dyes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                dye_type TEXT NOT NULL,               -- Type: pattern/primary/secondary
                m_dye INTEGER,                        -- Dye color ID
                m_texture INTEGER,                    -- Texture ID
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Mount-specific data
        "item_mount_data": """
            CREATE TABLE item_mount_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                m_conversionLevel INTEGER,            -- Mount conversion level
                m_eGender INTEGER,                    -- Mount gender
                m_eRace INTEGER,                      -- Mount race
                m_fScale REAL,                        -- Mount scale factor
                m_flyingOffset REAL,                  -- Flying animation offset
                m_hideName INTEGER,                   -- Boolean: hide mount name
                m_houseGuestOpacity REAL,             -- House guest opacity
                m_maxSpeed REAL,                      -- Maximum mount speed
                m_mountType TEXT,                     -- Mount type (Ground, Flying, etc.)
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Mount dye to texture mappings
        "item_mount_dyes": """
            CREATE TABLE item_mount_dyes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                dye_type TEXT NOT NULL,               -- Type: pattern/primary/secondary
                m_dye INTEGER,                        -- Dye color ID
                m_texture INTEGER,                    -- Texture ID
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Mount talents
        "item_mount_talents": """
            CREATE TABLE item_mount_talents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                talent_type TEXT NOT NULL,            -- Type: talent/guaranteed/conversion
                talent_name TEXT,                     -- Talent name
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Jewel socket data
        "item_jewel_sockets": """
            CREATE TABLE item_jewel_sockets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                socket_index INTEGER NOT NULL,        -- Order in the sockets list
                m_bLockable INTEGER,                  -- Boolean: socket can be locked
                m_socketType INTEGER,                 -- Socket type (Circle, Square, etc.)
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Housing furniture properties
        "item_furniture_data": """
            CREATE TABLE item_furniture_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,               -- Foreign key to item_templates
                m_bounce INTEGER,                     -- Boolean: bounce animation
                m_cameraOffsetX REAL,                 -- Camera X offset
                m_cameraOffsetY REAL,                 -- Camera Y offset
                m_cameraOffsetZ REAL,                 -- Camera Z offset
                m_pitch REAL,                         -- Pitch rotation
                m_roll REAL,                          -- Roll rotation
                m_rotate INTEGER,                     -- Boolean: allow rotation
                m_textureFilename TEXT,               -- Texture filename
                m_textureIndex INTEGER,               -- Texture index
                m_yaw REAL,                           -- Yaw rotation
                FOREIGN KEY (filename) REFERENCES item_templates(filename)
            )
        """,
        
        # Processing statistics table
        "item_processing_stats": """
            CREATE TABLE item_processing_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_files_processed INTEGER,
                total_items_found INTEGER,
                total_behaviors_processed INTEGER,
                total_effects_processed INTEGER,
                total_requirements_processed INTEGER,
                total_pet_items INTEGER,
                total_mount_items INTEGER,
                total_housing_items INTEGER,
                total_equipment_items INTEGER,
                processing_duration_seconds REAL,
                success_rate REAL
            )
        """
    }
    
    # Index definitions for performance
    INDEX_SQL = {
        "idx_item_behaviors_filename": "CREATE INDEX idx_item_behaviors_filename ON item_behaviors(filename)",
        "idx_item_behaviors_type": "CREATE INDEX idx_item_behaviors_type ON item_behaviors(behavior_type)",
        "idx_item_equip_effects_filename": "CREATE INDEX idx_item_equip_effects_filename ON item_equip_effects(filename)",
        "idx_item_equip_effects_name": "CREATE INDEX idx_item_equip_effects_name ON item_equip_effects(m_effectName)",
        "idx_item_templates_school": "CREATE INDEX idx_item_templates_school ON item_templates(m_school)",
        "idx_item_templates_rarity": "CREATE INDEX idx_item_templates_rarity ON item_templates(m_rarity)",
        "idx_item_templates_object_type": "CREATE INDEX idx_item_templates_object_type ON item_templates(m_nObjectType)",
        "idx_item_requirements_filename": "CREATE INDEX idx_item_requirements_filename ON item_requirements(filename)",
        "idx_item_pet_data_filename": "CREATE INDEX idx_item_pet_data_filename ON item_pet_data(filename)",
        "idx_item_mount_data_filename": "CREATE INDEX idx_item_mount_data_filename ON item_mount_data(filename)",
        "idx_item_jewel_sockets_filename": "CREATE INDEX idx_item_jewel_sockets_filename ON item_jewel_sockets(filename)"
    }
    
    @classmethod
    def get_create_table_statements(cls) -> List[str]:
        """Get all CREATE TABLE statements in dependency order"""
        return [
            cls.SCHEMA_SQL["item_templates"],
            cls.SCHEMA_SQL["item_behaviors"],
            cls.SCHEMA_SQL["item_equip_effects"],
            cls.SCHEMA_SQL["item_avatar_options"],
            cls.SCHEMA_SQL["item_avatar_textures"],
            cls.SCHEMA_SQL["item_requirements"],
            cls.SCHEMA_SQL["item_pet_data"],
            cls.SCHEMA_SQL["item_pet_levels"],
            cls.SCHEMA_SQL["item_pet_stats"],
            cls.SCHEMA_SQL["item_pet_talents"],
            cls.SCHEMA_SQL["item_pet_morphing"],
            cls.SCHEMA_SQL["item_pet_dyes"],
            cls.SCHEMA_SQL["item_mount_data"],
            cls.SCHEMA_SQL["item_mount_dyes"],
            cls.SCHEMA_SQL["item_mount_talents"],
            cls.SCHEMA_SQL["item_jewel_sockets"],
            cls.SCHEMA_SQL["item_furniture_data"],
            cls.SCHEMA_SQL["item_processing_stats"]
        ]
    
    @classmethod
    def get_create_index_statements(cls) -> List[str]:
        """Get all CREATE INDEX statements"""
        return list(cls.INDEX_SQL.values())
    
    @classmethod
    def get_table_names(cls) -> List[str]:
        """Get list of all table names"""
        return list(cls.SCHEMA_SQL.keys())
    
    @classmethod
    def get_drop_table_statements(cls) -> List[str]:
        """Get DROP TABLE statements in reverse dependency order"""
        table_names = cls.get_table_names()
        table_names.reverse()  # Drop in reverse order to handle foreign keys
        return [f"DROP TABLE IF EXISTS {table}" for table in table_names]