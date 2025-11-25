# Technical Overview - Employee Data Clean-Up Tool

## 📦 Dependencies

### Core Python Libraries

#### 1. **pandas** (>=2.0.0)
- **Purpose**: Primary data manipulation and analysis library
- **Usage**: 
  - Reading/writing CSV and Excel files
  - DataFrame operations for data processing
  - Data filtering, merging, and transformation
  - Handling missing values and data validation
- **Key Features Used**:
  - `pd.read_csv()` / `pd.read_excel()` for file I/O
  - DataFrame operations (filtering, sorting, indexing)
  - Data type conversion and normalization
  - Multi-sheet Excel export

#### 2. **numpy** (>=1.24.0)
- **Purpose**: Numerical computing foundation
- **Usage**: 
  - Underlying support for pandas operations
  - Numerical data type handling
  - Array operations for performance optimization
- **Note**: Primarily used indirectly through pandas

#### 3. **openpyxl** (>=3.1.0)
- **Purpose**: Excel file format support (.xlsx files)
- **Usage**:
  - Reading and writing Excel files
  - Handling merged cells in Excel
  - Excel styling and formatting (colors, fonts, column widths)
  - Multi-sheet workbook creation
- **Key Features Used**:
  - `load_workbook()` for merged cell handling
  - ExcelWriter for styled exports
  - Cell formatting and styling

#### 4. **xlrd** (>=2.0.1)
- **Purpose**: Support for older Excel file formats (.xls)
- **Usage**: Reading legacy Excel files (pre-2007 format)
- **Note**: Used as fallback for older file formats

#### 5. **fuzzywuzzy** (>=0.18.0)
- **Purpose**: Fuzzy string matching for employee name matching
- **Usage**:
  - Matching employee names with variations
  - Handling typos, abbreviations, and name order differences
  - Similarity scoring between strings
- **Key Functions Used**:
  - `fuzz.ratio()` - Overall similarity score
  - `fuzz.partial_ratio()` - Partial string matching
- **Algorithm**: Uses Levenshtein distance algorithm

#### 6. **python-Levenshtein** (>=0.21.0)
- **Purpose**: Performance optimization for fuzzywuzzy
- **Usage**: 
  - C implementation of Levenshtein distance calculation
  - Speeds up fuzzy matching operations significantly
  - Reduces processing time for large datasets

#### 7. **tkinter** (Built-in)
- **Purpose**: GUI framework for desktop application
- **Usage**:
  - Main application window
  - File dialogs and user interactions
  - Progress bars and status updates
  - Form controls (buttons, labels, frames, scrollbars)
- **Note**: Comes pre-installed with Python (may need separate installation on Linux)

---

## 🏗️ Architecture

### Model-View-Controller (MVC) Pattern

The application follows a strict MVC architecture for separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Main Controller                       │
│              (Orchestrates all components)              │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
       ┌───────┴────────┐        ┌────────┴────────┐
       │   Controllers  │        │      Views       │
       ├────────────────┤        ├──────────────────┤
       │ FileController │        │  MainWindow      │
       │ProcessingCtrl  │        │  FileUploadView  │
       └────────┬───────┘        │  PreviewView     │
                │                │  CleanupView     │
                │                │  ResultsView     │
                │                └──────────────────┘
                │
       ┌────────┴────────┐
       │     Models      │
       ├─────────────────┤
       │ EmployeeDataset │
       │ MatchingEngine  │
       │  FileHandler    │
       │   DataSorter    │
       └─────────────────┘
```

### Layer Responsibilities

#### **Models** (`models/`)
- **Business Logic**: Core data processing algorithms
- **Data Management**: Employee records, datasets, file I/O
- **No UI Dependencies**: Pure Python logic, testable independently

#### **Views** (`views/`)
- **UI Presentation**: All user interface components
- **User Interaction**: Buttons, forms, dialogs
- **No Business Logic**: Only display and user input handling

#### **Controllers** (`controllers/`)
- **Coordination**: Bridge between models and views
- **Workflow Management**: Application flow and state management
- **Event Handling**: User actions and system responses

---

## 🔧 Technical Implementation Details

### 1. File Handling System

#### **Header Detection Algorithm**
```python
# Multi-step header detection process:
1. Check for specific keywords ("Full Name", "PERNR", "User ID")
2. Validate header row (check for expected column patterns)
3. Handle merged cells in Excel files
4. Fallback to first row if no valid headers found
```

**Key Features**:
- **Flexible Column Detection**: Searches first 10-15 rows for headers
- **Merged Cell Handling**: Uses `openpyxl` to process merged cells before pandas reads
- **Type-Specific Logic**: Different detection strategies for masterlists vs. system reports

#### **File Format Support**
- **CSV**: UTF-8 encoding with BOM support (`utf-8-sig`)
- **Excel (.xlsx)**: Modern format using `openpyxl`
- **Excel (.xls)**: Legacy format using `xlrd`
- **Data Preservation**: All data read as strings to preserve formatting

### 2. Matching Engine

#### **Multi-Tier Matching Strategy**

```
┌─────────────────────────────────────────┐
│  Step 1: User ID Lookup (Fast Path)    │
│  - Use Previous Reference if available │
│  - Direct User ID → PERNR mapping      │
│  - O(1) lookup time                    │
└──────────────┬──────────────────────────┘
               │ (if failed)
               ▼
