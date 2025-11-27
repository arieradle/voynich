#!/usr/bin/env python3
"""
Iteration File Manager
Ensures consistent naming and location for all iteration-related files.
"""

from pathlib import Path
from typing import Optional

# Standard locations
ITERATIONS_DIR = Path("data/iterations")
DOCS_DIR = Path("docs")
BACKUPS_DIR = Path(".")  # Dictionary backups stay in root

def get_iteration_file_path(iteration_num: int, file_type: str) -> Path:
    """
    Get standardized path for iteration files.
    
    Args:
        iteration_num: Iteration number (5, 6, 7, etc.)
        file_type: Type of file ('candidates', 'proposals', 'extended', 'high_priority')
    
    Returns:
        Path: Full path to the file
    
    Example:
        >>> get_iteration_file_path(8, 'candidates')
        Path('data/iterations/iter8_candidates.json')
    """
    ITERATIONS_DIR.mkdir(parents=True, exist_ok=True)
    return ITERATIONS_DIR / f"iter{iteration_num}_{file_type}.json"

def get_iteration_report_path(iteration_num: int) -> Path:
    """Get path for iteration report document."""
    return DOCS_DIR / f"ITERATION_{iteration_num}_REPORT.md"

def get_dictionary_backup_path(iteration_num: int, timestamp: Optional[str] = None) -> Path:
    """Get path for dictionary backup."""
    if timestamp:
        return BACKUPS_DIR / f"voynich.yaml.backup-iter{iteration_num}-{timestamp}"
    else:
        # For pattern matching
        return BACKUPS_DIR / f"voynich.yaml.backup-iter{iteration_num}-*"

# Usage examples for scripts:
"""
# In word_frequency.py:
from iteration_file_manager import get_iteration_file_path
output_path = get_iteration_file_path(9, 'candidates')

# In batch_dictionary_updater.py:
from iteration_file_manager import get_iteration_file_path
proposals_path = get_iteration_file_path(9, 'proposals')

# For reports:
from iteration_file_manager import get_iteration_report_path
report_path = get_iteration_report_path(9)
"""

if __name__ == "__main__":
    # Demonstrate usage
    print("Iteration File Manager")
    print("=" * 60)
    print("\nStandard paths for Iteration 9:")
    print(f"  Candidates:   {get_iteration_file_path(9, 'candidates')}")
    print(f"  Extended:     {get_iteration_file_path(9, 'extended')}")
    print(f"  Proposals:    {get_iteration_file_path(9, 'proposals')}")
    print(f"  High Priority:{get_iteration_file_path(9, 'high_priority')}")
    print(f"  Report:       {get_iteration_report_path(9)}")
    print(f"  Dict Backup:  {get_dictionary_backup_path(9, '20251127-220000')}")
    print("\nAll iteration data files go in: data/iterations/")
    print("All reports go in: docs/")
    print("Dictionary backups stay in: . (root)")

