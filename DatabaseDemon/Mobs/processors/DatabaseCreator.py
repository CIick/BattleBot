#!/usr/bin/env python3
"""
Wizard101 Mob Database Creator
=============================
Creates and populates SQLite database with Wizard101 mob data from ObjectData files.
Handles WizGameObjectTemplate processing with comprehensive behavior relationship management.
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import traceback

from .DatabaseSchema import MobDatabaseSchema

# Add parent directories to Python path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))  # DatabaseDemon level
sys.path.append(str(Path(__file__).parent.parent))         # Mobs level

from utils.conversion_utils import convert_lazy_object_to_dict_with_hash_only

# Import mob DTOs
from dtos import MobsDTOFactory
from dtos.MobsDTO import *


class MobDatabaseCreator:
    """Creates and manages the Wizard101 mob database"""
    
    def __init__(self, database_path: Optional[Path] = None, 
                 failed_mobs_dir: Optional[Path] = None):
        """
        Initialize the mob database creator
        
        Args:
            database_path: Path for the database file (auto-generated if None)
            failed_mobs_dir: Directory for failed mob analysis (auto-detected if None)
        """
        self.database_path = database_path
        self.failed_mobs_dir = failed_mobs_dir
        self.connection = None
        self.cursor = None
        
        # Statistics
        self.total_processed = 0
        self.total_success = 0
        self.total_failures = 0
        self.duplicate_count = 0
        self.processing_start_time = None
        self.processing_end_time = None
        
        # Error tracking
        self.duplicate_files = []
        self.failed_files = []
        
        # Skipped element tracking
        self.skipped_elements = {}  # {filename: {element_path: (element_type, reason, data)}}
        self.unhandled_fields = {}  # {filename: {field_name: value}}
        self.skipped_element_types = {}  # {element_type: count}
        self.total_skipped_elements = 0
        
        # Auto-detect paths if not provided
        if not self.database_path:
            self._auto_detect_database_path()
        if not self.failed_mobs_dir:
            self._auto_detect_failed_mobs_dir()
    
    def _auto_detect_database_path(self):
        """Auto-detect database path based on revision"""
        # For now, use a simple naming scheme - can enhance with revision detection later
        database_name = f"mob_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        self.database_path = Path("database") / database_name
    
    def _auto_detect_failed_mobs_dir(self):
        """Auto-detect failed mobs directory"""
        self.failed_mobs_dir = Path("failed_mobs")
    
    def initialize(self) -> bool:
        """
        Initialize the mob database creator
        
        Returns:
            True if initialization successful, False otherwise
        """
        print("Initializing Mob Database Creator...")
        
        # Create directories
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.failed_mobs_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[OK] Database path: {self.database_path}")
        print(f"[OK] Failed mobs directory: {self.failed_mobs_dir}")
        
        return True
    
    def create_database(self) -> bool:
        """
        Create the mob database with all necessary tables
        
        Returns:
            True if database creation successful, False otherwise
        """
        try:
            print(f"Creating mob database: {self.database_path}")
            
            # Connect to database
            self.connection = sqlite3.connect(str(self.database_path))
            self.cursor = self.connection.cursor()
            
            # Create all tables
            schema = MobDatabaseSchema.get_create_table_statements()
            for table_name, create_sql in schema.items():
                print(f"Creating table: {table_name}")
                self.cursor.execute(create_sql)
            
            # Create indexes
            indexes = MobDatabaseSchema.get_create_index_statements()
            for index_name, index_sql in indexes.items():
                print(f"Creating index: {index_name}")
                self.cursor.execute(index_sql)
            
            self.connection.commit()
            print("[OK] Database created successfully")
            return True
            
        except Exception as e:
            print(f"Error creating database: {e}")
            traceback.print_exc()
            return False
    
    def process_all_mobs(self, wad_path: Path, types_path: Path) -> bool:
        """
        Process all mobs from ObjectData files
        
        Args:
            wad_path: Path to Root.wad file
            types_path: Path to types.json file
            
        Returns:
            True if processing successful, False otherwise
        """
        try:
            print("Starting mob processing...")
            self.processing_start_time = datetime.now()
            
            # Import required classes here to avoid circular imports
            from katsuba.wad import Archive
            from katsuba.op import LazyObject, LazyList, TypeList, Serializer, SerializerOptions
            
            # Open WAD archive
            try:
                archive = Archive.mmap(str(wad_path))
                print(f"[OK] Opened WAD archive: {wad_path}")
            except Exception:
                archive = Archive.heap(str(wad_path))
                print(f"[OK] Opened WAD archive (heap): {wad_path}")
            
            # Load type list
            type_list = TypeList.open(str(types_path))
            print(f"[OK] Loaded type definitions: {types_path}")
            
            # Create serializer with proper options
            options = SerializerOptions()
            options.shallow = False  # Allow deep serialization
            options.skip_unknown_types = True  # Skip unknown server types
            serializer = Serializer(options, type_list)
            print("[OK] Created serializer with deep serialization and skip_unknown_types")
            
            # Find all ObjectData XML files
            object_files = list(archive.iter_glob("ObjectData/**/*.xml"))
            total_files = len(object_files)
            print(f"Found {total_files} XML files in ObjectData")
            
            # Process files in batches for better performance
            batch_size = 1000
            processed_count = 0
            
            for i in range(0, len(object_files), batch_size):
                batch_files = object_files[i:i + batch_size]
                
                # Begin transaction for this batch
                self.cursor.execute("BEGIN TRANSACTION")
                
                try:
                    for file_path in batch_files:
                        self._process_single_object_file(archive, serializer, type_list, file_path)
                        processed_count += 1
                        
                        # Progress reporting
                        if processed_count % 5000 == 0:
                            print(f"[PROGRESS] Processed {processed_count}/{total_files} files, "
                                  f"{self.total_success} mobs found, {self.total_failures} failures")
                    
                    # Commit batch
                    self.connection.commit()
                    
                except Exception as e:
                    # Rollback batch on error
                    self.connection.rollback()
                    print(f"Error processing batch starting at {i}: {e}")
                    traceback.print_exc()
            
            self.processing_end_time = datetime.now()
            self._generate_final_report()
            return True
            
        except Exception as e:
            print(f"Fatal error during mob processing: {e}")
            traceback.print_exc()
            return False
    
    def _process_single_object_file(self, archive, serializer, type_list, file_path: str):
        """Process a single ObjectData file"""
        try:
            self.total_processed += 1
            
            # Deserialize the object data
            object_data = archive.deserialize(file_path, serializer)
            
            # Convert to dictionary format (use hash-only to preserve integer type hashes)
            if hasattr(object_data, 'type_hash'):
                obj_dict = convert_lazy_object_to_dict_with_hash_only(object_data, type_list)
            else:
                obj_dict = object_data
            
            # Check for conversion errors
            if isinstance(obj_dict, dict) and "error" in obj_dict:
                self._log_processing_failure(file_path, obj_dict, "Conversion error")
                return
            
            # Check if this is a WizGameObjectTemplate (mob)
            obj_type = obj_dict.get('$__type')
            if obj_type != 701229577:  # Not a mob
                return
            
            # Try to create mob DTO
            mob_dto = MobsDTOFactory.create_from_json_data(obj_dict)
            if not mob_dto:
                self._log_processing_failure(file_path, obj_dict, "Failed to create mob DTO")
                return
            
            # Process the mob
            success = self._process_single_mob(file_path, obj_dict, mob_dto)
            if success:
                self.total_success += 1
            else:
                self.total_failures += 1
                
        except Exception as e:
            self._log_processing_failure(file_path, {"error": str(e)}, f"Exception: {e}")
            self.total_failures += 1
    
    def _process_single_mob(self, file_path: str, mob_dict: Dict[str, Any], mob_dto: WizGameObjectTemplateDTO) -> bool:
        """
        Process a single mob and insert into database
        
        Args:
            file_path: Path to the mob file
            mob_dict: Raw mob dictionary data
            mob_dto: Mob DTO instance
            
        Returns:
            True if processing successful, False otherwise
        """
        try:
            # Check for duplicates
            if self._is_duplicate_mob(mob_dto):
                self.duplicate_count += 1
                self.duplicate_files.append(file_path)
                return True  # Count as success but skip processing
            
            # Insert mob template
            template_id = self._insert_mob_template(mob_dto)
            if not template_id:
                return False
            
            # Process adjectives
            if mob_dto.m_adjectiveList:
                self._insert_mob_adjectives(template_id, mob_dto.m_adjectiveList)
            
            # Process loot tables
            if mob_dto.m_lootTable:
                self._insert_mob_loot_tables(template_id, mob_dto.m_lootTable)
            
            # Process behaviors
            if mob_dto.m_behaviors:
                self._insert_mob_behaviors(template_id, mob_dto.m_behaviors)
            
            return True
            
        except Exception as e:
            self._log_processing_failure(file_path, mob_dict, f"Database insertion error: {e}")
            return False
    
    def _is_duplicate_mob(self, mob_dto: WizGameObjectTemplateDTO) -> bool:
        """Check if mob already exists in database"""
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM mob_templates WHERE object_name = ?",
                (mob_dto.m_objectName,)
            )
            count = self.cursor.fetchone()[0]
            return count > 0
        except Exception:
            return False
    
    def _insert_mob_template(self, mob_dto: WizGameObjectTemplateDTO) -> Optional[int]:
        """Insert mob template and return template_id"""
        try:
            insert_sql = """
                INSERT INTO mob_templates (
                    template_id, object_name, display_name, description, visual_id,
                    object_type, primary_school_name, aggro_sound, cast_sound,
                    death_sound, hit_sound, death_particles, icon_path,
                    exempt_from_aoi, location_preference, leash_offset_override,
                    type_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                mob_dto.m_templateID,
                mob_dto.m_objectName,
                mob_dto.m_displayName,
                mob_dto.m_description,
                mob_dto.m_visualID,
                mob_dto.m_nObjectType,
                mob_dto.m_primarySchoolName,
                mob_dto.m_aggroSound,
                mob_dto.m_castSound,
                mob_dto.m_deathSound,
                mob_dto.m_hitSound,
                mob_dto.m_deathParticles,
                mob_dto.m_sIcon,
                1 if mob_dto.m_exemptFromAOI else 0,
                mob_dto.m_locationPreference,
                str(mob_dto.m_leashOffsetOverride) if mob_dto.m_leashOffsetOverride else None,
                mob_dto.type_hash
            )
            
            self.cursor.execute(insert_sql, values)
            return mob_dto.m_templateID
            
        except Exception as e:
            print(f"Error inserting mob template: {e}")
            return None
    
    def _insert_mob_adjectives(self, template_id: int, adjectives: List[str]):
        """Insert mob adjectives"""
        try:
            for i, adjective in enumerate(adjectives):
                self.cursor.execute(
                    "INSERT INTO mob_adjectives (template_id, adjective, adjective_order) VALUES (?, ?, ?)",
                    (template_id, adjective, i)
                )
        except Exception as e:
            print(f"Error inserting mob adjectives: {e}")
    
    def _insert_mob_loot_tables(self, template_id: int, loot_tables: List[str]):
        """Insert mob loot tables"""
        try:
            for i, loot_table in enumerate(loot_tables):
                self.cursor.execute(
                    "INSERT INTO mob_loot_tables (template_id, loot_table_name, loot_order) VALUES (?, ?, ?)",
                    (template_id, loot_table, i)
                )
        except Exception as e:
            print(f"Error inserting mob loot tables: {e}")
    
    def _insert_mob_behaviors(self, template_id: int, behaviors: List[Any]):
        """Insert mob behaviors and handle specialized behavior tables"""
        try:
            for i, behavior in enumerate(behaviors):
                if behavior is None:
                    continue
                
                # Insert into generic mob_behaviors table
                behavior_id = self._insert_generic_behavior(template_id, behavior, i)
                
                if behavior_id and hasattr(behavior, '__class__'):
                    # Insert into specialized tables based on behavior type
                    if isinstance(behavior, NPCBehaviorDTO):
                        self._insert_npc_behavior(template_id, behavior_id, behavior)
                    elif isinstance(behavior, AnimationBehaviorDTO):
                        self._insert_animation_behavior(template_id, behavior_id, behavior)
                    elif isinstance(behavior, WizardEquipmentBehaviorDTO):
                        self._insert_equipment_behavior(template_id, behavior_id, behavior)
                    elif isinstance(behavior, PathBehaviorDTO):
                        self._insert_path_behavior(template_id, behavior_id, behavior)
                    elif isinstance(behavior, PathMovementBehaviorDTO):
                        self._insert_path_movement_behavior(template_id, behavior_id, behavior)
                    elif isinstance(behavior, DuelistBehaviorDTO):
                        self._insert_duelist_behavior(template_id, behavior_id, behavior)
                    elif isinstance(behavior, CollisionBehaviorDTO):
                        self._insert_collision_behavior(template_id, behavior_id, behavior)
                    elif isinstance(behavior, MobMonsterMagicBehaviorDTO):
                        self._insert_monster_magic_behavior(template_id, behavior_id, behavior)
                    elif isinstance(behavior, BasicObjectStateBehaviorDTO):
                        self._insert_object_state_behavior(template_id, behavior_id, behavior)
                
        except Exception as e:
            print(f"Error inserting mob behaviors: {e}")
    
    def _insert_generic_behavior(self, template_id: int, behavior: Any, order: int) -> Optional[int]:
        """Insert into generic mob_behaviors table and return behavior_id"""
        try:
            behavior_name = getattr(behavior, 'm_behaviorName', 'Unknown')
            
            # Get behavior type hash by mapping class type to hash
            behavior_type_hash = 0
            if hasattr(behavior, '__class__'):
                behavior_class = behavior.__class__
                # Reverse lookup in factory mappings to find the hash
                for hash_value, dto_class in MobsDTOFactory.BEHAVIOR_TYPE_MAPPINGS.items():
                    if dto_class == behavior_class:
                        behavior_type_hash = hash_value
                        break
            
            behavior_data = json.dumps(behavior.__dict__ if hasattr(behavior, '__dict__') else str(behavior))
            
            self.cursor.execute("""
                INSERT INTO mob_behaviors (template_id, behavior_name, behavior_type_hash, behavior_order, behavior_data)
                VALUES (?, ?, ?, ?, ?)
            """, (template_id, behavior_name, behavior_type_hash, order, behavior_data))
            
            return self.cursor.lastrowid
            
        except Exception as e:
            print(f"Error inserting generic behavior: {e}")
            return None
    
    def _insert_npc_behavior(self, template_id: int, behavior_id: int, npc_dto: NPCBehaviorDTO):
        """Insert NPC behavior details"""
        try:
            self.cursor.execute("""
                INSERT INTO mob_npc_behaviors (
                    template_id, behavior_id, boss_mob, cylinder_scale_value, intelligence,
                    selfish_factor, max_shadow_pips, mob_title, aggressive_factor, level,
                    starting_health, name_color, school_of_focus, secondary_school_of_focus,
                    trigger_list, turn_towards_player
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_id, behavior_id,
                1 if npc_dto.m_bossMob else 0,
                npc_dto.m_cylinderScaleValue,
                npc_dto.m_fIntelligence,
                npc_dto.m_fSelfishFactor,
                npc_dto.m_maxShadowPips,
                npc_dto.m_mobTitle,
                npc_dto.m_nAggressiveFactor,
                npc_dto.m_nLevel,
                npc_dto.m_nStartingHealth,
                npc_dto.m_nameColor,
                npc_dto.m_schoolOfFocus,
                npc_dto.m_secondarySchoolOfFocus,
                npc_dto.m_triggerList,
                1 if npc_dto.m_turnTowardsPlayer else 0
            ))
        except Exception as e:
            print(f"Error inserting NPC behavior: {e}")
    
    def _insert_animation_behavior(self, template_id: int, behavior_id: int, anim_dto: AnimationBehaviorDTO):
        """Insert Animation behavior details"""
        try:
            self.cursor.execute("""
                INSERT INTO mob_animation_behaviors (
                    template_id, behavior_id, animation_asset_name, asset_name, casts_shadow,
                    fades_in, fades_out, portal_excluded, static_object, data_lookup_asset_name,
                    height, idle_animation_name, movement_scale, light_type, opacity,
                    proxy_name, scale_value, skeleton_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_id, behavior_id,
                anim_dto.m_animationAssetName,
                anim_dto.m_assetName,
                1 if anim_dto.m_bCastsShadow else 0,
                1 if anim_dto.m_bFadesIn else 0,
                1 if anim_dto.m_bFadesOut else 0,
                1 if anim_dto.m_bPortalExcluded else 0,
                1 if anim_dto.m_bStaticObject else 0,
                anim_dto.m_dataLookupAssetName,
                anim_dto.m_height,
                anim_dto.m_idleAnimationName,
                anim_dto.m_movementScale,
                anim_dto.m_nLightType,
                anim_dto.m_opacity,
                anim_dto.m_proxyName,
                anim_dto.m_scale,
                anim_dto.m_skeletonID
            ))
        except Exception as e:
            print(f"Error inserting Animation behavior: {e}")
    
    def _insert_equipment_behavior(self, template_id: int, behavior_id: int, equip_dto: WizardEquipmentBehaviorDTO):
        """Insert Equipment behavior details"""
        try:
            # Insert equipment behavior
            self.cursor.execute("""
                INSERT INTO mob_equipment_behaviors (template_id, behavior_id, equipment_template)
                VALUES (?, ?, ?)
            """, (template_id, behavior_id, equip_dto.m_equipmentTemplate))
            
            equipment_behavior_id = self.cursor.lastrowid
            
            # Insert equipment items
            if equip_dto.m_itemList:
                for i, item_id in enumerate(equip_dto.m_itemList):
                    self.cursor.execute("""
                        INSERT INTO mob_equipment_items (template_id, equipment_behavior_id, item_id, item_order)
                        VALUES (?, ?, ?, ?)
                    """, (template_id, equipment_behavior_id, item_id, i))
                    
        except Exception as e:
            print(f"Error inserting Equipment behavior: {e}")
    
    def _insert_path_behavior(self, template_id: int, behavior_id: int, path_dto: PathBehaviorDTO):
        """Insert Path behavior details"""
        try:
            self.cursor.execute("""
                INSERT INTO mob_path_behaviors (
                    template_id, behavior_id, path_type, path_direction, path_id,
                    pause_chance, time_to_pause
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                template_id, behavior_id,
                path_dto.m_kPathType,
                path_dto.m_nPathDirection,
                path_dto.m_pathID,
                path_dto.m_pauseChance,
                path_dto.m_timeToPause
            ))
        except Exception as e:
            print(f"Error inserting Path behavior: {e}")
    
    def _insert_path_movement_behavior(self, template_id: int, behavior_id: int, movement_dto: PathMovementBehaviorDTO):
        """Insert Path Movement behavior details"""
        try:
            self.cursor.execute("""
                INSERT INTO mob_path_movement_behaviors (template_id, behavior_id, movement_scale, movement_speed)
                VALUES (?, ?, ?, ?)
            """, (template_id, behavior_id, movement_dto.m_movementScale, movement_dto.m_movementSpeed))
        except Exception as e:
            print(f"Error inserting Path Movement behavior: {e}")
    
    def _insert_duelist_behavior(self, template_id: int, behavior_id: int, duelist_dto: DuelistBehaviorDTO):
        """Insert Duelist behavior details"""
        try:
            self.cursor.execute("""
                INSERT INTO mob_duelist_behaviors (template_id, behavior_id, npc_proximity)
                VALUES (?, ?, ?)
            """, (template_id, behavior_id, duelist_dto.m_npcProximity))
        except Exception as e:
            print(f"Error inserting Duelist behavior: {e}")
    
    def _insert_collision_behavior(self, template_id: int, behavior_id: int, collision_dto: CollisionBehaviorDTO):
        """Insert Collision behavior details"""
        try:
            self.cursor.execute("""
                INSERT INTO mob_collision_behaviors (
                    template_id, behavior_id, auto_click_box, client_only, disable_collision,
                    solid_collision_filename, walkable_collision_filename
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                template_id, behavior_id,
                1 if collision_dto.m_bAutoClickBox else 0,
                1 if collision_dto.m_bClientOnly else 0,
                1 if collision_dto.m_bDisableCollision else 0,
                collision_dto.m_solidCollisionFilename,
                collision_dto.m_walkableCollisionFilename
            ))
        except Exception as e:
            print(f"Error inserting Collision behavior: {e}")
    
    def _insert_monster_magic_behavior(self, template_id: int, behavior_id: int, magic_dto: MobMonsterMagicBehaviorDTO):
        """Insert Monster Magic behavior details"""
        try:
            self.cursor.execute("""
                INSERT INTO mob_monster_magic_behaviors (
                    template_id, behavior_id, alternate_mob_template_id, collected_as_template_id,
                    collection_resistance, essences_per_house_guest, essences_per_kill_tc,
                    essences_per_summon_tc, gold_per_house_guest, gold_per_kill_tc,
                    gold_per_summon_tc, house_guest_template_id, is_boss, world_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_id, behavior_id,
                magic_dto.m_alternateMobTemplateID,
                magic_dto.m_collectedAsTemplateID,
                magic_dto.m_collectionResistance,
                magic_dto.m_essencesPerHouseGuest,
                magic_dto.m_essencesPerKillTC,
                magic_dto.m_essencesPerSummonTC,
                magic_dto.m_goldPerHouseGuest,
                magic_dto.m_goldPerKillTC,
                magic_dto.m_goldPerSummonTC,
                magic_dto.m_houseGuestTemplateID,
                1 if magic_dto.m_isBoss else 0,
                magic_dto.m_worldName
            ))
        except Exception as e:
            print(f"Error inserting Monster Magic behavior: {e}")
    
    def _insert_object_state_behavior(self, template_id: int, behavior_id: int, state_dto: BasicObjectStateBehaviorDTO):
        """Insert Object State behavior details"""
        try:
            self.cursor.execute("""
                INSERT INTO mob_object_state_behaviors (template_id, behavior_id, state_set_name)
                VALUES (?, ?, ?)
            """, (template_id, behavior_id, state_dto.m_stateSetName))
        except Exception as e:
            print(f"Error inserting Object State behavior: {e}")
    
    def _log_processing_failure(self, file_path: str, mob_data: Dict[str, Any], reason: str):
        """Log processing failure for analysis"""
        try:
            failure_file = self.failed_mobs_dir / "mob_failures.json"
            
            failure_data = {
                "file_path": file_path,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "mob_data": mob_data
            }
            
            # Append to failures file
            if failure_file.exists():
                with open(failure_file, 'r') as f:
                    failures = json.load(f)
            else:
                failures = []
            
            failures.append(failure_data)
            
            with open(failure_file, 'w') as f:
                json.dump(failures, f, indent=2)
                
        except Exception as e:
            print(f"Error logging failure: {e}")
    
    def _generate_final_report(self):
        """Generate final processing report"""
        processing_time = self.processing_end_time - self.processing_start_time
        
        print("\n" + "=" * 60)
        print("MOB DATABASE CREATION COMPLETE!")
        print("=" * 60)
        print(f"Processing time: {processing_time}")
        print(f"Total files processed: {self.total_processed}")
        print(f"Successful mobs: {self.total_success}")
        print(f"Failed conversions: {self.total_failures}")
        print(f"Duplicate mobs: {self.duplicate_count}")
        
        if self.total_processed > 0:
            success_rate = (self.total_success / self.total_processed) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        print(f"Database file: {self.database_path}")
        print(f"Failed mobs directory: {self.failed_mobs_dir}")
        
        # Generate summary file
        summary_file = self.failed_mobs_dir / "processing_summary.json"
        summary = {
            "processing_time": str(processing_time),
            "total_processed": self.total_processed,
            "total_success": self.total_success,
            "total_failures": self.total_failures,
            "duplicate_count": self.duplicate_count,
            "success_rate": (self.total_success / self.total_processed * 100) if self.total_processed > 0 else 0,
            "database_path": str(self.database_path),
            "failed_files": self.failed_files[:100],  # Limit to first 100 for size
            "duplicate_files": self.duplicate_files[:100]
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Summary saved to: {summary_file}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("[OK] Database connection closed")


def main():
    """Main function for testing mob database creation"""
    from pathlib import Path
    import platform
    
    # Get platform-specific paths
    system = platform.system().lower()
    if system == "windows":
        wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("C:/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    else:
        wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
        types_path = Path("/mnt/c/Github Repos Python/BattleBots/DatabaseDemon/types.json")
    
    # Create and initialize database creator
    creator = MobDatabaseCreator()
    
    if not creator.initialize():
        print("Failed to initialize mob database creator")
        return 1
    
    if not creator.create_database():
        print("Failed to create mob database")
        return 1
    
    if not creator.process_all_mobs(wad_path, types_path):
        print("Failed to process mobs")
        return 1
    
    creator.close()
    print("Mob database creation completed successfully!")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())