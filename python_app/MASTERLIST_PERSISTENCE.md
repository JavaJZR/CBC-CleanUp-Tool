# Masterlist Persistence - Implementation Guide

## Feature: Persistent Masterlist Files with Update Option

### Date: October 25, 2025
### Status: ✅ COMPLETE

---

## Overview

The system now treats **Masterlist – Current** and **Masterlist – Resigned** as **persistent reference files** that don't need to be re-uploaded for each cleanup session. Users can:

- ✅ See which masterlist files are currently loaded
- ✅ Update masterlists only when needed
- ✅ Keep masterlists loaded across multiple app sessions (files are saved)
- ✅ Automatically load previously uploaded masterlists on app startup
- ✅ Only upload the changing files (Current System Report, Previous Reference)

---

## What Changed

### Files Modified:

#### 1. `python_app/models/employee_data.py`
- Added `load_persisted_masterlists()` method to automatically load saved masterlist files
- Masterlist file paths are saved to `masterlist_config.json` when uploaded
- Files are automatically loaded on app startup if they still exist
- Updated `clear_all_data()` to also clear persisted paths

#### 2. `python_app/controllers/main_controller.py`
- Added `load_persisted_masterlists()` method to call file loading after initialization
- Added `update_ui_with_persisted_files()` to update UI with loaded files
- App automatically loads saved masterlists when starting

#### 3. `python_app/views/file_upload_view.py`

**Enhanced Upload Cards for Masterlists:**
1. Masterlist cards show "🔄 Update" button instead of "📁 Upload"
2. File name is displayed for reference when loaded
3. Users can see what masterlist version is being used
4. Update button allows changing masterlists when needed

