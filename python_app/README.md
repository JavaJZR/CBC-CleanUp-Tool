# Employee Data Clean-Up Tool (Python Desktop Version)

A Python desktop application for cleaning and reconciling employee data across multiple sources, built for Chinabank Corporation.

## 🎯 Features

- **Multi-File Upload**: Support for Excel (.xlsx, .xls) and CSV files
- **Data Preview**: Review uploaded files before processing
- **Fuzzy Matching**: Intelligent record matching with configurable threshold
- **Data Export**: Export cleaned and unmatched data to Excel or CSV
- **User-Friendly GUI**: Built with Tkinter for easy desktop use
- **Progress Tracking**: Real-time progress updates during cleanup

## 📋 Prerequisites

- Python 3.8 or higher
- tkinter (usually comes pre-installed with Python)

### Installing tkinter (if needed)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-tk
```

**Linux (Fedora):**
```bash
sudo dnf install python3-tkinter
```

**macOS & Windows:**
tkinter should be included with your Python installation.

## 🚀 Installation

1. **Clone or download this directory**

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
```

3. **Activate the virtual environment:**

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

4. **Install required packages:**
```bash
pip install -r requirements.txt
```

## 🎮 Usage

1. **Run the application:**
```bash
python employee_cleanup_tool.py
```

2. **Follow the 4-step process:**

### Step 1: Upload Files
- Click "📁 Upload" on each card to select your files
- **Required files:**
  - Current System Report (latest employee data)
  - Masterlist – Current (active employees reference)
- **Optional files:**
  - Previous Reference (historical data)
  - Masterlist – Resigned (former employees)

### Step 2: Preview Data
- Use the dropdown to select which file to preview
- Verify data structure and content
- Click "Continue to Clean-Up" when ready

### Step 3: Configure & Run Clean-Up
- Adjust the fuzzy match threshold (50-100%)
  - Higher % = more strict matching
  - Default: 80%
- Click "🚀 Run Clean-Up Process"
- Monitor progress bar and status messages

### Step 4: Export Results
- **Cleaned Report**: Successfully matched records
- **Unmatched for Review**: Records needing manual attention
- Export each dataset to Excel or CSV format

## 📊 Supported File Formats

- **Excel**: `.xlsx`, `.xls`
- **CSV**: `.csv`
- **Maximum file size**: Limited by available memory

## 🔧 How It Works

1. **File Parsing**: Reads Excel and CSV files using pandas
2. **Fuzzy Matching**: Uses fuzzywuzzy library to match records based on text similarity
3. **Threshold Filtering**: Only matches above the configured threshold are considered valid
4. **Result Separation**: Splits data into matched (cleaned) and unmatched records
5. **Export**: Saves results to user-specified location

## 📝 File Requirements

Your uploaded files should have:
- Column headers in the first row
- Employee information (ID, Name, Department, etc.)
- Clean, readable text (not corrupted or password-protected)

## ⚠️ Important Notes

- **Data Privacy**: This tool processes employee data. Ensure proper authorization and follow data privacy guidelines.
- **Backup**: Always keep backups of your original files
- **Review**: Manually review unmatched records to ensure data quality
- **Performance**: Large files (>100,000 rows) may take several minutes to process

## 🐛 Troubleshooting

### "No module named 'tkinter'" error
- Install tkinter for your operating system (see Prerequisites)

### "Failed to parse file" error
- Ensure file is not corrupted
- Check that file is not password-protected
- Verify file has column headers in first row
- Try opening file in Excel to check for issues

### Slow performance
- Reduce file size by splitting large datasets
- Close other resource-intensive applications
- Lower the match threshold for faster processing

### Application freezes during cleanup
- This is normal for large datasets
- Wait for the progress bar to complete
- Avoid clicking buttons during processing

## 🔄 Differences from Web Version

This Python desktop version provides:
- ✅ Standalone application (no web server needed)
- ✅ Works offline
- ✅ Direct file system access
- ✅ Native OS file dialogs
- ❌ No browser required
- ❌ Single-user (not multi-user like web apps)

## 📚 Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical operations
- **openpyxl**: Excel file support (.xlsx)
- **xlrd**: Older Excel file support (.xls)
- **fuzzywuzzy**: Fuzzy string matching
- **python-Levenshtein**: Performance optimization for fuzzy matching
- **tkinter**: GUI framework (built-in)

## 🆘 Support

For issues or questions:
1. Check that all requirements are installed correctly
2. Verify your Python version (3.8+)
3. Review the troubleshooting section above
4. Check file format and structure

## 📄 License

Internal use only - Chinabank Corporation

## 🏦 About

**Employee Data Clean-Up Tool**  
Chinabank Corporation Internal System  
Version: 1.0.0  
Platform: Python Desktop Application

---

**Made with ❤️ for Chinabank Corporation**

