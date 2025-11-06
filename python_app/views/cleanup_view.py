"""
Cleanup View
Handles cleanup configuration UI components
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from controllers.main_controller import MainController

class CleanupView:
    """Cleanup configuration UI component"""
    
    def __init__(self, parent, controller: 'MainController'):
        self.parent = parent
        self.controller = controller
        self.cleanup_frame: Optional[tk.Frame] = None
        self.fuzzy_var: Optional[tk.BooleanVar] = None
        self.threshold_var: Optional[tk.DoubleVar] = None
        self.threshold_slider: Optional[tk.Scale] = None
        self.threshold_label: Optional[tk.Label] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.status_label: Optional[tk.Label] = None
        self.run_btn: Optional[tk.Button] = None
        self.cancel_btn: Optional[tk.Button] = None
        
        # Column selection UI components
        self.custom_column_var: Optional[tk.BooleanVar] = None
        self.current_user_id_var: Optional[tk.StringVar] = None
        self.previous_user_id_var: Optional[tk.StringVar] = None
        self.previous_pernr_var: Optional[tk.StringVar] = None
        self.current_full_name_var: Optional[tk.StringVar] = None
        self.current_user_id_combo: Optional[ttk.Combobox] = None
        self.previous_user_id_combo: Optional[ttk.Combobox] = None
        self.previous_pernr_combo: Optional[ttk.Combobox] = None
        self.current_full_name_combo: Optional[ttk.Combobox] = None
        self.column_selection_frame: Optional[tk.Frame] = None
        self.full_name_selection_frame: Optional[tk.Frame] = None
    
    def show(self):
        """Show cleanup configuration section"""
        # Check required files
        missing_files = self.controller.employee_dataset.get_missing_files()
        
        if missing_files:
            messagebox.showwarning(
                "Missing Required Files",
                f"Please upload all required files before proceeding.\n\nMissing files:\n• " + "\n• ".join(missing_files)
            )
            return
            
        if self.cleanup_frame:
            self.cleanup_frame.destroy()
            
        self.cleanup_frame = tk.LabelFrame(
            self.parent,
            text="3. Data Clean-Up",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#CD1C18",
            padx=20,
            pady=20
        )
        self.cleanup_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        # Description
        desc_label = tk.Label(
            self.cleanup_frame,
            text="This process will enrich your data by adding missing information:\n• Employee Numbers (PERNR) • Full Names • Resignation Dates • Job Details\n\nHow it works: 1) Find employee numbers using User IDs (if Previous Reference provided), 2) If that fails or no Previous Reference, match by name, 3) Get full names and job details from masterlists, 4) Optional: Use smart matching for similar names",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#374151",
            justify="left"
        )
        desc_label.pack(anchor="w", pady=(0, 20))
        
        # Column Selection Frame
        self.create_column_selection_frame()
        
        # Controls frame
        controls_frame = tk.Frame(self.cleanup_frame, bg="white")
        controls_frame.pack(fill="x")
        
        # Run button frame
        run_frame = tk.LabelFrame(
            controls_frame,
            text="Execute Clean-Up",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#9B1313",
            padx=15,
            pady=15
        )
        run_frame.pack(fill="both", expand=True)
        
        tk.Label(
            run_frame,
            text="Start the lookup process to add PERNRs, Full Names, Resignation Dates, and Organizational Data\n(Uses User ID lookup if Previous Reference provided, otherwise uses name matching)",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#374151"
        ).pack(anchor="w")
        
        # Fuzzy logic option
        fuzzy_frame = tk.Frame(run_frame, bg="white")
        fuzzy_frame.pack(fill="x", pady=(10, 0))
        
        self.fuzzy_var = tk.BooleanVar(value=self.controller.matching_engine.use_fuzzy_logic)
        fuzzy_checkbox = tk.Checkbutton(
            fuzzy_frame,
            text="Enable Fuzzy Logic for Name Matching",
            variable=self.fuzzy_var,
            command=self.toggle_fuzzy_logic,
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#374151",
            selectcolor="#FFA896"
        )
        fuzzy_checkbox.pack(side="left")
        
        # Fuzzy logic description
        fuzzy_desc = tk.Label(
            fuzzy_frame,
            text="(Uses fuzzy string matching when exact name match fails. Disable for exact matches only.)",
            font=("Segoe UI", 10),
            bg="white",
            fg="#6b7280"
        )
        fuzzy_desc.pack(side="left", padx=(12, 0))
        
        # Threshold control frame (created before Full Name frame so we can pack before it)
        threshold_frame = tk.Frame(run_frame, bg="white")
        threshold_frame.pack(fill="x", pady=(10, 0))
        
        # Full Name Column Selection (shown only when fuzzy matching is enabled)
        self.full_name_selection_frame = tk.Frame(run_frame, bg="white")
        self.create_full_name_selection_controls(self.full_name_selection_frame)
        
        # Store reference to threshold_frame for proper positioning
        self.threshold_frame_ref = threshold_frame
        
        # Initially show/hide based on fuzzy matching state
        if self.fuzzy_var.get():
            self.full_name_selection_frame.pack(fill="x", pady=(10, 0), before=threshold_frame)
        else:
            self.full_name_selection_frame.pack_forget()
        
        # Threshold label
        threshold_label = tk.Label(
            threshold_frame,
            text="Fuzzy Match Threshold:",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#374151"
        )
        threshold_label.pack(side="left")
        
        # Threshold slider
        self.threshold_var = tk.DoubleVar(value=self.controller.matching_engine.threshold)
        self.threshold_slider = tk.Scale(
            threshold_frame,
            from_=50,
            to=100,
            orient="horizontal",
            variable=self.threshold_var,
            command=self.update_threshold,
            bg="white",
            fg="#374151",
            font=("Segoe UI", 10),
            length=250,
            resolution=1,
            troughcolor="#FFA896",
            highlightthickness=0,
            activebackground="#CD1C18"
        )
        self.threshold_slider.pack(side="left", padx=(12, 12))
        
        # Threshold value label
        self.threshold_label = tk.Label(
            threshold_frame,
            text=f"{self.controller.matching_engine.threshold}%",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#CD1C18"
        )
        self.threshold_label.pack(side="left")
        
        # Threshold description
        threshold_desc = tk.Label(
            threshold_frame,
            text="(Only applies when Fuzzy Logic is enabled. Higher = more strict, Lower = more lenient)",
            font=("Segoe UI", 10),
            bg="white",
            fg="#6b7280"
        )
        threshold_desc.pack(side="left", padx=(12, 0))
        
        # Button frame for run and cancel buttons
        button_frame = tk.Frame(run_frame, bg="white")
        button_frame.pack(pady=(10, 0))
        
        self.run_btn = tk.Button(
            button_frame,
            text="🚀 Run Clean-Up Process",
            command=self.run_cleanup,
            bg="#CD1C18",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=10,
            activebackground="#9B1313",
            activeforeground="white"
        )
        self.run_btn.pack(side="left", padx=(0, 12))
        
        self.cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.cancel_cleanup,
            bg="#9B1313",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=10,
            state="normal",
            activebackground="#38000A",
            activeforeground="white"
        )
        # Hide cancel button by default
        self.cancel_btn.pack_forget()
        
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
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#9B1313"
        )
        self.status_label.pack(pady=(8, 0))
    
    def create_full_name_selection_controls(self, parent_frame):
        """Create Full Name column selection controls inside the Execute Clean-Up frame"""
        # Initialize Full Name column variable
        self.current_full_name_var = tk.StringVar()
        
        # Description
        desc_label = tk.Label(
            parent_frame,
            text="Select Full Name Column for Fuzzy Matching:",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#9B1313",
            justify="left"
        )
        desc_label.pack(anchor="w", pady=(0, 8))
        
        # Load column headers for Current System Report
        try:
            headers = self.controller.get_column_headers()
            current_columns = headers.get('current_system', [])
            
            # Combo box frame
            combo_frame = tk.Frame(parent_frame, bg="white")
            combo_frame.pack(fill="x")
            
            # Add hint
            hint_label = tk.Label(
                combo_frame,
                text="(Look for columns like 'Full Name', 'Name', 'Username', 'User Description')",
                font=("Arial", 7),
                bg="white",
                fg="#9ca3af"
            )
            hint_label.pack(anchor="w")
            
            self.current_full_name_combo = ttk.Combobox(
                combo_frame,
                textvariable=self.current_full_name_var,
                values=current_columns,
                state="readonly",
                width=40
            )
            self.current_full_name_combo.pack(anchor="w", pady=(2, 0))
            
            # Load current configuration if available
            _, _, configured_full_name = self.controller.employee_dataset.get_current_system_config()
            if configured_full_name and configured_full_name in current_columns:
                self.current_full_name_var.set(configured_full_name)
            else:
                # Auto-select first matching column
                for col in current_columns:
                    col_lower = str(col).lower()
                    if any(keyword in col_lower for keyword in ['full name', 'name', 'username', 'user description', 'description', 'user desc', 'desc']):
                        self.current_full_name_var.set(str(col))
                        break
                else:
                    # If no match, select first column if available
                    if len(current_columns) > 0:
                        self.current_full_name_var.set(str(current_columns[0]))
        except Exception as e:
            # If there's an error loading headers, show empty list
            pass
    
    def create_column_selection_frame(self):
        """Create column selection configuration frame"""
        self.column_selection_frame = tk.LabelFrame(
            self.cleanup_frame,
            text="🔧 Column Selection for PERNR Lookup",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#9B1313",
            padx=15,
            pady=15
        )
        self.column_selection_frame.pack(fill="x", pady=(0, 20))
        
        # Description
        desc_label = tk.Label(
            self.column_selection_frame,
            text="Choose which columns to use for User ID matching between Current System Report and Previous Reference.\nAll columns from Previous Reference are available for selection - look for User ID and PERNR columns.",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#374151",
            justify="left"
        )
        desc_label.pack(anchor="w", pady=(0, 12))
        
        # Enable/Disable custom column selection
        self.custom_column_var = tk.BooleanVar(value=False)
        custom_checkbox = tk.Checkbutton(
            self.column_selection_frame,
            text="Enable Custom Column Selection",
            variable=self.custom_column_var,
            command=self.toggle_column_selection,
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#374151",
            selectcolor="#FFA896"
        )
        custom_checkbox.pack(anchor="w", pady=(0, 12))
        
        # Column selection controls frame
        self.column_controls_frame = tk.Frame(self.column_selection_frame, bg="white")
        self.column_controls_frame.pack(fill="x")
        
        # Initialize column selection variables
        self.current_user_id_var = tk.StringVar()
        self.previous_user_id_var = tk.StringVar()
        self.previous_pernr_var = tk.StringVar()
        
        # Load column headers
        self.load_column_headers()
        
        # Initially hide the column controls
        self.column_controls_frame.pack_forget()
    
    def load_column_headers(self):
        """Load column headers from uploaded files"""
        try:
            headers = self.controller.get_column_headers()
            
            # Create comboboxes for column selection
            # Current System Report - User ID column
            current_frame = tk.Frame(self.column_controls_frame, bg="white")
            current_frame.pack(fill="x", pady=(0, 5))
            
            tk.Label(
                current_frame,
                text="Current System Report - User ID Column:",
                font=("Segoe UI", 11, "bold"),
                bg="white",
                fg="#9B1313"
            ).pack(anchor="w")
            
            # Add hint for current system
            hint_label1 = tk.Label(
                current_frame,
                text="(Look for columns like 'User ID', 'Username', 'SysID', 'Abbreviation')",
                font=("Segoe UI", 10),
                bg="white",
                fg="#6b7280"
            )
            hint_label1.pack(anchor="w")
            
            self.current_user_id_combo = ttk.Combobox(
                current_frame,
                textvariable=self.current_user_id_var,
                values=headers.get('current_system', []),
                state="readonly",
                width=40
            )
            self.current_user_id_combo.pack(anchor="w", pady=(2, 0))
            
            # Previous System Report - User ID column
            previous_user_frame = tk.Frame(self.column_controls_frame, bg="white")
            previous_user_frame.pack(fill="x", pady=(5, 5))
            
            tk.Label(
                previous_user_frame,
                text="Previous Reference - User ID Column:",
                font=("Segoe UI", 11, "bold"),
                bg="white",
                fg="#9B1313"
            ).pack(anchor="w")
            
            # Add hint for previous user ID
            hint_label2 = tk.Label(
                previous_user_frame,
                text="(Look for columns like 'User ID', 'Username', 'SysID', 'Abbreviation' - ALL columns shown)",
                font=("Segoe UI", 10),
                bg="white",
                fg="#6b7280"
            )
            hint_label2.pack(anchor="w")
            
            self.previous_user_id_combo = ttk.Combobox(
                previous_user_frame,
                textvariable=self.previous_user_id_var,
                values=headers.get('previous_system', []),
                state="readonly",
                width=40
            )
            self.previous_user_id_combo.pack(anchor="w", pady=(2, 0))
            
            # Previous System Report - PERNR column
            previous_pernr_frame = tk.Frame(self.column_controls_frame, bg="white")
            previous_pernr_frame.pack(fill="x", pady=(5, 0))
            
            tk.Label(
                previous_pernr_frame,
                text="Previous Reference - PERNR Column:",
                font=("Segoe UI", 11, "bold"),
                bg="white",
                fg="#9B1313"
            ).pack(anchor="w")
            
            # Add hint for PERNR column
            hint_label3 = tk.Label(
                previous_pernr_frame,
                text="(Look for columns like 'PERNR', 'Employee Number', 'Pers. Number' - ALL columns shown)",
                font=("Segoe UI", 10),
                bg="white",
                fg="#6b7280"
            )
            hint_label3.pack(anchor="w")
            
            self.previous_pernr_combo = ttk.Combobox(
                previous_pernr_frame,
                textvariable=self.previous_pernr_var,
                values=headers.get('previous_system', []),
                state="readonly",
                width=40
            )
            self.previous_pernr_combo.pack(anchor="w", pady=(2, 0))
            
            # Load current custom column settings
            custom_columns = self.controller.get_custom_lookup_columns()
            if custom_columns['current_user_id']:
                self.current_user_id_var.set(custom_columns['current_user_id'])
            if custom_columns['previous_user_id']:
                self.previous_user_id_var.set(custom_columns['previous_user_id'])
            if custom_columns['previous_pernr']:
                self.previous_pernr_var.set(custom_columns['previous_pernr'])
            
        except Exception as e:
            # If there's an error loading headers, show empty lists
            pass
    
    def toggle_column_selection(self):
        """Toggle column selection controls visibility"""
        if self.custom_column_var.get():
            self.column_controls_frame.pack(fill="x")
        else:
            self.column_controls_frame.pack_forget()
            # Clear custom columns when disabled
            self.controller.clear_custom_lookup_columns()
    
    def update_threshold(self, value):
        """Update threshold value and label"""
        threshold = int(float(value))
        if self.threshold_label:
            self.threshold_label.config(text=f"{threshold}%")
    
    def toggle_fuzzy_logic(self):
        """Toggle fuzzy logic option"""
        use_fuzzy = self.fuzzy_var.get()
        
        # Show/hide Full Name column selection based on fuzzy logic
        if self.full_name_selection_frame:
            if use_fuzzy:
                # Pack before threshold_frame to maintain correct order
                if hasattr(self, 'threshold_frame_ref'):
                    self.full_name_selection_frame.pack(fill="x", pady=(10, 0), before=self.threshold_frame_ref)
                else:
                    self.full_name_selection_frame.pack(fill="x", pady=(10, 0))
            else:
                self.full_name_selection_frame.pack_forget()
        
        # Enable/disable threshold controls based on fuzzy logic
        if self.threshold_slider:
            if use_fuzzy:
                self.threshold_slider.config(state="normal")
                if self.threshold_label:
                    self.threshold_label.config(fg="#CD1C18")  # Red when active
            else:
                self.threshold_slider.config(state="disabled")
                if self.threshold_label:
                    self.threshold_label.config(fg="#9ca3af")  # Gray when disabled
    
    def run_cleanup(self):
        """Run the cleanup process"""
        if self.run_btn:
            self.run_btn.config(state="disabled")
        if self.cancel_btn:
            self.cancel_btn.pack(side="left")  # Show cancel button
        if self.progress_bar:
            self.progress_bar['value'] = 0
        if self.status_label:
            self.status_label.config(text="Starting clean-up process...")
        
        # Get current settings
        use_fuzzy_logic = self.fuzzy_var.get() if self.fuzzy_var else True
        threshold = int(self.threshold_var.get()) if self.threshold_var else 80
        
        # Save Full Name column selection
        current_full_name = self.current_full_name_var.get() if self.current_full_name_var else None
        if current_full_name:
            # Update the dataset configuration with the selected Full Name column
            header_row, user_id_column, _ = self.controller.employee_dataset.get_current_system_config()
            self.controller.employee_dataset.set_current_system_config(header_row, user_id_column, current_full_name)
        
        # Save custom column selections if enabled
        if self.custom_column_var and self.custom_column_var.get():
            current_user_id = self.current_user_id_var.get() if self.current_user_id_var else None
            previous_user_id = self.previous_user_id_var.get() if self.previous_user_id_var else None
            previous_pernr = self.previous_pernr_var.get() if self.previous_pernr_var else None
            
            # Only set columns that have values
            if current_user_id or previous_user_id or previous_pernr:
                self.controller.set_custom_lookup_columns(current_user_id, previous_user_id, previous_pernr)
            # Also update the dataset with the selected User ID column
            if current_user_id:
                header_row, _, full_name_column = self.controller.employee_dataset.get_current_system_config()
                self.controller.employee_dataset.set_current_system_config(header_row, current_user_id, full_name_column)
        else:
            # Clear custom columns if disabled
            self.controller.clear_custom_lookup_columns()
        
        # Start cleanup process
        if hasattr(self, 'controller') and self.controller:
            self.controller.start_cleanup(use_fuzzy_logic, threshold)
    
    def cancel_cleanup(self):
        """Cancel the cleanup process"""
        if hasattr(self, 'controller') and self.controller:
            self.controller.processing_controller.cancel_cleanup()
    
    def update_progress(self, value: float, status: str):
        """Update progress bar and status"""
        if self.progress_bar:
            self.progress_bar.config(value=value)
        if self.status_label:
            self.status_label.config(text=status)
    
    def reset_run_button(self):
        """Reset run button to normal state"""
        if self.run_btn:
            self.run_btn.config(state="normal")
        if self.cancel_btn:
            self.cancel_btn.pack_forget()  # Hide cancel button
    
    def reset_cleanup_state(self):
        """Reset cleanup view to initial state"""
        # Reset progress bar
        if self.progress_bar:
            self.progress_bar['value'] = 0
        
        # Reset status label
        if self.status_label:
            self.status_label.config(text="Ready to start clean-up")
        
        # Reset run button
        if self.run_btn:
            self.run_btn.config(state="normal")
        if self.cancel_btn:
            self.cancel_btn.pack_forget()  # Hide cancel button
        
        # Reset fuzzy logic to default
        if self.fuzzy_var:
            self.fuzzy_var.set(True)
        
        # Reset threshold to default
        if self.threshold_var:
            self.threshold_var.set(80)
        if self.threshold_label:
            self.threshold_label.config(text="80%")
        
        # Reset threshold slider state
        if self.threshold_slider:
            self.threshold_slider.config(state="normal")
        
        # Reset column selection
        if self.custom_column_var:
            self.custom_column_var.set(False)
        if self.column_controls_frame:
            self.column_controls_frame.pack_forget()
        
        # Clear custom columns
        if hasattr(self, 'controller') and self.controller:
            self.controller.clear_custom_lookup_columns()
    
    def refresh_column_headers(self):
        """Refresh column headers when files are uploaded"""
        if self.column_selection_frame and self.custom_column_var and self.custom_column_var.get():
            # Reload column headers
            self.load_column_headers()