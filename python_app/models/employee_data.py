"""
Employee Data Models
Contains data structures and models for employee information
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd


@dataclass
class EmployeeRecord:
    """Represents a single employee record"""
    pernr: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    user_id: Optional[str] = None
    resignation_date: Optional[str] = None
    position_name: Optional[str] = None
    segment_name: Optional[str] = None
    group_name: Optional[str] = None
    area_division_name: Optional[str] = None
    department_branch: Optional[str] = None
    match_type: Optional[str] = None
    match_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation"""
        return {
            'PERNR': self.pernr,
            'Full Name (From Masterlist)': self.full_name,
            'Resignation Date': self.resignation_date,
            'Position Name': self.position_name,
            'Segment Name': self.segment_name,
            'Group Name': self.group_name,
            'Area/Division Name': self.area_division_name,
            'Department/Branch': self.department_branch,
            'Match Type': self.match_type,
            'Match Score': self.match_score
        }


class EmployeeDataset:
    """Manages collections of employee data"""
    
    def __init__(self):
        # Source data files
        self.current_system: Optional[pd.DataFrame] = None
        self.previous_reference: Optional[pd.DataFrame] = None
        self.masterlist_current: Optional[pd.DataFrame] = None
        self.masterlist_resigned: Optional[pd.DataFrame] = None
        
        # Processed data
        self.cleaned_data: Optional[pd.DataFrame] = None
        self.unmatched_data: Optional[pd.DataFrame] = None
        self.fuzzy_matched_data: Optional[pd.DataFrame] = None
        
        # File paths for reference
        self.file_paths: Dict[str, Optional[str]] = {
            'current_system': None,
            'previous_reference': None,
            'masterlist_current': None,
            'masterlist_resigned': None
        }
    
    def is_ready_for_processing(self) -> bool:
        """Check if all required files are loaded"""
        return all([
            self.current_system is not None,
            self.masterlist_current is not None,
            self.masterlist_resigned is not None
        ])
    
    def get_statistics(self) -> Dict[str, int]:
        """Get processing statistics"""
        total = len(self.current_system) if self.current_system is not None else 0
        
        # Calculate matched records (those with PERNR)
        matched = 0
        if self.cleaned_data is not None:
            matched = len(self.cleaned_data[self.cleaned_data['PERNR'].notna()])
        
        unmatched = len(self.unmatched_data) if self.unmatched_data is not None else 0
        fuzzy_matched = len(self.fuzzy_matched_data) if self.fuzzy_matched_data is not None else 0
        
        return {
            'total': total,
            'matched': matched,
            'unmatched': unmatched,
            'fuzzy_matched': fuzzy_matched
        }
    
    def clear_all_data(self):
        """Clear all data and reset the dataset"""
        self.current_system = None
        self.previous_reference = None
        self.masterlist_current = None
        self.masterlist_resigned = None
        self.cleaned_data = None
        self.unmatched_data = None
        self.fuzzy_matched_data = None
        
        for key in self.file_paths.keys():
            self.file_paths[key] = None
    
    def get_missing_files(self) -> list:
        """Get list of missing required files"""
        missing = []
        if self.current_system is None:
            missing.append('Current System Report')
        if self.masterlist_current is None:
            missing.append('Masterlist – Current')
        if self.masterlist_resigned is None:
            missing.append('Masterlist – Resigned')
        return missing
