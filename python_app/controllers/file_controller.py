"""
File Controller
Handles file operations and data management
"""

from typing import Optional
from tkinter import messagebox, filedialog
import pandas as pd
from pathlib import Path
from datetime import datetime
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
            
            # For current system report, show header selection dialog first
            if file_type == 'current_system':
                # Store file path temporarily
                temp_file_path = file_path
                
                # Reset cursor for dialog
                self.main_controller.main_window.root.config(cursor="")
                
                # Show header selection dialog
                from views.header_selection_dialog import HeaderSelectionDialog
                
                def on_header_selection_complete(header_row: int, user_id_column: Optional[str], full_name_column: Optional[str]):
                    """Callback when user confirms header and column selection"""
                    try:
                        # Show loading state again
                        self.main_controller.main_window.root.config(cursor="wait")
                        
                        # Load file with selected header row
                        file_extension = Path(temp_file_path).suffix.lower()
                        if file_extension == '.csv':
                            df = self.file_handler.detect_and_load_csv(temp_file_path, file_type, header_row)
                        elif file_extension in ['.xlsx', '.xls']:
                            df = self.file_handler.detect_and_load_excel(temp_file_path, file_type, header_row)
                        else:
                            messagebox.showerror("Error", "Unsupported file format. Please upload CSV, XLS, or XLSX files.")
                            return
                        
                        # Validate data
                        if df.empty:
                            messagebox.showerror("Error", "File is empty or contains no data.")
                            return
                        
                        # Auto-detect columns if not provided (they will be selected in cleanup section)
                        if not user_id_column:
                            # Try to find a User ID column automatically
                            name_columns = [col for col in df.columns 
                                          if any(keyword in str(col).lower() for keyword in ['user', 'id', 'sysid', 'username', 'abbreviation'])]
                            user_id_column = name_columns[0] if name_columns else None
                        
                        if not full_name_column:
                            # Try to find a Full Name column automatically
                            name_columns = [col for col in df.columns 
                                          if any(keyword in str(col).lower() for keyword in ['full name', 'name', 'username', 'user description', 'description', 'user desc', 'desc'])]
                            full_name_column = name_columns[0] if name_columns else None
                        
                        # Store configuration (columns can be None - they will be selected in cleanup section)
                        self.main_controller.employee_dataset.set_current_system_config(header_row, user_id_column, full_name_column)
                        
                        # Store data in model
                        self.store_file_data(file_type, df, temp_file_path)
                        
                        # Update view
                        file_name, _, row_count, col_count = self.file_handler.get_file_info(temp_file_path)
                        self.main_controller.main_window.file_upload_view.update_file_card(
                            file_type, file_name, row_count, col_count
                        )
                        
                        # Check if ready for next step
                        if self.main_controller.employee_dataset.is_ready_for_processing():
                            self.main_controller.show_preview_section()
                        
                    except Exception as e:
                        error_msg = f"Failed to load file with selected header row:\n{str(e)}\n\nPlease ensure your file:\n• Is a valid CSV, XLS, or XLSX file\n• Contains column headers in the selected row\n• Is not corrupted or password-protected"
                        messagebox.showerror("Error", error_msg)
                    finally:
                        self.main_controller.main_window.root.config(cursor="")
                
                # Show the dialog
                HeaderSelectionDialog(
                    self.main_controller.main_window.root,
                    temp_file_path,
                    on_header_selection_complete
                )
                
                return  # Exit early, dialog will handle the rest
            
            # For other file types, use standard loading
            # Load file based on extension
            file_extension = Path(file_path).suffix.lower()
            if file_extension == '.csv':
                df = self.file_handler.detect_and_load_csv(file_path, file_type)
            elif file_extension in ['.xlsx', '.xls']:
                df = self.file_handler.detect_and_load_excel(file_path, file_type)
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
            error_msg = f"Failed to parse file:\n{str(e)}\n\nPlease ensure your file:\n• Is a valid CSV, XLS, or XLSX file\n• Contains column headers (may not be in the first row)\n• Is not corrupted or password-protected\n\nNote: The system will automatically detect headers in different rows and handle merged cells for system reports."
            messagebox.showerror("Error", error_msg)
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
            dataset.save_masterlist_path(file_type, file_path)
        elif file_type == 'masterlist_resigned':
            dataset.masterlist_resigned = df
            dataset.save_masterlist_path(file_type, file_path)
    
    def reselect_current_system_header(self):
        """Allow user to change the header row selection for the current system report"""
        dataset = self.main_controller.employee_dataset
        current_path = dataset.file_paths.get('current_system')
        
        if not current_path:
            messagebox.showwarning("No File Loaded", "Please upload a Current System Report first before changing the header row.")
            return
        
        path_obj = Path(current_path)
        if not path_obj.exists():
            messagebox.showerror("File Not Found", "The previously uploaded Current System Report cannot be found. Please upload the file again.")
            return
        
        # Ensure cursor reset for dialog interaction
        self.main_controller.main_window.root.config(cursor="")
        
        from views.header_selection_dialog import HeaderSelectionDialog
        
        def on_header_selection_complete(header_row: int, user_id_column: Optional[str], full_name_column: Optional[str]):
            try:
                self.main_controller.main_window.root.config(cursor="wait")
                
                file_extension = path_obj.suffix.lower()
                if file_extension == '.csv':
                    df = self.file_handler.detect_and_load_csv(str(path_obj), 'current_system', header_row)
                elif file_extension in ['.xlsx', '.xls']:
                    df = self.file_handler.detect_and_load_excel(str(path_obj), 'current_system', header_row)
                else:
                    messagebox.showerror("Error", "Unsupported file format. Please upload CSV, XLS, or XLSX files.")
                    return
                
                if df.empty:
                    messagebox.showerror("Error", "File is empty or contains no data.")
                    return
                
                # Auto-detect columns if not provided
                if not user_id_column:
                    name_columns = [col for col in df.columns 
                                    if any(keyword in str(col).lower() for keyword in ['user', 'id', 'sysid', 'username', 'abbreviation'])]
                    user_id_column = name_columns[0] if name_columns else None
                
                if not full_name_column:
                    name_columns = [col for col in df.columns 
                                    if any(keyword in str(col).lower() for keyword in ['full name', 'name', 'username', 'user description', 'description', 'user desc', 'desc'])]
                    full_name_column = name_columns[0] if name_columns else None
                
                dataset.set_current_system_config(header_row, user_id_column, full_name_column)
                self.store_file_data('current_system', df, str(path_obj))
                
                # Update UI card info
                file_name, _, row_count, col_count = self.file_handler.get_file_info(str(path_obj))
                if self.main_controller.main_window and self.main_controller.main_window.file_upload_view:
                    self.main_controller.main_window.file_upload_view.update_file_card(
                        'current_system', file_name, row_count, col_count
                    )
                
                # Refresh cleanup column headers if available
                if self.main_controller.main_window and self.main_controller.main_window.cleanup_view:
                    cleanup_view = self.main_controller.main_window.cleanup_view
                    cleanup_view.refresh_column_headers()
                    cleanup_view.refresh_full_name_options()
                
                messagebox.showinfo("Header Updated", "Header row selection has been updated successfully.")
            except Exception as e:
                error_msg = f"Failed to load file with selected header row:\n{str(e)}\n\nPlease ensure your file:\n• Contains column headers in the selected row\n• Is not corrupted or password-protected"
                messagebox.showerror("Error", error_msg)
            finally:
                self.main_controller.main_window.root.config(cursor="")
        
        HeaderSelectionDialog(
            self.main_controller.main_window.root,
            str(path_obj),
            on_header_selection_complete
        )
    
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
                'Masterdata': df,
                'Resigned Users': resigned_users if resigned_users is not None and not resigned_users.empty else pd.DataFrame(columns=df.columns),
                'Active Users': current_users if current_users is not None and not current_users.empty else pd.DataFrame(columns=df.columns)
            }
            
            self.file_handler.export_to_excel(df, file_path, multi_sheet_data)
            messagebox.showinfo("Success", f"Data exported to:\n{file_path}\n\nSheets created:\n• Masterdata\n• Resigned Users\n• Active Users")
    
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
        
        resigned_mask = df['Resignation Date'].apply(self._is_valid_resignation_date)
        resigned_users = df[resigned_mask].copy()
        if 'PERNR' in resigned_users.columns:
            resigned_users['PERNR'] = resigned_users['PERNR'].apply(self._format_pernr_value)
        
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
        
        current_mask = ~df['Resignation Date'].apply(self._is_valid_resignation_date)
        current_users = df[current_mask].copy()
        
        if current_users.empty:
            return None
        
        # Sort by PERNR for consistent ordering
        try:
            current_users['PERNR_sort_key'] = pd.to_numeric(current_users['PERNR'], errors='coerce')
            current_users = current_users.sort_values('PERNR_sort_key', ascending=True)
        except:
            current_users = current_users.sort_values('PERNR', ascending=True)

        if 'PERNR' in current_users.columns:
            current_users['PERNR'] = current_users['PERNR'].apply(self._format_pernr_value)
        if 'PERNR_sort_key' in current_users.columns:
            current_users = current_users.drop(columns=['PERNR_sort_key'])
        
        return current_users

    def _format_pernr_value(self, value):
        """Normalize PERNR so exports have no trailing decimals."""
        if pd.isna(value):
            return ""

        if isinstance(value, str):
            value_str = value.strip()
            if not value_str:
                return ""
            if value_str.endswith(".0"):
                return value_str[:-2]
            return value_str

        try:
            if isinstance(value, float) and value.is_integer():
                return str(int(value))
            int_val = int(value)
            if float(int_val) == float(value):
                return str(int_val)
        except (ValueError, TypeError, OverflowError):
            pass

        value_str = str(value)
        if value_str.endswith(".0"):
            return value_str[:-2]
        return value_str

    def _is_valid_resignation_date(self, value):
        """Return True when value represents an actual resignation date."""
        if pd.isna(value):
            return False

        value_str = str(value).strip()
        if not value_str:
            return False

        invalid_keywords = [
            "ACTIVE",
            "EXTENDED",
            "WITH NEW PERNR",
            "W/ NEW PERNR",
            "NO RESIGNATION",
            "NONE",
            "N/A",
            "NA",
            "PENDING",
            "ON HOLD"
        ]
        value_upper = value_str.upper()
        if any(keyword in value_upper for keyword in invalid_keywords):
            return False
        
        parsed_date = pd.to_datetime(value_str, format='%m/%d/%Y', errors='coerce')
        return pd.notna(parsed_date)

