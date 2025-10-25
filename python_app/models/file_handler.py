"""
File Handler Model
Handles file I/O operations and data loading
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import re


class FileHandler:
    """Handles file I/O operations"""
    
    @staticmethod
    def detect_and_load_csv(file_path: str) -> pd.DataFrame:
        """Detect header row and load CSV file by searching for 'Full Name'"""
        # First try standard loading
        try:
            df = pd.read_csv(file_path)
            if 'Full Name' in df.columns:
                return df
        except:
            pass
        
        # Search for 'Full Name' in the first 10 rows
        for header_row in range(10):  # Check first 10 rows
            try:
                df = pd.read_csv(file_path, header=header_row)
                if 'Full Name' in df.columns:
                    return df
            except:
                continue
        
        # If 'Full Name' not found, try keyword detection
        for header_row in range(10):
            try:
                df = pd.read_csv(file_path, header=header_row)
                if FileHandler._is_valid_header(df.columns):
                    return df
            except:
                continue
        
        # Fallback to first row
        return pd.read_csv(file_path)
    
    @staticmethod
    def detect_and_load_excel(file_path: str) -> pd.DataFrame:
        """Detect header row and load Excel file by searching for 'Full Name'"""
        # First try standard loading
        try:
            df = pd.read_excel(file_path)
            if 'Full Name' in df.columns:
                return df
        except:
            pass
        
        # Search for 'Full Name' in the first 10 rows
        for header_row in range(10):  # Check first 10 rows
            try:
                df = pd.read_excel(file_path, header=header_row)
                if 'Full Name' in df.columns:
                    return df
            except:
                continue
        
        # If 'Full Name' not found, try keyword detection
        for header_row in range(10):
            try:
                df = pd.read_excel(file_path, header=header_row)
                if FileHandler._is_valid_header(df.columns):
                    return df
            except:
                continue
        
        # Fallback to first row
        return pd.read_excel(file_path)
    
    @staticmethod
    def _is_valid_header(columns) -> bool:
        """Check if columns look like valid headers by looking for expected keywords"""
        column_names = [str(col).lower() for col in columns]
        
        # Look for common employee data keywords
        expected_keywords = [
            'pernr', 'pers. number', 'employee number', 'emp number',
            'full name', 'name', 'employee name', 'username',
            'user id', 'userid', 'sysid', 'abbreviation', 'department', 'position',
            'resignation', 'date', 'effectivity'
        ]
        
        # Count how many expected keywords are found
        found_keywords = sum(1 for keyword in expected_keywords 
                           if any(keyword in col for col in column_names))
        
        # If we find at least 2 expected keywords, consider it a valid header
        return found_keywords >= 2
    
    @staticmethod
    def export_to_excel(df: pd.DataFrame, file_path: str, multi_sheet_data: Optional[dict] = None):
        """Export DataFrame to Excel with optional multi-sheet support and date formatting"""
        if multi_sheet_data:
            # Export with multiple sheets
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, sheet_df in multi_sheet_data.items():
                    if sheet_df is not None and not sheet_df.empty:
                        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # Apply date formatting to Resignation Date column if it exists
                        if 'Resignation Date' in sheet_df.columns:
                            FileHandler._format_resignation_date_column(writer, sheet_name, sheet_df)
                    else:
                        # Create empty sheet with headers if no data
                        empty_df = pd.DataFrame(columns=df.columns if df is not None else [])
                        empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Single sheet export
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                
                # Apply date formatting to Resignation Date column if it exists
                if 'Resignation Date' in df.columns:
                    FileHandler._format_resignation_date_column(writer, 'Sheet1', df)
    
    @staticmethod
    def _format_resignation_date_column(writer, sheet_name: str, df: pd.DataFrame):
        """Format the Resignation Date column as date type in Excel"""
        from openpyxl.styles import numbers
        
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Find the column index for "Resignation Date"
        column_index = None
        for col_num, column_title in enumerate(df.columns, 1):
            if column_title == 'Resignation Date':
                column_index = col_num
                break
        
        if column_index is not None:
            # Apply date format to all cells in the Resignation Date column (starting from row 2 to skip header)
            date_format = numbers.FORMAT_DATE_XLSX14  # This is the date format 'mm-dd-yy'
            
            for row_num in range(2, len(df) + 2):  # +2 because Excel is 1-indexed and has header
                cell = worksheet.cell(row=row_num, column=column_index)
                
                # Convert string date to datetime if it's not None/empty
                if cell.value and str(cell.value).strip():
                    try:
                        # Parse the MM/DD/YYYY format
                        from datetime import datetime
                        date_obj = datetime.strptime(str(cell.value), '%m/%d/%Y')
                        cell.value = date_obj
                        cell.number_format = date_format
                    except (ValueError, TypeError):
                        # If date parsing fails, leave as string
                        pass
    
    @staticmethod
    def export_to_csv(df: pd.DataFrame, file_path: str):
        """Export DataFrame to CSV"""
        df.to_csv(file_path, index=False)
    
    @staticmethod
    def build_filename(base_name: str, label: str, timestamp: str, extension: str) -> str:
        """Build a standardized filename"""
        # Sanitize base name
        sanitized_base = re.sub(r"[^A-Za-z0-9 _\-]", "", str(base_name)).strip()
        formatted_label = label.replace("_", " ").title()
        return f"{sanitized_base} - {formatted_label} - {timestamp}.{extension}"
    
    @staticmethod
    def get_file_info(file_path: str) -> Tuple[str, str, int, int]:
        """Get file information (name, extension, rows, columns)"""
        path_obj = Path(file_path)
        file_name = path_obj.name
        extension = path_obj.suffix.lower()
        
        # Try to get row and column count
        try:
            if extension == '.csv':
                df = pd.read_csv(file_path)
            elif extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                return file_name, extension, 0, 0
            
            return file_name, extension, len(df), len(df.columns)
        except:
            return file_name, extension, 0, 0
