"""
Main Controller
Coordinates all application components and manages the main application flow
"""

from typing import TYPE_CHECKING, Optional
from models.employee_data import EmployeeDataset
from models.matching_engine import MatchingEngine
from models.file_handler import FileHandler

if TYPE_CHECKING:
    from views.main_window import MainWindow
    from controllers.file_controller import FileController
    from controllers.processing_controller import ProcessingController

class MainController:
    """Main application controller coordinating all components"""
    
    def __init__(self):
        # Models
        self.employee_dataset = EmployeeDataset()
        self.matching_engine = MatchingEngine()
        self.file_handler = FileHandler()
        
        # Views
        self.main_window: Optional['MainWindow'] = None
        
        # Sub-controllers
        self.file_controller: Optional['FileController'] = None
        self.processing_controller: Optional['ProcessingController'] = None
        
        # Current state
        self.current_step = 1
    
    def initialize(self):
        """Initialize the application"""
        # Create main window and sub-controllers
        from views.main_window import MainWindow
        from controllers.file_controller import FileController
        from controllers.processing_controller import ProcessingController
        
        self.main_window = MainWindow(self)
        self.file_controller = FileController(self)
        self.processing_controller = ProcessingController(self)
        
        # Initialize views in main window
        self.main_window.initialize_views()
        
        # Setup view callbacks
        self.setup_view_callbacks()
    
    def setup_view_callbacks(self):
        """Setup callbacks between views and controllers"""
        # File upload callbacks
        if self.main_window.file_upload_view:
            # Store the controller methods in the view for callback access
            self.main_window.file_upload_view.controller = self
        
        # Preview callbacks
        if self.main_window.preview_view:
            self.main_window.preview_view.controller = self
        
        # Cleanup callbacks
        if self.main_window.cleanup_view:
            self.main_window.cleanup_view.controller = self
        
        # Results callbacks
        if self.main_window.results_view:
            self.main_window.results_view.controller = self
    
    def handle_file_upload(self, file_type: str, file_path: str):
        """Handle file upload request"""
        self.file_controller.handle_file_upload(file_type, file_path)
    
    def preview_file(self, file_type: str):
        """Preview a specific file"""
        if self.current_step >= 2:
            self.main_window.show_preview_section()
    
    def clear_all_files(self):
        """Clear all uploaded files and reset the UI"""
        self.employee_dataset.clear_all_data()
        
        # Reset UI components
        if self.main_window.file_upload_view:
            self.main_window.file_upload_view.reset_all_cards()
        
        # Hide all sections except file upload
        self.current_step = 1
        if self.main_window:
            # Hide preview section
            if self.main_window.preview_view and self.main_window.preview_view.preview_frame:
                self.main_window.preview_view.preview_frame.destroy()
                self.main_window.preview_view.preview_frame = None
            
            # Hide cleanup section
            if self.main_window.cleanup_view and self.main_window.cleanup_view.cleanup_frame:
                self.main_window.cleanup_view.cleanup_frame.destroy()
                self.main_window.cleanup_view.cleanup_frame = None
            # Reset cleanup state if cleanup view exists
            elif self.main_window.cleanup_view:
                self.main_window.cleanup_view.reset_cleanup_state()
            
            # Hide results section
            if self.main_window.results_view and self.main_window.results_view.results_frame:
                self.main_window.results_view.results_frame.destroy()
                self.main_window.results_view.results_frame = None
        
        # Show success message
        if self.main_window.file_upload_view:
            self.main_window.file_upload_view.show_success("All files cleared. You can now upload new files.")
    
    def show_preview_section(self):
        """Show data preview section"""
        if self.employee_dataset.is_ready_for_processing():
            self.current_step = 2
            self.main_window.show_preview_section()
    
    def show_cleanup_section(self):
        """Show cleanup configuration section"""
        if self.employee_dataset.is_ready_for_processing():
            self.current_step = 3
            self.main_window.show_cleanup_section()
    
    def start_cleanup(self, use_fuzzy_logic: bool, threshold: int):
        """Start the cleanup process"""
        self.processing_controller.start_cleanup(use_fuzzy_logic, threshold)
    
    def show_results_section(self):
        """Show results section"""
        self.current_step = 4
        statistics = self.employee_dataset.get_statistics()
        self.main_window.show_results_section(statistics)
    
    def handle_export_request(self, data_type: str, format_type: str):
        """Handle export request"""
        self.file_controller.handle_export_request(data_type, format_type)
    
    def update_progress(self, value: float, status: str):
        """Update progress bar and status"""
        if self.main_window:
            self.main_window.update_progress(value, status)
    
    def run(self):
        """Start the application"""
        if self.main_window:
            self.main_window.run()
