"""
Quick test script to verify the upload functionality works
This creates sample CSV files to test the upload feature
"""

import pandas as pd
import os

def create_test_files():
    """Create sample CSV files for testing the upload functionality"""
    
    # Create test directory
    test_dir = "test_files"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Sample Current System Report
    current_system_data = {
        'User ID': ['USER001', 'USER002', 'USER003'],
        'Username (Full Name)': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Department': ['IT', 'HR', 'Finance']
    }
    current_system_df = pd.DataFrame(current_system_data)
    current_system_df.to_csv(os.path.join(test_dir, 'current_system_report.csv'), index=False)
    
    # Sample Previous Reference (Optional - for faster User ID lookup)
    previous_reference_data = {
        'User ID': ['USER001', 'USER002', 'USER003'],
        'PERNR': [12345, 12346, 12347]
    }
    previous_reference_df = pd.DataFrame(previous_reference_data)
    previous_reference_df.to_csv(os.path.join(test_dir, 'previous_reference_optional.csv'), index=False)
    
    # Sample Masterlist Current
    masterlist_current_data = {
        'PERNR': [12345, 12346, 12347],
        'Full Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Position Name': ['Software Engineer', 'HR Manager', 'Financial Analyst'],
        'Department/Branch': ['IT Department', 'HR Department', 'Finance Department']
    }
    masterlist_current_df = pd.DataFrame(masterlist_current_data)
    masterlist_current_df.to_csv(os.path.join(test_dir, 'masterlist_current.csv'), index=False)
    
    # Sample Masterlist Resigned
    masterlist_resigned_data = {
        'PERNR': [],
        'Full Name': [],
        'Resignation Date': []
    }
    masterlist_resigned_df = pd.DataFrame(masterlist_resigned_data)
    masterlist_resigned_df.to_csv(os.path.join(test_dir, 'masterlist_resigned.csv'), index=False)
    
    print("Test files created successfully!")
    print(f"Test files location: {os.path.abspath(test_dir)}")
    print("\nFiles created:")
    print("- current_system_report.csv (Required)")
    print("- previous_reference_optional.csv (Optional - for faster User ID lookup)") 
    print("- masterlist_current.csv (Required)")
    print("- masterlist_resigned.csv (Required)")
    print("\nYou can now test the upload functionality with these files!")
    print("Note: Previous Reference is now optional. You can run cleanup with just the 3 required files.")

if __name__ == "__main__":
    create_test_files()
