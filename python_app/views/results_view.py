"""
Results View
Handles results display and export UI components
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import TYPE_CHECKING, Optional, Dict
import pandas as pd

if TYPE_CHECKING:
    from controllers.main_controller import MainController

class ResultsView:
    """Results display UI component"""
    
    def __init__(self, parent, controller: 'MainController'):
        self.parent = parent
        self.controller = controller
        self.results_frame: Optional[tk.Frame] = None
        self.results_selector: Optional[ttk.Combobox] = None
        self.results_preview_frame: Optional[tk.Frame] = None
    
    def show(self, statistics: Dict[str, int]):
        """Show results section"""
        if self.results_frame:
            self.results_frame.destroy()
            
        self.results_frame = tk.LabelFrame(
            self.parent,
            text="4️⃣ Clean-Up Results",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#059669",
            padx=15,
            pady=15
        )
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))
        
        # Description
        desc_label = tk.Label(
            self.results_frame,
            text="Review the enriched data with PERNRs, Full Names, Resignation Dates, and Organizational Data, then export your results",
            font=("Arial", 9),
            bg="white",
            fg="#6b7280"
        )
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Summary stats
        self.create_statistics_display(statistics)
        
        # Preview section
        self.create_preview_section()
        
        # Export buttons
        self.create_export_buttons(statistics)
    
    def create_statistics_display(self, statistics: Dict[str, int]):
        """Create statistics display"""
        stats_frame = tk.Frame(self.results_frame, bg="white")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        stats = [
            ("Total Records", statistics['total'], "#3b82f6"),
            ("Enriched with PERNR", statistics['matched'], "#059669"),
            ("Missing PERNR", statistics['unmatched'], "#ea580c"),
            ("Fuzzy Logic Matches", statistics['fuzzy_matched'], "#8b5cf6")
        ]
        
        for label, value, color in stats:
            stat_card = tk.Frame(stats_frame, bg="#f9fafb", relief="solid", borderwidth=1)
            stat_card.pack(side="left", fill="both", expand=True, padx=5)
            
            tk.Label(
                stat_card,
                text=str(value),
                font=("Arial", 24, "bold"),
                bg="#f9fafb",
                fg=color
            ).pack(pady=(10, 0))
            
            tk.Label(
                stat_card,
                text=label,
                font=("Arial", 9),
                bg="#f9fafb",
                fg="#6b7280"
            ).pack(pady=(0, 10))
    
    def create_preview_section(self):
        """Create data preview section"""
        preview_section = tk.LabelFrame(
            self.results_frame,
            text="📊 Data Preview",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        preview_section.pack(fill="both", expand=True, pady=(0, 15))
        
        # Preview selector
        selector_frame = tk.Frame(preview_section, bg="white")
        selector_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            selector_frame,
            text="View Dataset:",
            font=("Arial", 9, "bold"),
            bg="white"
        ).pack(side="left", padx=(0, 5))
        
        self.results_selector = ttk.Combobox(
            selector_frame,
            state="readonly",
            width=40,
            values=[
                "✓ Enriched Data (with PERNRs, Full Names, Resignation Dates & Organizational Data)",
                "📋 Resigned Users (with Resignation Dates)",
                "👥 Current Users (Active Employees Only)",
                "🔍 Fuzzy Logic Matches (PERNRs found using fuzzy matching)",
                "⚠ Missing PERNRs"
            ]
        )
        self.results_selector.pack(side="left")
        self.results_selector.current(0)
        self.results_selector.bind("<<ComboboxSelected>>", self.on_dataset_selected)
        
        # Preview table frame
        self.results_preview_frame = tk.Frame(preview_section, bg="white")
        self.results_preview_frame.pack(fill="both", expand=True)
        
        # Show initial preview
        self.update_preview()
    
    def create_export_buttons(self, statistics: Dict[str, int]):
        """Create export buttons"""
        export_frame = tk.Frame(self.results_frame, bg="white")
        export_frame.pack(fill="x", pady=(0, 15))
        
        # Cleaned data export
        cleaned_frame = tk.LabelFrame(
            export_frame,
            text="✓ Enriched Report",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#059669",
            padx=10,
            pady=10
        )
        cleaned_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(
            cleaned_frame,
            text=f"All {statistics['total']} records (matched + unmatched) with enriched data where available",
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
        ).pack()
        
        btn_frame1 = tk.Frame(cleaned_frame, bg="white")
        btn_frame1.pack(pady=(10, 0))
        
        tk.Button(
            btn_frame1,
            text="📊 Export Excel",
            command=lambda: self.export_data("cleaned_report", "excel"),
            bg="#059669",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        ).pack(side="left", padx=(0, 5))
        
        tk.Button(
            btn_frame1,
            text="📄 Export CSV",
            command=lambda: self.export_data("cleaned_report", "csv"),
            bg="#059669",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        ).pack(side="left")
        
        # Unmatched data export
        unmatched_frame = tk.LabelFrame(
            export_frame,
            text="⚠ Missing PERNRs",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#ea580c",
            padx=10,
            pady=10
        )
        unmatched_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        tk.Label(
            unmatched_frame,
            text=f"{statistics['unmatched']} records without PERNRs",
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
        ).pack()
        
        btn_frame2 = tk.Frame(unmatched_frame, bg="white")
        btn_frame2.pack(pady=(10, 0))
        
        tk.Button(
            btn_frame2,
            text="📊 Export Excel",
            command=lambda: self.export_data("unmatched_for_review", "excel"),
            bg="#ea580c",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        ).pack(side="left", padx=(0, 5))
        
        tk.Button(
            btn_frame2,
            text="📄 Export CSV",
            command=lambda: self.export_data("unmatched_for_review", "csv"),
            bg="#ea580c",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        ).pack(side="left")
        
        # Fuzzy matched data export (only show if there are fuzzy matches)
        if statistics['fuzzy_matched'] > 0:
            fuzzy_frame = tk.LabelFrame(
                export_frame,
                text="🔍 Fuzzy Logic Matches",
                font=("Arial", 10, "bold"),
                bg="white",
                fg="#8b5cf6",
                padx=10,
                pady=10
            )
            fuzzy_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
            
            tk.Label(
                fuzzy_frame,
                text=f"{statistics['fuzzy_matched']} records matched using fuzzy logic",
                font=("Arial", 8),
                bg="white",
                fg="#6b7280"
            ).pack()
            
            btn_frame3 = tk.Frame(fuzzy_frame, bg="white")
            btn_frame3.pack(pady=(10, 0))
            
            tk.Button(
                btn_frame3,
                text="📊 Export Excel",
                command=lambda: self.export_data("fuzzy_logic_matches", "excel"),
                bg="#8b5cf6",
                fg="white",
                font=("Arial", 9, "bold"),
                relief="flat",
                cursor="hand2",
                padx=15,
                pady=8
            ).pack(side="left", padx=(0, 5))
            
            tk.Button(
                btn_frame3,
                text="📄 Export CSV",
                command=lambda: self.export_data("fuzzy_logic_matches", "csv"),
                bg="#8b5cf6",
                fg="white",
                font=("Arial", 9, "bold"),
                relief="flat",
                cursor="hand2",
                padx=15,
                pady=8
            ).pack(side="left")
    
    def on_dataset_selected(self, event=None):
        """Handle dataset selection change"""
        self.update_preview()
    
    def update_preview(self):
        """Update preview table with selected dataset"""
        selected = self.results_selector.get() if self.results_selector else ""
        
        # Determine which dataset to show
        if "Enriched" in selected:
            df = self.controller.employee_dataset.cleaned_data
            dataset_name = "Enriched Data"
        elif "Resigned" in selected:
            df = self.get_resigned_users_data()
            dataset_name = "Resigned Users"
        elif "Current" in selected:
            df = self.get_current_users_data()
            dataset_name = "Current Users"
        elif "Fuzzy Logic" in selected:
            df = self.controller.employee_dataset.fuzzy_matched_data
            dataset_name = "Fuzzy Logic Matches"
        else:
            df = self.controller.employee_dataset.unmatched_data
            dataset_name = "Missing PERNRs"
        
        # Clear existing preview
        if self.results_preview_frame:
            for widget in self.results_preview_frame.winfo_children():
                widget.destroy()
        
        if df is None or df.empty:
            no_data_label = tk.Label(
                self.results_preview_frame,
                text=f"No data in {dataset_name}",
                font=("Arial", 10),
                bg="white",
                fg="#9ca3af"
            )
            no_data_label.pack(pady=20)
            return
        
        # Create table display
        self.create_data_table(df)
    
    def create_data_table(self, df: pd.DataFrame):
        """Create data table display"""
        table_container = tk.Frame(self.results_preview_frame, bg="white")
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
            height=12
        )
        
        x_scroll.config(command=tree.xview)
        y_scroll.config(command=tree.yview)
        
        # Configure columns
        tree.column("#0", width=50, minwidth=50)
        tree.heading("#0", text="Row")
        
        # Highlight key columns with wider width
        key_columns = ['PERNR', 'Full Name (From Masterlist)', 'Resignation Date', 'Position Name', 'Segment Name', 'Group Name', 'Area/Division Name', 'Department/Branch']
        for col in columns:
            width = 200 if col in key_columns else 150
            tree.column(col, width=width, minwidth=100)
            tree.heading(col, text=str(col), command=lambda c=col: self.sort_treeview(tree, c, False))
        
        # Add data (first 100 rows for performance)
        for idx, row in df.head(100).iterrows():
            values = [str(val) if pd.notna(val) else "" for val in row]
            tree.insert("", "end", text=str(idx + 1), values=values)
        
        # Pack elements
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Info label
        info_label = tk.Label(
            self.results_preview_frame,
            text=f"Showing first 100 rows of {len(df)} total rows | Highlighted: PERNR, Full Name, Resignation Date & Organizational Data columns",
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
        )
        info_label.pack(pady=(5, 0))
    
    def get_resigned_users_data(self) -> Optional[pd.DataFrame]:
        """Extract resigned users based on resignation date"""
        cleaned_data = self.controller.employee_dataset.cleaned_data
        if cleaned_data is None or cleaned_data.empty:
            return None
        
        resigned_mask = cleaned_data['Resignation Date'].notna() & (cleaned_data['Resignation Date'] != '') & (cleaned_data['Resignation Date'] != 'None')
        resigned_users = cleaned_data[resigned_mask].copy()
        
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
    
    def get_current_users_data(self) -> Optional[pd.DataFrame]:
        """Extract current users (exclude resigned users)"""
        cleaned_data = self.controller.employee_dataset.cleaned_data
        if cleaned_data is None or cleaned_data.empty:
            return None
        
        current_mask = cleaned_data['Resignation Date'].isna() | (cleaned_data['Resignation Date'] == '') | (cleaned_data['Resignation Date'] == 'None')
        current_users = cleaned_data[current_mask].copy()
        
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
        
        # Rearrange items in sorted positions
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
    
    def export_data(self, data_type: str, format_type: str):
        """Handle export request"""
        if hasattr(self, 'controller') and self.controller:
            self.controller.handle_export_request(data_type, format_type)
