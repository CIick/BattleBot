#!/usr/bin/env python3
"""
Wizard101 Items Database Creator
===============================
Creates and populates SQLite database with Wizard101 item data from ObjectData files.
Handles WizItemTemplate processing with comprehensive nested object relationship management.
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import traceback

from .DatabaseSchema import ItemsDatabaseSchema
from .WADProcessor import ItemsWADProcessor

# Add parent directories to Python path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))  # DatabaseDemon level
sys.path.append(str(Path(__file__).parent.parent))         # Items level

from dtos.ItemsDTO import *
from dtos.ItemsDTOFactory import ItemsDTOFactory


class ItemsDatabaseCreator:
    """Creates and manages the Wizard101 items database"""
    
    def __init__(self, database_path: Optional[Path] = None, 
                 failed_items_dir: Optional[Path] = None):
        """
        Initialize the items database creator
        
        Args:
            database_path: Path for the database file (auto-generated if None)
            failed_items_dir: Directory for failed item analysis (auto-detected if None)
        """
        self.database_path = database_path
        self.failed_items_dir = failed_items_dir
        self.connection = None
        self.cursor = None
        
        # Auto-generate paths if not provided
        if self.database_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            database_dir = Path("database")
            database_dir.mkdir(exist_ok=True)
            self.database_path = database_dir / f"item_templates_{timestamp}.db"
        
        if self.failed_items_dir is None:
            self.failed_items_dir = Path("failed_items")
            self.failed_items_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.total_processed = 0
        self.total_success = 0
        self.total_failed = 0
        self.total_behaviors = 0
        self.total_effects = 0
        self.total_requirements = 0
        self.total_pet_items = 0
        self.total_mount_items = 0
        self.total_housing_items = 0
        self.total_equipment_items = 0
        
        # Processing timing
        self.start_time = None
        self.end_time = None
        
        # Error tracking
        self.insertion_errors = []
    
    def initialize_database(self) -> bool:
        """Initialize the database with schema"""
        try:
            print(f"Initializing database: {self.database_path}")
            
            # Connect to database
            self.connection = sqlite3.connect(str(self.database_path))
            self.cursor = self.connection.cursor()
            
            # Create tables
            print("Creating database schema...")
            for create_statement in ItemsDatabaseSchema.get_create_table_statements():
                self.cursor.execute(create_statement)
            
            # Create indexes
            print("Creating database indexes...")
            for index_statement in ItemsDatabaseSchema.get_create_index_statements():
                try:
                    self.cursor.execute(index_statement)
                except sqlite3.OperationalError as e:
                    if "already exists" not in str(e):
                        print(f"Warning: Failed to create index: {e}")
            
            self.connection.commit()
            print("[OK] Database schema created successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize database: {e}")
            traceback.print_exc()
            return False
    
    def insert_item_template(self, file_path: str, item_dto: WizItemTemplateDTO, raw_dict: Dict[str, Any]) -> bool:
        """
        Insert main item template record
        
        Args:
            file_path: Source file path (used as primary key)
            item_dto: WizItemTemplate DTO
            raw_dict: Raw dictionary data for fallbacks
            
        Returns:
            True if insertion successful
        """
        try:
            # Extract filename from path
            filename = Path(file_path).name
            
            # Prepare main item data
            item_data = {
                'filename': filename,
                'item_type': 'WizItemTemplate',
                'm_templateID': item_dto.m_templateID,
                'm_objectName': item_dto.m_objectName,
                'm_displayName': item_dto.m_displayName,
                'm_description': item_dto.m_description,
                'm_visualID': item_dto.m_visualID,
                'm_nObjectType': item_dto.m_nObjectType,
                'm_school': item_dto.m_school,
                'm_rarity': item_dto.m_rarity,
                'm_rank': item_dto.m_rank,
                'm_baseCost': item_dto.m_baseCost,
                'm_creditsCost': item_dto.m_creditsCost,
                'm_arenaPointCost': item_dto.m_arenaPointCost,
                'm_pvpCurrencyCost': item_dto.m_pvpCurrencyCost,
                'm_pvpTourneyCurrencyCost': item_dto.m_pvpTourneyCurrencyCost,
                'm_sIcon': item_dto.m_sIcon,
                'm_boyIconIndex': item_dto.m_boyIconIndex,
                'm_girlIconIndex': item_dto.m_girlIconIndex,
                'm_holidayFlag': item_dto.m_holidayFlag,
                'm_itemLimit': item_dto.m_itemLimit,
                'm_itemSetBonusTemplateID': item_dto.m_itemSetBonusTemplateID,
                'm_exemptFromAOI': 1 if item_dto.m_exemptFromAOI else 0,
                'm_numPatterns': item_dto.m_numPatterns,
                'm_numPrimaryColors': item_dto.m_numPrimaryColors,
                'm_numSecondaryColors': item_dto.m_numSecondaryColors,
                'm_adjectiveList': json.dumps(item_dto.m_adjectiveList) if item_dto.m_adjectiveList else "[]",
                'm_avatarFlags': json.dumps(item_dto.m_avatarFlags) if item_dto.m_avatarFlags else "[]"
            }
            
            # Insert main item record
            columns = ", ".join(item_data.keys())
            placeholders = ", ".join(["?" for _ in item_data.values()])
            sql = f"INSERT OR REPLACE INTO item_templates ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(sql, list(item_data.values()))
            
            # Insert related data
            self._insert_item_behaviors(filename, item_dto.m_behaviors)
            self._insert_item_equip_effects(filename, item_dto.m_equipEffects)
            self._insert_item_avatar_data(filename, item_dto.m_avatarInfo)
            self._insert_item_requirements(filename, item_dto.m_equipRequirements, "equip")
            self._insert_item_requirements(filename, item_dto.m_purchaseRequirements, "purchase")
            
            return True
            
        except Exception as e:
            error_info = {
                'file_path': file_path,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            self.insertion_errors.append(error_info)
            print(f"[ERROR] Failed to insert item {file_path}: {e}")
            return False
    
    def _insert_item_behaviors(self, filename: str, behaviors: List[Any]):
        """Insert item behaviors data"""
        if not behaviors:
            return
        
        # Clear existing behaviors for this item
        self.cursor.execute("DELETE FROM item_behaviors WHERE filename = ?", (filename,))
        
        for i, behavior in enumerate(behaviors):
            if behavior is None:
                continue
            
            try:
                # Extract behavior type and name
                behavior_type = "Unknown"
                behavior_name = ""
                behavior_data = {}
                
                if isinstance(behavior, BehaviorTemplateDTO):
                    behavior_type = behavior.__class__.__name__.replace("DTO", "")
                    behavior_name = behavior.m_behaviorName or ""
                    # Convert DTO to dict for JSON storage
                    behavior_data = self._dto_to_dict(behavior)
                elif isinstance(behavior, dict):
                    behavior_type = behavior.get('$__type', 'Unknown')
                    behavior_name = behavior.get('m_behaviorName', '')
                    behavior_data = behavior
                
                # Insert behavior record
                self.cursor.execute("""
                    INSERT INTO item_behaviors 
                    (filename, behavior_index, behavior_type, behavior_name, behavior_data)
                    VALUES (?, ?, ?, ?, ?)
                """, (filename, i, behavior_type, behavior_name, json.dumps(behavior_data, default=str)))
                
                self.total_behaviors += 1
                
                # Handle special behavior types
                if isinstance(behavior, PetItemBehaviorTemplateDTO):
                    self._insert_pet_data(filename, behavior)
                    self.total_pet_items += 1
                elif isinstance(behavior, MountItemBehaviorTemplateDTO):
                    self._insert_mount_data(filename, behavior)
                    self.total_mount_items += 1
                elif isinstance(behavior, FurnitureInfoBehaviorTemplateDTO):
                    self._insert_furniture_data(filename, behavior)
                    self.total_housing_items += 1
                elif isinstance(behavior, EquipmentBehaviorTemplateDTO):
                    self.total_equipment_items += 1
                elif isinstance(behavior, JewelSocketBehaviorTemplateDTO):
                    self._insert_jewel_socket_data(filename, behavior)
                
            except Exception as e:
                print(f"[WARNING] Failed to insert behavior {i} for {filename}: {e}")
    
    def _insert_item_equip_effects(self, filename: str, effects: List[StatisticEffectInfoDTO]):
        """Insert item equipment effects data"""
        if not effects:
            return
        
        # Clear existing effects for this item
        self.cursor.execute("DELETE FROM item_equip_effects WHERE filename = ?", (filename,))
        
        for i, effect in enumerate(effects):
            if effect is None:
                continue
            
            try:
                self.cursor.execute("""
                    INSERT INTO item_equip_effects 
                    (filename, effect_index, m_effectName, m_lookupIndex, m_effectValue, 
                     m_effectPercent, m_schoolName, m_effectType)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (filename, i, effect.m_effectName, effect.m_lookupIndex, 
                     effect.m_effectValue, effect.m_effectPercent, 
                     effect.m_schoolName, effect.m_effectType))
                
                self.total_effects += 1
                
            except Exception as e:
                print(f"[WARNING] Failed to insert effect {i} for {filename}: {e}")
    
    def _insert_item_avatar_data(self, filename: str, avatar_info: Optional[WizAvatarItemInfoDTO]):
        """Insert item avatar customization data"""
        if not avatar_info:
            return
        
        # Clear existing avatar data for this item
        self.cursor.execute("DELETE FROM item_avatar_options WHERE filename = ?", (filename,))
        self.cursor.execute("DELETE FROM item_avatar_textures WHERE filename = ?", (filename,))
        
        # Insert avatar options
        if avatar_info.m_options:
            for i, option in enumerate(avatar_info.m_options):
                if option is None:
                    continue
                
                try:
                    self.cursor.execute("""
                        INSERT INTO item_avatar_options 
                        (filename, option_index, m_mesh, m_noMesh, m_geometry, 
                         m_conditionFlags, m_assetName, m_materialName)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (filename, i, option.m_mesh, 1 if option.m_noMesh else 0,
                         option.m_geometry, json.dumps(option.m_conditionFlags),
                         option.m_assetName, option.m_materialName))
                    
                except Exception as e:
                    print(f"[WARNING] Failed to insert avatar option {i} for {filename}: {e}")
        
        # Insert texture options
        if avatar_info.m_textureOptions:
            for i, texture in enumerate(avatar_info.m_textureOptions):
                if texture is None:
                    continue
                
                try:
                    self.cursor.execute("""
                        INSERT INTO item_avatar_textures 
                        (filename, texture_index, m_conditionFlags, m_decals, m_decals2,
                         m_materialName, m_textures, m_tintColorNames, m_tintColors, m_useTintColor)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (filename, i, json.dumps(texture.m_conditionFlags),
                         json.dumps(texture.m_decals), json.dumps(texture.m_decals2),
                         texture.m_materialName, json.dumps(texture.m_textures),
                         json.dumps(texture.m_tintColorNames), json.dumps(texture.m_tintColors),
                         1 if texture.m_useTintColor else 0))
                    
                except Exception as e:
                    print(f"[WARNING] Failed to insert texture option {i} for {filename}: {e}")
    
    def _insert_item_requirements(self, filename: str, requirements: Optional[RequirementListDTO], req_type: str):
        """Insert item requirements data"""
        if not requirements or not requirements.m_requirements:
            return
        
        for i, requirement in enumerate(requirements.m_requirements):
            if requirement is None:
                continue
            
            try:
                req_class = requirement.__class__.__name__.replace("DTO", "") if hasattr(requirement, "__class__") else "Unknown"
                req_data = self._dto_to_dict(requirement) if hasattr(requirement, "__dict__") else requirement
                
                self.cursor.execute("""
                    INSERT INTO item_requirements 
                    (filename, requirement_type, requirement_index, req_class, 
                     m_applyNOT, m_operator, requirement_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (filename, req_type, i, req_class,
                     getattr(requirement, 'm_applyNOT', 0),
                     getattr(requirement, 'm_operator', 0),
                     json.dumps(req_data, default=str)))
                
                self.total_requirements += 1
                
            except Exception as e:
                print(f"[WARNING] Failed to insert requirement {i} for {filename}: {e}")
    
    def _insert_pet_data(self, filename: str, pet_behavior: PetItemBehaviorTemplateDTO):
        """Insert pet-specific data"""
        try:
            # Insert main pet data
            self.cursor.execute("""
                INSERT OR REPLACE INTO item_pet_data 
                (filename, m_conversionLevel, m_conversionXP, m_eGender, m_eRace, m_eggColor,
                 m_eggName, m_excludeFromHatchOfTheDay, m_exclusivePet, m_fScale,
                 m_favoriteSnackCategories, m_flyingOffset, m_hatchesAsID,
                 m_hatchmakingInitalCooldownTime, m_hatchmakingMaximumHatches,
                 m_hideName, m_houseGuestOpacity, m_sHatchRate, m_wowFactor,
                 m_duckSound, m_jumpSound)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (filename, pet_behavior.m_conversionLevel, pet_behavior.m_conversionXP,
                 pet_behavior.m_eGender, pet_behavior.m_eRace, pet_behavior.m_eggColor,
                 pet_behavior.m_eggName, 1 if pet_behavior.m_excludeFromHatchOfTheDay else 0,
                 1 if pet_behavior.m_exclusivePet else 0, pet_behavior.m_fScale,
                 json.dumps(pet_behavior.m_favoriteSnackCategories), pet_behavior.m_flyingOffset,
                 pet_behavior.m_hatchesAsID, pet_behavior.m_hatchmakingInitalCooldownTime,
                 pet_behavior.m_hatchmakingMaximumHatches, 1 if pet_behavior.m_hideName else 0,
                 pet_behavior.m_houseGuestOpacity, pet_behavior.m_sHatchRate,
                 pet_behavior.m_wowFactor, pet_behavior.m_duckSound, pet_behavior.m_jumpSound))
            
            # Insert pet levels
            if pet_behavior.m_Levels:
                for level in pet_behavior.m_Levels:
                    self.cursor.execute("""
                        INSERT INTO item_pet_levels 
                        (filename, m_level, m_lootTable, m_powerCardCount, m_powerCardName,
                         m_powerCardName2, m_powerCardName3, m_requiredXP, m_template)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (filename, level.m_level, json.dumps(level.m_lootTable),
                         level.m_powerCardCount, level.m_powerCardName,
                         level.m_powerCardName2, level.m_powerCardName3,
                         level.m_requiredXP, level.m_template))
            
            # Insert pet stats (start, max, conversion)
            for stat_type, stats in [("start", pet_behavior.m_startStats),
                                   ("max", pet_behavior.m_maxStats),
                                   ("conversion", pet_behavior.m_conversionStats)]:
                if stats:
                    for stat in stats:
                        self.cursor.execute("""
                            INSERT INTO item_pet_stats 
                            (filename, stat_type, m_name, m_statID, m_value)
                            VALUES (?, ?, ?, ?, ?)
                        """, (filename, stat_type, stat.m_name, stat.m_statID, stat.m_value))
            
            # Insert pet talents
            for talent_type, talents in [("talent", pet_behavior.m_talents),
                                       ("derby", pet_behavior.m_derbyTalents),
                                       ("guaranteed", pet_behavior.m_guaranteedTalents),
                                       ("conversion", pet_behavior.m_conversionTalents)]:
                if talents:
                    for talent in talents:
                        self.cursor.execute("""
                            INSERT INTO item_pet_talents 
                            (filename, talent_type, talent_name)
                            VALUES (?, ?, ?)
                        """, (filename, talent_type, talent))
            
            # Insert morphing exceptions
            if pet_behavior.m_morphingExceptions:
                for morphing in pet_behavior.m_morphingExceptions:
                    self.cursor.execute("""
                        INSERT INTO item_pet_morphing 
                        (filename, m_eggTemplateID, m_probability, m_secondPetTemplateID)
                        VALUES (?, ?, ?, ?)
                    """, (filename, morphing.m_eggTemplateID, morphing.m_probability,
                         morphing.m_secondPetTemplateID))
            
            # Insert dye mappings
            for dye_type, dyes in [("pattern", pet_behavior.m_patternToTexture),
                                 ("primary", pet_behavior.m_primaryDyeToTexture),
                                 ("secondary", pet_behavior.m_secondaryDyeToTexture)]:
                if dyes:
                    for dye in dyes:
                        self.cursor.execute("""
                            INSERT INTO item_pet_dyes 
                            (filename, dye_type, m_dye, m_texture)
                            VALUES (?, ?, ?, ?)
                        """, (filename, dye_type, dye.m_dye, dye.m_texture))
            
        except Exception as e:
            print(f"[WARNING] Failed to insert pet data for {filename}: {e}")
    
    def _insert_mount_data(self, filename: str, mount_behavior: MountItemBehaviorTemplateDTO):
        """Insert mount-specific data"""
        try:
            # Insert main mount data
            self.cursor.execute("""
                INSERT OR REPLACE INTO item_mount_data 
                (filename, m_conversionLevel, m_eGender, m_eRace, m_fScale,
                 m_flyingOffset, m_hideName, m_houseGuestOpacity, m_maxSpeed, m_mountType)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (filename, mount_behavior.m_conversionLevel, mount_behavior.m_eGender,
                 mount_behavior.m_eRace, mount_behavior.m_fScale, mount_behavior.m_flyingOffset,
                 1 if mount_behavior.m_hideName else 0, mount_behavior.m_houseGuestOpacity,
                 mount_behavior.m_maxSpeed, mount_behavior.m_mountType))
            
            # Insert mount talents
            for talent_type, talents in [("talent", mount_behavior.m_talents),
                                       ("guaranteed", mount_behavior.m_guaranteedTalents),
                                       ("conversion", mount_behavior.m_conversionTalents)]:
                if talents:
                    for talent in talents:
                        self.cursor.execute("""
                            INSERT INTO item_mount_talents 
                            (filename, talent_type, talent_name)
                            VALUES (?, ?, ?)
                        """, (filename, talent_type, talent))
            
            # Insert dye mappings
            for dye_type, dyes in [("pattern", mount_behavior.m_patternToTexture),
                                 ("primary", mount_behavior.m_primaryDyeToTexture),
                                 ("secondary", mount_behavior.m_secondaryDyeToTexture)]:
                if dyes:
                    for dye in dyes:
                        self.cursor.execute("""
                            INSERT INTO item_mount_dyes 
                            (filename, dye_type, m_dye, m_texture)
                            VALUES (?, ?, ?, ?)
                        """, (filename, dye_type, dye.m_dye, dye.m_texture))
            
        except Exception as e:
            print(f"[WARNING] Failed to insert mount data for {filename}: {e}")
    
    def _insert_furniture_data(self, filename: str, furniture_behavior: FurnitureInfoBehaviorTemplateDTO):
        """Insert furniture-specific data"""
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO item_furniture_data 
                (filename, m_bounce, m_cameraOffsetX, m_cameraOffsetY, m_cameraOffsetZ,
                 m_pitch, m_roll, m_rotate, m_textureFilename, m_textureIndex, m_yaw)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (filename, 1 if furniture_behavior.m_bounce else 0,
                 furniture_behavior.m_cameraOffsetX, furniture_behavior.m_cameraOffsetY,
                 furniture_behavior.m_cameraOffsetZ, furniture_behavior.m_pitch,
                 furniture_behavior.m_roll, 1 if furniture_behavior.m_rotate else 0,
                 furniture_behavior.m_textureFilename, furniture_behavior.m_textureIndex,
                 furniture_behavior.m_yaw))
            
        except Exception as e:
            print(f"[WARNING] Failed to insert furniture data for {filename}: {e}")
    
    def _insert_jewel_socket_data(self, filename: str, socket_behavior: JewelSocketBehaviorTemplateDTO):
        """Insert jewel socket data"""
        try:
            if socket_behavior.m_jewelSockets:
                for i, socket in enumerate(socket_behavior.m_jewelSockets):
                    self.cursor.execute("""
                        INSERT INTO item_jewel_sockets 
                        (filename, socket_index, m_bLockable, m_socketType)
                        VALUES (?, ?, ?, ?)
                    """, (filename, i, 1 if socket.m_bLockable else 0, socket.m_socketType))
            
        except Exception as e:
            print(f"[WARNING] Failed to insert jewel socket data for {filename}: {e}")
    
    def _dto_to_dict(self, dto: Any) -> Dict[str, Any]:
        """Convert DTO to dictionary for JSON storage"""
        if hasattr(dto, '__dict__'):
            result = {}
            for key, value in dto.__dict__.items():
                if hasattr(value, '__dict__'):
                    result[key] = self._dto_to_dict(value)
                elif isinstance(value, list):
                    result[key] = [self._dto_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                else:
                    result[key] = value
            return result
        else:
            return dto
    
    def process_all_items_from_wad(self) -> bool:
        """Process all items from WAD and insert into database"""
        self.start_time = datetime.now()
        
        try:
            # Initialize WAD processor
            print("Initializing WAD processor...")
            wad_processor = ItemsWADProcessor()
            if not wad_processor.initialize():
                print("[ERROR] Failed to initialize WAD processor")
                return False
            
            # Process all items
            print("Processing all items from WAD...")
            if not wad_processor.process_all_items():
                print("[ERROR] Failed to process items from WAD")
                return False
            
            # Get successful items
            successful_items = wad_processor.get_successful_items()
            print(f"Processing {len(successful_items)} successful items...")
            
            # Insert items into database
            for item_data in successful_items:
                self.total_processed += 1
                
                try:
                    success = self.insert_item_template(
                        item_data['file_path'],
                        item_data['item_dto'],
                        item_data['raw_dict']
                    )
                    
                    if success:
                        self.total_success += 1
                    else:
                        self.total_failed += 1
                    
                    # Progress reporting
                    if self.total_processed % 100 == 0:
                        progress = (self.total_processed / len(successful_items)) * 100
                        print(f"[PROGRESS] {self.total_processed}/{len(successful_items)} ({progress:.1f}%) - "
                              f"Success: {self.total_success}, Failed: {self.total_failed}")
                
                except Exception as e:
                    self.total_failed += 1
                    print(f"[ERROR] Failed to process item {item_data['file_path']}: {e}")
            
            # Insert processing statistics
            self._insert_processing_statistics()
            
            # Commit all changes
            self.connection.commit()
            
            self.end_time = datetime.now()
            
            print(f"\n[COMPLETE] Database creation finished!")
            print(f"Database saved: {self.database_path}")
            print(f"Total items processed: {self.total_processed}")
            print(f"Successfully inserted: {self.total_success}")
            print(f"Failed insertions: {self.total_failed}")
            print(f"Processing time: {self.end_time - self.start_time}")
            
            # Cleanup
            wad_processor.cleanup()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Database creation failed: {e}")
            traceback.print_exc()
            return False
    
    def _insert_processing_statistics(self):
        """Insert processing statistics into database"""
        try:
            duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
            success_rate = (self.total_success / max(1, self.total_processed)) * 100
            
            self.cursor.execute("""
                INSERT INTO item_processing_stats 
                (total_files_processed, total_items_found, total_behaviors_processed,
                 total_effects_processed, total_requirements_processed,
                 total_pet_items, total_mount_items, total_housing_items, total_equipment_items,
                 processing_duration_seconds, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.total_processed, self.total_success, self.total_behaviors,
                 self.total_effects, self.total_requirements, self.total_pet_items,
                 self.total_mount_items, self.total_housing_items, self.total_equipment_items,
                 duration, success_rate))
            
        except Exception as e:
            print(f"[WARNING] Failed to insert processing statistics: {e}")
    
    def cleanup(self):
        """Clean up database resources"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
        print("[OK] Items Database Creator cleanup completed")