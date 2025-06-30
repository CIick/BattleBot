#!/usr/bin/env python3
"""
Wizard101 Database Schema Definition
===================================
Database schema for Wizard101 spell data with SQL Server compatibility.
Uses filename as PRIMARY KEY to prevent duplicates.
"""

from typing import Dict, List, Any


class DatabaseSchema:
    """Database schema definition for Wizard101 spell data"""
    
    # SQLite schema (compatible with SQL Server migration)
    SCHEMA_SQL = {
        # Main spell cards table - filename as PRIMARY KEY
        "spell_cards": """
            CREATE TABLE spell_cards (
                filename TEXT PRIMARY KEY,              -- "0P Minotaur - MOB.xml"
                spell_type TEXT NOT NULL,               -- "SpellTemplate", "TieredSpellTemplate"
                m_name TEXT,                           -- Spell display name (may not be unique)
                m_PvE INTEGER,                         -- Boolean as INTEGER for SQL Server compat
                m_PvP INTEGER,
                m_Treasure INTEGER,
                m_accuracy INTEGER,
                m_advancedDescription TEXT,
                m_alwaysFizzle INTEGER,
                m_backRowFriendly INTEGER,
                m_baseCost INTEGER,
                m_battlegroundsOnly INTEGER,
                m_boosterPackIcon TEXT,
                m_cardFront TEXT,
                m_casterInvisible INTEGER,
                m_cloaked INTEGER,
                m_cloakedName TEXT,
                m_creditsCost INTEGER,
                m_delayEnchantment INTEGER,
                m_description TEXT,
                m_descriptionCombatHUD TEXT,
                m_descriptionTrainer TEXT,
                m_displayIndex INTEGER,
                m_displayName TEXT,
                m_hiddenFromEffectsWindow INTEGER,
                m_ignoreCharms INTEGER,
                m_ignoreDispel INTEGER,
                m_imageIndex INTEGER,
                m_imageName TEXT,
                m_leavesPlayWhenCast INTEGER,
                m_levelRestriction INTEGER,
                m_maxCopies INTEGER,
                m_noDiscard INTEGER,
                m_noPvEEnchant INTEGER,
                m_noPvPEnchant INTEGER,
                m_previousSpellName TEXT,
                m_pvpCurrencyCost INTEGER,
                m_pvpTourneyCurrencyCost INTEGER,
                m_requiredSchoolName TEXT,
                m_sMagicSchoolName TEXT,
                m_sTypeName TEXT,
                m_secondarySchoolName TEXT,
                m_showPolymorphedName INTEGER,
                m_skipTruncation INTEGER,
                m_spellBase TEXT,
                m_spellCategory TEXT,
                m_spellFusion INTEGER,
                m_spellSourceType INTEGER,
                m_trainingCost INTEGER,
                m_useGloss INTEGER,
                
                -- Timestamps for tracking
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """,
        
        # Base spell effects table (only for basic SpellEffect objects)
        "spell_effects": """
            CREATE TABLE spell_effects (
                filename TEXT,                          -- FK to spell_cards.filename
                effect_order INTEGER,                   -- Position in effects array (0, 1, 2...)
                parent_table TEXT,                      -- Table containing this effect ("spell_cards", "conditional_spell_elements")
                parent_effect_order INTEGER,            -- Position in parent's effect list (NULL for top-level)
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # DelaySpellEffect table
        "delay_spell_effects": """
            CREATE TABLE delay_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                -- DelaySpellEffect specific fields
                m_damage INTEGER,
                m_rounds INTEGER,
                m_spellDelayedTemplateID INTEGER,
                m_spellDelayedTemplateDamageID INTEGER,
                m_spellEnchanterTemplateID INTEGER,
                m_spellHits INTEGER,
                m_spell TEXT,                           -- JSON for complex object
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # DelaySpellEffect target subcircles (nested array)
        "delay_spell_target_subcircles": """
            CREATE TABLE delay_spell_target_subcircles (
                filename TEXT,
                effect_order INTEGER,
                subcircle_order INTEGER,
                subcircle_value INTEGER,
                
                PRIMARY KEY (filename, effect_order, subcircle_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ConditionalSpellEffect table
        "conditional_spell_effects": """
            CREATE TABLE conditional_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ConditionalSpellElement table (nested in ConditionalSpellEffect)
        "conditional_spell_elements": """
            CREATE TABLE conditional_spell_elements (
                filename TEXT,
                parent_effect_order INTEGER,            -- Which ConditionalSpellEffect this belongs to
                element_order INTEGER,                  -- Position in m_elements array
                
                PRIMARY KEY (filename, parent_effect_order, element_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # RequirementList table (nested in ConditionalSpellElement.m_pReqs)
        "requirement_lists": """
            CREATE TABLE requirement_lists (
                filename TEXT,
                parent_effect_order INTEGER,            -- Which ConditionalSpellEffect this belongs to
                element_order INTEGER,                  -- Which ConditionalSpellElement this belongs to
                m_applyNOT INTEGER,
                m_operator INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Individual Requirement Tables (nested in RequirementList.m_requirements)
        
        # ReqIsSchool table (most common - 8,175 occurrences)
        "req_is_school": """
            CREATE TABLE req_is_school (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,              -- Position in m_requirements array
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_magicSchoolName TEXT,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqHangingCharm table (3,058 occurrences)
        "req_hanging_charm": """
            CREATE TABLE req_hanging_charm (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_disposition INTEGER,
                m_minCount INTEGER,
                m_maxCount INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqHangingWard table (2,427 occurrences)
        "req_hanging_ward": """
            CREATE TABLE req_hanging_ward (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_disposition INTEGER,
                m_minCount INTEGER,
                m_maxCount INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqHangingOverTime table (1,803 occurrences)
        "req_hanging_over_time": """
            CREATE TABLE req_hanging_over_time (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_disposition INTEGER,
                m_minCount INTEGER,
                m_maxCount INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqHangingEffectType table (650 occurrences)
        "req_hanging_effect_type": """
            CREATE TABLE req_hanging_effect_type (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_effectType INTEGER,
                m_minCount INTEGER,
                m_maxCount INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqHangingAura table (111 occurrences)
        "req_hanging_aura": """
            CREATE TABLE req_hanging_aura (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_disposition INTEGER,
                m_minCount INTEGER,
                m_maxCount INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqSchoolOfFocus table (108 occurrences)
        "req_school_of_focus": """
            CREATE TABLE req_school_of_focus (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_magicSchoolName TEXT,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqMinion table (102 occurrences)
        "req_minion": """
            CREATE TABLE req_minion (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_minCount INTEGER,
                m_maxCount INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqHasEntry table (98 occurrences)
        "req_has_entry": """
            CREATE TABLE req_has_entry (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_entryName TEXT,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqCombatHealth table (75 occurrences)
        "req_combat_health": """
            CREATE TABLE req_combat_health (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_fMinPercent REAL,
                m_fMaxPercent REAL,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqPvPCombat table (32 occurrences)
        "req_pvp_combat": """
            CREATE TABLE req_pvp_combat (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqShadowPipCount table (21 occurrences)
        "req_shadow_pip_count": """
            CREATE TABLE req_shadow_pip_count (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_minPips INTEGER,
                m_maxPips INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqCombatStatus table (13 occurrences)
        "req_combat_status": """
            CREATE TABLE req_combat_status (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_combatStatus INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ReqPipCount table (11 occurrences)
        "req_pip_count": """
            CREATE TABLE req_pip_count (
                filename TEXT,
                parent_effect_order INTEGER,
                element_order INTEGER,
                requirement_order INTEGER,
                m_applyNOT INTEGER,
                m_operator INTEGER,
                m_targetType INTEGER,
                m_minPips INTEGER,
                m_maxPips INTEGER,
                
                PRIMARY KEY (filename, parent_effect_order, element_order, requirement_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # VariableSpellEffect table
        "variable_spell_effects": """
            CREATE TABLE variable_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # EffectListSpellEffect table
        "effect_list_spell_effects": """
            CREATE TABLE effect_list_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # RandomSpellEffect table
        "random_spell_effects": """
            CREATE TABLE random_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # RandomPerTargetSpellEffect table
        "random_per_target_spell_effects": """
            CREATE TABLE random_per_target_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # HangingConversionSpellEffect table
        "hanging_conversion_spell_effects": """
            CREATE TABLE hanging_conversion_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                -- HangingConversionSpellEffect specific fields
                m_hangingEffectType INTEGER,
                m_outputSelector INTEGER,
                m_minEffectValue INTEGER,
                m_maxEffectValue INTEGER,
                m_minEffectCount INTEGER,
                m_maxEffectCount INTEGER,
                m_notDamageType INTEGER,
                m_scaleSourceEffectValue INTEGER,
                m_sourceEffectValuePercent REAL,
                m_applyToEffectSource INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # TargetCountSpellEffect table
        "target_count_spell_effects": """
            CREATE TABLE target_count_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # ShadowSpellEffect table
        "shadow_spell_effects": """
            CREATE TABLE shadow_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                -- ShadowSpellEffect specific fields
                m_shadowType INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # CountBasedSpellEffect table
        "count_based_spell_effects": """
            CREATE TABLE count_based_spell_effects (
                filename TEXT,
                effect_order INTEGER,
                parent_table TEXT,
                parent_effect_order INTEGER,
                -- Base SpellEffect fields
                m_act INTEGER,
                m_actNum INTEGER,
                m_armorPiercingParam INTEGER,
                m_bypassProtection INTEGER,
                m_chancePerTarget INTEGER,
                m_cloaked INTEGER,
                m_converted INTEGER,
                m_damageType INTEGER,
                m_disposition INTEGER,
                m_effectParam INTEGER,
                m_effectTarget INTEGER,
                m_effectType INTEGER,
                m_enchantmentSpellTemplateID INTEGER,
                m_healModifier REAL,
                m_numRounds INTEGER,
                m_paramPerRound INTEGER,
                m_pipNum INTEGER,
                m_protected INTEGER,
                m_rank INTEGER,
                m_sDamageType TEXT,
                m_spellTemplateID INTEGER,
                -- CountBasedSpellEffect specific fields
                m_countThreshold INTEGER,
                
                PRIMARY KEY (filename, effect_order, parent_table, parent_effect_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Spell ranks table (one-to-one with spell_cards)
        "spell_ranks": """
            CREATE TABLE spell_ranks (
                filename TEXT PRIMARY KEY,              -- FK to spell_cards.filename
                m_balancePips INTEGER,
                m_deathPips INTEGER,
                m_firePips INTEGER,
                m_icePips INTEGER,
                m_lifePips INTEGER,
                m_mythPips INTEGER,
                m_shadowPips INTEGER,
                m_spellRank INTEGER,
                m_stormPips INTEGER,
                m_xPipSpell INTEGER,
                
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Spell adjectives (many-to-many relationship)
        "spell_adjectives": """
            CREATE TABLE spell_adjectives (
                filename TEXT,                          -- FK to spell_cards.filename
                adjective_order INTEGER,                -- Position in adjectives array
                adjective_value TEXT,                   -- The actual adjective string
                
                PRIMARY KEY (filename, adjective_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Spell behaviors (many-to-many relationship)
        "spell_behaviors": """
            CREATE TABLE spell_behaviors (
                filename TEXT,                          -- FK to spell_cards.filename
                behavior_order INTEGER,                 -- Position in behaviors array
                behavior_value TEXT,                    -- The actual behavior string or JSON
                
                PRIMARY KEY (filename, behavior_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Valid target spells (many-to-many relationship)
        "spell_valid_targets": """
            CREATE TABLE spell_valid_targets (
                filename TEXT,                          -- FK to spell_cards.filename
                target_order INTEGER,                   -- Position in validTargetSpells array
                target_spell TEXT,                      -- Target spell name or identifier
                
                PRIMARY KEY (filename, target_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Type-specific data tables for inheritance hierarchy
        
        # Tiered spell template data
        "tiered_spell_data": """
            CREATE TABLE tiered_spell_data (
                filename TEXT PRIMARY KEY,              -- FK to spell_cards.filename
                m_levelRestriction INTEGER,
                m_retired INTEGER,
                m_shardCost INTEGER,
                
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Tiered spell next tier relationships
        "tiered_spell_next_tiers": """
            CREATE TABLE tiered_spell_next_tiers (
                filename TEXT,                          -- FK to spell_cards.filename
                tier_order INTEGER,                     -- Position in nextTierSpells array
                next_tier_spell TEXT,                   -- Next tier spell name
                
                PRIMARY KEY (filename, tier_order),
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Cantrips spell template data
        "cantrips_spell_data": """
            CREATE TABLE cantrips_spell_data (
                filename TEXT PRIMARY KEY,              -- FK to spell_cards.filename
                m_cantripsSpellEffect INTEGER,
                m_cantripsSpellImageIndex INTEGER,
                m_cantripsSpellImageName TEXT,
                m_cantripsSpellType INTEGER,
                m_cooldownSeconds INTEGER,
                m_effectParameter TEXT,
                m_energyCost INTEGER,
                m_soundEffectGain REAL,
                m_soundEffectName TEXT,
                
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Castle magic spell template data
        "castle_magic_spell_data": """
            CREATE TABLE castle_magic_spell_data (
                filename TEXT PRIMARY KEY,              -- FK to spell_cards.filename
                m_animationKFM TEXT,
                m_animationSequence TEXT,
                m_castleMagicSpellEffect INTEGER,
                m_castleMagicSpellType INTEGER,
                m_effectSchool TEXT,
                
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Fishing spell template data
        "fishing_spell_data": """
            CREATE TABLE fishing_spell_data (
                filename TEXT PRIMARY KEY,              -- FK to spell_cards.filename
                m_animationKFM TEXT,
                m_animationName TEXT,
                m_energyCost INTEGER,
                m_fishingSchoolFocus TEXT,
                m_fishingSpellImageIndex INTEGER,
                m_fishingSpellImageName TEXT,
                m_fishingSpellType INTEGER,
                m_soundEffectGain REAL,
                m_soundEffectName TEXT,
                
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Garden spell template data
        "garden_spell_data": """
            CREATE TABLE garden_spell_data (
                filename TEXT PRIMARY KEY,              -- FK to spell_cards.filename
                m_affectedRadius INTEGER,
                m_animationKFM TEXT,
                m_animationName TEXT,
                m_animationNameLarge TEXT,
                m_animationNameSmall TEXT,
                m_bugZapLevel INTEGER,
                m_energyCost INTEGER,
                m_gardenSpellImageIndex INTEGER,
                m_gardenSpellImageName TEXT,
                m_gardenSpellType INTEGER,
                m_protectionTemplateID INTEGER,
                m_providesMagic INTEGER,
                m_providesMusic INTEGER,
                m_providesPollination INTEGER,
                m_providesSun INTEGER,
                m_providesWater INTEGER,
                m_soilTemplateID INTEGER,
                m_soundEffectGain REAL,
                m_soundEffectName TEXT,
                m_utilitySpellType INTEGER,
                m_yOffset REAL,
                
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # WhirlyBurly spell template data
        "whirlyburly_spell_data": """
            CREATE TABLE whirlyburly_spell_data (
                filename TEXT PRIMARY KEY,              -- FK to spell_cards.filename
                m_specialUnits TEXT,
                m_unitMovement TEXT,
                
                FOREIGN KEY (filename) REFERENCES spell_cards(filename) ON DELETE CASCADE
            )
        """,
        
        # Processing metadata and error tracking
        "processing_metadata": """
            CREATE TABLE processing_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                revision TEXT,
                total_files_processed INTEGER,
                successful_files INTEGER,
                failed_files INTEGER,
                processing_start_time DATETIME,
                processing_end_time DATETIME,
                types_file_path TEXT,
                wad_file_path TEXT
            )
        """,
        
        # Duplicate detection log
        "duplicate_log": """
            CREATE TABLE duplicate_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                duplicate_type TEXT,                    -- "filename_collision", "name_collision"
                error_message TEXT,
                spell_data TEXT,                        -- JSON dump of spell data for analysis
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
    }
    
    # Indexes for performance
    INDEXES_SQL = {
        # Indexes on spell_cards for common queries
        "idx_spell_cards_name": "CREATE INDEX idx_spell_cards_name ON spell_cards(m_name)",
        "idx_spell_cards_school": "CREATE INDEX idx_spell_cards_school ON spell_cards(m_sMagicSchoolName)",
        "idx_spell_cards_type": "CREATE INDEX idx_spell_cards_type ON spell_cards(m_sTypeName)",
        "idx_spell_cards_spell_type": "CREATE INDEX idx_spell_cards_spell_type ON spell_cards(spell_type)",
        "idx_spell_cards_accuracy": "CREATE INDEX idx_spell_cards_accuracy ON spell_cards(m_accuracy)",
        
        # Indexes on effect tables for joins
        "idx_spell_effects_filename": "CREATE INDEX idx_spell_effects_filename ON spell_effects(filename)",
        "idx_spell_effects_type": "CREATE INDEX idx_spell_effects_type ON spell_effects(m_effectType)",
        "idx_spell_effects_damage_type": "CREATE INDEX idx_spell_effects_damage_type ON spell_effects(m_sDamageType)",
        "idx_delay_spell_effects_filename": "CREATE INDEX idx_delay_spell_effects_filename ON delay_spell_effects(filename)",
        "idx_delay_spell_target_subcircles_filename": "CREATE INDEX idx_delay_spell_target_subcircles_filename ON delay_spell_target_subcircles(filename)",
        "idx_conditional_spell_effects_filename": "CREATE INDEX idx_conditional_spell_effects_filename ON conditional_spell_effects(filename)",
        "idx_conditional_spell_elements_filename": "CREATE INDEX idx_conditional_spell_elements_filename ON conditional_spell_elements(filename)",
        "idx_variable_spell_effects_filename": "CREATE INDEX idx_variable_spell_effects_filename ON variable_spell_effects(filename)",
        "idx_effect_list_spell_effects_filename": "CREATE INDEX idx_effect_list_spell_effects_filename ON effect_list_spell_effects(filename)",
        "idx_random_spell_effects_filename": "CREATE INDEX idx_random_spell_effects_filename ON random_spell_effects(filename)",
        "idx_random_per_target_spell_effects_filename": "CREATE INDEX idx_random_per_target_spell_effects_filename ON random_per_target_spell_effects(filename)",
        "idx_hanging_conversion_spell_effects_filename": "CREATE INDEX idx_hanging_conversion_spell_effects_filename ON hanging_conversion_spell_effects(filename)",
        "idx_target_count_spell_effects_filename": "CREATE INDEX idx_target_count_spell_effects_filename ON target_count_spell_effects(filename)",
        "idx_shadow_spell_effects_filename": "CREATE INDEX idx_shadow_spell_effects_filename ON shadow_spell_effects(filename)",
        "idx_count_based_spell_effects_filename": "CREATE INDEX idx_count_based_spell_effects_filename ON count_based_spell_effects(filename)",
        
        # Indexes on requirement tables for joins
        "idx_requirement_lists_filename": "CREATE INDEX idx_requirement_lists_filename ON requirement_lists(filename)",
        "idx_req_is_school_filename": "CREATE INDEX idx_req_is_school_filename ON req_is_school(filename)",
        "idx_req_hanging_charm_filename": "CREATE INDEX idx_req_hanging_charm_filename ON req_hanging_charm(filename)",
        "idx_req_hanging_ward_filename": "CREATE INDEX idx_req_hanging_ward_filename ON req_hanging_ward(filename)",
        "idx_req_hanging_over_time_filename": "CREATE INDEX idx_req_hanging_over_time_filename ON req_hanging_over_time(filename)",
        "idx_req_hanging_effect_type_filename": "CREATE INDEX idx_req_hanging_effect_type_filename ON req_hanging_effect_type(filename)",
        "idx_req_hanging_aura_filename": "CREATE INDEX idx_req_hanging_aura_filename ON req_hanging_aura(filename)",
        "idx_req_school_of_focus_filename": "CREATE INDEX idx_req_school_of_focus_filename ON req_school_of_focus(filename)",
        "idx_req_minion_filename": "CREATE INDEX idx_req_minion_filename ON req_minion(filename)",
        "idx_req_has_entry_filename": "CREATE INDEX idx_req_has_entry_filename ON req_has_entry(filename)",
        "idx_req_combat_health_filename": "CREATE INDEX idx_req_combat_health_filename ON req_combat_health(filename)",
        "idx_req_pvp_combat_filename": "CREATE INDEX idx_req_pvp_combat_filename ON req_pvp_combat(filename)",
        "idx_req_shadow_pip_count_filename": "CREATE INDEX idx_req_shadow_pip_count_filename ON req_shadow_pip_count(filename)",
        "idx_req_combat_status_filename": "CREATE INDEX idx_req_combat_status_filename ON req_combat_status(filename)",
        "idx_req_pip_count_filename": "CREATE INDEX idx_req_pip_count_filename ON req_pip_count(filename)",
        
        # Indexes on spell_ranks for pip costs
        "idx_spell_ranks_total_rank": "CREATE INDEX idx_spell_ranks_total_rank ON spell_ranks(m_spellRank)",
    }
    
    @classmethod
    def get_create_table_sql(cls, table_name: str) -> str:
        """Get CREATE TABLE SQL for a specific table"""
        return cls.SCHEMA_SQL.get(table_name, "")
    
    @classmethod
    def get_all_table_names(cls) -> List[str]:
        """Get list of all table names"""
        return list(cls.SCHEMA_SQL.keys())
    
    @classmethod
    def get_create_index_sql(cls, index_name: str) -> str:
        """Get CREATE INDEX SQL for a specific index"""
        return cls.INDEXES_SQL.get(index_name, "")
    
    @classmethod
    def get_all_index_names(cls) -> List[str]:
        """Get list of all index names"""
        return list(cls.INDEXES_SQL.keys())
    
    @classmethod
    def get_full_schema_sql(cls) -> str:
        """Get complete schema SQL (tables + indexes)"""
        sql_parts = []
        
        # Add all table creation statements
        for table_name in cls.get_all_table_names():
            sql_parts.append(f"-- Table: {table_name}")
            sql_parts.append(cls.get_create_table_sql(table_name))
            sql_parts.append("")
        
        # Add all index creation statements
        sql_parts.append("-- Indexes")
        for index_name in cls.get_all_index_names():
            sql_parts.append(cls.get_create_index_sql(index_name) + ";")
        
        return "\n".join(sql_parts)