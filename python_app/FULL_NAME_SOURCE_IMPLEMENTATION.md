# Full Name Source Tracking - Implementation Guide

## Overview

The system now tracks **where each employee's full name was retrieved from** by adding a new `Full Name Source` column to all output datasets. This provides complete data lineage and transparency about the matching process.

## What's New

### New Column: "Full Name Source"

**Location**: Added to all cleaned data output files  
**Possible Values**:
- `"Current Masterlist"` - Full name was found in the current employees masterlist
- `"Resigned Masterlist"` - Full name was found in the resigned employees masterlist
- `None` - Full name could not be found in any masterlist

## How It Works

### Data Flow with Source Tracking

```
┌─────────────────────────────────────────────────────────────────┐
│                    Process Each Employee Record                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │ Step 1: Lookup PERNR by      │
                │         User ID              │
                └──────────────────────────────┘
                              │
                         ┌────┴─────┐
                         │           │
                    ✓ Found      ✗ Not Found
                         │           │
                         ▼           ▼
                 Continue    ┌─────────────────────────┐
                             │ Step 2: Name Matching   │
                             └─────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
              Found in Current   Found in Resigned   Not Found
                    │                │                │
                    ▼                ▼                ▼
            source =            source =         Continue to
            "Current            "Resigned        Step 3
            Masterlist"         Masterlist"
                    │                │
                    └────────┬───────┘
                             │
                             ▼
              ┌──────────────────────────────────┐
              │ Step 3: PERNR-based Lookup       │
              │ (if PERNR found but name missing)│
              └──────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
        Found in Current   Found in Resigned   Not Found
           │                 │                 │
           ▼                 ▼                 ▼
       source =          source =         source = None
       "Current          "Resigned
       Masterlist"       Masterlist"
           │                 │
           └────────┬────────┘
                    │
                    ▼
       ┌─────────────────────────────────┐
       │ Record Saved with Source Info   │
       └─────────────────────────────────┘
```

### Step-by-Step Tracking

#### Step 1: User ID Lookup (from Previous Reference)
- PERNR found from previous reference
- **No source tracking needed** (PERNR, not full name)
- If full name still missing, proceed to Step 3

#### Step 2: Name Matching (Primary Lookup)
```python
# Try Current Masterlist first
if full_name found:
    full_name_source = "Current Masterlist"

# If not found, try Resigned Masterlist
elif full_name found:
    full_name_source = "Resigned Masterlist"
```

#### Step 3: PERNR-Based Lookup (Secondary Lookup)
Only runs if PERNR exists but full name is still missing
```python
full_name, source = get_full_name_from_pernr(
    employee_number,
    masterlist_current_df,
    masterlist_resigned_df
)
# Returns one of:
# - (full_name, "Current Masterlist")
# - (full_name, "Resigned Masterlist")
# - (None, None)
```

## Implementation Details

### Modified Methods

#### 1. `initialize_new_columns()` (Line 158-167)
Added new column to the list:
```python
new_columns = [
    'PERNR', 
    'Full Name (From Masterlist)', 
    'Full Name Source',  # ← NEW
    'Resignation Date',
    ...
]
```

#### 2. `get_full_name_from_pernr()` (Line 216-282)
**Changed signature** to return both name and source:
```python
def get_full_name_from_pernr(...) -> Tuple[Optional[str], Optional[str]]:
    """Returns: (full_name, source)"""
    # Returns:
    # - (full_name, "Current Masterlist")
    # - (full_name, "Resigned Masterlist")
    # - (None, None)
```

#### 3. `cleanup_worker()` (Line 54-127)
**Added source tracking variable**:
```python
for idx, row in current_df.iterrows():
    full_name = None
    full_name_source = None  # ← NEW: Track where name came from
    
    # During name matching
    if full_name is not None:
        full_name_source = "Current Masterlist"  # or "Resigned Masterlist"
    
    # During PERNR lookup
    full_name, full_name_source = get_full_name_from_pernr(...)
```

#### 4. `update_employee_record()` (Line 409-421)
**Added parameter and field assignment**:
```python
def update_employee_record(self, df, idx, employee_number, 
                          full_name, full_name_source,  # ← NEW parameter
                          resignation_date, ...):
    df.at[idx, 'Full Name Source'] = full_name_source  # ← NEW: Store source
```

## Usage Examples

### Example 1: Name Found in Current Masterlist
| User ID | PERNR | Full Name (From Masterlist) | Full Name Source |
|---------|-------|---------------------------|------------------|
| emp001  | 1001  | John Smith | **Current Masterlist** |

### Example 2: Name Found in Resigned Masterlist
| User ID | PERNR | Full Name (From Masterlist) | Full Name Source |
|---------|-------|---------------------------|------------------|
| emp002  | 2002  | Jane Doe | **Resigned Masterlist** |

### Example 3: Name Not Found
| User ID | PERNR | Full Name (From Masterlist) | Full Name Source |
|---------|-------|---------------------------|------------------|
| emp003  | 3003  | (empty) | **(empty)** |

### Example 4: PERNR from Previous Reference, Name from Resigned Masterlist
| User ID | PERNR | Full Name (From Masterlist) | Full Name Source |
|---------|-------|---------------------------|------------------|
| emp004  | 4004  | Robert Johnson | **Resigned Masterlist** |
| (PERNR looked up from previous ref, name looked up via PERNR in resigned list) |||

## Benefits

1. **Data Lineage** - Know exactly where each data point originated
2. **Quality Control** - Identify if data came from expected source
3. **Auditing** - Track which masterlist was used for each employee
4. **Troubleshooting** - Help debug data quality issues
5. **Validation** - Verify matching process worked correctly

## Testing Checklist

- [ ] Verify "Full Name Source" column appears in output files
- [ ] Check that "Current Masterlist" appears when name is found in current list
- [ ] Check that "Resigned Masterlist" appears when name is found in resigned list
- [ ] Verify empty source when full name is not found
- [ ] Test with employees matched by User ID (PERNR from previous ref)
- [ ] Test with employees matched by name matching
- [ ] Test with employees matched by PERNR lookup
- [ ] Verify source is populated for mixed scenarios

## Code Changes Summary

| File | Changes | Lines |
|------|---------|-------|
| `processing_controller.py` | Added source tracking throughout | 58, 100-109, 113-115, 161, 415 |
| - | Modified method signature | 216 (return Tuple) |
| - | Modified method return statements | 243, 273 |
| - | Added parameter to update_employee_record | 410 |

## Backward Compatibility

✅ **Fully backward compatible**
- Existing code continues to work
- New column is optional (can be ignored)
- No breaking changes to API signatures

## Future Enhancements

Possible future improvements:
- Add "Match Confidence" source tracking
- Track multiple data sources per field
- Generate source summary reports
- Add filtering/sorting by source in UI