┌─────────────────────────────────────────┐
│  Step 2: Exact Name Match               │
│  - Case-insensitive exact match         │
│  - O(n) linear search                   │
│  - 100% confidence score                │
└──────────────┬──────────────────────────┘
               │ (if failed & fuzzy enabled)
               ▼
┌─────────────────────────────────────────┐
│  Step 3: Fuzzy Name Matching            │
│  - Levenshtein distance algorithm      │
│  - Handles name order variations        │
│  - Configurable threshold (50-100%)    │
└─────────────────────────────────────────┘
```

#### **Fuzzy Matching Algorithms**

1. **Ratio Matching** (`fuzz.ratio()`)
   - Full string comparison
   - Best for exact or near-exact matches

2. **Partial Ratio** (`fuzz.partial_ratio()`)
   - Substring matching
   - Handles abbreviations and partial names

3. **Name Order Matching** (Custom)
   - Handles "First Last" vs "Last, First" variations
   - Component-based matching for multi-part names
   - Special handling for names with 3+ parts

#### **Normalization Process**
```python
# User ID normalization:
1. Convert to lowercase
2. Strip whitespace and special characters
3. Remove trailing ".0" from numeric strings
4. Handle Unicode characters (non-breaking spaces)
5. Create numeric fallback keys
```

### 3. Data Processing Pipeline

#### **Processing Workflow**

```
Upload Files
    ↓
Header Detection & Column Selection
    ↓
Data Validation
    ↓
┌─────────────────────────────────────┐
│  For each employee record:          │
│  1. Lookup PERNR (User ID or Name)  │
│  2. Retrieve Full Name from Master  │
│  3. Get Resignation Date (if resigned)│
│  4. Get Organizational Data         │
│  5. Calculate Match Score           │
└─────────────────────────────────────┘
    ↓
Data Enrichment
    ↓
Result Separation (Matched/Unmatched)
    ↓
Export Generation
```

#### **Performance Optimizations**

1. **Lookup Map Pre-building**
   - Previous Reference data indexed once before processing
   - O(1) lookup time instead of O(n) per record
   - Dictionary-based hash table for fast access

2. **DataFrame Copying**
   - Copies made once at start of processing
   - Prevents modification of original data
   - Enables cancellation without data loss

3. **Progress Tracking**
   - Real-time progress updates
   - Estimated time remaining calculation
   - Non-blocking UI updates using threading

4. **Threading Architecture**
   ```python
   # Main thread: UI updates
   # Worker thread: Data processing
   # Communication: Queue-based updates
   ```

### 4. Data Structures

#### **EmployeeRecord** (Dataclass)
```python
@dataclass
class EmployeeRecord:
    pernr: Optional[str]
    full_name: Optional[str]
    username: Optional[str]
    user_id: Optional[str]
    resignation_date: Optional[str]
    # Organizational fields...
    match_type: Optional[str]
    match_score: Optional[float]
```

#### **EmployeeDataset** (Data Container)
- Manages multiple DataFrames (current, previous, masterlists)
- Handles file path persistence
- Provides data validation methods
- Configures current system report settings

### 5. Excel Export Features

#### **Multi-Sheet Export**
- **Cleaned Data**: All processed records
- **Resigned Users**: Filtered by resignation date
- **Current Users**: Active employees only

#### **Styling & Formatting**
- **Header Row**: Red background (#CD1C18), white text, bold
- **Alternating Rows**: Light peach (#FFF5F3) and white
- **Auto-sized Columns**: Based on content (max 50 chars)
- **Frozen Header**: First row always visible
- **Date Formatting**: MM/DD/YYYY format for resignation dates

### 6. Error Handling & Validation

#### **File Validation**
- Empty file detection
- Corrupted file handling
- Unsupported format detection
- Missing column validation

#### **Data Validation**
- PERNR validity checking (excludes "not found", "n/a", etc.)
- Date format validation
- Missing value handling
- Type conversion safety

#### **User Experience**
- Clear error messages with actionable guidance
- Graceful degradation (fallback strategies)
- Progress cancellation support
- Data persistence across sessions

---

## 🔄 Data Flow Example

### Complete Processing Flow

```
1. USER UPLOADS FILES
   ├─ Current System Report → FileHandler.detect_and_load_excel()
   ├─ Previous Reference → FileHandler.detect_and_load_excel()
   ├─ Masterlist Current → FileHandler.detect_and_load_excel()
   └─ Masterlist Resigned → FileHandler.detect_and_load_excel()
   
