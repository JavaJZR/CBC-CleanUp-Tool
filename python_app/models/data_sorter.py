"""
Data Sorting Utility
Handles intelligent sorting of data with automatic type detection
"""

import re
import pandas as pd
from typing import List, Tuple, Any, Optional
from datetime import datetime


class DataSorter:
    """Handles intelligent data sorting with automatic type detection"""
    
    def __init__(self):
        self.date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
    
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
        if column not in df.columns:
            return df
        
        # Analyze column content to determine sort type
        sort_type = self._detect_sort_type(df[column])
        
        if sort_type == 'date':
            return self._sort_by_date(df, column, ascending)
        elif sort_type == 'numeric':
            return self._sort_by_numeric(df, column, ascending)
        else:
            return self._sort_by_string(df, column, ascending)
    
    def _detect_sort_type(self, series: pd.Series) -> str:
        """
        Detect the best sorting type for a pandas Series
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Sort type: 'date', 'numeric', or 'string'
        """
        if series.empty:
            return 'string'
        
        # Count different types of values
        total_count = len(series)
        date_count = 0
        numeric_count = 0
        
        for value in series:
            if pd.isna(value) or value == '' or value is None:
                continue
                
            value_str = str(value).strip()
            if not value_str:
                continue
            
            # Check if value is a date in MM/DD/YYYY format
            if self._is_date_format(value_str):
                date_count += 1
            # Check if value is numeric
            elif self._is_numeric(value_str):
                numeric_count += 1
        
        # Determine sort type based on content analysis
        if total_count > 0 and (date_count / total_count) > 0.5:
            return 'date'
        elif total_count > 0 and (numeric_count / total_count) > 0.7:
            return 'numeric'
        else:
            return 'string'
    
    def _is_date_format(self, value: str) -> bool:
        """
        Check if a value matches MM/DD/YYYY date format
        
        Args:
            value: String value to check
            
        Returns:
            True if value matches date format
        """
        if not value or not isinstance(value, str):
            return False
        
        # Check for MM/DD/YYYY pattern
        if re.match(self.date_pattern, value.strip()):
            try:
                # Validate the date components
                parts = value.strip().split('/')
                if len(parts) == 3:
                    month, day, year = parts
                    month, day, year = int(month), int(day), int(year)
                    # Basic validation
                    if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100:
                        return True
            except ValueError:
                pass
        
        return False
    
    def _is_numeric(self, value: str) -> bool:
        """
        Check if a value is numeric (including decimals and negative numbers)
        
        Args:
            value: String value to check
            
        Returns:
            True if value is numeric
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _sort_by_date(self, df: pd.DataFrame, column: str, ascending: bool) -> pd.DataFrame:
        """
        Sort DataFrame by date column
        
        Args:
            df: DataFrame to sort
            column: Date column name
            ascending: Sort order
            
        Returns:
            Sorted DataFrame
        """
        def date_key(x):
            if pd.isna(x) or x == '' or x is None:
                # Blank entries go to bottom for ascending, top for descending
                return (1, float('inf')) if ascending else (0, float('-inf'))
            
            value_str = str(x).strip()
            if not value_str:
                return (1, float('inf')) if ascending else (0, float('-inf'))
            
            if self._is_date_format(value_str):
                try:
                    # Parse MM/DD/YYYY format
                    month, day, year = value_str.split('/')
                    # Convert to sortable format (YYYYMMDD)
                    date_value = int(year) * 10000 + int(month) * 100 + int(day)
                    # Content entries get priority (0), then sorted by date
                    return (0, date_value)
                except:
                    # Invalid dates go to bottom
                    return (1, float('inf')) if ascending else (0, float('-inf'))
            else:
                # Non-date values go to bottom
                return (1, float('inf')) if ascending else (0, float('-inf'))
        
        # Create a copy to avoid modifying original
        df_copy = df.copy()
        
        # Add temporary column for sorting
        df_copy['_sort_key'] = df_copy[column].apply(date_key)
        
        # Sort by the key
        df_copy = df_copy.sort_values('_sort_key', ascending=ascending)
        
        # Remove temporary column
        df_copy = df_copy.drop('_sort_key', axis=1)
        
        return df_copy
    
    def _sort_by_numeric(self, df: pd.DataFrame, column: str, ascending: bool) -> pd.DataFrame:
        """
        Sort DataFrame by numeric column
        
        Args:
            df: DataFrame to sort
            column: Numeric column name
            ascending: Sort order
            
        Returns:
            Sorted DataFrame
        """
        def numeric_key(x):
            if pd.isna(x) or x == '' or x is None:
                # Blank entries go to bottom for ascending, top for descending
                return (1, float('inf')) if ascending else (0, float('-inf'))
            
            value_str = str(x).strip()
            if not value_str:
                return (1, float('inf')) if ascending else (0, float('-inf'))
            
            try:
                num_value = float(value_str)
                # Content entries get priority (0), then sorted by number
                return (0, num_value)
            except ValueError:
                # Non-numeric values go to bottom
                return (1, float('inf')) if ascending else (0, float('-inf'))
        
        # Create a copy to avoid modifying original
        df_copy = df.copy()
        
        # Add temporary column for sorting
        df_copy['_sort_key'] = df_copy[column].apply(numeric_key)
        
        # Sort by the key
        df_copy = df_copy.sort_values('_sort_key', ascending=ascending)
        
        # Remove temporary column
        df_copy = df_copy.drop('_sort_key', axis=1)
        
        return df_copy
    
    def _sort_by_string(self, df: pd.DataFrame, column: str, ascending: bool) -> pd.DataFrame:
        """
        Sort DataFrame by string column (alphabetical)
        
        Args:
            df: DataFrame to sort
            column: String column name
            ascending: Sort order
            
        Returns:
            Sorted DataFrame
        """
        def string_key(x):
            if pd.isna(x) or x == '' or x is None:
                # Blank entries go to bottom for ascending, top for descending
                return (1, "zzz") if ascending else (0, "")
            
            value_str = str(x).strip()
            if not value_str:
                return (1, "zzz") if ascending else (0, "")
            
            # Content entries get priority (0), then sorted alphabetically
            return (0, value_str.lower())
        
        # Create a copy to avoid modifying original
        df_copy = df.copy()
        
        # Add temporary column for sorting
        df_copy['_sort_key'] = df_copy[column].apply(string_key)
        
        # Sort by the key
        df_copy = df_copy.sort_values('_sort_key', ascending=ascending)
        
        # Remove temporary column
        df_copy = df_copy.drop('_sort_key', axis=1)
        
        return df_copy
    
    def sort_list(self, data: List[Any], ascending: bool = True) -> List[Any]:
        """
        Sort a list with intelligent type detection
        
        Args:
            data: List to sort
            ascending: Sort order
            
        Returns:
            Sorted list
        """
        if not data:
            return data
        
        # Convert to pandas Series for analysis
        series = pd.Series(data)
        sort_type = self._detect_sort_type(series)
        
        if sort_type == 'date':
            return self._sort_list_by_date(data, ascending)
        elif sort_type == 'numeric':
            return self._sort_list_by_numeric(data, ascending)
        else:
            return self._sort_list_by_string(data, ascending)
    
    def _sort_list_by_date(self, data: List[Any], ascending: bool) -> List[Any]:
        """Sort list by date values"""
        def date_key(x):
            if pd.isna(x) or x == '' or x is None:
                return (1, float('inf')) if ascending else (0, float('-inf'))
            
            value_str = str(x).strip()
            if not value_str:
                return (1, float('inf')) if ascending else (0, float('-inf'))
            
            if self._is_date_format(value_str):
                try:
                    month, day, year = value_str.split('/')
                    date_value = int(year) * 10000 + int(month) * 100 + int(day)
                    return (0, date_value)
                except:
                    return (1, float('inf')) if ascending else (0, float('-inf'))
            else:
                return (1, float('inf')) if ascending else (0, float('-inf'))
        
        return sorted(data, key=date_key, reverse=not ascending)
    
    def _sort_list_by_numeric(self, data: List[Any], ascending: bool) -> List[Any]:
        """Sort list by numeric values"""
        def numeric_key(x):
            if pd.isna(x) or x == '' or x is None:
                return (1, float('inf')) if ascending else (0, float('-inf'))
            
            value_str = str(x).strip()
            if not value_str:
                return (1, float('inf')) if ascending else (0, float('-inf'))
            
            try:
                return (0, float(value_str))
            except ValueError:
                return (1, float('inf')) if ascending else (0, float('-inf'))
        
        return sorted(data, key=numeric_key, reverse=not ascending)
    
    def _sort_list_by_string(self, data: List[Any], ascending: bool) -> List[Any]:
        """Sort list by string values"""
        def string_key(x):
            if pd.isna(x) or x == '' or x is None:
                return (1, "zzz") if ascending else (0, "")
            
            value_str = str(x).strip()
            if not value_str:
                return (1, "zzz") if ascending else (0, "")
            
            return (0, value_str.lower())
        
        return sorted(data, key=string_key, reverse=not ascending)
    
    def get_sort_direction_indicator(self, column: str, ascending: bool) -> str:
        """
        Get visual indicator for sort direction
        
        Args:
            column: Column name
            ascending: Sort direction
            
        Returns:
            Column name with sort indicator
        """
        indicator = "↑" if ascending else "↓"
        return f"{column} {indicator}"
