"""
Matching Engine Model
Handles employee matching logic including fuzzy matching and data sorting
"""

from typing import Optional, Tuple
import pandas as pd
from fuzzywuzzy import fuzz
from .data_sorter import DataSorter


class MatchingEngine:
    """Handles employee matching logic and data sorting"""
    
    def __init__(self, use_fuzzy_logic: bool = True, threshold: int = 80):
        self.use_fuzzy_logic = use_fuzzy_logic
        self.threshold = threshold
        self.data_sorter = DataSorter()
    
    def is_valid_pernr(self, pernr_value) -> bool:
        """
        Check if a PERNR value is valid (not null, not empty, not invalid indicators)
        
        Args:
            pernr_value: The PERNR value to validate
            
        Returns:
            True if PERNR is valid, False otherwise
        """
        if pd.isna(pernr_value):
            return False
        
        # Convert to string and strip whitespace
        pernr_str = str(pernr_value).strip()
        
        # Check if it's empty after stripping
        if not pernr_str:
            return False
        
        # Check for invalid PERNR indicators
        invalid_indicators = [
            'cant find', 'can\'t find', 'cannot find', 'not found', 'unknown',
            'n/a', 'na', 'null', 'none', 'empty', 'missing', 'error',
            'invalid', 'invalid pernr', 'no match', 'no data'
        ]
        
        # Case-insensitive check for invalid indicators
        if pernr_str.lower() in [indicator.lower() for indicator in invalid_indicators]:
            return False
        
        # If it has any content and is not an invalid indicator, consider it valid
        return True

    def find_employee_by_user_id(self, user_id: str, previous_df: pd.DataFrame) -> Optional[str]:
        """Find PERNR using User ID from previous reference"""
        user_id_col = self._find_column(previous_df, ['user', 'id', 'sysid', 'username'])
        pernr_col = self._find_column(previous_df, ['pernr', 'employee number'])
        
        if user_id_col and pernr_col:
            match = previous_df[previous_df[user_id_col] == user_id]
            if not match.empty:
                pernr_value = match.iloc[0][pernr_col]
                
                # Check if PERNR is valid
                if not self.is_valid_pernr(pernr_value):
                    return None
                
                # Convert to string and clean up whitespace
                pernr_str = str(pernr_value).strip()
                
                # Return the PERNR as-is if it has any content
                # This includes values like "SAMU-  ", "generic", numeric values, etc.
                if pernr_str:
                    return pernr_str
        return None
    
    def find_employee_by_name(self, current_name: str, masterlist_df: pd.DataFrame) -> Tuple[Optional[str], Optional[str], str, float]:
        """
        Find employee by name using fuzzy matching
        
        Args:
            current_name: Name from current system report (Username/Full Name)
            masterlist_df: Masterlist dataframe (current or resigned)
            
        Returns:
            Tuple of (employee_number, full_name, match_type, match_score) or (None, None, "no_match", 0.0) if not found
        """
        if masterlist_df is None or masterlist_df.empty:
            return None, None, "no_match", 0.0
        
        # Find name columns in masterlist - prioritize "Full Name" column
        name_columns = [col for col in masterlist_df.columns if col == 'Full Name']
        if not name_columns:
            # Fallback to flexible matching (could be "Name", "Employee Name", etc.)
            name_columns = [col for col in masterlist_df.columns if 'name' in str(col).lower()]
        if not name_columns:
            return None, None, "no_match", 0.0
        
        # Find PERNR column - prioritize "PERNR" then "Pers. Number"
        emp_num_columns = [col for col in masterlist_df.columns if str(col).upper() == 'PERNR']
        if not emp_num_columns:
            # Try "Pers. Number" as alternative
            emp_num_columns = [col for col in masterlist_df.columns if col == 'Pers. Number']
        if not emp_num_columns:
            # Fallback to old naming convention
            emp_num_columns = [col for col in masterlist_df.columns if 'employee' in str(col).lower() and 'number' in str(col).lower()]
        if not emp_num_columns:
            return None, None, "no_match", 0.0
        
        name_col = name_columns[0]  # Use first name column found
        emp_num_col = emp_num_columns[0]  # Use first PERNR column found
        
        best_match = None
        best_score = 0
        best_employee_number = None
        best_full_name = None
        
        # Clean the current name for comparison
        current_name_clean = str(current_name).strip().lower()
        
        # PRIORITY 1: Try exact match first (case-insensitive)
        # This ensures we get the most accurate Employee Number when names match exactly
        for idx, row in masterlist_df.iterrows():
            masterlist_name = str(row[name_col]).strip().lower()
            if pd.notna(row[name_col]) and current_name_clean == masterlist_name:
                # Convert PERNR to integer, return as string for consistency
                emp_num = pd.to_numeric(row[emp_num_col], errors='coerce')
                return str(int(emp_num)) if pd.notna(emp_num) else None, str(row[name_col]), "exact_match", 100.0
        
        # PRIORITY 2: If no exact match, try fuzzy matching as fallback (if enabled)
        # Only use fuzzy logic when exact matching fails AND fuzzy logic is enabled
        if not self.use_fuzzy_logic:
            return None, None, "no_match", 0.0
            
        for idx, row in masterlist_df.iterrows():
            if pd.isna(row[name_col]):
                continue
                
            masterlist_name = str(row[name_col]).strip()
            masterlist_name_clean = masterlist_name.lower()
            
            # Calculate similarity score
            score = fuzz.ratio(current_name_clean, masterlist_name_clean)
            
            # Also try partial ratio for better matching
            partial_score = fuzz.partial_ratio(current_name_clean, masterlist_name_clean)
            
            # Try name order reversal matching (e.g., "Jared Ranjo" vs "Ranjo, Jared")
            name_order_score = self._calculate_name_order_score(current_name_clean, masterlist_name_clean)
            
            # Use the highest score from all methods
            final_score = max(score, partial_score, name_order_score)
            
            # Update best match if this is better
            if final_score > best_score and final_score >= self.threshold:
                best_score = final_score
                best_match = masterlist_name
                # Convert PERNR to integer, store as string for consistency
                emp_num = pd.to_numeric(row[emp_num_col], errors='coerce')
                best_employee_number = str(int(emp_num)) if pd.notna(emp_num) else None
                best_full_name = masterlist_name
        
        if best_employee_number is not None:
            return best_employee_number, best_full_name, "fuzzy_match", best_score
        else:
            return None, None, "no_match", 0.0
    
    def _calculate_name_order_score(self, name1: str, name2: str) -> float:
        """
        Calculate similarity score for name order variations
        Handles cases like "Jared Ranjo" vs "Ranjo, Jared"
        """
        # Split names into parts
        name1_parts = [part.strip() for part in name1.split() if part.strip()]
        name2_parts = [part.strip() for part in name2.split() if part.strip()]
        
        # If either name has less than 2 parts, use regular fuzzy matching
        if len(name1_parts) < 2 or len(name2_parts) < 2:
            return 0.0
        
        # Try different name order combinations
        best_score = 0.0
        
        # Method 1: Try reversed order (First Last vs Last, First)
        if len(name1_parts) >= 2 and len(name2_parts) >= 2:
            # Try "First Last" vs "Last, First"
            name1_reversed = f"{name1_parts[-1]}, {name1_parts[0]}"  # "Ranjo, Jared"
            name2_reversed = f"{name2_parts[-1]}, {name2_parts[0]}"  # "Ranjo, Jared"
            
            # Compare original with reversed
            score1 = fuzz.ratio(name1, name2_reversed)
            score2 = fuzz.ratio(name1_reversed, name2)
            best_score = max(best_score, score1, score2)
        
        # Method 2: Try different combinations for names with 3+ parts
        if len(name1_parts) >= 3 or len(name2_parts) >= 3:
            # For names like "John Michael Smith" vs "Smith, John Michael"
            # Try different combinations
            for i in range(1, min(len(name1_parts), len(name2_parts))):
                # Try splitting at different points
                name1_first = " ".join(name1_parts[:i])
                name1_last = " ".join(name1_parts[i:])
                name2_first = " ".join(name2_parts[:i])
                name2_last = " ".join(name2_parts[i:])
                
                # Compare "First Last" vs "Last, First"
                combo1 = f"{name1_first} {name1_last}"
                combo2 = f"{name2_last}, {name2_first}"
                score = fuzz.ratio(combo1, combo2)
                best_score = max(best_score, score)
                
                # Also try the reverse
                combo3 = f"{name1_last}, {name1_first}"
                combo4 = f"{name2_first} {name2_last}"
                score = fuzz.ratio(combo3, combo4)
                best_score = max(best_score, score)
        
        # Method 3: Try partial matching for name components
        # This helps with cases like "Jared Ranjo" vs "Ranjo, Jared Michael"
        for part1 in name1_parts:
            for part2 in name2_parts:
                if len(part1) >= 3 and len(part2) >= 3:  # Only for substantial name parts
                    partial_score = fuzz.ratio(part1, part2)
                    if partial_score >= 80:  # High similarity for name parts
                        # Calculate overall score based on matching parts
                        matching_parts = 0
                        total_parts = max(len(name1_parts), len(name2_parts))
                        
                        for p1 in name1_parts:
                            for p2 in name2_parts:
                                if fuzz.ratio(p1, p2) >= 80:
                                    matching_parts += 1
                                    break
                        
                        if matching_parts >= 2:  # At least 2 parts match
                            component_score = (matching_parts / total_parts) * 100
                            best_score = max(best_score, component_score)
        
        return best_score

    def _find_column(self, df: pd.DataFrame, keywords: list) -> Optional[str]:
        """Find column by keywords with flexible matching"""
        # Try exact match first
        for col in df.columns:
            if any(keyword in str(col).lower() for keyword in keywords):
                return col
        return None
    
    def test_matching(self, name1: str, name2: str) -> dict:
        """Test fuzzy matching with current threshold settings"""
        # Clean names
        name1_clean = str(name1).strip().lower()
        name2_clean = str(name2).strip().lower()
        
        # Check exact match first
        exact_match = name1_clean == name2_clean
        
        # Calculate similarity scores
        score = fuzz.ratio(name1_clean, name2_clean)
        partial_score = fuzz.partial_ratio(name1_clean, name2_clean)
        final_score = max(score, partial_score)
        
        # Check if it would match (only if fuzzy logic is enabled)
        would_match = exact_match or (self.use_fuzzy_logic and final_score >= self.threshold)
        
        return {
            'name1': name1,
            'name2': name2,
            'exact_match': exact_match,
            'ratio_score': score,
            'partial_score': partial_score,
            'final_score': final_score,
            'threshold': self.threshold,
            'fuzzy_enabled': self.use_fuzzy_logic,
            'would_match': would_match
        }
    
    def update_settings(self, use_fuzzy_logic: bool, threshold: int):
        """Update matching engine settings"""
        self.use_fuzzy_logic = use_fuzzy_logic
        self.threshold = max(50, min(100, threshold))  # Clamp between 50-100
    
    def sort_dataframe(self, df: pd.DataFrame, column: str, ascending: bool = True) -> pd.DataFrame:
        """
        Sort a DataFrame by a specific column with intelligent type detection
        
        Args:
            df: DataFrame to sort
            column: Column name to sort by
            ascending: Sort order (True for ascending, False for descending)
            
        Returns:
            Sorted DataFrame
        """
        return self.data_sorter.sort_dataframe(df, column, ascending)
    
    def sort_list(self, data: list, ascending: bool = True) -> list:
        """
        Sort a list with intelligent type detection
        
        Args:
            data: List to sort
            ascending: Sort order
            
        Returns:
            Sorted list
        """
        return self.data_sorter.sort_list(data, ascending)
    
    def get_sort_direction_indicator(self, column: str, ascending: bool) -> str:
        """
        Get visual indicator for sort direction
        
        Args:
            column: Column name
            ascending: Sort direction
            
        Returns:
            Column name with sort indicator
        """
        return self.data_sorter.get_sort_direction_indicator(column, ascending)
