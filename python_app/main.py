"""
Employee Data Clean-Up Tool - MVC Architecture
Chinabank Corporation Internal System

This is the main entry point for the refactored MVC version of the application.
The original monolithic version is preserved in backup_original/employee_cleanup_tool_original.py
"""

from controllers.main_controller import MainController

def main():
    """Main application entry point"""
    try:
        # Create and initialize the main controller
        app = MainController()
        app.initialize()
        
        # Start the application
        app.run()
        
    except Exception as e:
        print(f"Application failed to start: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
