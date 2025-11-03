"""
Header Selection Dialog
Dialog for selecting header row and User ID column for current system report
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from typing import Optional, Callable


class HeaderSelectionDialog:
    """Dialog for selecting header row and User ID column"""
    
    def __init__(self, parent, file_path: str, on_complete: Callable):
        """
        Initialize the dialog
        
        Args:
            parent: Parent window
            file_path: Path to the file to load
            on_complete: Callback function with (header_row, user_id_column) parameters
        """
        self.parent = parent
        self.file_path = file_path
        self.on_complete = on_complete
        
        # Store preview dataframes for each potential header row
        self.preview_dataframes = {}
        
        # Selected values
        self.selected_header_row = None
        self.selected_user_id_column = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Header Row and User ID Column")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Make dialog modal
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Center the dialog
        self.center_dialog()
        
        # Load preview data for rows 1-5
        self.load_preview_data()
        
        # Create UI
        self.create_ui()
    
    def center_dialog(self):
        """Center the dialog on the screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_preview_data(self):
        """Load preview data for rows 1-5"""
        try:
            # Read file without headers to see raw data
            file_extension = self.file_path.lower().split('.')[-1]
            
            # Read first 5 rows as raw data
            if file_extension == 'csv':
                # Read CSV without header
                df_raw = pd.read_csv(self.file_path, header=None, nrows=5, dtype=str)
            else:
                # Read Excel without header
                df_raw = pd.read_excel(self.file_path, header=None, nrows=5, dtype=str)
            
            # Store each row as a potential header row (0-indexed, so row 1 = index 0)
            for row_idx in range(min(5, len(df_raw))):
                # Read file with this row as header (read enough rows to show preview)
                try:
                    # Read with more rows to account for header row position
                    # e.g., if header is row 2, read 7 rows total to get 5 data rows after header
                    nrows_to_read = row_idx + 6  # header row + 5 data rows + 1 buffer
                    if file_extension == 'csv':
                        df = pd.read_csv(self.file_path, header=row_idx, nrows=nrows_to_read, dtype=str)
                    else:
                        df = pd.read_excel(self.file_path, header=row_idx, nrows=nrows_to_read, dtype=str)
                    
                    # Limit to first 5 data rows for preview
                    df = df.head(5)
                    
                    # Only store if we got valid columns (not all unnamed)
                    if len(df.columns) > 0 and not all('unnamed' in str(col).lower() for col in df.columns[:5]):
                        self.preview_dataframes[row_idx] = {
                            'df': df,
                            'raw_row': df_raw.iloc[row_idx].tolist() if row_idx < len(df_raw) else []
                        }
                except Exception as e:
                    # Skip this row if it fails
                    continue
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preview data:\n{str(e)}")
            self.dialog.destroy()
    
    def create_ui(self):
        """Create the dialog UI"""
        main_frame = tk.Frame(self.dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Configure Current System Report",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#111827"
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Select which row (1-5) contains the column headers.\n\nNote: Column selections (User ID and Full Name) are available in Step 3 (Data Clean-Up) section.",
            font=("Arial", 10),
            bg="white",
            fg="#6b7280",
            justify="left"
        )
        instructions.pack(anchor="w", pady=(0, 20))
        
        # Step 1: Header Row Selection
        step1_frame = tk.LabelFrame(
            main_frame,
            text="Step 1: Select Header Row",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#dc2626",
            padx=15,
            pady=15
        )
        step1_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Create notebook for tabs (one per potential header row)
        notebook = ttk.Notebook(step1_frame)
        notebook.pack(fill="both", expand=True)
        
        # Variable to track selected header row
        self.header_row_var = tk.IntVar(value=0)
        
        # Create tabs for each potential header row
        self.header_row_frames = {}
        for row_idx in range(5):
            if row_idx in self.preview_dataframes:
                tab_frame = tk.Frame(notebook, bg="white")
                notebook.add(tab_frame, text=f"Row {row_idx + 1}")
                
                # Radio button to select this header row
                radio = tk.Radiobutton(
                    tab_frame,
                    text=f"Use Row {row_idx + 1} as headers",
                    variable=self.header_row_var,
                    value=row_idx,
                    command=lambda r=row_idx: self.on_header_row_selected(r),
                    font=("Arial", 11, "bold"),
                    bg="white",
                    fg="#dc2626",
                    activebackground="white",
                    activeforeground="#dc2626"
                )
                radio.pack(anchor="w", padx=10, pady=10)
                
                # Show preview table
                preview_table_frame = tk.Frame(tab_frame, bg="white")
                preview_table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
                
                # Create treeview to show preview
                preview_data = self.preview_dataframes[row_idx]['df']
                
                # Create scrollable frame
                canvas = tk.Canvas(preview_table_frame, bg="white")
                scrollbar = ttk.Scrollbar(preview_table_frame, orient="horizontal", command=canvas.xview)
                scrollable_frame = tk.Frame(canvas, bg="white")
                
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(xscrollcommand=scrollbar.set)
                
                # Show first few rows of data with these headers
                tree = ttk.Treeview(scrollable_frame, show="headings", height=4)
                
                # Configure columns
                columns = list(preview_data.columns)[:10]  # Show first 10 columns
                tree["columns"] = columns
                
                # Set column widths
                for col in columns:
                    tree.heading(col, text=str(col)[:30])  # Truncate long names
                    tree.column(col, width=120, minwidth=100)
                
                # Insert data rows (first 5 rows, but limit display to 3 for space)
                for idx, row in preview_data.head(5).iterrows():
                    values = [str(row.get(col, ''))[:30] for col in columns]
                    tree.insert("", "end", values=values)
                
                tree.pack(side="left", fill="both", expand=True)
                
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                self.header_row_frames[row_idx] = tab_frame
        
        # Variable to track selected Full Name column (not used in dialog anymore)
        self.selected_full_name_column = None
        self.selected_user_id_column = None  # Not used in dialog, but kept for compatibility
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            bg="#6b7280",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        self.confirm_btn = tk.Button(
            button_frame,
            text="Confirm Selection",
            command=self.on_confirm,
            bg="#dc2626",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            state="disabled"
        )
        self.confirm_btn.pack(side="right")
    
    def on_header_row_selected(self, row_idx: int):
        """Handle header row selection"""
        self.selected_header_row = row_idx
        # Enable confirm button when header row is selected
        self.update_confirm_button()
    
    def update_confirm_button(self):
        """Update confirm button state"""
        if self.selected_header_row is not None:
            self.confirm_btn.config(state="normal")
        else:
            self.confirm_btn.config(state="disabled")
    
    def on_confirm(self):
        """Handle confirm button click"""
        if self.selected_header_row is not None:
            # Call the callback with selected values (user_id_column and full_name_column are None - selected in cleanup section)
            self.on_complete(self.selected_header_row, None, None)
            self.dialog.destroy()
        else:
            messagebox.showwarning("Incomplete Selection", "Please select a header row.")
    
    def on_cancel(self):
        """Handle cancel or window close"""
        self.dialog.destroy()
