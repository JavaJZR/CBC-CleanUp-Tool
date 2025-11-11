"""
Employee Data Clean-Up Tool - MVC Architecture
Chinabank Corporation Internal System

This is the main entry point for the refactored MVC version of the application.
The original monolithic version is preserved in backup_original/employee_cleanup_tool_original.py
"""

from controllers.main_controller import MainController
from views.splash_screen import SplashScreen


def main():
    """Main application entry point"""
    splash = SplashScreen()
    splash.show()

    app = MainController()
    app.initialize()
    splash.close(new_default_root=app.main_window.root)
    app.run()


if __name__ == "__main__":
    main()
