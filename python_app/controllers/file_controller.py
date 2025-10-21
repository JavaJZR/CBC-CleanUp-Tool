"""
File Controller
Handles file operations and data management
"""

from typing import Optional
from tkinter import messagebox, filedialog
import pandas as pd
from pathlib import Path
from datetime import datetime
import re
from models.file_handler import FileHandler

class FileController:
    """Handles file operations"""
    
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.file_handler = FileHandler()
    
    def handle_file_upload(self, file_type: str, file_path: str):
        """Handle file upload request"""
        try:
            # Show loading state
            self.main_controller.main_window.root.config(cursor="wait")
            
            # Load file based on extension
            file_extension = Path(file_path).suffix.lower()
            if file_extension == '.csv':
                df = self.file_handler.detect_and_load_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = self.file_handler.detect_and_load_excel(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format. Please upload CSV, XLS, or XLSX files.")
                return
            
            # Validate data
            if df.empty:
                messagebox.showerror("Error", "File is empty or contains no data.")
                return
            
            # Store data in model
            self.store_file_data(file_type, df, file_path)
            
            # Update view
            file_name, _, row_count, col_count = self.file_handler.get_file_info(file_path)
            self.main_controller.main_window.file_upload_view.update_file_card(
                file_type, file_name, row_count, col_count
            )
            
            # Check if ready for next step
            if self.main_controller.employee_dataset.is_ready_for_processing():
                self.main_controller.show_preview_section()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse file:\n{str(e)}\n\nPlease ensure your file:\n• Is a valid CSV, XLS, or XLSX file\n• Contains column headers in the first row\n• Is not corrupted or password-protected")
        finally:
            self.main_controller.main_window.root.config(cursor="")
    
    def store_file_data(self, file_type: str, df: pd.DataFrame, file_path: str):
        """Store file data in the model"""
        dataset = self.main_controller.employee_dataset
        
        # Store file path
        dataset.file_paths[file_type] = file_path
        
        # Store dataframe
        if file_type == 'current_system':
            dataset.current_system = df
        elif file_type == 'previous_reference':
            dataset.previous_reference = df
        elif file_type == 'masterlist_current':
            dataset.masterlist_current = df
        elif file_type == 'masterlist_resigned':
            dataset.masterlist_resigned = df
    
    def handle_export_request(self, data_type: str, format_type: str):
        """Handle export request"""
        try:
            # Build filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = "Report"
            
            # Try to get base name from uploaded current system file
            if self.main_controller.employee_dataset.file_paths.get('current_system'):
                base_name = Path(self.main_controller.employee_dataset.file_paths['current_system']).stem
            
            # Get data based on type
            if data_type == "cleaned_report":
                df = self.main_controller.employee_dataset.cleaned_data
                if format_type == "excel":
                    self.export_cleaned_data_excel(df, base_name, timestamp)
                else:
                    self.export_cleaned_data_csv(df, base_name, timestamp)
            elif data_type == "unmatched_for_review":
                df = self.main_controller.employee_dataset.unmatched_data
                filename = self.file_handler.build_filename(base_name, "unmatched_for_review", timestamp, format_type)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=f".{format_type}",
                    initialfile=filename,
                    filetypes=[("Excel files", "*.xlsx")] if format_type == "excel" else [("CSV files", "*.csv")]
                )
                if file_path:
                    if format_type == "excel":
                        self.file_handler.export_to_excel(df, file_path)
                    else:
                        self.file_handler.export_to_csv(df, file_path)
                    messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
            elif data_type == "fuzzy_logic_matches":
                df = self.main_controller.employee_dataset.fuzzy_matched_data
                filename = self.file_handler.build_filename(base_name, "fuzzy_logic_matches", timestamp, format_type)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=f".{format_type}",
                    initialfile=filename,
                    filetypes=[("Excel files", "*.xlsx")] if format_type == "excel" else [("CSV files", "*.csv")]
                )
                if file_path:
                    if format_type == "excel":
                        self.file_handler.export_to_excel(df, file_path)
                    else:
                        self.file_handler.export_to_csv(df, file_path)
                    messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_cleaned_data_excel(self, df: pd.DataFrame, base_name: str, timestamp: str):
        """Export cleaned data to Excel with multiple sheets"""
        if df is None or df.empty:
            messagebox.showwarning("No Data", "No data available to export.")
            return
        
        filename = self.file_handler.build_filename(base_name, "cleaned_report", timestamp, "xlsx")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=filename,
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if file_path:
            # Create resigned users dataframe
            resigned_users = self.get_resigned_users_data(df)
            
            # Create current users dataframe (exclude resigned users)
            current_users = self.get_current_users_data(df)
            
            # Export with multiple sheets
            multi_sheet_data = {
                'Cleaned Data': df,
                'Resigned Users': resigned_users if resigned_users is not None and not resigned_users.empty else pd.DataFrame(columns=df.columns),
                'Current Users': current_users if current_users is not None and not current_users.empty else pd.DataFrame(columns=df.columns)
            }
            
            self.file_handler.export_to_excel(df, file_path, multi_sheet_data)
            messagebox.showinfo("Success", f"Data exported to:\n{file_path}\n\nSheets created:\n• Cleaned Data\n• Resigned Users\n• Current Users")
    
    def export_cleaned_data_csv(self, df: pd.DataFrame, base_name: str, timestamp: str):
        """Export cleaned data to CSV"""
        if df is None or df.empty:
            messagebox.showwarning("No Data", "No data available to export.")
            return
        
        filename = self.file_handler.build_filename(base_name, "cleaned_report", timestamp, "csv")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=filename,
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            self.file_handler.export_to_csv(df, file_path)
            messagebox.showinfo("Success", f"Data exported to:\n{file_path}\n\nNote: CSV format doesn't support multiple sheets. Only main data exported.")
    
    def get_resigned_users_data(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Extract resigned users based on resignation date"""
        if df is None or df.empty:
            return None
        
        resigned_mask = df['Resignation Date'].notna() & (df['Resignation Date'] != '') & (df['Resignation Date'] != 'None')
        resigned_users = df[resigned_mask].copy()
        
        if resigned_users.empty:
            return None
        
        # Sort by resignation date (most recent first)
        try:
            resigned_users['Resignation Date'] = pd.to_datetime(resigned_users['Resignation Date'], format='%m/%d/%Y', errors='coerce')
            resigned_users = resigned_users.sort_values('Resignation Date', ascending=False)
            resigned_users['Resignation Date'] = resigned_users['Resignation Date'].dt.strftime('%m/%d/%Y')
        except:
            resigned_users = resigned_users.sort_values('Resignation Date', ascending=False)
        
        return resigned_users
    
    def get_current_users_data(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Extract current users (exclude resigned users)"""
        if df is None or df.empty:
            return None
        
        current_mask = df['Resignation Date'].isna() | (df['Resignation Date'] == '') | (df['Resignation Date'] == 'None')
        current_users = df[current_mask].copy()
        
        if current_users.empty:
            return None
        
        # Sort by PERNR for consistent ordering
        try:
            current_users['PERNR'] = pd.to_numeric(current_users['PERNR'], errors='coerce')
            current_users = current_users.sort_values('PERNR', ascending=True)
            current_users['PERNR'] = current_users['PERNR'].astype(str)
        except:
            current_users = current_users.sort_values('PERNR', ascending=True)
        
        return current_users
