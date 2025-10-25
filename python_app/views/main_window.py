"""
Main Window View
Main application window and layout management
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from controllers.main_controller import MainController

class MainWindow:
    """Main application window view"""
    
    def __init__(self, controller: 'MainController'):
        self.controller = controller
        self.root = tk.Tk()
        self.scrollable_frame: Optional[ttk.Frame] = None
        
        # View components
        self.file_upload_view: Optional['FileUploadView'] = None
        self.preview_view: Optional['PreviewView'] = None
        self.cleanup_view: Optional['CleanupView'] = None
        self.results_view: Optional['ResultsView'] = None
        
        self.setup_window()
        self.create_ui()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Employee Data Clean-Up Tool - Chinabank Corporation")
        self.root.state('zoomed')  # Windows maximized state
        self.root.configure(bg="#f8fafc")
        
        # Configure grid weights for full expansion
        self.root.grid_rowconfigure(1, weight=1)  # Main content row
        self.root.grid_columnconfigure(0, weight=1)  # Main content column
    
    def create_ui(self):
        """Create the main UI layout"""
        self.create_header()
        self.create_scrollable_area()
        self.create_footer()
        self.create_instructions_section()
    
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
    
    def create_scrollable_area(self):
        """Create scrollable main content area"""
        main_canvas = tk.Canvas(self.root, bg="#f8fafc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        # Throttle scroll region updates for better performance
        self._update_scroll_region_pending = False
        
        def update_scroll_region(event=None):
            """Update scroll region (throttled for performance)"""
            if not self._update_scroll_region_pending:
                self._update_scroll_region_pending = True
                main_canvas.after_idle(lambda: self._do_update_scroll_region(main_canvas))
        
        self.scrollable_frame.bind("<Configure>", update_scroll_region)
        
        # Create window for scrollable frame and bind canvas width to frame
        canvas_window = main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make scrollable frame expand to canvas width
        def on_canvas_configure(event):
            main_canvas.itemconfig(canvas_window, width=event.width)
        main_canvas.bind("<Configure>", on_canvas_configure)
        
        # Add mouse wheel support for smoother scrolling (Windows/Mac)
        def on_mousewheel(event):
            """Handle mouse wheel scrolling"""
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        
        # Bind mouse wheel to the canvas
        main_canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Also support Linux mouse wheel events
        def on_linux_mousewheel(event):
            """Handle Linux mouse wheel scrolling"""
            if event.num == 4:
                main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                main_canvas.yview_scroll(1, "units")
            return "break"
        
        main_canvas.bind("<Button-4>", on_linux_mousewheel)
        main_canvas.bind("<Button-5>", on_linux_mousewheel)
        
        # Use grid layout instead of pack for better expansion control
        main_canvas.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        scrollbar.grid(row=1, column=1, sticky="ns")
    
    def _do_update_scroll_region(self, canvas):
        """Actually update the scroll region"""
        canvas.configure(scrollregion=canvas.bbox("all"))
        self._update_scroll_region_pending = False
    
    def create_instructions_section(self):
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
   • Previous Reference (Optional) - Contains User ID → PERNR mapping for faster lookup
   • Masterlist Current (Required) - Active employees with PERNR and Full Name
   • Masterlist Resigned (Required) - Resigned employees with PERNR and Full Name

2️⃣ PREVIEW DATA: Review uploaded files to verify structure and content

3️⃣ CONFIGURE CLEANUP: Add "PERNR", "Full Name (From Masterlist)", "Resignation Date", and Organizational Data columns
   • PERNR: Looked up by User ID from Previous Reference (if provided), with fallback name matching
   • Full Name: Retrieved from Current/Resigned Masterlist using the PERNR
   • Resignation Date: Retrieved from Resigned Masterlist using the PERNR (if employee is resigned)
   • Organizational Data: Position Name, Segment Name, Group Name, Area/Division Name, Department/Branch from Current Masterlist
   • Fallback: If User ID lookup fails or no Previous Reference, matches "Username (Full Name)" with masterlist names
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
    
    def initialize_views(self):
        """Initialize view components"""
        from views.file_upload_view import FileUploadView
        from views.preview_view import PreviewView
        from views.cleanup_view import CleanupView
        from views.results_view import ResultsView
        
        # Create view components
        self.file_upload_view = FileUploadView(self.scrollable_frame, self.controller)
        self.preview_view = PreviewView(self.scrollable_frame, self.controller)
        self.cleanup_view = CleanupView(self.scrollable_frame, self.controller)
        self.results_view = ResultsView(self.scrollable_frame, self.controller)
    
    def show_preview_section(self):
        """Show data preview section"""
        if self.preview_view:
            self.preview_view.show()
    
    def show_cleanup_section(self):
        """Show cleanup configuration section"""
        if self.cleanup_view:
            self.cleanup_view.show()
    
    def show_results_section(self, statistics: dict):
        """Show results section"""
        if self.results_view:
            self.results_view.show(statistics)
    
    def update_progress(self, value: float, status: str):
        """Update progress bar and status"""
        if self.cleanup_view:
            self.cleanup_view.update_progress(value, status)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
