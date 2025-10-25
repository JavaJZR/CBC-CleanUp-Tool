"""
Employee Data Models
Contains data structures and models for employee information
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd
import json
import os
from pathlib import Path


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
    
    # Config file path for persisting masterlist file paths
    CONFIG_FILE = Path(__file__).parent.parent / 'masterlist_config.json'
    
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
        
        # Load persisted masterlist paths on initialization
        self._load_masterlist_paths()
    
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
    
    def clear_system_reports(self):
        """Clear only system report files (keep masterlists)"""
        self.current_system = None
        self.previous_reference = None
        self.cleaned_data = None
        self.unmatched_data = None
        self.fuzzy_matched_data = None
        
        # Clear only system report file paths
        self.file_paths['current_system'] = None
        self.file_paths['previous_reference'] = None
    
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
        
        # Also clear persisted masterlist paths
        self._save_masterlist_paths()
    
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
    
    def _load_masterlist_paths(self):
        """Load persisted masterlist file paths from config file"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Restore masterlist paths if files still exist
                    if 'masterlist_current' in config:
                        path = config['masterlist_current']
                        if path and os.path.exists(path):
                            self.file_paths['masterlist_current'] = path
                    if 'masterlist_resigned' in config:
                        path = config['masterlist_resigned']
                        if path and os.path.exists(path):
                            self.file_paths['masterlist_resigned'] = path
            except Exception:
                # If config file is corrupted, ignore it
                pass
    
    def load_persisted_masterlists(self, file_handler) -> bool:
        """Load persisted masterlist files if they exist"""
        files_loaded = False
        
        # Load current masterlist
        current_path = self.file_paths.get('masterlist_current')
        if current_path and os.path.exists(current_path):
            try:
                file_extension = Path(current_path).suffix.lower()
                if file_extension == '.csv':
                    self.masterlist_current = file_handler.detect_and_load_csv(current_path)
                elif file_extension in ['.xlsx', '.xls']:
                    self.masterlist_current = file_handler.detect_and_load_excel(current_path)
                files_loaded = True
            except Exception:
                # If loading fails, remove the path
                self.file_paths['masterlist_current'] = None
        
        # Load resigned masterlist
        resigned_path = self.file_paths.get('masterlist_resigned')
        if resigned_path and os.path.exists(resigned_path):
            try:
                file_extension = Path(resigned_path).suffix.lower()
                if file_extension == '.csv':
                    self.masterlist_resigned = file_handler.detect_and_load_csv(resigned_path)
                elif file_extension in ['.xlsx', '.xls']:
                    self.masterlist_resigned = file_handler.detect_and_load_excel(resigned_path)
                files_loaded = True
            except Exception:
                # If loading fails, remove the path
                self.file_paths['masterlist_resigned'] = None
        
        # Save cleaned paths back to config
        if files_loaded:
            self._save_masterlist_paths()
        
        return files_loaded
    
    def _save_masterlist_paths(self):
        """Save masterlist file paths to config file"""
        try:
            config = {
                'masterlist_current': self.file_paths.get('masterlist_current'),
                'masterlist_resigned': self.file_paths.get('masterlist_resigned')
            }
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            # If saving fails, continue without error
            pass
    
    def save_masterlist_path(self, file_type: str, file_path: str):
        """Save a masterlist file path and persist it"""
        if file_type in ['masterlist_current', 'masterlist_resigned']:
            self.file_paths[file_type] = file_path
            self._save_masterlist_paths()
    
    def get_persisted_masterlist_path(self, file_type: str) -> Optional[str]:
        """Get persisted masterlist file path if it exists"""
        if file_type in ['masterlist_current', 'masterlist_resigned']:
            path = self.file_paths.get(file_type)
            if path and os.path.exists(path):
                return path
        return None
