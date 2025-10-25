"""
Processing Controller
Handles data processing operations and cleanup workflow
"""

import threading
import pandas as pd
from typing import Optional, Tuple
from tkinter import messagebox
import time

class ProcessingController:
    """Handles data processing operations"""
    
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.cancel_flag = False
        self.cleanup_thread = None
    
    def start_cleanup(self, use_fuzzy_logic: bool, threshold: int):
        """Start the cleanup process"""
        # Reset cancel flag
        self.cancel_flag = False
        
        # Update matching engine settings
        self.main_controller.matching_engine.update_settings(use_fuzzy_logic, threshold)
        
        # Run in separate thread to avoid freezing UI
        self.cleanup_thread = threading.Thread(target=self.cleanup_worker)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
    
    def cancel_cleanup(self):
        """Cancel the cleanup process"""
        self.cancel_flag = True
        self.main_controller.update_progress(0, "Cancelling cleanup process...")
    
    def cleanup_worker(self):
        """Worker thread for cleanup process"""
        try:
            # Track start time for ETA calculation
            start_time = time.time()
            
            dataset = self.main_controller.employee_dataset
            matching_engine = self.main_controller.matching_engine
            
            # Get data copies
            current_df = dataset.current_system.copy()
            previous_df = dataset.previous_reference.copy() if dataset.previous_reference is not None else None
            masterlist_current_df = dataset.masterlist_current.copy() if dataset.masterlist_current is not None else None
            masterlist_resigned_df = dataset.masterlist_resigned.copy() if dataset.masterlist_resigned is not None else None
            
            # Get total rows for progress calculation
            total_rows = len(current_df)
            
            # Check if Previous Reference is available
            has_previous_reference = previous_df is not None and not previous_df.empty
            
            self.main_controller.update_progress(10, "Loading and validating data...")
            
            # Initialize new columns
            self.initialize_new_columns(current_df)
            
            fuzzy_status = "with fuzzy matching" if self.main_controller.matching_engine.use_fuzzy_logic else "exact matching only"
            lookup_method = "User ID lookup + Name fallback" if has_previous_reference else "Name matching only"
            self.main_controller.update_progress(20, f"Looking up PERNRs, Full Names, Resignation Dates, and Organizational Data ({lookup_method} {fuzzy_status})...")
            
            # Detect columns for lookup once (outside the loop for performance)
            user_id_current, user_id_previous, pernr_previous = self.detect_lookup_columns(current_df, previous_df)
            
            # Process each row to add PERNR, Full Name, Resignation Date, and Organizational Data
            rows_processed = 0
            for idx, row in current_df.iterrows():
                # Check for cancellation
                if self.cancel_flag:
                    self.main_controller.update_progress(0, "Cleanup cancelled by user")
                    # Reset run button
                    if self.main_controller.main_window.cleanup_view:
                        self.main_controller.main_window.cleanup_view.reset_run_button()
                    return
                
                rows_processed += 1
                employee_number = None
                full_name = None
                full_name_source = None  # Track where full name came from
                match_type = "no_match"  # Initialize match tracking
                match_score = 0.0
                
                # Step 1: Lookup PERNR by User ID from previous_reference (if available)
                if has_previous_reference and user_id_current and user_id_previous and pernr_previous:
                    user_id = row.get(user_id_current)
                    if pd.notna(user_id):
                        match = previous_df[previous_df[user_id_previous] == user_id]
                        if not match.empty:
                            # Handle all types of PERNR values (numeric, text, special formats)
                            pernr_value = match.iloc[0][pernr_previous]
                            
                            # Check if PERNR is valid (not "cant find", "unknown", etc.)
                            if self.main_controller.matching_engine.is_valid_pernr(pernr_value):
                                # Convert to string and clean up whitespace
                                pernr_str = str(pernr_value).strip()
                                
                                # Return the PERNR as-is if it has any content
                                # This includes values like "SAMU-  ", "generic", numeric values, etc.
                                employee_number = pernr_str if pernr_str else None
                                
                                if employee_number is not None:
                                    match_type = "user_id_match"  # Track User ID match
                                    match_score = 100.0
                            # If PERNR is invalid (like "cant find"), employee_number remains None
                            # and will trigger name matching fallback
                
                # Step 2: Lookup using name matching (if User ID lookup failed or no Previous Reference)
                if employee_number is None:
                    # Get the current system's username/full name for comparison
                    current_name = None
                    name_columns_current = [col for col in current_df.columns if 'username' in str(col).lower() or 'name' in str(col).lower()]
                    if name_columns_current:
                        current_name = row.get(name_columns_current[0])
                    
                    if current_name and pd.notna(current_name):
                        # Try to find matching employee in masterlist_current
                        if masterlist_current_df is not None:
                            employee_number, full_name, match_type, match_score = self.main_controller.matching_engine.find_employee_by_name(
                                current_name, masterlist_current_df
                            )
                            if full_name is not None:
                                full_name_source = "Current Masterlist"
                        
                        # If not found in current, try masterlist_resigned
                        if employee_number is None and masterlist_resigned_df is not None:
                            employee_number, full_name, match_type, match_score = self.main_controller.matching_engine.find_employee_by_name(
                                current_name, masterlist_resigned_df
                            )
                            if full_name is not None:
                                full_name_source = "Resigned Masterlist"
                
                # Step 3: If PERNR was found but Full Name is still missing, lookup Full Name from masterlists
                if employee_number is not None and full_name is None:
                    full_name, full_name_source = self.get_full_name_from_pernr(
                        employee_number, masterlist_current_df, masterlist_resigned_df
                    )
                
                # Step 4: Lookup Resignation Date from resigned employee list if PERNR was found
                resignation_date = self.get_resignation_date(employee_number, masterlist_resigned_df)
                
                # Step 5: Lookup Organizational Data from current employee list if PERNR was found
                org_data = self.get_organizational_data(employee_number, masterlist_current_df)
                
                # Assign all found data (or leave as None)
                self.update_employee_record(
                    current_df, idx, employee_number, full_name, full_name_source, resignation_date,
                    org_data, match_type, match_score
                )
                
                # Update progress with estimated time remaining
                progress = 20 + (idx / len(current_df)) * 70
                
                # Calculate estimated time remaining
                elapsed_time = time.time() - start_time
                if rows_processed > 0:
                    avg_time_per_row = elapsed_time / rows_processed
                    remaining_rows = total_rows - rows_processed
                    estimated_seconds = avg_time_per_row * remaining_rows
                    
                    # Format time remaining
                    if estimated_seconds < 60:
                        time_str = f"{int(estimated_seconds)}s"
                    elif estimated_seconds < 3600:
                        minutes = int(estimated_seconds // 60)
                        seconds = int(estimated_seconds % 60)
                        time_str = f"{minutes}m {seconds}s"
                    else:
                        hours = int(estimated_seconds // 3600)
                        minutes = int((estimated_seconds % 3600) // 60)
                        time_str = f"{hours}h {minutes}m"
                    
                    status_msg = f"Processing row {idx + 1} of {len(current_df)}... (Est. {time_str} remaining)"
                else:
                    status_msg = f"Processing row {idx + 1} of {len(current_df)}..."
                
                self.main_controller.update_progress(progress, status_msg)
            
            self.main_controller.update_progress(95, "Generating clean reports...")
            
            # Finalize processing
            self.finalize_processing(current_df, dataset)
            
            self.main_controller.update_progress(100, "Clean-up completed successfully!")
            
            # Reset run button
            self.main_controller.main_window.root.after(
                0, lambda: self.main_controller.main_window.cleanup_view.reset_run_button()
            )
            
            # Show results
            self.main_controller.show_results_section()
            
        except Exception as e:
            self.main_controller.main_window.root.after(
                0, lambda: messagebox.showerror("Error", f"Cleanup failed:\n{str(e)}")
            )
            self.main_controller.main_window.root.after(
                0, lambda: self.main_controller.main_window.cleanup_view.reset_run_button()
            )
    
    def initialize_new_columns(self, df: pd.DataFrame):
        """Initialize new columns for enriched data"""
        new_columns = [
            'PERNR', 'Full Name (From Masterlist)', 'Full Name Source',
            'Resignation Date',
            'Position Name', 'Segment Name', 'Group Name',
            'Area/Division Name', 'Department/Branch',
            'Match Type', 'Match Score'
        ]
        
        for col in new_columns:
            df[col] = None
    
    def detect_lookup_columns(self, current_df: pd.DataFrame, previous_df: Optional[pd.DataFrame]) -> tuple:
        """Detect columns for lookup with flexible matching"""
        # Current System - User ID column
        user_id_current = None
        if current_df is not None:
            # Try exact match first
            exact_match = [col for col in current_df.columns if col == 'User ID']
            if exact_match:
                user_id_current = exact_match[0]
            else:
                # Try flexible matching
                flexible_match = [col for col in current_df.columns 
                                 if any(keyword in str(col).lower() for keyword in ['user', 'id', 'sysid', 'username', 'abbreviation'])]
                if flexible_match:
                    user_id_current = flexible_match[0]
        
        # Previous Reference - User ID column
        user_id_previous = None
        if previous_df is not None:
            # Try exact match first
            exact_match = [col for col in previous_df.columns if col == 'User ID']
            if exact_match:
                user_id_previous = exact_match[0]
            else:
                # Try flexible matching
                flexible_match = [col for col in previous_df.columns 
                                 if any(keyword in str(col).lower() for keyword in ['user', 'id', 'sysid', 'username', 'abbreviation'])]
                if flexible_match:
                    user_id_previous = flexible_match[0]
        
        # Previous Reference - PERNR column
        pernr_previous = None
        if previous_df is not None:
            # Try exact match first
            exact_match = [col for col in previous_df.columns if col == 'PERNR']
            if exact_match:
                pernr_previous = exact_match[0]
            else:
                # Try flexible matching
                flexible_match = [col for col in previous_df.columns 
                                 if str(col).upper() == 'PERNR' or ('employee' in str(col).lower() and 'number' in str(col).lower())]
                if flexible_match:
                    pernr_previous = flexible_match[0]
        
        return user_id_current, user_id_previous, pernr_previous
    
    def get_full_name_from_pernr(self, employee_number: str, masterlist_current_df: Optional[pd.DataFrame], 
                                 masterlist_resigned_df: Optional[pd.DataFrame]) -> Tuple[Optional[str], Optional[str]]:
        """
        Get full name using PERNR from masterlists
        
        Returns:
            Tuple of (full_name, source) where source is "Current Masterlist" or "Resigned Masterlist" or None
        """
        if not employee_number:
            return None, None
        
        # Convert employee_number to integer for proper comparison
        emp_num_numeric = pd.to_numeric(employee_number, errors='coerce')
        if pd.notna(emp_num_numeric):
            emp_num_numeric = int(emp_num_numeric)
        else:
            return None, None
        
        # Try masterlist_current first
        pernr_col = None
        if masterlist_current_df is not None:
            # Check for PERNR column first, then "Pers. Number"
            if 'PERNR' in masterlist_current_df.columns:
                pernr_col = 'PERNR'
            elif 'Pers. Number' in masterlist_current_df.columns:
                pernr_col = 'Pers. Number'
        
        if pernr_col is not None:
            # Check for Full Name column - prioritize exact "Full Name" match
            name_columns = [col for col in masterlist_current_df.columns if col == 'Full Name']
            if not name_columns:
                # Fallback to flexible matching (could be "Name", "Employee Name", etc.)
                name_columns = [col for col in masterlist_current_df.columns if 'name' in str(col).lower()]
            if name_columns:
                # Convert masterlist PERNR to integer for comparison
                masterlist_current_df_copy = masterlist_current_df.copy()
                masterlist_current_df_copy[pernr_col] = pd.to_numeric(masterlist_current_df_copy[pernr_col], errors='coerce')
                masterlist_current_df_copy[pernr_col] = masterlist_current_df_copy[pernr_col].astype('Int64')
                match = masterlist_current_df_copy[masterlist_current_df_copy[pernr_col] == emp_num_numeric]
                if not match.empty:
                    # Get the original index to retrieve the full name from original dataframe
                    original_idx = match.index[0]
                    full_name_value = masterlist_current_df.loc[original_idx, name_columns[0]]
                    return full_name_value, "Current Masterlist"
        
        # If not found in current, try masterlist_resigned
        if masterlist_resigned_df is not None and 'PERNR' in masterlist_resigned_df.columns:
            # Prioritize "Fullname" column, then flexible matching for name columns
            name_columns = [col for col in masterlist_resigned_df.columns if col == 'Fullname']
            if not name_columns:
                # Try "Full Name" as alternative
                name_columns = [col for col in masterlist_resigned_df.columns if col == 'Full Name']
            if not name_columns:
                # Fallback to flexible matching (could be "Name", "Employee Name", etc.)
                name_columns = [col for col in masterlist_resigned_df.columns if 'name' in str(col).lower()]
            
            if name_columns:
                # Convert masterlist PERNR to integer for comparison
                masterlist_resigned_df_copy = masterlist_resigned_df.copy()
                masterlist_resigned_df_copy['PERNR'] = pd.to_numeric(masterlist_resigned_df_copy['PERNR'], errors='coerce')
                masterlist_resigned_df_copy['PERNR'] = masterlist_resigned_df_copy['PERNR'].astype('Int64')
                match = masterlist_resigned_df_copy[masterlist_resigned_df_copy['PERNR'] == emp_num_numeric]
                if not match.empty:
                    # Get the original index to retrieve the full name from original dataframe
                    original_idx = match.index[0]
                    full_name_value = masterlist_resigned_df.loc[original_idx, name_columns[0]]
                    # Only return if the full name is not empty/null
                    if pd.notna(full_name_value) and str(full_name_value).strip():
                        return full_name_value, "Resigned Masterlist"
        
        return None, None
    
    def get_resignation_date(self, employee_number: Optional[str], masterlist_resigned_df: Optional[pd.DataFrame]) -> Optional[str]:
        """
        Get resignation date or status for employees
        Returns actual dates in MM/DD/YYYY format, or status values like "ACTIVE", "RETRACTED", etc.
        """
        if not employee_number or masterlist_resigned_df is None or 'PERNR' not in masterlist_resigned_df.columns:
            return None
        
        # Convert employee_number to integer for proper comparison
        emp_num_numeric = pd.to_numeric(employee_number, errors='coerce')
        if pd.notna(emp_num_numeric):
            emp_num_numeric = int(emp_num_numeric)
        else:
            return None
        
        # Convert masterlist PERNR to integer for comparison
        masterlist_resigned_df_copy = masterlist_resigned_df.copy()
        masterlist_resigned_df_copy['PERNR'] = pd.to_numeric(masterlist_resigned_df_copy['PERNR'], errors='coerce')
        masterlist_resigned_df_copy['PERNR'] = masterlist_resigned_df_copy['PERNR'].astype('Int64')
        match = masterlist_resigned_df_copy[masterlist_resigned_df_copy['PERNR'] == emp_num_numeric]
        
        if not match.empty:
            # Prioritize "Effectivity from HR Separation Report" column, then fallback to other date columns
            date_columns = [col for col in masterlist_resigned_df.columns if 'effectivity from hr separation report' in str(col).lower()]
            
            # If not found, try other effectivity-related columns
            if not date_columns:
                date_columns = [col for col in masterlist_resigned_df.columns if 'effectivity' in str(col).lower() and 'separation' in str(col).lower()]
            
            # If still not found, try generic separation/resignation/termination date columns
            if not date_columns:
                date_columns = [col for col in masterlist_resigned_df.columns if any(keyword in str(col).lower() for keyword in ['resignation', 'date', 'end', 'termination', 'exit', 'effectivity', 'separation', 'report'])]
            
            if date_columns:
                # Get the original index to retrieve the resignation date from original dataframe
                original_idx = match.index[0]
                raw_date = masterlist_resigned_df.loc[original_idx, date_columns[0]]
                
                # Return the raw value if it exists (whether it's a date or status text like "ACTIVE", "RETRACTED", etc.)
                if pd.notna(raw_date):
                    raw_value = str(raw_date).strip()
                    
                    # Only skip if it's completely empty after stripping
                    if raw_value:
                        # Try to parse as date first
                        try:
                            if isinstance(raw_date, str):
                                # Handle string dates
                                parsed_date = pd.to_datetime(raw_date, errors='coerce')
                            else:
                                # Handle datetime objects
                                parsed_date = pd.to_datetime(raw_date, errors='coerce')
                            
                            if pd.notna(parsed_date):
                                # It's a valid date, format it as MM/DD/YYYY
                                return parsed_date.strftime('%m/%d/%Y')
                            else:
                                # Not a valid date, return the original value as-is
                                # This handles cases like "ACTIVE", "RETRACTED", etc.
                                return raw_value
                        except:
                            # If date parsing fails, return the original value as-is
                            # This ensures status values like "ACTIVE", "RETRACTED" are preserved
                            return raw_value
                    else:
                        return None
                else:
                    return None
        
        return None
    
    def get_organizational_data(self, employee_number: Optional[str], masterlist_current_df: Optional[pd.DataFrame]) -> dict:
        """Get organizational data for employee"""
        org_data = {
            'Position Name': None,
            'Segment Name': None,
            'Group Name': None,
            'Area/Division Name': None,
            'Department/Branch': None
        }
        
        if not employee_number or masterlist_current_df is None:
            return org_data
        
        # Check for PERNR or "Pers. Number" column
        pernr_col_org = None
        if 'PERNR' in masterlist_current_df.columns:
            pernr_col_org = 'PERNR'
        elif 'Pers. Number' in masterlist_current_df.columns:
            pernr_col_org = 'Pers. Number'
        
        if pernr_col_org is None:
            return org_data
        
        # Convert employee_number to integer for proper comparison
        emp_num_numeric = pd.to_numeric(employee_number, errors='coerce')
        if pd.notna(emp_num_numeric):
            emp_num_numeric = int(emp_num_numeric)
        else:
            return org_data
        
        # Convert masterlist PERNR to integer for comparison
        masterlist_current_df_copy = masterlist_current_df.copy()
        masterlist_current_df_copy[pernr_col_org] = pd.to_numeric(masterlist_current_df_copy[pernr_col_org], errors='coerce')
        masterlist_current_df_copy[pernr_col_org] = masterlist_current_df_copy[pernr_col_org].astype('Int64')
        match = masterlist_current_df_copy[masterlist_current_df_copy[pernr_col_org] == emp_num_numeric]
        
        if not match.empty:
            # Get the original index to retrieve organizational data from original dataframe
            original_idx = match.index[0]
            
            # Find and retrieve organizational columns
            org_columns = {
                'Position Name': ['position', 'job', 'title', 'role', 'pos. name'],
                'Segment Name': ['segment'],
                'Group Name': ['group'],
                'Area/Division Name': ['area', 'division'],
                'Department/Branch': ['department', 'branch', 'unit']
            }
            
            for target_col, keywords in org_columns.items():
                # Find matching column in masterlist
                matching_cols = [col for col in masterlist_current_df.columns 
                               if any(keyword in str(col).lower() for keyword in keywords)]
                
                if matching_cols:
                    # Use the first matching column found
                    value = masterlist_current_df.loc[original_idx, matching_cols[0]]
                    if pd.notna(value):
                        org_data[target_col] = str(value)
        
        return org_data
    
    def update_employee_record(self, df: pd.DataFrame, idx, employee_number: Optional[str], 
                              full_name: Optional[str], full_name_source: Optional[str], resignation_date: Optional[str], 
                              org_data: dict, match_type: str, match_score: float):
        """Update employee record with found data"""
        df.at[idx, 'PERNR'] = employee_number
        df.at[idx, 'Full Name (From Masterlist)'] = full_name
        df.at[idx, 'Full Name Source'] = full_name_source
        df.at[idx, 'Resignation Date'] = resignation_date
        df.at[idx, 'Match Type'] = match_type
        df.at[idx, 'Match Score'] = match_score
        
        # Update organizational data
        for key, value in org_data.items():
            df.at[idx, key] = value
    
    def finalize_processing(self, current_df: pd.DataFrame, dataset):
        """Finalize processing and create result datasets"""
        # Keep PERNR column as string to preserve all values including "SAMU-  ", "generic", etc.
        # Only convert numeric PERNRs to clean format, keep text values as-is
        def clean_pernr(pernr_value):
            if pd.isna(pernr_value):
                return None
            
            pernr_str = str(pernr_value).strip()
            if not pernr_str:
                return None
            
            # Try to convert to numeric for cleaning, but keep original if it fails
            try:
                numeric_val = pd.to_numeric(pernr_str, errors='coerce')
                if pd.notna(numeric_val):
                    return str(int(numeric_val))  # Clean numeric format
                else:
                    return pernr_str  # Keep original text format
            except:
                return pernr_str  # Keep original text format
        
        current_df['PERNR'] = current_df['PERNR'].apply(clean_pernr)
        
        # Store all data (both matched and unmatched) in cleaned_data
        dataset.cleaned_data = current_df.copy()
        
        # Create separate unmatched data for review (records without PERNR)
        dataset.unmatched_data = current_df[current_df['PERNR'].isna()].copy()
        
        # Create fuzzy matched data sheet (records matched using fuzzy logic)
        fuzzy_matched_mask = (current_df['PERNR'].notna()) & (current_df['Match Type'] == 'fuzzy_match')
        dataset.fuzzy_matched_data = current_df[fuzzy_matched_mask].copy()
