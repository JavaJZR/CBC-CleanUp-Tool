"""
Employee Data Clean-Up Tool - Python Desktop Application
Chinabank Corporation Internal System
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from fuzzywuzzy import fuzz
from datetime import datetime
import re
import threading


class EmployeeCleanupTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Data Clean-Up Tool - Chinabank Corporation")
        # Maximize window to fill screen
        self.root.state('zoomed')  # Windows maximized state
        self.root.configure(bg="#f8fafc")
        
        # Data storage
        self.uploaded_files: Dict[str, Optional[pd.DataFrame]] = {
            'current_system': None,
            'previous_reference': None,
            'masterlist_current': None,
            'masterlist_resigned': None
        }
        
        self.file_paths: Dict[str, Optional[str]] = {
            'current_system': None,
            'previous_reference': None,
            'masterlist_current': None,
            'masterlist_resigned': None
        }
        
        self.cleaned_data: Optional[pd.DataFrame] = None
        self.unmatched_data: Optional[pd.DataFrame] = None
        self.fuzzy_matched_data: Optional[pd.DataFrame] = None  # Track fuzzy logic matches
        self.threshold = 80
        self.use_fuzzy_logic = True  # Default to using fuzzy logic
        self.current_step = 1
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Configure root window grid weights for full expansion
        self.root.grid_rowconfigure(1, weight=1)  # Main content row
        self.root.grid_columnconfigure(0, weight=1)  # Main content column
        
        # Header
        self.create_header()
        
        # Main container with scrollbar using grid layout
        main_canvas = tk.Canvas(self.root, bg="#f8fafc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        # Create window for scrollable frame and bind canvas width to frame
        canvas_window = main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make scrollable frame expand to canvas width
        def on_canvas_configure(event):
            main_canvas.itemconfig(canvas_window, width=event.width)
        main_canvas.bind("<Configure>", on_canvas_configure)
        
        # Use grid layout instead of pack for better expansion control
        main_canvas.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Instructions Section
        self.create_instructions()
        
        # Step 1: File Upload
        self.create_file_upload_section()
        
        # Step 2: Data Preview
        self.preview_frame = None
        
        # Step 3: Cleanup Controls
        self.cleanup_frame = None
        
        # Step 4: Results
        self.results_frame = None
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Create application header"""
        header = tk.Frame(self.root, bg="#dc2626", height=80)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)  # Maintain fixed height
        
        # Title
        title_label = tk.Label(
            header,
            text="Employee Data Clean-Up Tool",
            font=("Arial", 20, "bold"),
            bg="#dc2626",
            fg="white"
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            header,
            text="Chinabank Internal System",
            font=("Arial", 10),
            bg="#dc2626",
            fg="#fecaca"
        )
        subtitle_label.place(x=20, y=50)
        
    def create_instructions(self):
        """Create instructions section"""
        inst_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="📋 How to Use This Tool",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#1e40af",
            padx=15,
            pady=15
        )
        inst_frame.pack(fill="both", expand=True, padx=20, pady=(10, 5))
        
        instructions = """
1️⃣ UPLOAD FILES: Upload your Excel (.xlsx, .xls) or CSV files
   • Current System Report (Required) - Latest employee data to enrich
   • Previous Reference (Required) - Contains User ID → PERNR mapping
   • Masterlist Current (Required) - Active employees with PERNR and Full Name
   • Masterlist Resigned (Required) - Resigned employees with PERNR and Full Name

2️⃣ PREVIEW DATA: Review uploaded files to verify structure and content

3️⃣ CONFIGURE CLEANUP: Add "PERNR", "Full Name (From Masterlist)", "Resignation Date", and Organizational Data columns
   • PERNR: Looked up by User ID from Previous Reference, with fallback name matching
   • Full Name: Retrieved from Current/Resigned Masterlist using the PERNR
   • Resignation Date: Retrieved from Resigned Masterlist using the PERNR (if employee is resigned)
   • Organizational Data: Position Name, Segment Name, Group Name, Area/Division Name, Department/Branch from Current Masterlist
   • Fallback: If User ID lookup fails, matches "Username (Full Name)" with masterlist names
   • Fuzzy Logic: Optional fuzzy string matching for name variations (can be disabled for exact matches only)

4️⃣ EXPORT RESULTS: Download enriched data (with PERNRs, Full Names, Resignation Dates, and Organizational Data) and unmatched records
        """
        
        inst_text = tk.Label(
            inst_frame,
            text=instructions,
            font=("Arial", 9),
            bg="white",
            fg="#374151",
            justify="left"
        )
        inst_text.pack(anchor="w")
        
        # Warning
        warning_frame = tk.Frame(inst_frame, bg="#fef3c7", relief="solid", borderwidth=1)
        warning_frame.pack(fill="x", pady=(10, 0))
        
        warning_label = tk.Label(
            warning_frame,
            text="⚠️ Important: This tool processes employee data. Ensure proper authorization and follow data privacy guidelines.",
            font=("Arial", 8),
            bg="#fef3c7",
            fg="#92400e",
            wraplength=2000,
            justify="left"
        )
        warning_label.pack(padx=10, pady=8, fill="x", expand=True)
        
    def create_file_upload_section(self):
        """Create file upload section"""
        upload_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="1️⃣ File Upload",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#dc2626",
            padx=15,
            pady=15
        )
        upload_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        # Description
        desc_label = tk.Label(
            upload_frame,
            text="Upload your employee data files in Excel (.xlsx, .xls) or CSV format",
            font=("Arial", 9),
            bg="white",
            fg="#6b7280"
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Upload cards grid
        cards_frame = tk.Frame(upload_frame, bg="white")
        cards_frame.pack(fill="both", expand=True)
        
        self.upload_cards = {}
        file_configs = [
            ('current_system', 'Current System Report', 'Latest employee data to enrich with Employee Numbers and Full Names', 'Required'),
            ('previous_reference', 'Previous Reference', 'Contains User ID to Employee Number mapping', 'Required'),
            ('masterlist_current', 'Masterlist – Current', 'Active employees with Employee Number and Full Name', 'Required'),
            ('masterlist_resigned', 'Masterlist – Resigned', 'Resigned employees with Employee Number and Full Name', 'Required')
        ]
        
        for idx, (key, title, desc, req) in enumerate(file_configs):
            card = self.create_upload_card(cards_frame, key, title, desc, req)
            card.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            self.upload_cards[key] = card
            cards_frame.columnconfigure(idx, weight=1)
        
        # Clear All button
        clear_button_frame = tk.Frame(upload_frame, bg="white")
        clear_button_frame.pack(fill="x", pady=(15, 0))
        
        clear_all_btn = tk.Button(
            clear_button_frame,
            text="🗑️ Clear All Files",
            command=self.clear_all_files,
            bg="#6b7280",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        clear_all_btn.pack(side="right")
            
    def create_upload_card(self, parent, key, title, description, requirement):
        """Create a file upload card"""
        card = tk.Frame(parent, bg="#f9fafb", relief="solid", borderwidth=1)
        
        # Title
        title_label = tk.Label(
            card,
            text=title,
            font=("Arial", 10, "bold"),
            bg="#f9fafb",
            fg="#111827"
        )
        title_label.pack(padx=10, pady=(10, 5), anchor="w")
        
        # Description
        desc_label = tk.Label(
            card,
            text=description,
            font=("Arial", 8),
            bg="#f9fafb",
            fg="#6b7280",
            wraplength=400,
            justify="left"
        )
        desc_label.pack(padx=10, pady=(0, 10), anchor="w", fill="x")
        
        # Requirement badge
        req_color = "#dc2626" if requirement == "Required" else "#6b7280"
        req_label = tk.Label(
            card,
            text=requirement,
            font=("Arial", 7, "bold"),
            bg=req_color,
            fg="white",
            padx=8,
            pady=2
        )
        req_label.pack(padx=10, pady=(0, 10), anchor="w")
        
        # File name label
        file_label = tk.Label(
            card,
            text="No file selected",
            font=("Arial", 8),
            bg="#f9fafb",
            fg="#9ca3af",
            wraplength=400
        )
        file_label.pack(padx=10, pady=(0, 10), fill="x")
        
        # Buttons frame
        btn_frame = tk.Frame(card, bg="#f9fafb")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Upload button
        upload_btn = tk.Button(
            btn_frame,
            text="📁 Upload",
            command=lambda: self.upload_file(key),
            bg="#dc2626",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5
        )
        upload_btn.pack(side="left", padx=(0, 5))
        
        # Preview button
        preview_btn = tk.Button(
            btn_frame,
            text="👁 Preview",
            command=lambda: self.preview_file(key),
            bg="#3b82f6",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            state="disabled",
            padx=15,
            pady=5
        )
        preview_btn.pack(side="left")
        
        # Store references
        card.file_label = file_label
        card.preview_btn = preview_btn
        
        return card
    
    def detect_and_load_csv(self, file_path: str) -> pd.DataFrame:
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
                if self.is_valid_header(df.columns):
                    return df
            except:
                continue
        
        # Fallback to first row
        return pd.read_csv(file_path)
    
    def detect_and_load_excel(self, file_path: str) -> pd.DataFrame:
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
                if self.is_valid_header(df.columns):
                    return df
            except:
                continue
        
        # Fallback to first row
        return pd.read_excel(file_path)
    
    def is_valid_header(self, columns) -> bool:
        """Check if columns look like valid headers by looking for expected keywords"""
        column_names = [str(col).lower() for col in columns]
        
        # Look for common employee data keywords
        expected_keywords = [
            'pernr', 'pers. number', 'employee number', 'emp number',
            'full name', 'name', 'employee name', 'username',
            'user id', 'userid', 'sysid', 'department', 'position',
            'resignation', 'date', 'effectivity'
        ]
        
        # Count how many expected keywords are found
        found_keywords = sum(1 for keyword in expected_keywords 
                           if any(keyword in col for col in column_names))
        
        # If we find at least 2 expected keywords, consider it a valid header
        return found_keywords >= 2
        
    def upload_file(self, file_type: str):
        """Handle file upload"""
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            # Show loading message
            self.root.config(cursor="wait")
            self.root.update()
            
            # Parse file
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.csv':
                # Try to detect header row automatically
                df = self.detect_and_load_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                # Try to detect header row automatically
                df = self.detect_and_load_excel(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format. Please upload CSV, XLS, or XLSX files.")
                return
                
            # Validate data
            if df.empty:
                messagebox.showerror("Error", "File is empty or contains no data.")
                return
                
            # Store data
            self.uploaded_files[file_type] = df
            self.file_paths[file_type] = file_path
            
            # Update UI
            card = self.upload_cards[file_type]
            card.file_label.config(
                text=f"✓ {Path(file_path).name}\n({len(df)} rows, {len(df.columns)} columns)",
                fg="#059669"
            )
            card.preview_btn.config(state="normal")
            
            # Show preview section if this is the first file
            if self.current_step == 1:
                self.current_step = 2
                self.show_preview_section()
            else:
                # Update dropdown with newly uploaded file if preview section already exists
                if self.preview_frame:
                    self.update_file_selector()
                
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse file:\n{str(e)}\n\nPlease ensure your file:\n• Is a valid CSV, XLS, or XLSX file\n• Contains column headers in the first row\n• Is not corrupted or password-protected")
        finally:
            self.root.config(cursor="")
            
    def show_preview_section(self):
        """Show data preview section"""
        if self.preview_frame:
            self.preview_frame.destroy()
            
        self.preview_frame = tk.LabelFrame(
            self.scrollable_frame,
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
        self.preview_selector.bind("<<ComboboxSelected>>", self.update_preview)
        
        # Continue button
        continue_btn = tk.Button(
            selector_frame,
            text="Continue to Clean-Up →",
            command=self.show_cleanup_section,
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
        
        available_files = [
            file_names[key] for key, df in self.uploaded_files.items() if df is not None
        ]
        
        self.preview_selector['values'] = available_files
        if available_files and not self.preview_selector.get():
            self.preview_selector.current(0)
            self.update_preview()
            
    def update_preview(self, event=None):
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
        if not key or self.uploaded_files[key] is None:
            return
            
        df = self.uploaded_files[key]
        
        # Clear existing table
        for widget in self.preview_table_frame.winfo_children():
            widget.destroy()
            
        # Create table
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
        
    def show_cleanup_section(self):
        """Show cleanup configuration section"""
        # Check required files
        missing_files = []
        if self.uploaded_files['current_system'] is None:
            missing_files.append('Current System Report')
        if self.uploaded_files['previous_reference'] is None:
            missing_files.append('Previous Reference')
        if self.uploaded_files['masterlist_current'] is None:
            missing_files.append('Masterlist – Current')
        if self.uploaded_files['masterlist_resigned'] is None:
            missing_files.append('Masterlist – Resigned')
        
        if missing_files:
            messagebox.showwarning(
                "Missing Required Files",
                f"Please upload all required files before proceeding.\n\nMissing files:\n• " + "\n• ".join(missing_files)
            )
            return
            
        if self.cleanup_frame:
            self.cleanup_frame.destroy()
            
        self.current_step = 3
        
        self.cleanup_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="3️⃣ Data Clean-Up",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#ea580c",
            padx=15,
            pady=15
        )
        self.cleanup_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        # Description
        desc_label = tk.Label(
            self.cleanup_frame,
            text="This process will enrich your data by adding missing information:\n• Employee Numbers (PERNR) • Full Names • Resignation Dates • Job Details\n\nHow it works: 1) Find employee numbers using User IDs, 2) If that fails, match by name, 3) Get full names and job details from masterlists, 4) Optional: Use smart matching for similar names",
            font=("Arial", 9),
            bg="white",
            fg="#6b7280",
            justify="left"
        )
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Controls frame
        controls_frame = tk.Frame(self.cleanup_frame, bg="white")
        controls_frame.pack(fill="x")
        
        # Run button frame
        run_frame = tk.LabelFrame(
            controls_frame,
            text="Execute Clean-Up",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        run_frame.pack(fill="both", expand=True)
        
        tk.Label(
            run_frame,
            text="Start the lookup process to add PERNRs, Full Names, Resignation Dates, and Organizational Data",
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
        ).pack(anchor="w")
        
        # Fuzzy logic option
        fuzzy_frame = tk.Frame(run_frame, bg="white")
        fuzzy_frame.pack(fill="x", pady=(10, 0))
        
        self.fuzzy_var = tk.BooleanVar(value=self.use_fuzzy_logic)
        fuzzy_checkbox = tk.Checkbutton(
            fuzzy_frame,
            text="Enable Fuzzy Logic for Name Matching",
            variable=self.fuzzy_var,
            command=self.toggle_fuzzy_logic,
            font=("Arial", 9),
            bg="white",
            fg="#374151"
        )
        fuzzy_checkbox.pack(side="left")
        
        # Fuzzy logic description
        fuzzy_desc = tk.Label(
            fuzzy_frame,
            text="(Uses fuzzy string matching when exact name match fails. Disable for exact matches only.)",
            font=("Arial", 7),
            bg="white",
            fg="#6b7280"
        )
        fuzzy_desc.pack(side="left", padx=(10, 0))
        
        # Threshold control frame
        threshold_frame = tk.Frame(run_frame, bg="white")
        threshold_frame.pack(fill="x", pady=(10, 0))
        
        # Threshold label
        threshold_label = tk.Label(
            threshold_frame,
            text="Fuzzy Match Threshold:",
            font=("Arial", 9, "bold"),
            bg="white",
            fg="#374151"
        )
        threshold_label.pack(side="left")
        
        # Threshold slider
        self.threshold_var = tk.DoubleVar(value=self.threshold)
        self.threshold_slider = tk.Scale(
            threshold_frame,
            from_=50,
            to=100,
            orient="horizontal",
            variable=self.threshold_var,
            command=self.update_threshold,
            bg="white",
            fg="#374151",
            font=("Arial", 8),
            length=200,
            resolution=1
        )
        self.threshold_slider.pack(side="left", padx=(10, 10))
        
        # Threshold value label
        self.threshold_label = tk.Label(
            threshold_frame,
            text=f"{self.threshold}%",
            font=("Arial", 9, "bold"),
            bg="white",
            fg="#dc2626"
        )
        self.threshold_label.pack(side="left")
        
        # Threshold description
        threshold_desc = tk.Label(
            threshold_frame,
            text="(Only applies when Fuzzy Logic is enabled. Higher = more strict, Lower = more lenient)",
            font=("Arial", 7),
            bg="white",
            fg="#6b7280"
        )
        threshold_desc.pack(side="left", padx=(10, 0))
        
        self.run_btn = tk.Button(
            run_frame,
            text="🚀 Run Clean-Up Process",
            command=self.run_cleanup,
            bg="#dc2626",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=15
        )
        self.run_btn.pack(pady=(10, 0))
        
        # Progress frame
        progress_frame = tk.Frame(self.cleanup_frame, bg="white")
        progress_frame.pack(fill="x", pady=(15, 0))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=400
        )
        self.progress_bar.pack(fill="x")
        
        self.status_label = tk.Label(
            progress_frame,
            text="Ready to start clean-up",
            font=("Arial", 9),
            bg="white",
            fg="#6b7280"
        )
        self.status_label.pack(pady=(5, 0))
        
    def update_threshold(self, value):
        """Update threshold value and label"""
        self.threshold = int(float(value))
        if hasattr(self, 'threshold_label'):
            self.threshold_label.config(text=f"{self.threshold}%")
        
        # Update the slider value if it exists
        if hasattr(self, 'threshold_slider'):
            self.threshold_slider.set(self.threshold)
    
    def set_threshold(self, value):
        """Set threshold programmatically"""
        if 50 <= value <= 100:
            self.threshold = value
            if hasattr(self, 'threshold_var'):
                self.threshold_var.set(value)
            if hasattr(self, 'threshold_label'):
                self.threshold_label.config(text=f"{self.threshold}%")
            if hasattr(self, 'threshold_slider'):
                self.threshold_slider.set(value)
            return True
        return False
    
    def get_threshold(self):
        """Get current threshold value"""
        return self.threshold
    
    def reset_threshold(self):
        """Reset threshold to default value"""
        self.set_threshold(80)
    
    def test_threshold(self, name1, name2):
        """Test fuzzy matching with current threshold"""
        from fuzzywuzzy import fuzz
        
        # Clean names (same as in the application)
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
        
    def toggle_fuzzy_logic(self):
        """Toggle fuzzy logic option"""
        self.use_fuzzy_logic = self.fuzzy_var.get()
        
        # Enable/disable threshold controls based on fuzzy logic
        if hasattr(self, 'threshold_slider'):
            if self.use_fuzzy_logic:
                self.threshold_slider.config(state="normal")
                if hasattr(self, 'threshold_label'):
                    self.threshold_label.config(fg="#dc2626")  # Red when active
            else:
                self.threshold_slider.config(state="disabled")
                if hasattr(self, 'threshold_label'):
                    self.threshold_label.config(fg="#9ca3af")  # Gray when disabled
        
    def run_cleanup(self):
        """Run the cleanup process"""
        self.run_btn.config(state="disabled")
        self.progress_bar['value'] = 0
        self.status_label.config(text="Starting clean-up process...")
        
        # Run in separate thread to avoid freezing UI
        thread = threading.Thread(target=self.cleanup_worker)
        thread.daemon = True
        thread.start()
        
    def detect_lookup_columns(self):
        """Automatically detect columns for lookup with flexible matching"""
        
        # Current System - User ID column
        user_id_current = None
        if self.uploaded_files['current_system'] is not None:
            # Try exact match first
            exact_match = [col for col in self.uploaded_files['current_system'].columns if col == 'User ID']
            if exact_match:
                user_id_current = exact_match[0]
            else:
                # Try flexible matching
                flexible_match = [col for col in self.uploaded_files['current_system'].columns 
                                 if any(keyword in str(col).lower() for keyword in ['user', 'id', 'sysid', 'username'])]
                if flexible_match:
                    user_id_current = flexible_match[0]
        
        # Previous Reference - User ID column
        user_id_previous = None
        if self.uploaded_files['previous_reference'] is not None:
            # Try exact match first
            exact_match = [col for col in self.uploaded_files['previous_reference'].columns if col == 'User ID']
            if exact_match:
                user_id_previous = exact_match[0]
            else:
                # Try flexible matching
                flexible_match = [col for col in self.uploaded_files['previous_reference'].columns 
                                 if any(keyword in str(col).lower() for keyword in ['user', 'id', 'sysid', 'username'])]
                if flexible_match:
                    user_id_previous = flexible_match[0]
        
        # Previous Reference - PERNR column
        pernr_previous = None
        if self.uploaded_files['previous_reference'] is not None:
            # Try exact match first
            exact_match = [col for col in self.uploaded_files['previous_reference'].columns if col == 'PERNR']
            if exact_match:
                pernr_previous = exact_match[0]
            else:
                # Try flexible matching
                flexible_match = [col for col in self.uploaded_files['previous_reference'].columns 
                                 if str(col).upper() == 'PERNR' or ('employee' in str(col).lower() and 'number' in str(col).lower())]
                if flexible_match:
                    pernr_previous = flexible_match[0]
        
        return user_id_current, user_id_previous, pernr_previous
    
    def cleanup_worker(self):
        """Worker thread for cleanup process"""
        try:
            # Get data
            current_df = self.uploaded_files['current_system'].copy()
            previous_df = self.uploaded_files['previous_reference'].copy() if self.uploaded_files['previous_reference'] is not None else None
            masterlist_current_df = self.uploaded_files['masterlist_current'].copy() if self.uploaded_files['masterlist_current'] is not None else None
            masterlist_resigned_df = self.uploaded_files['masterlist_resigned'].copy() if self.uploaded_files['masterlist_resigned'] is not None else None
            
            self.update_progress(10, "Loading and validating data...")
            
            # Initialize new columns
            current_df['PERNR'] = None
            current_df['Full Name (From Masterlist)'] = None
            current_df['Resignation Date'] = None
            current_df['Position Name'] = None
            current_df['Segment Name'] = None
            current_df['Group Name'] = None
            current_df['Area/Division Name'] = None
            current_df['Department/Branch'] = None
            current_df['Match Type'] = None  # Track how PERNR was found
            current_df['Match Score'] = None  # Track fuzzy match score
            
            fuzzy_status = "with fuzzy matching" if self.use_fuzzy_logic else "exact matching only"
            self.update_progress(20, f"Looking up PERNRs, Full Names, Resignation Dates, and Organizational Data (User ID lookup + Name fallback {fuzzy_status})...")
            
            # Detect columns for lookup once (outside the loop for performance)
            user_id_current, user_id_previous, pernr_previous = self.detect_lookup_columns()
            
            # Process each row to add PERNR, Full Name, Resignation Date, and Organizational Data
            for idx, row in current_df.iterrows():
                employee_number = None
                full_name = None
                match_type = "no_match"  # Initialize match tracking
                match_score = 0.0
                
                # Step 1: Lookup PERNR by User ID from previous_reference
                # This is the primary lookup method with flexible column detection
                if previous_df is not None and user_id_current and user_id_previous and pernr_previous:
                    user_id = row.get(user_id_current)
                    if pd.notna(user_id):
                        match = previous_df[previous_df[user_id_previous] == user_id]
                        if not match.empty:
                            # Convert PERNR to integer
                            emp_num = pd.to_numeric(match.iloc[0][pernr_previous], errors='coerce')
                            employee_number = str(int(emp_num)) if pd.notna(emp_num) else None
                            if employee_number is not None:
                                match_type = "user_id_match"  # Track User ID match
                                match_score = 100.0
                
                # Step 2: Fallback lookup using name matching if User ID lookup failed
                # Priority: 1) Exact name match, 2) Fuzzy matching (if exact fails)
                # This finds PERNR by comparing "Username (Full Name)" with "Full Name" from masterlists
                # Order: Current masterlist first, then resigned masterlist
                if employee_number is None:
                    # Get the current system's username/full name for comparison
                    current_name = None
                    name_columns_current = [col for col in current_df.columns if 'username' in str(col).lower() or 'name' in str(col).lower()]
                    if name_columns_current:
                        current_name = row.get(name_columns_current[0])
                    
                    if current_name and pd.notna(current_name):
                        # Try to find matching employee in masterlist_current
                        if masterlist_current_df is not None:
                            employee_number, full_name, match_type, match_score = self.find_employee_by_name(
                                current_name, masterlist_current_df, "current"
                            )
                        
                        # If not found in current, try masterlist_resigned
                        if employee_number is None and masterlist_resigned_df is not None:
                            employee_number, full_name, match_type, match_score = self.find_employee_by_name(
                                current_name, masterlist_resigned_df, "resigned"
                            )
                
                # Step 3: If PERNR was found but Full Name is still missing, lookup Full Name from masterlists
                # This ensures we get the full name from the masterlist based on the PERNR
                if employee_number is not None and full_name is None:
                    # Debug: This indicates we found PERNR but not Full Name from name matching
                    # Convert employee_number to integer for proper comparison
                    emp_num_numeric = pd.to_numeric(employee_number, errors='coerce')
                    if pd.notna(emp_num_numeric):
                        emp_num_numeric = int(emp_num_numeric)
                    
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
                                full_name = masterlist_current_df.loc[original_idx, name_columns[0]]
                    
                    # If not found in current, try masterlist_resigned
                    if full_name is None and masterlist_resigned_df is not None and 'PERNR' in masterlist_resigned_df.columns:
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
                                full_name = masterlist_resigned_df.loc[original_idx, name_columns[0]]
                
                # Step 4: Lookup Resignation Date from resigned employee list if PERNR was found
                resignation_date = None
                if employee_number is not None and masterlist_resigned_df is not None and 'PERNR' in masterlist_resigned_df.columns:
                    # Convert employee_number to integer for proper comparison
                    emp_num_numeric = pd.to_numeric(employee_number, errors='coerce')
                    if pd.notna(emp_num_numeric):
                        emp_num_numeric = int(emp_num_numeric)
                        
                        # Convert masterlist PERNR to integer for comparison
                        masterlist_resigned_df_copy = masterlist_resigned_df.copy()
                        masterlist_resigned_df_copy['PERNR'] = pd.to_numeric(masterlist_resigned_df_copy['PERNR'], errors='coerce')
                        masterlist_resigned_df_copy['PERNR'] = masterlist_resigned_df_copy['PERNR'].astype('Int64')
                        match = masterlist_resigned_df_copy[masterlist_resigned_df_copy['PERNR'] == emp_num_numeric]
                        
                        if not match.empty:
                            # Find resignation date column (could be "Resignation Date", "Date", "End Date", etc.)
                            date_columns = [col for col in masterlist_resigned_df.columns if any(keyword in str(col).lower() for keyword in ['resignation', 'date', 'end', 'termination', 'exit', 'effectivity', 'separation', 'report'])]
                            if date_columns:
                                # Get the original index to retrieve the resignation date from original dataframe
                                original_idx = match.index[0]
                                raw_date = masterlist_resigned_df.loc[original_idx, date_columns[0]]
                                
                                # Format the date to short date format
                                if pd.notna(raw_date):
                                    try:
                                        # Try to parse the date and format it as MM/DD/YYYY
                                        if isinstance(raw_date, str):
                                            # Handle string dates
                                            parsed_date = pd.to_datetime(raw_date, errors='coerce')
                                        else:
                                            # Handle datetime objects
                                            parsed_date = pd.to_datetime(raw_date, errors='coerce')
                                        
                                        if pd.notna(parsed_date):
                                            resignation_date = parsed_date.strftime('%m/%d/%Y')
                                        else:
                                            resignation_date = None
                                    except:
                                        # If date parsing fails, keep original value
                                        resignation_date = str(raw_date) if raw_date else None
                                else:
                                    resignation_date = None
                
                # Step 5: Lookup Organizational Data from current employee list if PERNR was found
                position_name = None
                segment_name = None
                group_name = None
                area_division_name = None
                department_branch = None
                
                # Check for PERNR or "Pers. Number" column
                pernr_col_org = None
                if employee_number is not None and masterlist_current_df is not None:
                    if 'PERNR' in masterlist_current_df.columns:
                        pernr_col_org = 'PERNR'
                    elif 'Pers. Number' in masterlist_current_df.columns:
                        pernr_col_org = 'Pers. Number'
                
                if pernr_col_org is not None:
                    # Convert employee_number to integer for proper comparison
                    emp_num_numeric = pd.to_numeric(employee_number, errors='coerce')
                    if pd.notna(emp_num_numeric):
                        emp_num_numeric = int(emp_num_numeric)
                        
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
                                        if target_col == 'Position Name':
                                            position_name = str(value)
                                        elif target_col == 'Segment Name':
                                            segment_name = str(value)
                                        elif target_col == 'Group Name':
                                            group_name = str(value)
                                        elif target_col == 'Area/Division Name':
                                            area_division_name = str(value)
                                        elif target_col == 'Department/Branch':
                                            department_branch = str(value)
                
                # Assign all found data (or leave as None)
                current_df.at[idx, 'PERNR'] = employee_number
                current_df.at[idx, 'Full Name (From Masterlist)'] = full_name
                current_df.at[idx, 'Resignation Date'] = resignation_date
                current_df.at[idx, 'Position Name'] = position_name
                current_df.at[idx, 'Segment Name'] = segment_name
                current_df.at[idx, 'Group Name'] = group_name
                current_df.at[idx, 'Area/Division Name'] = area_division_name
                current_df.at[idx, 'Department/Branch'] = department_branch
                
                # Track match type and score
                if employee_number is not None:
                    current_df.at[idx, 'Match Type'] = match_type
                    current_df.at[idx, 'Match Score'] = match_score
                
                # Update progress
                progress = 20 + (idx / len(current_df)) * 70
                self.update_progress(progress, f"Processing row {idx + 1} of {len(current_df)}...")
            
            self.update_progress(95, "Generating clean reports...")
            
            # Convert PERNR column to integer format (no decimal places)
            # Handle any non-numeric values by converting to NaN
            current_df['PERNR'] = pd.to_numeric(current_df['PERNR'], errors='coerce').astype('Int64')
            
            # Separate matched (has PERNR) and unmatched (no PERNR)
            self.cleaned_data = current_df[current_df['PERNR'].notna()].copy()
            self.unmatched_data = current_df[current_df['PERNR'].isna()].copy()
            
            # Create fuzzy matched data sheet (records matched using fuzzy logic)
            fuzzy_matched_mask = (current_df['PERNR'].notna()) & (current_df['Match Type'] == 'fuzzy_match')
            self.fuzzy_matched_data = current_df[fuzzy_matched_mask].copy()
            
            self.update_progress(100, "Clean-up completed successfully!")
            
            # Show results
            self.root.after(500, self.show_results_section)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Cleanup failed:\n{str(e)}"))
            self.root.after(0, lambda: self.run_btn.config(state="normal"))
            
    def find_employee_by_name(self, current_name: str, masterlist_df: pd.DataFrame, list_type: str) -> Tuple[Optional[str], Optional[str], str, float]:
        """
        Find employee by name using fuzzy matching
        
        Args:
            current_name: Name from current system report (Username/Full Name)
            masterlist_df: Masterlist dataframe (current or resigned)
            list_type: "current" or "resigned" for logging purposes
            
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
            
            # Use the higher score
            final_score = max(score, partial_score)
            
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
    
    def update_progress(self, value, status):
        """Update progress bar and status"""
        self.root.after(0, lambda: self.progress_bar.config(value=value))
        self.root.after(0, lambda: self.status_label.config(text=status))
        
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
        
    def show_results_section(self):
        """Show results section"""
        if self.results_frame:
            self.results_frame.destroy()
            
        self.current_step = 4
        self.run_btn.config(state="normal")
        
        self.results_frame = tk.LabelFrame(
            self.scrollable_frame,
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
        stats_frame = tk.Frame(self.results_frame, bg="white")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        total = len(self.uploaded_files['current_system'])
        matched = len(self.cleaned_data) if self.cleaned_data is not None else 0
        unmatched = len(self.unmatched_data) if self.unmatched_data is not None else 0
        fuzzy_matched = len(self.fuzzy_matched_data) if self.fuzzy_matched_data is not None else 0
        
        stats = [
            ("Total Records", total, "#3b82f6"),
            ("Enriched with PERNR", matched, "#059669"),
            ("Missing PERNR", unmatched, "#ea580c"),
            ("Fuzzy Logic Matches", fuzzy_matched, "#8b5cf6")
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
        
        # Preview section
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
            values=["✓ Enriched Data (with PERNRs, Full Names, Resignation Dates & Organizational Data)", "📋 Resigned Users (with Resignation Dates)", "👥 Current Users (Active Employees Only)", "🔍 Fuzzy Logic Matches (PERNRs found using fuzzy matching)", "⚠ Missing PERNRs"]
        )
        self.results_selector.pack(side="left")
        self.results_selector.current(0)
        self.results_selector.bind("<<ComboboxSelected>>", self.update_results_preview)
        
        # Preview table frame
        self.results_preview_frame = tk.Frame(preview_section, bg="white")
        self.results_preview_frame.pack(fill="both", expand=True)
        
        # Show initial preview
        self.update_results_preview()
            
        # Export buttons
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
            text=f"{matched} records with PERNRs, Full Names, Resignation Dates, and Organizational Data",
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
        ).pack()
        
        btn_frame1 = tk.Frame(cleaned_frame, bg="white")
        btn_frame1.pack(pady=(10, 0))
        
        tk.Button(
            btn_frame1,
            text="📊 Export Excel",
            command=lambda: self.export_cleaned_data_with_resigned(self.cleaned_data, "cleaned_report", "excel"),
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
            command=lambda: self.export_cleaned_data_with_resigned(self.cleaned_data, "cleaned_report", "csv"),
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
            text=f"{unmatched} records without PERNRs",
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
        ).pack()
        
        btn_frame2 = tk.Frame(unmatched_frame, bg="white")
        btn_frame2.pack(pady=(10, 0))
        
        tk.Button(
            btn_frame2,
            text="📊 Export Excel",
            command=lambda: self.export_data(self.unmatched_data, "unmatched_for_review", "excel"),
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
            command=lambda: self.export_data(self.unmatched_data, "unmatched_for_review", "csv"),
            bg="#ea580c",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        ).pack(side="left")
        
        # Fuzzy matched data export (only show if there are fuzzy matches)
        fuzzy_count = len(self.fuzzy_matched_data) if self.fuzzy_matched_data is not None else 0
        if fuzzy_count > 0:
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
                text=f"{fuzzy_count} records matched using fuzzy logic",
                font=("Arial", 8),
                bg="white",
                fg="#6b7280"
            ).pack()
            
            btn_frame3 = tk.Frame(fuzzy_frame, bg="white")
            btn_frame3.pack(pady=(10, 0))
            
            tk.Button(
                btn_frame3,
                text="📊 Export Excel",
                command=lambda: self.export_data(self.fuzzy_matched_data, "fuzzy_logic_matches", "excel"),
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
                command=lambda: self.export_data(self.fuzzy_matched_data, "fuzzy_logic_matches", "csv"),
                bg="#8b5cf6",
                fg="white",
                font=("Arial", 9, "bold"),
                relief="flat",
                cursor="hand2",
                padx=15,
                pady=8
            ).pack(side="left")
        
    def export_data(self, df: pd.DataFrame, filename: str, format_type: str):
        """Export data to file"""
        if df is None or df.empty:
            messagebox.showwarning("No Data", "No data available to export.")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Build a clearer default file name using the uploaded current system file as base
        def build_initial_filename(suggested_label: str, ext: str) -> str:
            # Try to base the file name on the uploaded Current System file name
            base_name = "Report"
            try:
                if self.file_paths.get('current_system'):
                    base_name = Path(self.file_paths['current_system']).stem
            except Exception:
                pass
            # Sanitize
            base_name = re.sub(r"[^A-Za-z0-9 _\-]", "", str(base_name)).strip()
            label = suggested_label.replace("_", " ").title()
            return f"{base_name} - {label} - {timestamp}.{ext}"
        
        if format_type == "excel":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=build_initial_filename(filename, "xlsx"),
                filetypes=[("Excel files", "*.xlsx")]
            )
            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
        else:  # csv
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=build_initial_filename(filename, "csv"),
                filetypes=[("CSV files", "*.csv")]
            )
            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
    
    def export_cleaned_data_with_resigned(self, df: pd.DataFrame, filename: str, format_type: str):
        """Export cleaned data with additional resigned users sheet"""
        if df is None or df.empty:
            messagebox.showwarning("No Data", "No data available to export.")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Build a clearer default file name using the uploaded current system file as base
        def build_initial_filename(suggested_label: str, ext: str) -> str:
            base_name = "Report"
            try:
                if self.file_paths.get('current_system'):
                    base_name = Path(self.file_paths['current_system']).stem
            except Exception:
                pass
            base_name = re.sub(r"[^A-Za-z0-9 _\-]", "", str(base_name)).strip()
            label = suggested_label.replace("_", " ").title()
            return f"{base_name} - {label} - {timestamp}.{ext}"
        
        if format_type == "excel":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=build_initial_filename(filename, "xlsx"),
                filetypes=[("Excel files", "*.xlsx")]
            )
            if file_path:
                # Create resigned users dataframe
                resigned_users = self.get_resigned_users_data(df)
                
                # Create current users dataframe (exclude resigned users)
                current_users = self.get_current_users_data(df)
                
                # Export with multiple sheets
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Main cleaned data sheet
                    df.to_excel(writer, sheet_name='Cleaned Data', index=False)
                    
                    # Resigned users sheet
                    if not resigned_users.empty:
                        resigned_users.to_excel(writer, sheet_name='Resigned Users', index=False)
                    else:
                        # Create empty sheet with headers if no resigned users
                        empty_df = pd.DataFrame(columns=df.columns)
                        empty_df.to_excel(writer, sheet_name='Resigned Users', index=False)
                    
                    # Current users sheet
                    if not current_users.empty:
                        current_users.to_excel(writer, sheet_name='Current Users', index=False)
                    else:
                        # Create empty sheet with headers if no current users
                        empty_df = pd.DataFrame(columns=df.columns)
                        empty_df.to_excel(writer, sheet_name='Current Users', index=False)
                
                messagebox.showinfo("Success", f"Data exported to:\n{file_path}\n\nSheets created:\n• Cleaned Data\n• Resigned Users\n• Current Users")
        else:  # csv - export main data only (CSV doesn't support multiple sheets)
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=build_initial_filename(filename, "csv"),
                filetypes=[("CSV files", "*.csv")]
            )
            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to:\n{file_path}\n\nNote: CSV format doesn't support multiple sheets. Only main data exported.")
    
    def get_resigned_users_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract resigned users based on resignation date"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Filter for users with resignation dates (not null/empty)
        resigned_mask = df['Resignation Date'].notna() & (df['Resignation Date'] != '') & (df['Resignation Date'] != 'None')
        resigned_users = df[resigned_mask].copy()
        
        if resigned_users.empty:
            return pd.DataFrame(columns=df.columns)
        
        # Sort by resignation date (most recent first)
        try:
            # Convert resignation dates to datetime for proper sorting
            resigned_users['Resignation Date'] = pd.to_datetime(resigned_users['Resignation Date'], format='%m/%d/%Y', errors='coerce')
            resigned_users = resigned_users.sort_values('Resignation Date', ascending=False)
            
            # Convert back to string format for display
            resigned_users['Resignation Date'] = resigned_users['Resignation Date'].dt.strftime('%m/%d/%Y')
        except:
            # If date conversion fails, sort as strings
            resigned_users = resigned_users.sort_values('Resignation Date', ascending=False)
        
        return resigned_users
    
    def get_current_users_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract current users (exclude resigned users)"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Filter for users without resignation dates (current employees)
        current_mask = df['Resignation Date'].isna() | (df['Resignation Date'] == '') | (df['Resignation Date'] == 'None')
        current_users = df[current_mask].copy()
        
        if current_users.empty:
            return pd.DataFrame(columns=df.columns)
        
        # Sort by PERNR for consistent ordering
        try:
            # Convert PERNR to numeric for proper sorting
            current_users['PERNR'] = pd.to_numeric(current_users['PERNR'], errors='coerce')
            current_users = current_users.sort_values('PERNR', ascending=True)
            # Convert back to string for display
            current_users['PERNR'] = current_users['PERNR'].astype(str)
        except:
            # If PERNR conversion fails, sort as strings
            current_users = current_users.sort_values('PERNR', ascending=True)
        
        return current_users
    
    def clear_all_files(self):
        """Clear all uploaded files and reset the UI"""
        # Confirm with user
        confirm = messagebox.askyesno(
            "Clear All Files",
            "Are you sure you want to clear all uploaded files?\n\nThis will reset the application."
        )
        
        if not confirm:
            return
        
        # Clear all uploaded files
        for key in self.uploaded_files.keys():
            self.uploaded_files[key] = None
            self.file_paths[key] = None
        
        # Reset UI for upload cards
        for key, card in self.upload_cards.items():
            card.file_label.config(
                text="No file selected",
                fg="#9ca3af"
            )
            card.preview_btn.config(state="disabled")
        
        # Clear results data
        self.cleaned_data = None
        self.unmatched_data = None
        
        # Remove preview section
        if self.preview_frame:
            self.preview_frame.destroy()
            self.preview_frame = None
        
        # Remove cleanup section
        if self.cleanup_frame:
            self.cleanup_frame.destroy()
            self.cleanup_frame = None
        
        # Remove results section
        if self.results_frame:
            self.results_frame.destroy()
            self.results_frame = None
        
        # Reset step
        self.current_step = 1
        
        messagebox.showinfo("Success", "All files cleared. You can now upload new files.")
    
    def update_results_preview(self, event=None):
        """Update results preview table with selected dataset"""
        selected = self.results_selector.get()
        
        # Determine which dataset to show
        if "Enriched" in selected:
            df = self.cleaned_data
            dataset_name = "Enriched Data"
        elif "Resigned" in selected:
            df = self.get_resigned_users_data(self.cleaned_data) if self.cleaned_data is not None else None
            dataset_name = "Resigned Users"
        elif "Current" in selected:
            df = self.get_current_users_data(self.cleaned_data) if self.cleaned_data is not None else None
            dataset_name = "Current Users"
        elif "Fuzzy Logic" in selected:
            df = self.fuzzy_matched_data
            dataset_name = "Fuzzy Logic Matches"
        else:
            df = self.unmatched_data
            dataset_name = "Missing PERNRs"
        
        # Clear existing preview
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
        
        # Create table container
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
        
        # Info label with dataset-specific information
        if "Resigned" in selected:
            info_text = f"Showing first 100 rows of {len(df)} total rows | Resigned Users sorted by resignation date (newest first) | Highlighted: PERNR, Full Name, Resignation Date & Organizational Data columns"
        elif "Current" in selected:
            info_text = f"Showing first 100 rows of {len(df)} total rows | Current Users (Active Employees Only) sorted by PERNR | Highlighted: PERNR, Full Name, Resignation Date & Organizational Data columns"
        else:
            info_text = f"Showing first 100 rows of {len(df)} total rows | Highlighted: PERNR, Full Name, Resignation Date & Organizational Data columns"
        
        info_label = tk.Label(
            self.results_preview_frame,
            text=info_text,
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
        )
        info_label.pack(pady=(5, 0))
                
    def preview_file(self, file_type: str):
        """Preview a specific file"""
        if not self.preview_frame:
            self.show_preview_section()
            
        # Map key to display name
        key_to_name = {
            'current_system': 'Current System Report',
            'previous_reference': 'Previous Reference',
            'masterlist_current': 'Masterlist – Current',
            'masterlist_resigned': 'Masterlist – Resigned'
        }
        
        display_name = key_to_name.get(file_type)
        if display_name:
            self.preview_selector.set(display_name)
            self.update_preview()
            
        # Scroll to preview section
        self.scrollable_frame.update_idletasks()
        
    def create_footer(self):
        """Create application footer"""
        footer = tk.Frame(self.root, bg="#1f2937", height=50)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        footer.grid_propagate(False)  # Maintain fixed height
        
        timestamp = datetime.now().strftime("%b %d, %Y %I:%M %p")
        
        left_label = tk.Label(
            footer,
            text=f"🟢 Last clean-up: {timestamp}  •  👤 User: System Administrator",
            font=("Arial", 8),
            bg="#1f2937",
            fg="#d1d5db"
        )
        left_label.pack(side="left", padx=20, pady=15)
        
        right_label = tk.Label(
            footer,
            text="🏦 Chinabank Corporation",
            font=("Arial", 8, "bold"),
            bg="#1f2937",
            fg="#d1d5db"
        )
        right_label.pack(side="right", padx=20, pady=15)


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EmployeeCleanupTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()

