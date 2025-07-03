"""
Mob Database Schema
==================
Database table definitions for Wizard101 mob data storage.
"""

from typing import Dict


class MobDatabaseSchema:
    """Database schema definitions for mob data"""
    
    # Main database schema with all mob-related tables
    MOB_SCHEMA: Dict[str, str] = {
        
        # Main mob templates table
        "mob_templates": """
            CREATE TABLE mob_templates (
                template_id INTEGER PRIMARY KEY,
                object_name TEXT UNIQUE NOT NULL,
                display_name TEXT,
                description TEXT,
                visual_id INTEGER DEFAULT 0,
                object_type INTEGER DEFAULT 0,
                primary_school_name TEXT,
                aggro_sound TEXT,
                cast_sound TEXT,
                death_sound TEXT,
                hit_sound TEXT,
                death_particles TEXT,
                icon_path TEXT,
                exempt_from_aoi INTEGER DEFAULT 0,
                location_preference TEXT,
                leash_offset_override TEXT,
                type_hash INTEGER DEFAULT 701229577,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        
        # Mob adjectives lookup table
        "mob_adjectives": """
            CREATE TABLE mob_adjectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                adjective TEXT NOT NULL,
                adjective_order INTEGER DEFAULT 0,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                UNIQUE(template_id, adjective)
            )
        """,
        
        # Mob loot tables
        "mob_loot_tables": """
            CREATE TABLE mob_loot_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                loot_table_name TEXT NOT NULL,
                loot_order INTEGER DEFAULT 0,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                UNIQUE(template_id, loot_table_name, loot_order)
            )
        """,
        
        # Mob behaviors (normalized storage)
        "mob_behaviors": """
            CREATE TABLE mob_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_name TEXT NOT NULL,
                behavior_type_hash INTEGER NOT NULL,
                behavior_order INTEGER DEFAULT 0,
                behavior_data TEXT,  -- JSON storage for complex behavior data
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE
            )
        """,
        
        # Animation behaviors (detailed table)
        "mob_animation_behaviors": """
            CREATE TABLE mob_animation_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                animation_asset_name TEXT,
                asset_name TEXT,
                casts_shadow INTEGER DEFAULT 1,
                fades_in INTEGER DEFAULT 1,
                fades_out INTEGER DEFAULT 1,
                portal_excluded INTEGER DEFAULT 0,
                static_object INTEGER DEFAULT 0,
                data_lookup_asset_name TEXT,
                height REAL DEFAULT 0.0,
                idle_animation_name TEXT,
                movement_scale REAL DEFAULT 1.0,
                light_type INTEGER DEFAULT 1,
                opacity REAL DEFAULT 1.0,
                proxy_name TEXT,
                scale_value REAL DEFAULT 1.0,
                skeleton_id INTEGER DEFAULT 0,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # NPC behaviors (detailed table)
        "mob_npc_behaviors": """
            CREATE TABLE mob_npc_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                boss_mob INTEGER DEFAULT 0,
                cylinder_scale_value REAL DEFAULT 1.0,
                intelligence REAL DEFAULT 0.8,
                selfish_factor REAL DEFAULT 0.8,
                max_shadow_pips INTEGER DEFAULT 0,
                mob_title INTEGER DEFAULT 1,
                aggressive_factor INTEGER DEFAULT 8,
                level INTEGER DEFAULT 1,
                starting_health INTEGER DEFAULT 100,
                name_color TEXT,  -- Converted from Color object
                school_of_focus TEXT,
                secondary_school_of_focus TEXT,
                trigger_list TEXT,
                turn_towards_player INTEGER DEFAULT 1,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # Equipment behaviors
        "mob_equipment_behaviors": """
            CREATE TABLE mob_equipment_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                equipment_template TEXT,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # Equipment items (for WizardEquipmentBehavior)
        "mob_equipment_items": """
            CREATE TABLE mob_equipment_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                equipment_behavior_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                item_order INTEGER DEFAULT 0,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (equipment_behavior_id) REFERENCES mob_equipment_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # Path behaviors
        "mob_path_behaviors": """
            CREATE TABLE mob_path_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                path_type INTEGER DEFAULT 0,
                path_direction INTEGER DEFAULT 1,
                path_id INTEGER DEFAULT 0,
                pause_chance INTEGER DEFAULT 0,
                time_to_pause REAL DEFAULT 0.0,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # Path movement behaviors
        "mob_path_movement_behaviors": """
            CREATE TABLE mob_path_movement_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                movement_scale REAL DEFAULT 1.0,
                movement_speed REAL DEFAULT 133.0,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # Duelist behaviors
        "mob_duelist_behaviors": """
            CREATE TABLE mob_duelist_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                npc_proximity REAL DEFAULT 350.0,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # Collision behaviors
        "mob_collision_behaviors": """
            CREATE TABLE mob_collision_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                auto_click_box INTEGER DEFAULT 1,
                client_only INTEGER DEFAULT 0,
                disable_collision INTEGER DEFAULT 0,
                solid_collision_filename TEXT,
                walkable_collision_filename TEXT,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # Monster magic behaviors
        "mob_monster_magic_behaviors": """
            CREATE TABLE mob_monster_magic_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                alternate_mob_template_id INTEGER DEFAULT 0,
                collected_as_template_id INTEGER DEFAULT 0,
                collection_resistance INTEGER DEFAULT 0,
                essences_per_house_guest INTEGER DEFAULT 20,
                essences_per_kill_tc INTEGER DEFAULT 15,
                essences_per_summon_tc INTEGER DEFAULT 10,
                gold_per_house_guest INTEGER DEFAULT 1500,
                gold_per_kill_tc INTEGER DEFAULT 2000,
                gold_per_summon_tc INTEGER DEFAULT 500,
                house_guest_template_id INTEGER DEFAULT 0,
                is_boss INTEGER DEFAULT 0,
                world_name TEXT,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """,
        
        # Object state behaviors
        "mob_object_state_behaviors": """
            CREATE TABLE mob_object_state_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                behavior_id INTEGER NOT NULL,
                state_set_name TEXT,
                
                FOREIGN KEY (template_id) REFERENCES mob_templates(template_id) ON DELETE CASCADE,
                FOREIGN KEY (behavior_id) REFERENCES mob_behaviors(id) ON DELETE CASCADE
            )
        """
    }
    
    # Indexes for better query performance
    MOB_INDEXES: Dict[str, str] = {
        "idx_mob_templates_object_name": "CREATE INDEX idx_mob_templates_object_name ON mob_templates(object_name)",
        "idx_mob_templates_display_name": "CREATE INDEX idx_mob_templates_display_name ON mob_templates(display_name)",
        "idx_mob_templates_school": "CREATE INDEX idx_mob_templates_school ON mob_templates(primary_school_name)",
        "idx_mob_adjectives_template": "CREATE INDEX idx_mob_adjectives_template ON mob_adjectives(template_id)",
        "idx_mob_loot_template": "CREATE INDEX idx_mob_loot_template ON mob_loot_tables(template_id)",
        "idx_mob_behaviors_template": "CREATE INDEX idx_mob_behaviors_template ON mob_behaviors(template_id)",
        "idx_mob_behaviors_type": "CREATE INDEX idx_mob_behaviors_type ON mob_behaviors(behavior_type_hash)",
        "idx_mob_npc_level": "CREATE INDEX idx_mob_npc_level ON mob_npc_behaviors(level)",
        "idx_mob_npc_health": "CREATE INDEX idx_mob_npc_health ON mob_npc_behaviors(starting_health)",
        "idx_mob_npc_school": "CREATE INDEX idx_mob_npc_school ON mob_npc_behaviors(school_of_focus)",
    }
    
    @classmethod
    def get_create_table_statements(cls) -> Dict[str, str]:
        """Get all CREATE TABLE statements"""
        return cls.MOB_SCHEMA.copy()
    
    @classmethod
    def get_create_index_statements(cls) -> Dict[str, str]:
        """Get all CREATE INDEX statements"""
        return cls.MOB_INDEXES.copy()
    
    @classmethod
    def get_table_names(cls) -> list:
        """Get list of all table names"""
        return list(cls.MOB_SCHEMA.keys())