2. HEADER DETECTION
   ├─ Search rows 0-15 for valid headers
   ├─ Check for keywords ("Full Name", "PERNR", etc.)
   └─ Handle merged cells if needed
   
3. USER CONFIGURES CLEANUP
   ├─ Selects fuzzy matching option
   ├─ Sets threshold (50-100%)
   └─ Optionally selects custom columns
   
4. PROCESSING STARTS (Thread)
   ├─ For each row in Current System:
   │   ├─ Try User ID → PERNR lookup (Previous Reference)
   │   ├─ If failed: Try exact name match (Masterlists)
   │   ├─ If failed: Try fuzzy name match (if enabled)
   │   ├─ Retrieve Full Name using PERNR
   │   ├─ Get Resignation Date (if resigned)
   │   └─ Get Organizational Data
   └─ Update progress bar
   
5. RESULT GENERATION
   ├─ Cleaned Data: All records with enrichment
   ├─ Unmatched: Records without PERNR
   └─ Fuzzy Matched: Records matched via fuzzy logic
   
6. EXPORT
   ├─ Excel: Multi-sheet with styling
   └─ CSV: Single file export
```

---

## 🎯 Key Algorithms

### 1. **Levenshtein Distance** (Fuzzy Matching)
- **Purpose**: Calculate similarity between two strings
- **Complexity**: O(n*m) where n, m are string lengths
- **Optimization**: C implementation via `python-Levenshtein`

### 2. **Hash Table Lookup** (User ID Matching)
- **Purpose**: Fast PERNR retrieval from Previous Reference
- **Complexity**: O(1) average case
- **Implementation**: Python dictionary with normalized keys

### 3. **Linear Search with Early Exit** (Name Matching)
- **Purpose**: Find employee in masterlist
- **Complexity**: O(n) worst case, O(1) best case (exact match)
- **Optimization**: Exact match checked first, then fuzzy

### 4. **DataFrame Filtering** (Result Separation)
- **Purpose**: Separate matched/unmatched records
- **Complexity**: O(n) where n is number of records
- **Implementation**: Boolean masking with pandas

---

## 🛠️ Development Patterns

### 1. **Dependency Injection**
- Controllers receive main_controller reference
- Views receive controller references
- Enables testing and modularity

### 2. **Observer Pattern**
- Progress updates via callbacks
- UI updates triggered by model changes
- Event-driven architecture

### 3. **Strategy Pattern**
- Matching strategies (exact vs. fuzzy)
- File loading strategies (CSV vs. Excel)
- Export strategies (Excel vs. CSV)

### 4. **Factory Pattern**
- FileHandler creates appropriate readers
- View factory in MainWindow
- Controller initialization

---

## 📊 Performance Characteristics

### Time Complexity
- **File Loading**: O(n) where n = file size
- **Header Detection**: O(rows × columns) for first 15 rows
- **User ID Lookup**: O(1) per record (pre-built map)
- **Name Matching**: O(m) where m = masterlist size
- **Overall Processing**: O(n × m) worst case, O(n) best case

### Space Complexity
- **DataFrames**: O(n × c) where n = rows, c = columns
- **Lookup Maps**: O(m) where m = Previous Reference size
- **Overall**: Linear with input size

### Optimization Strategies
1. **Pre-computation**: Build lookup maps before processing
2. **Early Exit**: Stop searching on exact match
3. **Lazy Evaluation**: Only process visible data in preview
4. **Threading**: Non-blocking UI during processing

---

## 🔐 Data Persistence

### Masterlist Persistence
- **Location**: `%APPDATA%/CBCEmployeeCleanup/masterlist_config.json`
- **Purpose**: Remember masterlist file paths across sessions
- **Format**: JSON with file paths
- **Validation**: Checks file existence before loading

### Session State
- **Current Step**: Tracks user progress (1-4)
- **File Paths**: Stored in EmployeeDataset
- **Configuration**: Header rows, column selections

---

## 🧪 Testing Considerations

### Testable Components
- **Models**: Pure Python, no UI dependencies
- **Matching Engine**: Can test matching algorithms independently
- **File Handler**: Can test file I/O with sample files
- **Data Processing**: Can test with mock DataFrames

### Mock-Friendly Architecture
- Controllers can be tested with mock views
- Models can be tested with mock data
- File operations can be stubbed

---

## 📝 Code Quality Features

### Type Hints
- Extensive use of `typing` module
- `TYPE_CHECKING` for forward references
- Optional types for nullable values

### Error Handling
- Try-except blocks with specific error messages
- Graceful degradation strategies
- User-friendly error messages

### Documentation
- Docstrings for all classes and methods
- Inline comments for complex logic
- Architecture documentation (README_MVC.md)

---

## 🚀 Future Enhancement Opportunities

### Potential Improvements
1. **Database Integration**: Store masterlists in database
2. **Caching**: Cache matching results for repeated processing
3. **Batch Processing**: Process multiple files simultaneously
4. **API Integration**: Connect to HR systems directly
5. **Machine Learning**: Improve matching accuracy with ML models
6. **Cloud Storage**: Support for cloud file storage
7. **Multi-language**: Support for international character sets

---

## 🛠️ Troubleshooting Tips

### File Import Issues
- **"Failed to parse file"**: Verify the file opens in Excel, contains headers, and is not password protected. Re-export CSVs with UTF-8 encoding if characters look garbled.
- **Headers detected incorrectly**: Use `Reselect Current System Header` in the File Upload section to manually pick the header row and key columns. For files with merged headers, save a copy from Excel to flatten merges before uploading.
- **Missing columns (e.g., PERNR column in Previous Reference)**: Confirm all columns are visible by opening the file directly. If columns like Column O are invisible, use `FileHandler.load_file_with_all_columns` via re-uploading to force pandas to read the entire width.

### Matching & Processing Problems
- **No matches found**: Double-check the chosen User ID and Full Name columns from the Cleanup section. Ensure Previous Reference and Masterlists share the same formats (no trailing spaces). Run once with `use fuzzy logic` enabled and threshold set lower (50–60%) to verify matching behavior (`ProcessingController.start_cleanup`).
- **Unexpected fuzzy matches**: Raise the threshold closer to 90%, or temporarily disable fuzzy logic to inspect exact matches only. Use `matching_engine.test_matching()` during debugging to inspect specific name pairs.
- **PERNR values showing decimals**: The export cleans numeric PERNRs in `FileController._format_pernr_value`. If decimals still appear, inspect the source masterlists for mixed types and normalize them before upload.

### UI & Performance
- **App freezes during cleanup**: Processing runs in a background thread, but Windows may mark the window as "Not Responding" for very large datasets. Wait for the progress bar to advance; the log in `ProcessingController` prints detailed status if run from a console.
- **Slow header selection dialog**: Large Excel files may take time to render previews. Save a trimmed version with just the header rows for faster selection, then switch back to the full file.
- **Scrollbar not updating**: Call `main_window.scroll_to_top()` or resize the window; the scroll region throttling (`MainWindow._do_update_scroll_region`) recalculates dimensions on resize.

### Export Errors
- **Excel export fails**: Ensure you have write permissions to the target folder. If the file is open in Excel, close it before exporting. Check that `openpyxl` is installed and matches the Python version (`pip show openpyxl`).
- **CSV looks misaligned in Excel**: Use Excel's `Data > From Text/CSV` import and specify UTF-8. The app exports with `utf-8-sig`, which should work with double-click, but regional settings can interfere.
- **Missing data in export sheets**: Confirm `ProcessingController.finalize_processing` produced non-empty `cleaned_data`, `unmatched_data`, and `fuzzy_matched_data`. The exporter writes empty headers if a sheet is empty; inspect the cleaned dataset in Preview before exporting.

### Environment & Dependency Checks
- Run `pip install -r requirements.txt` inside the `venv` to ensure pandas/openpyxl/fuzzywuzzy are consistent.
- If tkinter is missing (Linux servers), install via the system package manager (`sudo apt-get install python3-tk`).
- When bundling with PyInstaller, include the `python-Levenshtein` wheel to keep fuzzy matching fast; missing this dependency dramatically increases processing time.

Keep a console open when launching `python main.py`; stack traces and debug logs from controllers provide immediate hints about missing columns or misconfigured headers.

---

## 📚 Additional Resources

- **pandas Documentation**: https://pandas.pydata.org/
- **fuzzywuzzy Documentation**: https://github.com/seatgeek/fuzzywuzzy
- **tkinter Documentation**: https://docs.python.org/3/library/tkinter.html
- **openpyxl Documentation**: https://openpyxl.readthedocs.io/

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Maintained by**: Chinabank Corporation Development Team

