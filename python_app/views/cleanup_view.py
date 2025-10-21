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
            text="This process will enrich your data by adding missing information:\n• Employee Numbers (PERNR) • Full Names • Resignation Dates • Job Details\n\nHow it works: 1) Find employee numbers using User IDs (if Previous Reference provided), 2) If that fails or no Previous Reference, match by name, 3) Get full names and job details from masterlists, 4) Optional: Use smart matching for similar names",
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
            text="Start the lookup process to add PERNRs, Full Names, Resignation Dates, and Organizational Data\n(Uses User ID lookup if Previous Reference provided, otherwise uses name matching)",
            font=("Arial", 8),
            bg="white",
            fg="#6b7280"
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
            font=("Arial", 8),
            length=200,
            resolution=1
        )
        self.threshold_slider.pack(side="left", padx=(10, 10))
        
        # Threshold value label
        self.threshold_label = tk.Label(
            threshold_frame,
            text=f"{self.controller.matching_engine.threshold}%",
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
        threshold = int(float(value))
        if self.threshold_label:
            self.threshold_label.config(text=f"{threshold}%")
    
    def toggle_fuzzy_logic(self):
        """Toggle fuzzy logic option"""
        use_fuzzy = self.fuzzy_var.get()
        
        # Enable/disable threshold controls based on fuzzy logic
        if self.threshold_slider:
            if use_fuzzy:
                self.threshold_slider.config(state="normal")
                if self.threshold_label:
                    self.threshold_label.config(fg="#dc2626")  # Red when active
            else:
                self.threshold_slider.config(state="disabled")
                if self.threshold_label:
                    self.threshold_label.config(fg="#9ca3af")  # Gray when disabled
    
    def run_cleanup(self):
        """Run the cleanup process"""
        if self.run_btn:
            self.run_btn.config(state="disabled")
        if self.progress_bar:
            self.progress_bar['value'] = 0
        if self.status_label:
            self.status_label.config(text="Starting clean-up process...")
        
        # Get current settings
        use_fuzzy_logic = self.fuzzy_var.get() if self.fuzzy_var else True
        threshold = int(self.threshold_var.get()) if self.threshold_var else 80
        
        # Start cleanup process
        if hasattr(self, 'controller') and self.controller:
            self.controller.start_cleanup(use_fuzzy_logic, threshold)
    
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