#!/usr/bin/env python3
"""
Comprehensive WizItemTemplate Discovery and Type Analysis
========================================================
Searches the entire Root.wad archive to discover all WizItemTemplate objects,
analyze their distribution across directories, and recursively discover all
nested class types required for perfect parsing.

Outputs:
- Complete directory distribution analysis
- Recursive nested type discovery
- Sample items from each unique location
- Comprehensive reports for DTO development planning

This script explores the ENTIRE WAD archive, not just ObjectData, to discover
if WizItemTemplates exist in unexpected locations.
"""

import json
import os
import platform
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Tuple, Optional
import traceback
from datetime import datetime

import katsuba
from katsuba.wad import Archive
from katsuba.op import LazyObject, LazyList, TypeList, Serializer, SerializerOptions

# Add DatabaseDemon to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.conversion_utils import convert_lazy_object_to_dict


class ItemTypeDiscoverer:
    """Comprehensive discoverer for WizItemTemplate objects and nested types"""
    
    # WizItemTemplate type hash from type dump
    WIZITEMTEMPLATE_HASH = 991922385
    
    def __init__(self, max_samples_per_dir: int = 3, max_file_size_mb: int = 50):
        """
        Initialize the item type discoverer
        
        Args:
            max_samples_per_dir: Maximum sample items to store per directory
            max_file_size_mb: Maximum file size for individual reports
        """
        self.max_samples_per_dir = max_samples_per_dir
        self.max_file_size = max_file_size_mb * 1024 * 1024
        
        # WAD processing components
        self.wad_path = None
        self.types_path = None
        self.archive = None
        self.type_list = None
        self.serializer = None
        
        # Discovery data structures
        self.directory_distribution = defaultdict(list)  # directory -> list of file paths
        self.directory_samples = defaultdict(list)       # directory -> sample items
        self.nested_types_found = set()                  # all discovered nested class types
        self.nested_type_counts = Counter()              # frequency of each nested type
        self.nested_type_samples = defaultdict(list)     # sample data for each nested type
        
        # Processing statistics
        self.total_files_processed = 0
        self.total_items_found = 0
        self.total_non_items = 0
        self.unique_directories = 0
        self.processing_errors = []
        self.failed_files = []
        
        # Location analysis
        self.objectdata_items = 0
        self.non_objectdata_items = 0
        self.unexpected_locations = []
        
        # Reports directory
        self.reports_dir = Path("../../Reports/Item Reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize(self) -> bool:
        """Initialize WAD processor and type system"""
        print("Initializing WizItemTemplate Type Discoverer...")
        print("=" * 60)
        
        # Auto-detect paths
        if not self._auto_detect_paths():
            return False
        
        # Load type list
        if not self._load_type_list():
            return False
        
        # Open WAD archive
        if not self._open_wad_archive():
            return False
        
        # Create serializer
        if not self._create_serializer():
            return False
        
        print("[OK] Item Type Discoverer initialized successfully")
        print(f"WAD Path: {self.wad_path}")
        print(f"Types Path: {self.types_path}")
        print(f"Reports Directory: {self.reports_dir}")
        return True
    
    def _auto_detect_paths(self) -> bool:
        """Auto-detect platform-specific paths"""
        system = platform.system().lower()
        
        if system == "windows":
            self.wad_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            self.types_path = Path("../../types.json")
        else:  # Linux/WSL
            self.wad_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Data/GameData/Root.wad")
            self.types_path = Path("../../types.json")
        
        # Verify paths exist
        if not self.wad_path.exists():
            print(f"[ERROR] WAD file not found: {self.wad_path}")
            return False
        
        if not self.types_path.exists():
            print(f"[ERROR] Types file not found: {self.types_path}")
            return False
        
        return True
    
    def _load_type_list(self) -> bool:
        """Load TypeList from types.json"""
        try:
            self.type_list = TypeList.open(str(self.types_path))
            print(f"[OK] Loaded type definitions from {self.types_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load type list: {e}")
            return False
    
    def _open_wad_archive(self) -> bool:
        """Open WAD archive file"""
        try:
            # Try memory mapping first, fall back to heap if needed
            try:
                self.archive = Archive.mmap(str(self.wad_path))
                print(f"[OK] Opened WAD archive (mmap): {self.wad_path}")
            except Exception:
                self.archive = Archive.heap(str(self.wad_path))
                print(f"[OK] Opened WAD archive (heap): {self.wad_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to open WAD archive: {e}")
            return False
    
    def _create_serializer(self) -> bool:
        """Create serializer with proper options"""
        try:
            options = SerializerOptions()
            options.shallow = False  # Allow deep serialization (required for skip_unknown_types)
            options.skip_unknown_types = True  # Equivalent to CLI --ignore-unknown-types
            self.serializer = Serializer(options, self.type_list)
            print("[OK] Created serializer with deep serialization and skip_unknown_types enabled")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create serializer: {e}")
            return False
    
    def discover_all_item_types(self) -> bool:
        """Main discovery function - search entire WAD for WizItemTemplates"""
        print("\nStarting Comprehensive Item Type Discovery...")
        print("=" * 60)
        print("SCOPE: Searching ENTIRE Root.wad archive (not just ObjectData)")
        print("TARGET: WizItemTemplate objects (hash: 991922385)")
        print("GOAL: Directory distribution + nested type analysis")
        print()
        
        try:
            # Get ALL XML files in WAD archive
            all_xml_files = list(self.archive.iter_glob("**/*.xml"))
            total_files = len(all_xml_files)
            
            print(f"Found {total_files} XML files in entire WAD archive")
            print("Processing files to discover WizItemTemplates...\n")
            
            # Process each file
            for i, file_path in enumerate(all_xml_files):
                self.total_files_processed += 1
                
                try:
                    self._process_single_file(file_path)
                except Exception as e:
                    error_info = {
                        "file": file_path,
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
                    self.processing_errors.append(error_info)
                    self.failed_files.append(file_path)
                
                # Progress reporting
                if self.total_files_processed % 5000 == 0:
                    progress = (self.total_files_processed / total_files) * 100
                    print(f"[PROGRESS] {self.total_files_processed}/{total_files} ({progress:.1f}%) - "
                          f"Found {self.total_items_found} WizItemTemplates in {len(self.directory_distribution)} directories")
            
            print(f"\n[COMPLETE] Discovery finished!")
            print(f"Total files processed: {self.total_files_processed}")
            print(f"WizItemTemplates found: {self.total_items_found}")
            print(f"Unique directories: {len(self.directory_distribution)}")
            print(f"Nested types discovered: {len(self.nested_types_found)}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Discovery failed: {e}")
            traceback.print_exc()
            return False
    
    def _process_single_file(self, file_path: str):
        """Process a single XML file to check for WizItemTemplate"""
        try:
            # Deserialize the file
            if self.serializer:
                obj_data = self.archive.deserialize(file_path, self.serializer)
            else:
                obj_data = self.archive[file_path]
            
            # Convert to dictionary if it's a LazyObject
            if isinstance(obj_data, LazyObject):
                obj_dict = convert_lazy_object_to_dict(obj_data, self.type_list)
            else:
                obj_dict = obj_data
            
            # Check if this is a WizItemTemplate
            if isinstance(obj_dict, dict) and obj_dict.get('$__type') == 'class WizItemTemplate':
                self._process_wizitem_template(file_path, obj_dict)
            else:
                self.total_non_items += 1
        
        except Exception as e:
            # Add to failed files but continue processing
            self.failed_files.append(file_path)
            if len(self.processing_errors) < 100:  # Limit error logging
                self.processing_errors.append({
                    "file": file_path,
                    "error": str(e)
                })
    
    def _process_wizitem_template(self, file_path: str, item_dict: Dict[str, Any]):
        """Process a discovered WizItemTemplate"""
        self.total_items_found += 1
        
        # Extract directory information
        directory = str(Path(file_path).parent)
        self.directory_distribution[directory].append(file_path)
        
        # Track ObjectData vs non-ObjectData locations
        if file_path.startswith("ObjectData/"):
            self.objectdata_items += 1
        else:
            self.non_objectdata_items += 1
            self.unexpected_locations.append(file_path)
            print(f"[SURPRISE] WizItemTemplate found outside ObjectData: {file_path}")
        
        # Store sample data (limited per directory)
        if len(self.directory_samples[directory]) < self.max_samples_per_dir:
            # Extract key item information for sample
            sample_item = {
                "file_path": file_path,
                "m_objectName": item_dict.get('m_objectName', 'N/A'),
                "m_displayName": item_dict.get('m_displayName', 'N/A'),
                "m_templateID": item_dict.get('m_templateID', 'N/A'),
                "m_nObjectType": item_dict.get('m_nObjectType', 'N/A'),
                "m_school": item_dict.get('m_school', 'N/A'),
                "m_rarity": item_dict.get('m_rarity', 'N/A')
            }
            self.directory_samples[directory].append(sample_item)
        
        # Discover nested types recursively
        self._discover_nested_types(item_dict, "WizItemTemplate")
    
    def _discover_nested_types(self, obj: Any, parent_path: str = "", depth: int = 0):
        """Recursively discover all nested class types"""
        if depth > 10:  # Prevent infinite recursion
            return
        
        if isinstance(obj, dict):
            # Check if this dictionary has a type
            obj_type = obj.get('$__type')
            if obj_type and obj_type.startswith('class '):
                class_name = obj_type.replace('class ', '')
                self.nested_types_found.add(class_name)
                self.nested_type_counts[class_name] += 1
                
                # Store sample data for this type (limited)
                if len(self.nested_type_samples[class_name]) < 3:
                    # Store a simplified version of the object
                    sample_data = {}
                    for key, value in obj.items():
                        if not key.startswith('$__') and not isinstance(value, (list, dict)):
                            sample_data[key] = value
                    
                    self.nested_type_samples[class_name].append({
                        "parent_path": parent_path,
                        "sample_data": sample_data
                    })
            
            # Recurse into dictionary values
            for key, value in obj.items():
                if not key.startswith('$__'):  # Skip metadata
                    new_path = f"{parent_path}.{key}" if parent_path else key
                    self._discover_nested_types(value, new_path, depth + 1)
        
        elif isinstance(obj, list):
            # Recurse into list items
            for i, item in enumerate(obj[:5]):  # Limit to first 5 items for performance
                new_path = f"{parent_path}[{i}]" if parent_path else f"item[{i}]"
                self._discover_nested_types(item, new_path, depth + 1)
    
    def analyze_directory_distribution(self):
        """Analyze the distribution of items across directories"""
        print("\nAnalyzing Directory Distribution...")
        
        # Sort directories by item count
        sorted_dirs = sorted(
            self.directory_distribution.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        print(f"WizItemTemplates found in {len(sorted_dirs)} unique directories:")
        print("=" * 60)
        
        for directory, file_list in sorted_dirs[:20]:  # Show top 20
            count = len(file_list)
            print(f"{directory}: {count} items")
        
        if len(sorted_dirs) > 20:
            print(f"... and {len(sorted_dirs) - 20} more directories")
        
        self.unique_directories = len(sorted_dirs)
    
    def generate_comprehensive_reports(self) -> bool:
        """Generate all discovery reports"""
        print(f"\nGenerating Comprehensive Reports...")
        print(f"Reports will be saved to: {self.reports_dir}")
        
        try:
            # Generate individual reports
            self._generate_discovery_summary_report()
            self._generate_directory_distribution_report()
            self._generate_nested_types_analysis_report()
            self._generate_sample_items_report()
            self._generate_location_analysis_report()
            self._generate_dto_development_roadmap()
            
            print(f"[OK] All reports generated successfully in {self.reports_dir}")
            return True
        
        except Exception as e:
            print(f"[ERROR] Report generation failed: {e}")
            traceback.print_exc()
            return False
    
    def _generate_discovery_summary_report(self):
        """Generate main discovery summary report"""
        report_path = self.reports_dir / "item_discovery_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("WizItemTemplate Comprehensive Discovery Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Target Type: WizItemTemplate (hash: {self.WIZITEMTEMPLATE_HASH})\n")
            f.write(f"Search Scope: Entire Root.wad archive\n\n")
            
            f.write("DISCOVERY SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total XML files processed: {self.total_files_processed:,}\n")
            f.write(f"WizItemTemplates found: {self.total_items_found:,}\n")
            f.write(f"Non-item objects: {self.total_non_items:,}\n")
            f.write(f"Processing errors: {len(self.processing_errors)}\n")
            f.write(f"Success rate: {(self.total_items_found / max(1, self.total_files_processed)) * 100:.3f}%\n\n")
            
            f.write("LOCATION ANALYSIS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Items in ObjectData/: {self.objectdata_items:,}\n")
            f.write(f"Items outside ObjectData/: {self.non_objectdata_items:,}\n")
            f.write(f"Unique directories: {self.unique_directories}\n\n")
            
            f.write("TYPE DISCOVERY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Nested class types found: {len(self.nested_types_found)}\n")
            f.write(f"Most common nested types:\n")
            for type_name, count in self.nested_type_counts.most_common(15):
                f.write(f"  - {type_name}: {count:,} occurrences\n")
            
            if self.unexpected_locations:
                f.write(f"\nUNEXPECTED LOCATIONS\n")
                f.write("-" * 20 + "\n")
                f.write("WizItemTemplates found outside ObjectData/:\n")
                for location in self.unexpected_locations[:10]:
                    f.write(f"  - {location}\n")
                if len(self.unexpected_locations) > 10:
                    f.write(f"  ... and {len(self.unexpected_locations) - 10} more\n")
    
    def _generate_directory_distribution_report(self):
        """Generate detailed directory distribution report"""
        report_path = self.reports_dir / "directory_distribution.txt"
        
        # Sort directories by count
        sorted_dirs = sorted(
            self.directory_distribution.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("WizItemTemplate Directory Distribution Analysis\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Total Directories: {len(sorted_dirs)}\n")
            f.write(f"Total Items: {self.total_items_found:,}\n\n")
            
            f.write("COMPLETE DIRECTORY LISTING\n")
            f.write("-" * 30 + "\n")
            f.write("Format: Directory → Count → Example Files\n\n")
            
            for directory, file_list in sorted_dirs:
                count = len(file_list)
                f.write(f"{directory}: {count} items\n")
                
                # Show sample files from this directory
                sample_files = file_list[:3]  # First 3 files
                for sample_file in sample_files:
                    f.write(f"  Example: {Path(sample_file).name}\n")
                
                if len(file_list) > 3:
                    f.write(f"  ... and {len(file_list) - 3} more files\n")
                f.write("\n")
    
    def _generate_nested_types_analysis_report(self):
        """Generate comprehensive nested types analysis"""
        report_path = self.reports_dir / "nested_types_analysis.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("WizItemTemplate Nested Types Analysis\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Total Nested Types Discovered: {len(self.nested_types_found)}\n\n")
            
            f.write("ALL DISCOVERED NESTED TYPES\n")
            f.write("-" * 30 + "\n")
            f.write("Format: TypeName (Frequency) → Usage Context\n\n")
            
            # Sort by frequency
            sorted_types = self.nested_type_counts.most_common()
            
            for type_name, count in sorted_types:
                f.write(f"{type_name} ({count:,} occurrences)\n")
                
                # Show sample usage context
                if type_name in self.nested_type_samples:
                    samples = self.nested_type_samples[type_name]
                    for sample in samples[:2]:  # Show first 2 samples
                        f.write(f"  Context: {sample['parent_path']}\n")
                        if sample['sample_data']:
                            # Show a few key fields
                            sample_fields = list(sample['sample_data'].items())[:3]
                            for key, value in sample_fields:
                                f.write(f"    {key}: {value}\n")
                f.write("\n")
            
            f.write("\nDTO DEVELOPMENT PRIORITIES\n")
            f.write("-" * 25 + "\n")
            f.write("Types ordered by frequency (implement most common first):\n\n")
            
            for i, (type_name, count) in enumerate(sorted_types[:30], 1):
                f.write(f"{i:2d}. {type_name} ({count:,} uses)\n")
    
    def _generate_sample_items_report(self):
        """Generate sample items from each directory"""
        report_path = self.reports_dir / "sample_items.json"
        
        # Prepare sample data structure
        sample_data = {
            "generation_info": {
                "timestamp": str(datetime.now()),
                "total_directories": len(self.directory_samples),
                "total_items_sampled": sum(len(samples) for samples in self.directory_samples.values())
            },
            "samples_by_directory": {}
        }
        
        # Add samples from each directory
        for directory, samples in self.directory_samples.items():
            sample_data["samples_by_directory"][directory] = {
                "item_count": len(self.directory_distribution[directory]),
                "samples": samples
            }
        
        # Write JSON report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, default=str)
    
    def _generate_location_analysis_report(self):
        """Generate analysis of item locations"""
        report_path = self.reports_dir / "location_analysis.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("WizItemTemplate Location Analysis\n")
            f.write("=" * 35 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            f.write("LOCATION DISTRIBUTION\n")
            f.write("-" * 20 + "\n")
            f.write(f"ObjectData/ items: {self.objectdata_items:,} ({(self.objectdata_items/max(1,self.total_items_found))*100:.1f}%)\n")
            f.write(f"Non-ObjectData/ items: {self.non_objectdata_items:,} ({(self.non_objectdata_items/max(1,self.total_items_found))*100:.1f}%)\n\n")
            
            if self.unexpected_locations:
                f.write("UNEXPECTED LOCATIONS (Items found outside ObjectData/)\n")
                f.write("-" * 50 + "\n")
                f.write("These locations were surprising discoveries:\n\n")
                
                for location in self.unexpected_locations:
                    f.write(f"  - {location}\n")
                
                f.write(f"\nTotal unexpected locations: {len(self.unexpected_locations)}\n")
            else:
                f.write("NO UNEXPECTED LOCATIONS\n")
                f.write("-" * 25 + "\n")
                f.write("All WizItemTemplates were found in ObjectData/ as expected.\n")
            
            # Analyze ObjectData subdirectories
            objectdata_dirs = {}
            for directory, files in self.directory_distribution.items():
                if directory.startswith("ObjectData/"):
                    subdir = directory.split('/')[1] if '/' in directory else "root"
                    objectdata_dirs[subdir] = objectdata_dirs.get(subdir, 0) + len(files)
            
            if objectdata_dirs:
                f.write("\nOBJECTDATA SUBDIRECTORY BREAKDOWN\n")
                f.write("-" * 35 + "\n")
                sorted_subdirs = sorted(objectdata_dirs.items(), key=lambda x: x[1], reverse=True)
                for subdir, count in sorted_subdirs:
                    f.write(f"  {subdir}/: {count:,} items\n")
    
    def _generate_dto_development_roadmap(self):
        """Generate DTO development roadmap based on discoveries"""
        report_path = self.reports_dir / "dto_development_roadmap.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("WizItemTemplate DTO Development Roadmap\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("Based on comprehensive type discovery analysis\n\n")
            
            f.write("IMPLEMENTATION PHASES\n")
            f.write("-" * 20 + "\n\n")
            
            # Phase 1: Core types
            f.write("PHASE 1: Core Item Types (Implement First)\n")
            f.write("-" * 45 + "\n")
            core_types = ["WizItemTemplate", "WizAvatarItemInfo", "AvatarTextureOption", 
                         "RequirementList", "BehaviorTemplate"]
            for type_name in core_types:
                count = self.nested_type_counts.get(type_name, 0)
                f.write(f"  - {type_name} ({count:,} uses)\n")
            
            # Phase 2: Behavior types
            f.write("\nPHASE 2: Behavior Types\n")
            f.write("-" * 25 + "\n")
            behavior_types = [t for t in self.nested_types_found if "Behavior" in t and t != "BehaviorTemplate"]
            behavior_types.sort(key=lambda x: self.nested_type_counts[x], reverse=True)
            for type_name in behavior_types[:10]:
                count = self.nested_type_counts[type_name]
                f.write(f"  - {type_name} ({count:,} uses)\n")
            
            # Phase 3: Supporting types
            f.write("\nPHASE 3: Supporting Types\n")
            f.write("-" * 25 + "\n")
            supporting_types = [t for t in self.nested_types_found 
                              if t not in core_types and "Behavior" not in t]
            supporting_types.sort(key=lambda x: self.nested_type_counts[x], reverse=True)
            for type_name in supporting_types[:15]:
                count = self.nested_type_counts[type_name]
                f.write(f"  - {type_name} ({count:,} uses)\n")
            
            f.write(f"\nTOTAL TYPES TO IMPLEMENT: {len(self.nested_types_found)}\n")
            f.write(f"ESTIMATED DEVELOPMENT TIME: {len(self.nested_types_found) // 5} - {len(self.nested_types_found) // 3} days\n")
            f.write("(Based on 3-5 DTOs per day development rate)\n")
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get comprehensive discovery statistics"""
        return {
            "total_files_processed": self.total_files_processed,
            "total_items_found": self.total_items_found,
            "total_non_items": self.total_non_items,
            "unique_directories": len(self.directory_distribution),
            "nested_types_found": len(self.nested_types_found),
            "objectdata_items": self.objectdata_items,
            "non_objectdata_items": self.non_objectdata_items,
            "unexpected_locations_count": len(self.unexpected_locations),
            "processing_errors": len(self.processing_errors),
            "success_rate": (self.total_items_found / max(1, self.total_files_processed)) * 100
        }
    
    def cleanup(self):
        """Clean up resources"""
        if self.archive:
            # Archive cleanup is handled by katsuba
            pass
        
        self.archive = None
        self.type_list = None
        self.serializer = None
        print("[OK] Item Type Discoverer cleanup completed")


def main():
    """Main execution function"""
    print("WizItemTemplate Comprehensive Type Discovery")
    print("=" * 50)
    print("Searching ENTIRE Root.wad for WizItemTemplate objects")
    print("Analyzing directory distribution and nested types")
    print()
    
    # Create discoverer
    discoverer = ItemTypeDiscoverer()
    
    try:
        # Initialize
        if not discoverer.initialize():
            print("[ERROR] Failed to initialize discoverer")
            return False
        
        # Run discovery
        if not discoverer.discover_all_item_types():
            print("[ERROR] Discovery process failed")
            return False
        
        # Analyze results
        discoverer.analyze_directory_distribution()
        
        # Generate reports
        if not discoverer.generate_comprehensive_reports():
            print("[ERROR] Report generation failed")
            return False
        
        # Print final statistics
        stats = discoverer.get_discovery_statistics()
        print("\n" + "=" * 60)
        print("FINAL DISCOVERY STATISTICS")
        print("=" * 60)
        print(f"Files processed: {stats['total_files_processed']:,}")
        print(f"WizItemTemplates found: {stats['total_items_found']:,}")
        print(f"Unique directories: {stats['unique_directories']}")
        print(f"Nested types discovered: {stats['nested_types_found']}")
        print(f"ObjectData items: {stats['objectdata_items']:,}")
        print(f"Non-ObjectData items: {stats['non_objectdata_items']:,}")
        print(f"Success rate: {stats['success_rate']:.3f}%")
        
        if stats['non_objectdata_items'] > 0:
            print(f"\n🎉 SURPRISE: Found {stats['non_objectdata_items']} WizItemTemplates outside ObjectData!")
        else:
            print(f"\n✅ All WizItemTemplates found in ObjectData/ as expected")
        
        print(f"\n📁 Reports saved to: {discoverer.reports_dir}")
        print("\nDiscovery complete! Check reports for detailed analysis.")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Discovery failed: {e}")
        traceback.print_exc()
        return False
    
    finally:
        discoverer.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)