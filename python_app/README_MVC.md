# Employee Data Clean-Up Tool - MVC Architecture

This is the refactored version of the Employee Data Clean-Up Tool using the Model-View-Controller (MVC) architecture pattern.

## 📁 Directory Structure

```
python_app/
├── 📁 backup_original/
│   └── employee_cleanup_tool_original.py  # Original monolithic version
├── 📁 models/
│   ├── __init__.py
│   ├── employee_data.py                   # Employee data models and structures
│   ├── file_handler.py                    # File I/O operations
│   └── matching_engine.py                 # Fuzzy matching logic
├── 📁 views/
│   ├── __init__.py
│   ├── main_window.py                     # Main application window
│   ├── file_upload_view.py                # File upload UI components
│   ├── preview_view.py                    # Data preview UI components
│   ├── cleanup_view.py                    # Cleanup controls UI components
│   └── results_view.py                    # Results display UI components
├── 📁 controllers/
│   ├── __init__.py
│   ├── main_controller.py                 # Main application controller
│   ├── file_controller.py                 # File operations controller
│   └── processing_controller.py           # Data processing controller
├── main.py                                # Application entry point
└── README_MVC.md                          # This file
```

## 🏗️ Architecture Overview

### Model Layer (`models/`)
- **`employee_data.py`**: Contains `EmployeeRecord` and `EmployeeDataset` classes for data management
- **`file_handler.py`**: Handles file I/O operations, CSV/Excel loading, and export functionality
- **`matching_engine.py`**: Implements fuzzy matching algorithms and employee lookup logic

### View Layer (`views/`)
- **`main_window.py`**: Main application window and layout management
- **`file_upload_view.py`**: File upload UI components and cards
- **`preview_view.py`**: Data preview table and file selector
- **`cleanup_view.py`**: Cleanup configuration controls and progress display
- **`results_view.py`**: Results display, statistics, and export buttons

### Controller Layer (`controllers/`)
- **`main_controller.py`**: Coordinates all components and manages application flow
- **`file_controller.py`**: Handles file operations and data loading
- **`processing_controller.py`**: Manages data processing workflow and cleanup operations

## 🚀 Running the Application

### Option 1: MVC Version (Recommended)
```bash
cd python_app
python main.py
```

### Option 2: Original Version (Backup)
```bash
cd python_app/backup_original
python employee_cleanup_tool_original.py
```

## ✨ Benefits of MVC Architecture

### 1. **Separation of Concerns**
- **Models**: Handle data and business logic independently
- **Views**: Focus solely on UI presentation
- **Controllers**: Coordinate between models and views

### 2. **Improved Maintainability**
- Each component has a single responsibility
- Changes to UI don't affect business logic
- Data processing logic is isolated and testable

### 3. **Better Testability**
- Models can be tested independently
- Controllers can be unit tested without UI dependencies
- Business logic is decoupled from presentation

### 4. **Enhanced Scalability**
- Easy to add new features without affecting existing code
- Multiple developers can work on different layers
- Easy to swap UI frameworks (e.g., from Tkinter to PyQt)

### 5. **Code Reusability**
- Models can be used in different views
- Controllers can be reused for different UI frameworks
- Business logic is independent of UI technology

## 🔧 Key Features

- **Smart File Detection**: Automatically detects headers in CSV/Excel files
- **Fuzzy Matching**: Configurable fuzzy string matching for employee names
- **Multi-format Export**: Excel (multi-sheet) and CSV export options
- **Progress Tracking**: Real-time progress updates during processing
- **Data Validation**: Comprehensive error handling and validation
- **Professional UI**: Modern, responsive interface with Chinabank branding

## 📊 Data Flow

1. **Upload** → 3 required files + 1 optional (Current System, Masterlist Current, Masterlist Resigned, Previous Reference optional)
2. **Preview** → Validate file structure and content
3. **Configure** → Set fuzzy logic preferences and threshold
4. **Process** → Multi-step enrichment with User ID lookup (if Previous Reference provided) → Name matching → Data retrieval
5. **Results** → Export enriched data with multiple views and formats

## 🛠️ Development Notes

- The original monolithic file is preserved in `backup_original/` for reference
- All functionality from the original version is maintained
- The MVC structure makes the codebase more professional and maintainable
- Future enhancements can be easily added to the appropriate layer

## 📝 Requirements

- Python 3.7+
- tkinter (built-in)
- pandas
- numpy
- fuzzywuzzy
- openpyxl (for Excel support)

## 🏦 Chinabank Corporation

This tool is specifically designed for Chinabank Corporation to:
- Enrich employee reports with missing PERNRs and full names
- Consolidate data from multiple HR systems
- Handle name variations and data inconsistencies
- Export clean, standardized reports for further processing
- Track resigned vs. current employees with organizational details
