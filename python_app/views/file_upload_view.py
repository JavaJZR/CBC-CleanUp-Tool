"""
File Upload View
Handles file upload UI components
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Dict, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.main_controller import MainController

class FileUploadView:
    """File upload UI component"""
    
    def __init__(self, parent, controller: 'MainController'):
        self.parent = parent
        self.controller = controller
        self.upload_cards: Dict[str, tk.Frame] = {}
        self.create_upload_section()
    
    def create_upload_section(self):
        """Create the file upload section"""
        self.upload_frame = tk.LabelFrame(
            self.parent,
            text="1️⃣ File Upload",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#dc2626",
            padx=15,
            pady=15
        )
        self.upload_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        # Description
        desc_label = tk.Label(
            self.upload_frame,
            text="Upload your employee data files in Excel (.xlsx, .xls) or CSV format",
            font=("Arial", 9),
            bg="white",
            fg="#6b7280"
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Upload cards grid
        cards_frame = tk.Frame(self.upload_frame, bg="white")
        cards_frame.pack(fill="both", expand=True)
        
        file_configs = [
            ('current_system', 'Current System Report', 'Latest employee data to enrich with Employee Numbers and Full Names', 'Required'),
            ('previous_reference', 'Previous Reference', 'Contains User ID to Employee Number mapping for faster User ID lookup', 'Optional'),
            ('masterlist_current', 'Masterlist – Current', 'Active employees with Employee Number and Full Name', 'Required'),
            ('masterlist_resigned', 'Masterlist – Resigned', 'Resigned employees with Employee Number and Full Name', 'Required')
        ]
        
        for idx, (key, title, desc, req) in enumerate(file_configs):
            card = self.create_upload_card(cards_frame, key, title, desc, req)
            card.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            self.upload_cards[key] = card
            cards_frame.columnconfigure(idx, weight=1)
        
        # Clear All button
        self.create_clear_all_button()
    
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
        req_color = "#dc2626" if requirement == "Required" else "#059669"
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
            command=lambda k=key: self.upload_file(k),
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
            command=lambda k=key: self.preview_file(k),
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
        
        # Store references for later updates
        card.file_label = file_label
        card.preview_btn = preview_btn
        
        return card
    
    def create_clear_all_button(self):
        """Create clear all files button"""
        clear_button_frame = tk.Frame(self.upload_frame, bg="white")
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
        
        if file_path:
            # Call the controller method through the main controller
            if hasattr(self, 'controller') and self.controller:
                self.controller.handle_file_upload(file_type, file_path)
    
    def preview_file(self, file_type: str):
        """Preview a specific file"""
        if hasattr(self, 'controller') and self.controller:
            self.controller.preview_file(file_type)
    
    def clear_all_files(self):
        """Clear all uploaded files and reset the UI"""
        confirm = messagebox.askyesno(
            "Clear All Files",
            "Are you sure you want to clear all uploaded files?\n\nThis will reset the application."
        )
        
        if confirm and hasattr(self, 'controller') and self.controller:
            self.controller.clear_all_files()
    
    def update_file_card(self, file_type: str, file_name: str, row_count: int, col_count: int):
        """Update file card display after successful upload"""
        card = self.upload_cards[file_type]
        card.file_label.config(
            text=f"✓ {file_name}\n({row_count} rows, {col_count} columns)",
            fg="#059669"
        )
        card.preview_btn.config(state="normal")
    
    def reset_file_card(self, file_type: str):
        """Reset file card to initial state"""
        card = self.upload_cards[file_type]
        card.file_label.config(
            text="No file selected",
            fg="#9ca3af"
        )
        card.preview_btn.config(state="disabled")
    
    def reset_all_cards(self):
        """Reset all file cards"""
        for file_type in self.upload_cards.keys():
            self.reset_file_card(file_type)
    
    def show_error(self, message: str):
        """Show error message"""
        messagebox.showerror("Error", message)
    
    def show_success(self, message: str):
        """Show success message"""
        messagebox.showinfo("Success", message)
