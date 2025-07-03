#!/usr/bin/env python3
"""
Wizard101 Revision Detector
===========================
Utility for detecting the current Wizard101 revision from revision.dat file.
"""

import os
import platform
from pathlib import Path
from typing import Optional


class RevisionDetector:
    """Detects Wizard101 revision from system files"""
    
    def __init__(self, revision_path: Optional[Path] = None):
        """Initialize with optional custom revision.dat path"""
        self.revision_path = revision_path
        if not self.revision_path:
            self._auto_detect_revision_path()
    
    def _auto_detect_revision_path(self):
        """Auto-detect platform-specific path to revision.dat"""
        system = platform.system().lower()
        
        if system == "windows":
            self.revision_path = Path("C:/ProgramData/KingsIsle Entertainment/Wizard101/Bin/revision.dat")
        else:  # Linux or other (WSL)
            self.revision_path = Path("/mnt/c/ProgramData/KingsIsle Entertainment/Wizard101/Bin/revision.dat")
    
    def get_revision(self) -> Optional[str]:
        """
        Get the current Wizard101 revision
        
        Returns:
            Revision string (e.g., "r777820") or None if not found
        """
        try:
            if not self.revision_path.exists():
                print(f"Warning: Revision file not found at {self.revision_path}")
                return None
            
            # Read the revision.dat file
            with open(self.revision_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
            
            # The revision.dat file typically contains just the revision number
            # It might be in format like "777820" or "r777820"
            revision = content.strip()
            
            # Ensure it starts with 'r' prefix
            if revision and not revision.startswith('r'):
                revision = f"r{revision}"
            
            if revision:
                print(f"[OK] Detected Wizard101 revision: {revision}")
                return revision
            else:
                print("Warning: Empty revision file")
                return None
                
        except Exception as e:
            print(f"Error reading revision file: {e}")
            return None
    
    def get_revision_for_database_name(self) -> str:
        """
        Get revision formatted for database naming
        
        Returns:
            Revision string for database name (e.g., "r777820") or "unknown" if not found
        """
        revision = self.get_revision()
        return revision if revision else "unknown"
    
    def validate_types_compatibility(self, types_path: Path) -> bool:
        """
        Validate that the types.json file is compatible with the current revision
        
        Args:
            types_path: Path to the types.json file
            
        Returns:
            True if compatible (or cannot determine), False if definitely incompatible
        """
        revision = self.get_revision()
        if not revision:
            print("Warning: Cannot determine revision for types compatibility check")
            return True  # Assume compatible if we can't determine
        
        if not types_path.exists():
            print(f"Error: Types file not found at {types_path}")
            return False
        
        # Check if the types filename contains the revision
        types_filename = types_path.name
        if revision in types_filename:
            print(f"[OK] Types file appears compatible with revision {revision}")
            return True
        else:
            print(f"Warning: Types file '{types_filename}' may not match revision {revision}")
            print("Check if the type dump (types.json) is the correct version for this revision")
            return True  # Don't fail hard, just warn
    
    def suggest_database_name(self, prefix: str = "spells") -> str:
        """
        Suggest a database name based on the current revision
        
        Args:
            prefix: Database name prefix (default: "spells")
            
        Returns:
            Suggested database name (e.g., "r777820_spells.db")
        """
        revision = self.get_revision_for_database_name()
        return f"{revision}_{prefix}.db"


# Convenience functions
def get_current_revision() -> Optional[str]:
    """Get current Wizard101 revision"""
    detector = RevisionDetector()
    return detector.get_revision()


def get_database_name(prefix: str = "spells") -> str:
    """Get suggested database name for current revision"""
    detector = RevisionDetector()
    return detector.suggest_database_name(prefix)


def validate_types_file(types_path: Path) -> bool:
    """Validate types file compatibility with current revision"""
    detector = RevisionDetector()
    return detector.validate_types_compatibility(types_path)