**Behavior:**
- **First upload**: Button shows "🔄 Update" (indicating it's a masterlist)
- **After upload**: File name appears showing what's loaded and path is saved
- **Subsequent app sessions**: Files are automatically loaded from saved paths
- **Update option**: Users can upload a new version when masterlist changes

---

## User Experience

### Initial Session
```
File Upload Section:
├─ Current System Report: [📁 Upload] ← Upload each time
├─ Previous Reference: [📁 Upload] ← Upload each time
├─ Masterlist – Current: [🔄 Update] ← Upload once, then update only when needed
└─ Masterlist – Resigned: [🔄 Update] ← Upload once, then update only when needed
```

### After First Upload
```
File Upload Section:
├─ Current System Report: [📁 Upload]
│   ✓ current_report_2025.xlsx (1,250 rows, 15 columns)
├─ Previous Reference: [📁 Upload]
│   ✓ previous_ref_2024.xlsx (980 rows, 12 columns)
├─ Masterlist – Current: [🔄 Update]
│   ✓ masterlist_current_2025.xlsx (5,200 rows, 20 columns) ← Persistent
└─ Masterlist – Resigned: [🔄 Update]
    ✓ masterlist_resigned_2025.xlsx (1,800 rows, 18 columns) ← Persistent
```

### Typical Workflow

**Session 1:**
1. Upload Current System Report
2. Upload Previous Reference
3. Upload Masterlist – Current (once)
4. Upload Masterlist – Resigned (once)
5. Run cleanup

**Session 2 (Next Month - App Restarted):**
1. **App starts**: Masterlist files are automatically loaded from saved paths
2. Upload NEW Current System Report (changed)
3. Upload NEW Previous Reference (changed)
4. Masterlist – Current: Shows "masterlist_current_2025.xlsx" (already loaded automatically)
5. Masterlist – Resigned: Shows "masterlist_resigned_2025.xlsx" (already loaded automatically)
6. Run cleanup (uses existing masterlists)

**Session 3 (Masterlist Updated):**
1. Upload NEW Current System Report
2. Upload NEW Previous Reference
3. Click "🔄 Update" on Masterlist – Current to upload new version
4. Masterlist – Resigned: Still shows old file (no update needed)
5. Run cleanup

---

## Benefits

✅ **Improved Workflow**
- Don't re-upload unchanged masterlists every time
- Only upload files that actually change
- Faster setup for recurring cleanup sessions

✅ **Clear File Management**
- See which masterlist version is loaded
- Easy to identify when masterlists need updating
- File names shown for reference

✅ **Better UX**
- "Update" button clearly indicates masterlists are persistent
- Users understand which files are references vs. data files
- Reduces user confusion about what to upload

✅ **Time Savings**
- Skip uploading masterlists for each cleanup
- Focus on the data files that change
- Streamlined process

---

## Technical Implementation

### File Persistence

**File Path Storage (`masterlist_config.json`):**
```json
{
  "masterlist_current": "C:/path/to/masterlist_current.xlsx",
  "masterlist_resigned": "C:/path/to/masterlist_resigned.xlsx"
}
```

**Automatic Loading on Startup:**
```python
# In EmployeeDataset class
def load_persisted_masterlists(self, file_handler) -> bool:
    """Load persisted masterlist files if they exist"""
    # Check if paths exist and load the files
    # Return True if any files were loaded successfully
```

**Controller Initialization:**
```python
# In MainController class
def initialize(self):
    # ... setup views and controllers ...
    
    # Load persisted masterlist files if they exist
    self.load_persisted_masterlists()
```

### Button Text Logic

```python
# Check if file type is a masterlist
is_masterlist = key in ['masterlist_current', 'masterlist_resigned']

# Set button text
button_text = "🔄 Update" if is_masterlist else "📁 Upload"
```

### UI Updates

**On File Upload:**
```python
def update_file_card(self, file_type, file_name, row_count, col_count):
    # Update file label with filename
    card.file_label.config(
        text=f"✓ {file_name}\n({row_count} rows, {col_count} columns)",
        fg="#059669"
    )
    
    # Update button text for masterlists
    if card.is_masterlist:
        card.upload_btn.config(text="🔄 Update")
```

**On App Startup:**
```python
def update_ui_with_persisted_files(self):
    """Update UI to show persisted masterlist files"""
    for file_type in ['masterlist_current', 'masterlist_resigned']:
        file_path = self.employee_dataset.file_paths.get(file_type)
        if file_path:
            # Update UI card to show loaded file
            self.main_window.file_upload_view.update_file_card(...)
```

---

## File Categories

### Changing Files (Upload Each Time)
- **Current System Report**: New data to process each session
- **Previous Reference**: Historical data for lookups

### Persistent Files (Update Only When Changed)
- **Masterlist – Current**: Reference list of active employees
- **Masterlist – Resigned**: Reference list of resigned employees

---

## Summary

The masterlist persistence feature improves workflow by:

✅ **Clearer UI**: "Update" button indicates persistent files  
✅ **Better UX**: See which masterlist version is loaded  
✅ **Automatic Loading**: Files are automatically loaded on app startup  
✅ **Persistent Storage**: File paths saved in `masterlist_config.json`  
✅ **Time Savings**: Don't re-upload unchanged files  
✅ **Flexibility**: Still easy to update when needed  
✅ **Professional**: File names shown for reference  
✅ **Selective Clearing**: "Clear System Reports" button clears only data files, keeps masterlists  

This makes the tool more efficient for regular users who process multiple cleanup sessions with the same masterlist references. The masterlist files are saved and automatically loaded when you restart the app, so you only need to upload them once or when they change.

### Clearing Options

- **🗑️ Clear System Reports**: Clears only Current System Report and Previous Reference, keeps masterlists loaded
- **🗑️ Clear All Files**: Clears everything including masterlists (full reset)

---

**Implementation Date**: October 25, 2025  
**Last Updated**: January 2025 (Added automatic file loading on startup)  
**Status**: ✅ Production Ready  
**Version**: 1.2.0 (Automatic Persistence)


