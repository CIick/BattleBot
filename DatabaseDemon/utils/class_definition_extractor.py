#!/usr/bin/env python3
"""
Universal Class Definition Extractor
====================================
Universal tool for extracting class definitions from types.json file and saving
them as individual reference files for DTO development.

Features:
- Extract single class or batch extract multiple classes
- Read class lists from discovery reports
- Smart JSON parsing with proper brace matching
- Organized output with consistent naming
- Comprehensive error handling and reporting

Usage:
    extractor = ClassDefinitionExtractor("types.json", "Reference Material/Items/")
    extractor.extract_multiple_classes(["WizItemTemplate", "AvatarTextureOption"])
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import argparse
import traceback


class ClassDefinitionExtractor:
    """Universal extractor for class definitions from types.json"""
    
    def __init__(self, types_json_path: Path, output_base_path: Path, debug: bool = False):
        """
        Initialize the class definition extractor
        
        Args:
            types_json_path: Path to types.json file
            output_base_path: Base path for output files (e.g., "Reference Material/Items/")
            debug: Enable debug output for troubleshooting
        """
        self.types_json_path = Path(types_json_path)
        self.output_base_path = Path(output_base_path)
        self.debug = debug
        
        # Create output directory structure
        self.extracts_dir = self.output_base_path / "Item Type Extracts"
        self.extracts_dir.mkdir(parents=True, exist_ok=True)
        
        # Data storage
        self.types_content = ""
        self.types_data = {}
        self.extraction_results = {}
        
        # Statistics
        self.total_requested = 0
        self.total_extracted = 0
        self.total_failed = 0
        self.extraction_errors = []
        
    def load_types_data(self) -> bool:
        """Load types.json content for processing"""
        try:
            if not self.types_json_path.exists():
                print(f"[ERROR] Types file not found: {self.types_json_path}")
                return False
            
            print(f"Loading types data from: {self.types_json_path}")
            
            # Load as text for pattern matching
            with open(self.types_json_path, 'r', encoding='utf-8') as f:
                self.types_content = f.read()
            
            # Also load as JSON for validation
            with open(self.types_json_path, 'r', encoding='utf-8') as f:
                self.types_data = json.load(f)
            
            print(f"[OK] Loaded types data ({len(self.types_content):,} characters)")
            print(f"[OK] Found {len(self.types_data):,} type definitions")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load types data: {e}")
            traceback.print_exc()
            return False
    
    def extract_class_definition(self, class_name: str) -> Optional[str]:
        """
        Extract a single class definition from types.json
        
        Args:
            class_name: Name of the class to extract (without "class " prefix)
            
        Returns:
            Complete JSON definition as string, or None if not found
        """
        try:
            # Search pattern: "name": "class ClassName"
            pattern = rf'"name":\s*"class\s+{re.escape(class_name)}"'
            
            # Find the pattern in the content
            match = re.search(pattern, self.types_content)
            if not match:
                print(f"[WARNING] Class '{class_name}' not found in types.json")
                return None
            
            # Find the start of the class definition (opening brace of the hash object)
            # We need to find the opening brace that contains this "name" field
            start_pos = match.start()
            
            # Search backwards to find the opening brace of the hash object
            hash_start = -1
            brace_count = 0
            pos = start_pos - 1
            
            while pos >= 0:
                char = self.types_content[pos]
                if char == '}':
                    brace_count += 1
                elif char == '{':
                    if brace_count == 0:
                        hash_start = pos
                        break
                    brace_count -= 1
                pos -= 1
            
            if hash_start == -1:
                print(f"[ERROR] Could not find opening brace for class '{class_name}'")
                return None
            
            # Now find the matching closing brace
            brace_count = 0
            hash_end = -1
            pos = hash_start
            in_string = False
            escape_next = False
            
            while pos < len(self.types_content):
                char = self.types_content[pos]
                
                # Handle string escaping
                if escape_next:
                    escape_next = False
                elif char == '\\' and in_string:
                    escape_next = True
                elif char == '"' and not escape_next:
                    in_string = not in_string
                elif not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            hash_end = pos
                            break
                
                pos += 1
            
            if hash_end == -1:
                print(f"[ERROR] Could not find closing brace for class '{class_name}'")
                return None
            
            # Extract the complete class definition
            class_definition = self.types_content[hash_start:hash_end + 1]
            
            # Validate that it's proper JSON
            try:
                json.loads(class_definition)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Extracted definition for '{class_name}' is not valid JSON: {e}")
                return None
            
            return class_definition
            
        except Exception as e:
            print(f"[ERROR] Failed to extract class '{class_name}': {e}")
            traceback.print_exc()
            return None
    
    def save_class_definition(self, class_name: str, definition: str, output_path: Optional[Path] = None) -> bool:
        """
        Save class definition to file
        
        Args:
            class_name: Name of the class
            definition: JSON definition string
            output_path: Optional custom output path
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            if output_path is None:
                output_path = self.extracts_dir / f"{class_name}_extract.txt"
            
            # Format the JSON nicely
            json_obj = json.loads(definition)
            formatted_json = json.dumps(json_obj, indent=4, ensure_ascii=False)
            
            # Create header
            header = f"Class Definition Extract: {class_name}\n"
            header += "=" * (len(header) - 1) + "\n"
            header += f"Extracted: {datetime.now()}\n"
            header += f"Source: {self.types_json_path.name}\n"
            header += f"Hash: {json_obj.get('hash', 'unknown')}\n\n"
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(header)
                f.write(formatted_json)
            
            print(f"[OK] Saved {class_name} → {output_path.name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save class '{class_name}': {e}")
            return False
    
    def extract_multiple_classes(self, class_list: List[str], auto_save: bool = True) -> Dict[str, Optional[str]]:
        """
        Extract multiple class definitions
        
        Args:
            class_list: List of class names to extract
            auto_save: Whether to automatically save extracted definitions
            
        Returns:
            Dictionary mapping class names to their definitions (or None if failed)
        """
        print(f"\nExtracting {len(class_list)} class definitions...")
        print("=" * 50)
        
        results = {}
        self.total_requested = len(class_list)
        
        for i, class_name in enumerate(class_list, 1):
            print(f"[{i:3d}/{len(class_list)}] Extracting {class_name}...")
            
            try:
                definition = self.extract_class_definition(class_name)
                
                if definition:
                    results[class_name] = definition
                    self.total_extracted += 1
                    
                    if auto_save:
                        if self.save_class_definition(class_name, definition):
                            self.extraction_results[class_name] = "success"
                        else:
                            self.extraction_results[class_name] = "save_failed"
                            self.total_failed += 1
                    else:
                        self.extraction_results[class_name] = "extracted"
                else:
                    results[class_name] = None
                    self.extraction_results[class_name] = "not_found"
                    self.total_failed += 1
            
            except Exception as e:
                results[class_name] = None
                self.extraction_results[class_name] = f"error: {str(e)}"
                self.extraction_errors.append({
                    "class_name": class_name,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                self.total_failed += 1
        
        print(f"\n[COMPLETE] Extraction finished:")
        print(f"  Requested: {self.total_requested}")
        print(f"  Extracted: {self.total_extracted}")
        print(f"  Failed: {self.total_failed}")
        print(f"  Success Rate: {(self.total_extracted/max(1,self.total_requested))*100:.1f}%")
        
        return results
    
    def parse_nested_types_report(self, report_path: Path) -> List[str]:
        """
        Parse class names from nested_types_analysis.txt report
        
        Args:
            report_path: Path to nested types analysis report
            
        Returns:
            List of class names found in the report
        """
        try:
            class_names = []
            
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for pattern: "ClassName (count occurrences)" or "ClassName (count uses)"
            pattern = r'^([A-Za-z][A-Za-z0-9_]*)\s+\(\d+[\s,]*(?:occurrences?|uses)\)'
            
            for line in content.split('\n'):
                line = line.strip()
                match = re.match(pattern, line)
                if match:
                    class_name = match.group(1)
                    class_names.append(class_name)
                    if self.debug:
                        print(f"[DEBUG] Parsed from report: '{line}' -> '{class_name}'")
            
            print(f"[OK] Parsed {len(class_names)} class names from {report_path.name}")
            return class_names
            
        except Exception as e:
            print(f"[ERROR] Failed to parse report {report_path}: {e}")
            return []
    
    def parse_class_list_file(self, list_path: Path) -> List[str]:
        """
        Parse class names from a simple list file (one per line)
        
        Args:
            list_path: Path to file containing class names (one per line)
            
        Returns:
            List of class names
        """
        try:
            class_names = []
            
            with open(list_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    original_line = line.strip()
                    
                    # Skip empty lines and comment-only lines
                    if not original_line or original_line.startswith('#'):
                        continue
                    
                    # Extract just the class name (before any comment)
                    # Handle formats like: "ClassName  # 123 uses"
                    class_name = original_line.split('#')[0].strip()
                    
                    if class_name:  # Only add non-empty class names
                        class_names.append(class_name)
                        if self.debug:
                            print(f"[DEBUG] Line {line_num}: '{original_line}' -> '{class_name}'")
            
            print(f"[OK] Read {len(class_names)} class names from {list_path.name}")
            return class_names
            
        except Exception as e:
            print(f"[ERROR] Failed to read class list {list_path}: {e}")
            return []
    
    def generate_extraction_report(self, output_path: Optional[Path] = None) -> bool:
        """
        Generate comprehensive extraction report
        
        Args:
            output_path: Optional custom output path for report
            
        Returns:
            True if report generated successfully
        """
        try:
            if output_path is None:
                output_path = self.extracts_dir / "extraction_report.txt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Class Definition Extraction Report\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(f"Source: {self.types_json_path}\n")
                f.write(f"Output Directory: {self.extracts_dir}\n\n")
                
                f.write("EXTRACTION SUMMARY\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total Requested: {self.total_requested}\n")
                f.write(f"Successfully Extracted: {self.total_extracted}\n")
                f.write(f"Failed Extractions: {self.total_failed}\n")
                f.write(f"Success Rate: {(self.total_extracted/max(1,self.total_requested))*100:.1f}%\n\n")
                
                if self.extraction_results:
                    f.write("DETAILED RESULTS\n")
                    f.write("-" * 20 + "\n")
                    
                    # Group by status
                    status_groups = {}
                    for class_name, status in self.extraction_results.items():
                        if status not in status_groups:
                            status_groups[status] = []
                        status_groups[status].append(class_name)
                    
                    for status, classes in status_groups.items():
                        f.write(f"\n{status.upper()} ({len(classes)}):\n")
                        for class_name in sorted(classes):
                            f.write(f"  - {class_name}\n")
                
                if self.extraction_errors:
                    f.write(f"\nERRORS ({len(self.extraction_errors)})\n")
                    f.write("-" * 20 + "\n")
                    for error in self.extraction_errors:
                        f.write(f"Class: {error['class_name']}\n")
                        f.write(f"Error: {error['error']}\n\n")
            
            print(f"[OK] Extraction report saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to generate extraction report: {e}")
            return False
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return {
            "total_requested": self.total_requested,
            "total_extracted": self.total_extracted,
            "total_failed": self.total_failed,
            "success_rate": (self.total_extracted / max(1, self.total_requested)) * 100,
            "extraction_results": dict(self.extraction_results),
            "extraction_errors": list(self.extraction_errors)
        }


def main():
    """Command line interface for the class definition extractor"""
    parser = argparse.ArgumentParser(
        description="Extract class definitions from types.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract single class
  python class_definition_extractor.py --class "WizItemTemplate" --output "Reference Material/Items/"
  
  # Extract from discovery report
  python class_definition_extractor.py --from-report "Reports/Item Reports/nested_types_analysis.txt"
  
  # Extract from list file
  python class_definition_extractor.py --from-list "class_list.txt"
        """
    )
    
    parser.add_argument("--types-json", "-t", 
                       default="../types.json",
                       help="Path to types.json file (default: ../types.json)")
    
    parser.add_argument("--output", "-o",
                       default="../../Reference Material/Items/",
                       help="Output base directory (default: ../../Reference Material/Items/)")
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--class", "-c", dest="single_class",
                            help="Extract single class by name")
    
    input_group.add_argument("--from-report", "-r",
                            help="Extract classes from nested_types_analysis.txt report")
    
    input_group.add_argument("--from-list", "-l", 
                            help="Extract classes from list file (one per line)")
    
    input_group.add_argument("--classes", nargs="+",
                            help="Extract multiple classes (space separated)")
    
    parser.add_argument("--no-save", action="store_true",
                       help="Don't save extracted definitions to files")
    
    parser.add_argument("--no-report", action="store_true",
                       help="Don't generate extraction report")
    
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug output for troubleshooting")
    
    args = parser.parse_args()
    
    try:
        print("Universal Class Definition Extractor")
        print("=" * 40)
        
        # Create extractor
        extractor = ClassDefinitionExtractor(
            types_json_path=Path(args.types_json),
            output_base_path=Path(args.output),
            debug=args.debug
        )
        
        # Load types data
        if not extractor.load_types_data():
            print("[ERROR] Failed to load types data")
            return False
        
        # Determine class list to extract
        class_list = []
        
        if args.single_class:
            class_list = [args.single_class]
            print(f"Extracting single class: {args.single_class}")
        
        elif args.from_report:
            report_path = Path(args.from_report)
            class_list = extractor.parse_nested_types_report(report_path)
            print(f"Extracting classes from report: {report_path}")
        
        elif args.from_list:
            list_path = Path(args.from_list)
            class_list = extractor.parse_class_list_file(list_path)
            print(f"Extracting classes from list: {list_path}")
        
        elif args.classes:
            class_list = args.classes
            print(f"Extracting {len(class_list)} specified classes")
        
        if not class_list:
            print("[ERROR] No classes to extract")
            return False
        
        # Extract classes
        results = extractor.extract_multiple_classes(class_list, auto_save=not args.no_save)
        
        # Generate report
        if not args.no_report:
            extractor.generate_extraction_report()
        
        # Print summary
        stats = extractor.get_extraction_statistics()
        print(f"\nFinal Statistics:")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        print(f"  Output Directory: {extractor.extracts_dir}")
        
        return stats['total_failed'] == 0
        
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)