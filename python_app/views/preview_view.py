"""
Preview View
Handles data preview UI components
"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Optional
import pandas as pd

if TYPE_CHECKING:
    from controllers.main_controller import MainController

class PreviewView:
    """Data preview UI component"""
    
    def __init__(self, parent, controller: 'MainController'):
        self.parent = parent
        self.controller = controller
        self.preview_frame: Optional[tk.Frame] = None
        self.preview_selector: Optional[ttk.Combobox] = None
        self.preview_table_frame: Optional[tk.Frame] = None
    
    def show(self):
        """Show data preview section"""
        if self.preview_frame:
            self.preview_frame.destroy()
            
        self.preview_frame = tk.LabelFrame(
            self.parent,
            text="2️⃣ Data Preview",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2563eb",
            padx=15,
            pady=15
        )
        self.preview_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        # Description and controls
        top_frame = tk.Frame(self.preview_frame, bg="white")
        top_frame.pack(fill="x", pady=(0, 10))
        
        desc_label = tk.Label(
            top_frame,
            text="Review your uploaded data to ensure it's structured correctly",
            font=("Arial", 9),
            bg="white",
            fg="#6b7280"
        )
        desc_label.pack(side="left")
        
        # File selector
        selector_frame = tk.Frame(top_frame, bg="white")
        selector_frame.pack(side="right")
        
        tk.Label(
            selector_frame,
            text="Select File:",
            font=("Arial", 9),
            bg="white"
        ).pack(side="left", padx=(0, 5))
        
        self.preview_selector = ttk.Combobox(
            selector_frame,
            state="readonly",
            width=30
        )
        self.preview_selector.pack(side="left", padx=(0, 10))
        self.preview_selector.bind("<<ComboboxSelected>>", self.on_file_selected)
        
        # Continue button
        continue_btn = tk.Button(
            selector_frame,
            text="Continue to Clean-Up →",
            command=self.continue_to_cleanup,
            bg="#dc2626",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        continue_btn.pack(side="left")
        
        # Preview table
        self.preview_table_frame = tk.Frame(self.preview_frame, bg="white")
        self.preview_table_frame.pack(fill="both", expand=True)
        
        self.update_file_selector()
    
    def update_file_selector(self):
        """Update file selector with uploaded files"""
        file_names = {
            'current_system': 'Current System Report',
            'previous_reference': 'Previous Reference',
            'masterlist_current': 'Masterlist – Current',
            'masterlist_resigned': 'Masterlist – Resigned'
        }
        
        dataset = self.controller.employee_dataset
        available_files = []
        
        if dataset.current_system is not None:
            available_files.append(file_names['current_system'])
        if dataset.previous_reference is not None:
            available_files.append(file_names['previous_reference'])
        if dataset.masterlist_current is not None:
            available_files.append(file_names['masterlist_current'])
        if dataset.masterlist_resigned is not None:
            available_files.append(file_names['masterlist_resigned'])
        
        self.preview_selector['values'] = available_files
        if available_files and not self.preview_selector.get():
            self.preview_selector.current(0)
            self.update_preview()
    
    def on_file_selected(self, event=None):
        """Handle file selection change"""
        self.update_preview()
    
    def update_preview(self):
        """Update preview table with selected file"""
        selected = self.preview_selector.get()
        if not selected:
            return
            
        # Map display name to key
        name_to_key = {
            'Current System Report': 'current_system',
            'Previous Reference': 'previous_reference',
            'Masterlist – Current': 'masterlist_current',
            'Masterlist – Resigned': 'masterlist_resigned'
        }
        
        key = name_to_key.get(selected)
        dataset = self.controller.employee_dataset
        
        if key == 'current_system':
            df = dataset.current_system
        elif key == 'previous_reference':
            df = dataset.previous_reference
        elif key == 'masterlist_current':
            df = dataset.masterlist_current
        elif key == 'masterlist_resigned':
            df = dataset.masterlist_resigned
        else:
            return
        
        if df is None:
            return
            
        # Clear existing table
        for widget in self.preview_table_frame.winfo_children():
            widget.destroy()
            
        # Create table
        self.create_preview_table(df)
    
    def create_preview_table(self, df: pd.DataFrame):
        """Create preview table display"""
        table_container = tk.Frame(self.preview_table_frame, bg="white")
        table_container.pack(fill="both", expand=True)
        
        # Add scrollbars
        x_scroll = ttk.Scrollbar(table_container, orient="horizontal")
        y_scroll = ttk.Scrollbar(table_container, orient="vertical")
        
        # Create treeview
        columns = list(df.columns)
        tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="tree headings",
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
            height=15
        )
        
        x_scroll.config(command=tree.xview)
        y_scroll.config(command=tree.yview)
        
        # Configure columns
        tree.column("#0", width=50, minwidth=50)
        tree.heading("#0", text="Row")
        
        for col in columns:
            tree.column(col, width=150, minwidth=100)
            tree.heading(col, text=str(col), command=lambda c=col: self.sort_treeview(tree, c, False))
            
        # Add data (first 100 rows for performance)
        for idx, row in df.head(100).iterrows():
            values = [str(val) for val in row]
            tree.insert("", "end", text=str(idx + 1), values=values)
            
        # Pack elements
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Info label
        info_label = tk.Label(
            self.preview_table_frame,
            text=f"Showing first 100 rows of {len(df)} total rows",
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
        )
        info_label.pack(pady=(5, 0))
    
    def sort_treeview(self, tree, col, reverse):
        """Sort treeview by column"""
        # Get all items
        items = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        # Determine data type by analyzing column content
        numeric_count = 0
        date_count = 0
        total_count = len(items)
        
        for val, _ in items:
            if val and val.strip():  # Skip empty values
                # Check if value is numeric (including decimals and negative numbers)
                try:
                    float(val)
                    numeric_count += 1
                except ValueError:
                    pass
                
                # Check if value is a date in MM/DD/YYYY format
                if self.is_date_format(val):
                    date_count += 1
        
        # Determine sorting method based on content analysis
        if total_count > 0 and (date_count / total_count) > 0.5:
            # Sort as dates (MM/DD/YYYY format)
            def date_key(x):
                val = x[0]
                if not val or not val.strip():
                    # Blank entries go to bottom for ascending, top for descending
                    return (1, float('inf')) if not reverse else (0, float('-inf'))
                
                if self.is_date_format(val):
                    try:
                        # Parse MM/DD/YYYY format
                        month, day, year = val.split('/')
                        # Convert to sortable format (YYYYMMDD)
                        date_value = int(year) * 10000 + int(month) * 100 + int(day)
                        # Content entries get priority (0), then sorted by date
                        return (0, date_value)
                    except:
                        # Invalid dates go to bottom
                        return (1, float('inf')) if not reverse else (0, float('-inf'))
                else:
                    # Non-date values go to bottom
                    return (1, float('inf')) if not reverse else (0, float('-inf'))
            
            items.sort(key=date_key, reverse=reverse)
            
        elif total_count > 0 and (numeric_count / total_count) > 0.7:
            # Sort as numbers
            def numeric_key(x):
                val = x[0]
                if not val or not val.strip():
                    # Blank entries go to bottom for ascending, top for descending
                    return (1, float('inf')) if not reverse else (0, float('-inf'))
                
                try:
                    num_value = float(val)
                    # Content entries get priority (0), then sorted by number
                    return (0, num_value)
                except ValueError:
                    # Non-numeric values go to bottom
                    return (1, float('inf')) if not reverse else (0, float('-inf'))
            
            items.sort(key=numeric_key, reverse=reverse)
        else:
            # Sort as strings (alphabetical)
            def string_key(x):
                val = x[0]
                if not val or not val.strip():
                    # Blank entries go to bottom for ascending, top for descending
                    return (1, "zzz") if not reverse else (0, "")
                
                # Content entries get priority (0), then sorted alphabetically
                return (0, val.lower())
            
            items.sort(key=string_key, reverse=reverse)
        
        # Align items in sorted positions
        for index, (val, child) in enumerate(items):
            tree.move(child, '', index)
        
        # Update column header to show sort direction
        for c in tree['columns']:
            if c == col:
                tree.heading(c, text=f"{str(c)} {'↓' if reverse else '↑'}")
            else:
                tree.heading(c, text=str(c))
        
        # Store sort state
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))
    
    def is_date_format(self, value):
        """Check if a value matches MM/DD/YYYY date format"""
        if not value or not isinstance(value, str):
            return False
        
        # Check for MM/DD/YYYY pattern
        import re
        date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
        if re.match(date_pattern, value.strip()):
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
    
    def continue_to_cleanup(self):
        """Continue to cleanup section"""
        if hasattr(self, 'controller') and self.controller:
            self.controller.show_cleanup_section()
