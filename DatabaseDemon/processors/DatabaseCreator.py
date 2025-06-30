#!/usr/bin/env python3
"""
Wizard101 Database Creator
==========================
Creates and populates SQLite database with Wizard101 spell data.
Handles duplicate detection and comprehensive error logging.
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import traceback

from .DatabaseSchema import DatabaseSchema
from .WADProcessor import WADProcessor
from .RevisionDetector import RevisionDetector
import sys
sys.path.append(str(Path(__file__).parent.parent))
from dtos import FixedSpellDTOFactory


class DatabaseCreator:
    """Creates and manages the Wizard101 spell database"""
    
    def __init__(self, database_path: Optional[Path] = None, 
                 failed_spells_dir: Optional[Path] = None):
        """
        Initialize the database creator
        
        Args:
            database_path: Path for the database file (auto-generated if None)
            failed_spells_dir: Directory for failed spell analysis (auto-detected if None)
        """
        self.database_path = database_path
        self.failed_spells_dir = failed_spells_dir
        self.connection = None
        self.cursor = None
        
        # Initialize WAD processor and revision detector
        self.wad_processor = WADProcessor()
        self.revision_detector = RevisionDetector()
        
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
        
        # Effect counter for unique effect ordering within each spell
        self.current_effect_counter = 0
        
        # Error tracking for current spell
        self.current_spell_errors = []
        
        # Auto-detect paths if not provided
        if not self.database_path:
            self._auto_detect_database_path()
        if not self.failed_spells_dir:
            self._auto_detect_failed_spells_dir()
    
    def _auto_detect_database_path(self):
        """Auto-detect database path based on revision"""
        database_name = self.revision_detector.suggest_database_name("spells")
        self.database_path = Path("database") / database_name
    
    def _auto_detect_failed_spells_dir(self):
        """Auto-detect failed spells directory"""
        self.failed_spells_dir = Path("failed_spells")
    
    def initialize(self) -> bool:
        """
        Initialize the database creator
        
        Returns:
            True if initialization successful, False otherwise
        """
        print("Initializing Database Creator...")
        
        # Initialize WAD processor
        if not self.wad_processor.initialize():
            print("Failed to initialize WAD processor")
            return False
        
        # Validate types file compatibility
        types_path = self.wad_processor.types_path
        if not self.revision_detector.validate_types_compatibility(types_path):
            print("Warning: Types file may not be compatible with current revision")
        
        # Create directories
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.failed_spells_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        if not self._create_database():
            print("Failed to create database")
            return False
        
        print("[OK] Database Creator initialized successfully")
        return True
    
    def _create_database(self) -> bool:
        """Create the database and schema"""
        try:
            # Connect to database
            self.connection = sqlite3.connect(str(self.database_path))
            self.cursor = self.connection.cursor()
            
            print(f"[OK] Connected to database: {self.database_path}")
            
            # Create all tables
            schema = DatabaseSchema()
            for table_name in schema.get_all_table_names():
                create_sql = schema.get_create_table_sql(table_name)
                self.cursor.execute(create_sql)
                print(f"[OK] Created table: {table_name}")
            
            # Create all indexes
            for index_name in schema.get_all_index_names():
                index_sql = schema.get_create_index_sql(index_name)
                self.cursor.execute(index_sql)
                print(f"[OK] Created index: {index_name}")
            
            self.connection.commit()
            print("[OK] Database schema created successfully")
            return True
            
        except Exception as e:
            print(f"Error creating database: {e}")
            traceback.print_exc()
            return False
    
    def check_duplicate_filename(self, filename: str) -> bool:
        """
        Check if filename already exists in database
        
        Args:
            filename: The filename to check
            
        Returns:
            True if duplicate found, False otherwise
        """
        try:
            self.cursor.execute("SELECT filename FROM spell_cards WHERE filename = ?", (filename,))
            result = self.cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking duplicate filename: {e}")
            return False
    
    def log_duplicate(self, filename: str, duplicate_type: str, error_message: str, 
                     spell_data: Dict[str, Any]):
        """
        Log a duplicate to the database and failed_spells directory
        
        Args:
            filename: The duplicate filename
            duplicate_type: Type of duplicate ("filename_collision", etc.)
            error_message: Error description
            spell_data: The spell data that caused the duplicate
        """
        try:
            # Log to database
            self.cursor.execute("""
                INSERT INTO duplicate_log (filename, duplicate_type, error_message, spell_data)
                VALUES (?, ?, ?, ?)
            """, (filename, duplicate_type, error_message, json.dumps(spell_data, default=str)))
            
            # Log to file system
            duplicate_file = self.failed_spells_dir / f"duplicate_{self.duplicate_count:04d}_{filename.replace('/', '_')}.json"
            with open(duplicate_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "filename": filename,
                    "duplicate_type": duplicate_type,
                    "error_message": error_message,
                    "spell_data": spell_data,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2, default=str)
            
            self.duplicate_count += 1
            self.duplicate_files.append(filename)
            
        except Exception as e:
            print(f"Error logging duplicate: {e}")
    
    def log_failed_spell(self, filename: str, error_message: str, spell_data: Dict[str, Any]):
        """
        Log a failed spell processing attempt
        
        Args:
            filename: The filename that failed
            error_message: Error description
            spell_data: The spell data that failed to process
        """
        try:
            # Log to file system
            failed_file = self.failed_spells_dir / f"failed_{len(self.failed_files):04d}_{filename.replace('/', '_')}.json"
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "filename": filename,
                    "error_message": error_message,
                    "spell_data": spell_data,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2, default=str)
            
            self.failed_files.append(filename)
            
        except Exception as e:
            print(f"Error logging failed spell: {e}")
    
    def insert_spell_data(self, filename: str, spell_dict: Dict[str, Any], spell_dto: Any) -> bool:
        """
        Insert spell data into the database
        
        Args:
            filename: The spell filename (PRIMARY KEY)
            spell_dict: Raw spell data dictionary
            spell_dto: Processed spell DTO
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Reset effect counter and error tracking for this spell
            self.current_effect_counter = 0
            self.current_spell_errors = []
            
            # Check for duplicate filename
            if self.check_duplicate_filename(filename):
                self.log_duplicate(filename, "filename_collision", 
                                 f"Filename already exists in database", spell_dict)
                return False
            
            # Insert main spell data
            if not self._insert_main_spell_data(filename, spell_dict, spell_dto):
                return False
            
            # Insert nested data
            if not self._insert_nested_data(filename, spell_dict, spell_dto):
                return False
            
            # Insert type-specific data
            if not self._insert_type_specific_data(filename, spell_dict, spell_dto):
                return False
            
            # Check if any errors occurred during processing
            if self.current_spell_errors:
                error_summary = f"Spell had {len(self.current_spell_errors)} processing errors: {'; '.join(self.current_spell_errors[:3])}"
                self.log_failed_spell(filename, error_summary, spell_dict)
                return False
            
            return True
            
        except Exception as e:
            error_msg = f"Error inserting spell data: {e}"
            print(error_msg)
            self.log_failed_spell(filename, error_msg, spell_dict)
            return False
    
    def _insert_main_spell_data(self, filename: str, spell_dict: Dict[str, Any], spell_dto: Any) -> bool:
        """Insert data into main spell_cards table"""
        try:
            # Prepare data for insertion (handle None values)
            def safe_get(obj, attr, default=None):
                """Safely get attribute from object"""
                if hasattr(obj, attr):
                    value = getattr(obj, attr)
                    # Convert boolean to integer for SQLite
                    if isinstance(value, bool):
                        return 1 if value else 0
                    return value
                return default
            
            # Insert into spell_cards table
            self.cursor.execute("""
                INSERT INTO spell_cards (
                    filename, spell_type, m_name, m_PvE, m_PvP, m_Treasure, m_accuracy,
                    m_advancedDescription, m_alwaysFizzle, m_backRowFriendly, m_baseCost,
                    m_battlegroundsOnly, m_boosterPackIcon, m_cardFront, m_casterInvisible,
                    m_cloaked, m_cloakedName, m_creditsCost, m_delayEnchantment,
                    m_description, m_descriptionCombatHUD, m_descriptionTrainer,
                    m_displayIndex, m_displayName, m_hiddenFromEffectsWindow,
                    m_ignoreCharms, m_ignoreDispel, m_imageIndex, m_imageName,
                    m_leavesPlayWhenCast, m_levelRestriction, m_maxCopies, m_noDiscard,
                    m_noPvEEnchant, m_noPvPEnchant, m_previousSpellName,
                    m_pvpCurrencyCost, m_pvpTourneyCurrencyCost, m_requiredSchoolName,
                    m_sMagicSchoolName, m_sTypeName, m_secondarySchoolName,
                    m_showPolymorphedName, m_skipTruncation, m_spellBase,
                    m_spellCategory, m_spellFusion, m_spellSourceType, m_trainingCost,
                    m_useGloss
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filename,
                spell_dict.get("$__type", "").replace("class ", ""),
                safe_get(spell_dto, "m_name"),
                safe_get(spell_dto, "m_PvE"),
                safe_get(spell_dto, "m_PvP"),
                safe_get(spell_dto, "m_Treasure"),
                safe_get(spell_dto, "m_accuracy"),
                safe_get(spell_dto, "m_advancedDescription"),
                safe_get(spell_dto, "m_alwaysFizzle"),
                safe_get(spell_dto, "m_backRowFriendly"),
                safe_get(spell_dto, "m_baseCost"),
                safe_get(spell_dto, "m_battlegroundsOnly"),
                safe_get(spell_dto, "m_boosterPackIcon"),
                safe_get(spell_dto, "m_cardFront"),
                safe_get(spell_dto, "m_casterInvisible"),
                safe_get(spell_dto, "m_cloaked"),
                safe_get(spell_dto, "m_cloakedName"),
                safe_get(spell_dto, "m_creditsCost"),
                safe_get(spell_dto, "m_delayEnchantment"),
                safe_get(spell_dto, "m_description"),
                safe_get(spell_dto, "m_descriptionCombatHUD"),
                safe_get(spell_dto, "m_descriptionTrainer"),
                safe_get(spell_dto, "m_displayIndex"),
                safe_get(spell_dto, "m_displayName"),
                safe_get(spell_dto, "m_hiddenFromEffectsWindow"),
                safe_get(spell_dto, "m_ignoreCharms"),
                safe_get(spell_dto, "m_ignoreDispel"),
                safe_get(spell_dto, "m_imageIndex"),
                safe_get(spell_dto, "m_imageName"),
                safe_get(spell_dto, "m_leavesPlayWhenCast"),
                safe_get(spell_dto, "m_levelRestriction"),
                safe_get(spell_dto, "m_maxCopies"),
                safe_get(spell_dto, "m_noDiscard"),
                safe_get(spell_dto, "m_noPvEEnchant"),
                safe_get(spell_dto, "m_noPvPEnchant"),
                safe_get(spell_dto, "m_previousSpellName"),
                safe_get(spell_dto, "m_pvpCurrencyCost"),
                safe_get(spell_dto, "m_pvpTourneyCurrencyCost"),
                safe_get(spell_dto, "m_requiredSchoolName"),
                safe_get(spell_dto, "m_sMagicSchoolName"),
                safe_get(spell_dto, "m_sTypeName"),
                safe_get(spell_dto, "m_secondarySchoolName"),
                safe_get(spell_dto, "m_showPolymorphedName"),
                safe_get(spell_dto, "m_skipTruncation"),
                safe_get(spell_dto, "m_spellBase"),
                safe_get(spell_dto, "m_spellCategory"),
                safe_get(spell_dto, "m_spellFusion"),
                safe_get(spell_dto, "m_spellSourceType"),
                safe_get(spell_dto, "m_trainingCost"),
                safe_get(spell_dto, "m_useGloss")
            ))
            
            return True
            
        except Exception as e:
            print(f"Error inserting main spell data: {e}")
            return False
    
    def _insert_nested_data(self, filename: str, spell_dict: Dict[str, Any], spell_dto: Any) -> bool:
        """Insert nested data (effects, ranks, adjectives, etc.)"""
        try:
            # Insert spell rank data
            if hasattr(spell_dto, "m_spellRank") and spell_dto.m_spellRank:
                rank = spell_dto.m_spellRank
                self.cursor.execute("""
                    INSERT INTO spell_ranks (
                        filename, m_balancePips, m_deathPips, m_firePips, m_icePips,
                        m_lifePips, m_mythPips, m_shadowPips, m_spellRank,
                        m_stormPips, m_xPipSpell
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    filename,
                    getattr(rank, "m_balancePips", 0),
                    getattr(rank, "m_deathPips", 0),
                    getattr(rank, "m_firePips", 0),
                    getattr(rank, "m_icePips", 0),
                    getattr(rank, "m_lifePips", 0),
                    getattr(rank, "m_mythPips", 0),
                    getattr(rank, "m_shadowPips", 0),
                    getattr(rank, "m_spellRank", 0),
                    getattr(rank, "m_stormPips", 0),
                    1 if getattr(rank, "m_xPipSpell", False) else 0
                ))
            
            # Insert spell effects
            if hasattr(spell_dto, "m_effects") and spell_dto.m_effects:
                for effect in spell_dto.m_effects:
                    self._insert_spell_effect(filename, effect, "spell_cards", -1)
            
            # Insert adjectives
            if hasattr(spell_dto, "m_adjectives") and spell_dto.m_adjectives:
                for adj_order, adjective in enumerate(spell_dto.m_adjectives):
                    self.cursor.execute("""
                        INSERT INTO spell_adjectives (filename, adjective_order, adjective_value)
                        VALUES (?, ?, ?)
                    """, (filename, adj_order, str(adjective)))
            
            # Insert behaviors
            if hasattr(spell_dto, "m_behaviors") and spell_dto.m_behaviors:
                for beh_order, behavior in enumerate(spell_dto.m_behaviors):
                    self.cursor.execute("""
                        INSERT INTO spell_behaviors (filename, behavior_order, behavior_value)
                        VALUES (?, ?, ?)
                    """, (filename, beh_order, str(behavior)))
            
            # Insert valid target spells
            if hasattr(spell_dto, "m_validTargetSpells") and spell_dto.m_validTargetSpells:
                for target_order, target in enumerate(spell_dto.m_validTargetSpells):
                    self.cursor.execute("""
                        INSERT INTO spell_valid_targets (filename, target_order, target_spell)
                        VALUES (?, ?, ?)
                    """, (filename, target_order, str(target)))
            
            return True
            
        except Exception as e:
            print(f"Error inserting nested data: {e}")
            return False
    
    def _insert_spell_effect(self, filename: str, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert a single spell effect into appropriate table based on type"""
        try:
            # Check for invalid effect types (debugging)
            if effect is None:
                print(f"WARNING: None effect in {filename}, parent_table: {parent_table}")
                return
            
            if isinstance(effect, list):
                error_msg = f"List effect found - should be DTO object (parent_table: {parent_table})"
                print(f"ERROR: {error_msg} in {filename}")
                self.current_spell_errors.append(error_msg)
                # Try to process each item in the list
                for item in effect:
                    if hasattr(item, '__dict__') or isinstance(item, dict):
                        self._insert_spell_effect(filename, item, parent_table, parent_effect_order)
                return
            
            if isinstance(effect, dict) and "$__type" in effect:
                error_msg = f"Raw dict effect found - DTO conversion failed (type: {effect.get('$__type', 'unknown')})"
                print(f"WARNING: {error_msg} in {filename}")
                self.current_spell_errors.append(error_msg)
                return
            
            # Use and increment global effect counter
            effect_order = self.current_effect_counter
            self.current_effect_counter += 1
            
            effect_type = type(effect).__name__
            
            # Route to appropriate insert method based on effect type
            if effect_type == "SpellEffectDTO":
                self._insert_base_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "DelaySpellEffectDTO":
                self._insert_delay_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "ConditionalSpellEffectDTO":
                self._insert_conditional_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "VariableSpellEffectDTO":
                self._insert_variable_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "EffectListSpellEffectDTO":
                self._insert_effect_list_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "RandomSpellEffectDTO":
                self._insert_random_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "RandomPerTargetSpellEffectDTO":
                self._insert_random_per_target_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "HangingConversionSpellEffectDTO":
                self._insert_hanging_conversion_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "TargetCountSpellEffectDTO":
                self._insert_target_count_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "ShadowSpellEffectDTO":
                self._insert_shadow_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            elif effect_type == "CountBasedSpellEffectDTO":
                self._insert_count_based_spell_effect(filename, effect_order, effect, parent_table, parent_effect_order)
            else:
                error_msg = f"Unknown effect type: {effect_type}"
                print(f"ERROR: {error_msg} in {filename}, value: {effect}")
                self.current_spell_errors.append(error_msg)
                
        except Exception as e:
            error_msg = f"Exception in spell effect insertion: {e}"
            print(f"ERROR: {error_msg} in {filename}")
            self.current_spell_errors.append(error_msg)
            import traceback
            traceback.print_exc()
    
    def _get_base_effect_values(self, effect: Any):
        """Get base SpellEffect field values"""
        def safe_effect_get(attr, default=None):
            if hasattr(effect, attr):
                value = getattr(effect, attr)
                if isinstance(value, bool):
                    return 1 if value else 0
                return value
            return default
        
        return (
            safe_effect_get("m_act"), safe_effect_get("m_actNum"),
            safe_effect_get("m_armorPiercingParam"), safe_effect_get("m_bypassProtection"),
            safe_effect_get("m_chancePerTarget"), safe_effect_get("m_cloaked"),
            safe_effect_get("m_converted"), safe_effect_get("m_damageType"),
            safe_effect_get("m_disposition"), safe_effect_get("m_effectParam"),
            safe_effect_get("m_effectTarget"), safe_effect_get("m_effectType"),
            safe_effect_get("m_enchantmentSpellTemplateID"), safe_effect_get("m_healModifier"),
            safe_effect_get("m_numRounds"), safe_effect_get("m_paramPerRound"),
            safe_effect_get("m_pipNum"), safe_effect_get("m_protected"),
            safe_effect_get("m_rank"), safe_effect_get("m_sDamageType"),
            safe_effect_get("m_spellTemplateID")
        )
    
    def _insert_base_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert basic SpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values)
    
    def _insert_delay_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert DelaySpellEffect with specific fields"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO delay_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID,
                m_damage, m_rounds, m_spellDelayedTemplateID, m_spellDelayedTemplateDamageID,
                m_spellEnchanterTemplateID, m_spellHits, m_spell
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values + (
            getattr(effect, "m_damage", 0),
            getattr(effect, "m_rounds", 0),
            getattr(effect, "m_spellDelayedTemplateID", 0),
            getattr(effect, "m_spellDelayedTemplateDamageID", 0),
            getattr(effect, "m_spellEnchanterTemplateID", 0),
            getattr(effect, "m_spellHits", 0),
            str(getattr(effect, "m_spell", None))
        ))
        
        # Handle m_targetSubcircleList for DelaySpellEffect
        if hasattr(effect, "m_targetSubcircleList") and effect.m_targetSubcircleList:
            for subcircle_order, subcircle in enumerate(effect.m_targetSubcircleList):
                self.cursor.execute("""
                    INSERT INTO delay_spell_target_subcircles (
                        filename, effect_order, subcircle_order, subcircle_value
                    ) VALUES (?, ?, ?, ?)
                """, (filename, effect_order, subcircle_order, subcircle))
    
    def _insert_conditional_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert ConditionalSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO conditional_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values)
        
        # Handle ConditionalSpellElement objects in m_elements
        if hasattr(effect, "m_elements") and effect.m_elements:
            for element_order, element in enumerate(effect.m_elements):
                self._insert_conditional_spell_element(filename, effect_order, element_order, element)
    
    def _insert_conditional_spell_element(self, filename: str, parent_effect_order: int, element_order: int, element: Any):
        """Insert ConditionalSpellElement"""
        self.cursor.execute("""
            INSERT INTO conditional_spell_elements (
                filename, parent_effect_order, element_order
            ) VALUES (?, ?, ?)
        """, (filename, parent_effect_order, element_order))
        
        # Handle nested effects in m_pEffect
        if hasattr(element, "m_pEffect") and element.m_pEffect:
            self._insert_spell_effect(filename, element.m_pEffect, "conditional_spell_elements", element_order)
        
        # Handle requirements in m_pReqs
        if hasattr(element, "m_pReqs") and element.m_pReqs:
            self._insert_requirement_list(filename, parent_effect_order, element_order, element.m_pReqs)
    
    def _insert_variable_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert VariableSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO variable_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values)
        
        # Handle nested effects in m_effectList
        if hasattr(effect, "m_effectList") and effect.m_effectList:
            for nested_effect in effect.m_effectList:
                self._insert_spell_effect(filename, nested_effect, "variable_spell_effects", effect_order)
    
    def _insert_effect_list_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert EffectListSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO effect_list_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values)
        
        # Handle nested effects in m_effectList
        if hasattr(effect, "m_effectList") and effect.m_effectList:
            for nested_effect in effect.m_effectList:
                self._insert_spell_effect(filename, nested_effect, "effect_list_spell_effects", effect_order)
    
    def _insert_random_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert RandomSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO random_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values)
        
        # Handle nested effects in m_effectList
        if hasattr(effect, "m_effectList") and effect.m_effectList:
            for nested_effect in effect.m_effectList:
                self._insert_spell_effect(filename, nested_effect, "random_spell_effects", effect_order)
    
    def _insert_random_per_target_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert RandomPerTargetSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO random_per_target_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values)
        
        # Handle nested effects in m_effectList
        if hasattr(effect, "m_effectList") and effect.m_effectList:
            for nested_effect in effect.m_effectList:
                self._insert_spell_effect(filename, nested_effect, "random_per_target_spell_effects", effect_order)
    
    def _insert_hanging_conversion_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert HangingConversionSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO hanging_conversion_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID,
                m_hangingEffectType, m_outputSelector, m_minEffectValue, m_maxEffectValue,
                m_minEffectCount, m_maxEffectCount, m_notDamageType, m_scaleSourceEffectValue,
                m_sourceEffectValuePercent, m_applyToEffectSource
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values + (
            getattr(effect, "m_hangingEffectType", 0),
            getattr(effect, "m_outputSelector", 0),
            getattr(effect, "m_minEffectValue", 0),
            getattr(effect, "m_maxEffectValue", 0),
            getattr(effect, "m_minEffectCount", 0),
            getattr(effect, "m_maxEffectCount", 0),
            getattr(effect, "m_notDamageType", 0),
            1 if getattr(effect, "m_scaleSourceEffectValue", False) else 0,
            getattr(effect, "m_sourceEffectValuePercent", 0.0),
            1 if getattr(effect, "m_applyToEffectSource", False) else 0
        ))
        
        # Handle nested effects in m_outputEffect (LIST of effects)
        if hasattr(effect, "m_outputEffect") and effect.m_outputEffect:
            for output_effect in effect.m_outputEffect:
                self._insert_spell_effect(filename, output_effect, "hanging_conversion_spell_effects", effect_order)
    
    def _insert_target_count_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert TargetCountSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO target_count_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values)
        
        # Handle nested effects in m_effectLists
        if hasattr(effect, "m_effectLists") and effect.m_effectLists:
            for nested_effect in effect.m_effectLists:
                self._insert_spell_effect(filename, nested_effect, "target_count_spell_effects", effect_order)
    
    def _insert_shadow_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert ShadowSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO shadow_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID,
                m_shadowType
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values + (
            getattr(effect, "m_shadowType", 0),
        ))
        
        # Handle nested effects in m_effectList
        if hasattr(effect, "m_effectList") and effect.m_effectList:
            for nested_effect in effect.m_effectList:
                self._insert_spell_effect(filename, nested_effect, "shadow_spell_effects", effect_order)
    
    def _insert_count_based_spell_effect(self, filename: str, effect_order: int, effect: Any, parent_table: str, parent_effect_order: int):
        """Insert CountBasedSpellEffect"""
        base_values = self._get_base_effect_values(effect)
        
        self.cursor.execute("""
            INSERT INTO count_based_spell_effects (
                filename, effect_order, parent_table, parent_effect_order,
                m_act, m_actNum, m_armorPiercingParam, m_bypassProtection, m_chancePerTarget,
                m_cloaked, m_converted, m_damageType, m_disposition,
                m_effectParam, m_effectTarget, m_effectType,
                m_enchantmentSpellTemplateID, m_healModifier, m_numRounds,
                m_paramPerRound, m_pipNum, m_protected, m_rank,
                m_sDamageType, m_spellTemplateID,
                m_countThreshold
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, effect_order, parent_table, parent_effect_order) + base_values + (
            getattr(effect, "m_countThreshold", 0),
        ))
        
        # Handle nested effects in m_effectList
        if hasattr(effect, "m_effectList") and effect.m_effectList:
            for nested_effect in effect.m_effectList:
                self._insert_spell_effect(filename, nested_effect, "count_based_spell_effects", effect_order)
    
    def _insert_type_specific_data(self, filename: str, spell_dict: Dict[str, Any], spell_dto: Any) -> bool:
        """Insert type-specific data based on spell template type"""
        try:
            spell_type = type(spell_dto).__name__
            
            # Handle TieredSpellTemplateDTO
            if spell_type == "TieredSpellTemplateDTO":
                self.cursor.execute("""
                    INSERT INTO tiered_spell_data (filename, m_levelRestriction, m_retired, m_shardCost)
                    VALUES (?, ?, ?, ?)
                """, (
                    filename,
                    getattr(spell_dto, "m_levelRestriction", None),
                    1 if getattr(spell_dto, "m_retired", False) else 0,
                    getattr(spell_dto, "m_shardCost", None)
                ))
                
                # Insert next tier spells
                if hasattr(spell_dto, "m_nextTierSpells") and spell_dto.m_nextTierSpells:
                    for tier_order, next_tier in enumerate(spell_dto.m_nextTierSpells):
                        self.cursor.execute("""
                            INSERT INTO tiered_spell_next_tiers (filename, tier_order, next_tier_spell)
                            VALUES (?, ?, ?)
                        """, (filename, tier_order, str(next_tier)))
            
            # Handle other spell template types similarly...
            # (CantripsSpellTemplateDTO, CastleMagicSpellTemplateDTO, etc.)
            
            return True
            
        except Exception as e:
            print(f"Error inserting type-specific data: {e}")
            return False
    
    def _insert_requirement_list(self, filename: str, parent_effect_order: int, element_order: int, req_list: Any):
        """Insert RequirementList into requirement_lists table"""
        try:
            # Insert RequirementList data
            self.cursor.execute("""
                INSERT INTO requirement_lists (
                    filename, parent_effect_order, element_order, m_applyNOT, m_operator
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                filename,
                parent_effect_order,
                element_order,
                1 if getattr(req_list, "m_applyNOT", False) else 0,
                getattr(req_list, "m_operator", 0)
            ))
            
            # Handle individual requirements in m_requirements array
            if hasattr(req_list, "m_requirements") and req_list.m_requirements:
                for requirement_order, requirement in enumerate(req_list.m_requirements):
                    self._insert_individual_requirement(filename, parent_effect_order, element_order, requirement_order, requirement)
                    
        except Exception as e:
            error_msg = f"Error inserting requirement list: {e}"
            print(f"ERROR: {error_msg} in {filename}")
            self.current_spell_errors.append(error_msg)
    
    def _insert_individual_requirement(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, requirement: Any):
        """Insert individual requirement into appropriate table based on type"""
        try:
            requirement_type = type(requirement).__name__
            
            # Route to appropriate insert method based on requirement type
            if requirement_type == "ReqIsSchoolDTO":
                self._insert_req_is_school(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqHangingCharmDTO":
                self._insert_req_hanging_charm(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqHangingWardDTO":
                self._insert_req_hanging_ward(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqHangingOverTimeDTO":
                self._insert_req_hanging_over_time(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqHangingEffectTypeDTO":
                self._insert_req_hanging_effect_type(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqHangingAuraDTO":
                self._insert_req_hanging_aura(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqSchoolOfFocusDTO":
                self._insert_req_school_of_focus(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqMinionDTO":
                self._insert_req_minion(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqHasEntryDTO":
                self._insert_req_has_entry(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqCombatHealthDTO":
                self._insert_req_combat_health(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqPvPCombatDTO":
                self._insert_req_pvp_combat(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqShadowPipCountDTO":
                self._insert_req_shadow_pip_count(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqCombatStatusDTO":
                self._insert_req_combat_status(filename, parent_effect_order, element_order, requirement_order, requirement)
            elif requirement_type == "ReqPipCountDTO":
                self._insert_req_pip_count(filename, parent_effect_order, element_order, requirement_order, requirement)
            else:
                error_msg = f"Unknown requirement type: {requirement_type}"
                print(f"ERROR: {error_msg} in {filename}")
                self.current_spell_errors.append(error_msg)
                
        except Exception as e:
            error_msg = f"Error inserting individual requirement: {e}"
            print(f"ERROR: {error_msg} in {filename}")
            self.current_spell_errors.append(error_msg)
    
    # Individual requirement insertion methods
    
    def _insert_req_is_school(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqIsSchool requirement"""
        self.cursor.execute("""
            INSERT INTO req_is_school (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_magicSchoolName
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_magicSchoolName", "")
        ))
    
    def _insert_req_hanging_charm(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqHangingCharm requirement"""
        self.cursor.execute("""
            INSERT INTO req_hanging_charm (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_disposition, m_minCount, m_maxCount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_disposition", 0),
            getattr(req, "m_minCount", 0),
            getattr(req, "m_maxCount", 0)
        ))
    
    def _insert_req_hanging_ward(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqHangingWard requirement"""
        self.cursor.execute("""
            INSERT INTO req_hanging_ward (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_disposition, m_minCount, m_maxCount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_disposition", 0),
            getattr(req, "m_minCount", 0),
            getattr(req, "m_maxCount", 0)
        ))
    
    def _insert_req_hanging_over_time(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqHangingOverTime requirement"""
        self.cursor.execute("""
            INSERT INTO req_hanging_over_time (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_disposition, m_minCount, m_maxCount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_disposition", 0),
            getattr(req, "m_minCount", 0),
            getattr(req, "m_maxCount", 0)
        ))
    
    def _insert_req_hanging_effect_type(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqHangingEffectType requirement"""
        self.cursor.execute("""
            INSERT INTO req_hanging_effect_type (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_effectType, m_minCount, m_maxCount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_effectType", 0),
            getattr(req, "m_minCount", 0),
            getattr(req, "m_maxCount", 0)
        ))
    
    def _insert_req_hanging_aura(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqHangingAura requirement"""
        self.cursor.execute("""
            INSERT INTO req_hanging_aura (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_disposition, m_minCount, m_maxCount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_disposition", 0),
            getattr(req, "m_minCount", 0),
            getattr(req, "m_maxCount", 0)
        ))
    
    def _insert_req_school_of_focus(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqSchoolOfFocus requirement"""
        self.cursor.execute("""
            INSERT INTO req_school_of_focus (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_magicSchoolName
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_magicSchoolName", "")
        ))
    
    def _insert_req_minion(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqMinion requirement"""
        self.cursor.execute("""
            INSERT INTO req_minion (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_minCount, m_maxCount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_minCount", 0),
            getattr(req, "m_maxCount", 0)
        ))
    
    def _insert_req_has_entry(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqHasEntry requirement"""
        self.cursor.execute("""
            INSERT INTO req_has_entry (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_entryName
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_entryName", "")
        ))
    
    def _insert_req_combat_health(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqCombatHealth requirement"""
        self.cursor.execute("""
            INSERT INTO req_combat_health (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_fMinPercent, m_fMaxPercent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_fMinPercent", 0.0),
            getattr(req, "m_fMaxPercent", 0.0)
        ))
    
    def _insert_req_pvp_combat(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqPvPCombat requirement"""
        self.cursor.execute("""
            INSERT INTO req_pvp_combat (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0)
        ))
    
    def _insert_req_shadow_pip_count(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqShadowPipCount requirement"""
        self.cursor.execute("""
            INSERT INTO req_shadow_pip_count (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_minPips, m_maxPips
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_minPips", 0),
            getattr(req, "m_maxPips", 0)
        ))
    
    def _insert_req_combat_status(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqCombatStatus requirement"""
        self.cursor.execute("""
            INSERT INTO req_combat_status (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_combatStatus
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_combatStatus", 0)
        ))
    
    def _insert_req_pip_count(self, filename: str, parent_effect_order: int, element_order: int, requirement_order: int, req: Any):
        """Insert ReqPipCount requirement"""
        self.cursor.execute("""
            INSERT INTO req_pip_count (
                filename, parent_effect_order, element_order, requirement_order,
                m_applyNOT, m_operator, m_targetType, m_minPips, m_maxPips
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, parent_effect_order, element_order, requirement_order,
            1 if getattr(req, "m_applyNOT", False) else 0,
            getattr(req, "m_operator", 0),
            getattr(req, "m_targetType", 0),
            getattr(req, "m_minPips", 0),
            getattr(req, "m_maxPips", 0)
        ))
    
    def process_all_spells(self) -> bool:
        """Process all spells from WAD archive into database"""
        print("Starting spell processing...")
        self.processing_start_time = datetime.now()
        
        try:
            # Get all spell files
            spell_files = self.wad_processor.get_all_spell_files()
            if not spell_files:
                print("No spell files found")
                return False
            
            print(f"Processing {len(spell_files)} spell files...")
            
            for i, file_path in enumerate(spell_files):
                self.total_processed += 1
                
                # Process single spell
                success, spell_dict, spell_dto, error_msg = self.wad_processor.process_single_spell(file_path)
                
                if success and spell_dto:
                    # Insert into database
                    if self.insert_spell_data(file_path, spell_dict, spell_dto):
                        self.total_success += 1
                    else:
                        self.total_failures += 1
                else:
                    # Log failure
                    self.total_failures += 1
                    if spell_dict:
                        self.log_failed_spell(file_path, error_msg or "Unknown error", spell_dict)
                
                # Progress update
                if self.total_processed % 1000 == 0:
                    print(f"[PROGRESS] {self.total_processed} processed, "
                          f"{self.total_success} success, {self.total_failures} failed, "
                          f"{self.duplicate_count} duplicates")
                
                # Periodic commit
                if self.total_processed % 100 == 0:
                    self.connection.commit()
            
            # Final commit
            self.connection.commit()
            self.processing_end_time = datetime.now()
            
            # Insert processing metadata
            self._insert_processing_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error during spell processing: {e}")
            traceback.print_exc()
            return False
    
    def _insert_processing_metadata(self):
        """Insert processing metadata into database"""
        try:
            revision = self.revision_detector.get_revision()
            
            self.cursor.execute("""
                INSERT INTO processing_metadata (
                    revision, total_files_processed, successful_files, failed_files,
                    processing_start_time, processing_end_time, types_file_path, wad_file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                revision,
                self.total_processed,
                self.total_success,
                self.total_failures,
                self.processing_start_time.isoformat(),
                self.processing_end_time.isoformat(),
                str(self.wad_processor.types_path),
                str(self.wad_processor.wad_path)
            ))
            
            self.connection.commit()
            
        except Exception as e:
            print(f"Error inserting processing metadata: {e}")
    
    def print_summary(self):
        """Print processing summary"""
        duration = self.processing_end_time - self.processing_start_time if self.processing_end_time else None
        
        print("\n" + "=" * 60)
        print("DATABASE CREATION COMPLETE!")
        print("=" * 60)
        print(f"Database: {self.database_path}")
        print(f"Total processed: {self.total_processed}")
        print(f"Successful: {self.total_success}")
        print(f"Failed: {self.total_failures}")
        print(f"Duplicates: {self.duplicate_count}")
        print(f"Success rate: {(self.total_success/self.total_processed*100):.1f}%")
        if duration:
            print(f"Processing time: {duration}")
        print(f"Failed spells directory: {self.failed_spells_dir}")
        
        if self.duplicate_count > 0:
            print(f"\nWARNING: {self.duplicate_count} duplicate filenames found!")
            print("Check failed_spells/ directory for analysis")
    
    def cleanup(self):
        """Clean up resources"""
        if self.connection:
            self.connection.close()
        self.wad_processor.cleanup()
        print("[OK] Database Creator cleaned up")