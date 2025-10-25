# How PERNR Retrieval Works

## Overview
The PERNR (Employee Number) retrieval system uses a multi-step approach to find employee numbers from user data. It starts with the fastest method (User ID lookup) and falls back to name matching if needed.

## Step-by-Step Process

### Step 1: User ID Lookup (Fastest Method) ⚡

**When**: Previous Reference file is provided and user has a User ID

**How it works**:
1. Looks for User ID column in Current System Report
2. Looks for matching User ID in Previous Reference file
3. Retrieves the corresponding PERNR from Previous Reference
4. Validates that PERNR is not "cant find", "unknown", etc.

**Example**:
```
Current System Report:
┌──────────┬──────────────────────────┐
│ User ID  │ Username (Full Name)      │
├──────────┼──────────────────────────┤
│ USER001  │ jdoe John Doe            │
└──────────┴──────────────────────────┘

Previous Reference:
┌──────────┬────────┐
│ User ID  │ PERNR  │
├──────────┼────────┤
│ USER001  │ 1001   │
└──────────┴────────┘

Result: PERNR = 1001 (from User ID lookup)
```

**Code Flow**:
```python
# Step 1: Lookup PERNR by User ID from previous_reference
if has_previous_reference and user_id_current and user_id_previous and pernr_previous:
    user_id = row.get(user_id_current)  # Get User ID from current row
    if pd.notna(user_id):
        match = previous_df[previous_df[user_id_previous] == user_id]  # Find match
        if not match.empty:
            pernr_value = match.iloc[0][pernr_previous]  # Get PERNR
            
            # Validate PERNR
            if self.main_controller.matching_engine.is_valid_pernr(pernr_value):
                employee_number = str(pernr_value).strip()
                match_type = "user_id_match"
                match_score = 100.0
```

**Advantages**:
- ✅ Fastest method (direct lookup)
- ✅ 100% accurate when available
- ✅ No ambiguity
- ✅ Perfect match score

---

### Step 2: Name Matching (Fallback Method) 🔍

**When**: User ID lookup fails OR no Previous Reference provided

**How it works**:
1. Extracts name from Current System Report (Username/Full Name column)
2. Searches Masterlist Current for matching name
3. If not found, searches Masterlist Resigned
4. Uses exact match first, then fuzzy match if enabled

**Example**:
```
Current System Report:
┌──────────────────────────┐
│ Username (Full Name)     │
├──────────────────────────┤
│ jdoe John Doe            │
└──────────────────────────┘

Masterlist Current:
┌────────┬──────────────────┐
│ PERNR  │ Full Name         │
├────────┼──────────────────┤
│ 1001   │ John Doe          │
└────────┴──────────────────┘

Result: PERNR = 1001 (from name matching)
```

**Match Methods**:

#### A. Exact Match (Priority 1)
- Case-insensitive comparison
- Strips whitespace
- Direct column comparison
- Returns 100% match score

**Code**:
```python
for idx, row in masterlist_df.iterrows():
    masterlist_name = str(row[name_col]).strip().lower()
    if current_name_clean == masterlist_name:
        emp_num = pd.to_numeric(row[emp_num_col], errors='coerce')
        return str(int(emp_num)), str(row[name_col]), "exact_match", 100.0
```

#### B. Fuzzy Match (Priority 2)
- Only if exact match fails AND fuzzy logic is enabled
- Uses multiple scoring methods:
  - **Ratio**: Overall similarity
  - **Partial Ratio**: Best matching substring
  - **Name Order Score**: Handles reversed names
- Returns the highest score
- Must meet threshold (default 80%)

**Example Names**:
```
"John Doe" vs "Jon Doe" → 94% similarity
"Jared Ranjo" vs "Ranjo, Jared" → Name order handling
"María García" vs "Maria Garcia" → Handles accents
```

**Code**:
```python
if self.use_fuzzy_logic:
    for idx, row in masterlist_df.iterrows():
        masterlist_name = str(row[name_col]).strip()
        
        # Calculate multiple similarity scores
        score = fuzz.ratio(current_name_clean, masterlist_name_clean)
        partial_score = fuzz.partial_ratio(current_name_clean, masterlist_name_clean)
        name_order_score = self._calculate_name_order_score(current_name_clean, masterlist_name_clean)
        
        # Use highest score
        final_score = max(score, partial_score, name_order_score)
        
        # Check if meets threshold
        if final_score >= self.threshold:
            return best_employee_number, best_full_name, "fuzzy_match", final_score
```

**Fuzzy Match Scoring**:
- `fuzz.ratio()`: Overall similarity between strings
- `fuzz.partial_ratio()`: Best matching substring
- `_calculate_name_order_score()`: Handles name order variations

**Threshold Control**:
- Default: 80%
- User adjustable: 50-100%
- Higher = more strict matching
- Lower = more lenient matching

---

## Column Detection

### How the System Finds Columns

**User ID Detection** (in Current System and Previous Reference):
```python
# Exact match first
exact_match = [col for col in current_df.columns if col == 'User ID']

# Flexible matching
flexible_match = [col for col in current_df.columns 
                 if any(keyword in str(col).lower() for keyword in 
                       ['user', 'id', 'sysid', 'username', 'abbreviation'])]
```

**Supported User ID Column Names**:
- "User ID" (exact match)
- "User Abbreviation"
- "SysID"
- "Username"
- "User Abbr"
- Any column containing these keywords

**PERNR Detection** (in Masterlists):
```python
# Prioritize exact match
emp_num_columns = [col for col in masterlist_df.columns if str(col).upper() == 'PERNR']

# Fallback to alternatives
if not emp_num_columns:
    emp_num_columns = [col for col in masterlist_df.columns if col == 'Pers. Number']
```

**Supported PERNR Column Names**:
- "PERNR" (exact match)
- "Pers. Number"
- "Employee Number"
- Columns containing "employee" and "number"

**Name Detection** (in Masterlists):
```python
# Prioritize "Full Name"
name_columns = [col for col in masterlist_df.columns if col == 'Full Name']

# Fallback to flexible matching
if not name_columns:
    name_columns = [col for col in masterlist_df.columns if 'name' in str(col).lower()]
```

**Supported Name Column Names**:
- "Full Name" (prioritized)
- "Name"
- "Employee Name"
- Any column containing "name"

---

## Complete Flow Diagram

```
START
  │
  ├─ Previous Reference provided?
  │   │
  │   YES ──→ Step 1: User ID Lookup
  │   │           │
  │   │           ├─ User ID found in Current System?
  │   │           │   │
  │   │           │   YES ──→ Match in Previous Reference?
  │   │           │   │           │
  │   │           │   │           YES ──→ PERNR found! ✅
  │   │           │   │           │           │
  │   │           │   │           NO          │
  │   │           │   │           │           │
  │   │           │   NO          │           │
  │   │           │   │           │           │
  │   │           └───┴───────────┴───────────┘
  │   │
  │   NO  (or PERNR not found)
  │   │
  └───┴───────────────────────────────────────┘
                                          │
                                          ↓
                            Step 2: Name Matching
                                          │
                                          ├─ Try Masterlist Current
                                          │       │
                                          │       ├─ Exact Match?
                                          │       │   │
                                          │       │   YES ──→ PERNR found! ✅
                                          │       │   │
                                          │       │   NO ──→ Fuzzy Match?
                                          │       │           │
                                          │       │           YES ──→ Score ≥ Threshold?
                                          │       │                       │
                                          │       │                       YES ──→ PERNR found! ✅
                                          │       │                       │
                                          │       │                       NO ──→ Continue...
                                          │       │
                                          │       Not found? ──→ Try Masterlist Resigned
                                          │                             │
                                          │                             ├─ Exact Match?
                                          │                             │   │
                                          │                             │   YES ──→ PERNR found! ✅
                                          │                             │   │
                                          │                             │   NO ──→ Fuzzy Match?
                                          │                             │           │
                                          │                             │           YES ──→ Score ≥ Threshold?
                                          │                             │                       │
                                          │                             │                       YES ──→ PERNR found! ✅
                                          │                             │                       │
                                          │                             │                       NO ──→ No match ❌
                                          │                             │
                                          └─────────────────────────────┘
```

---

## Example Scenarios

### Scenario 1: Perfect Match with User ID
```
Current System: User ID = "USER001"
Previous Reference: USER001 → PERNR 1001
Result: PERNR = 1001, Match Type = "user_id_match", Score = 100%
```

### Scenario 2: Name Match - Exact
```
Current System: Username = "John Doe"
Masterlist Current: Full Name = "John Doe"
Result: PERNR = 1001, Match Type = "exact_match", Score = 100%
```

### Scenario 3: Name Match - Fuzzy
```
Current System: Username = "John Doe"
Masterlist Current: Full Name = "Jon Doe"
Fuzzy Logic: Enabled, Threshold = 80%
Result: PERNR = 1001, Match Type = "fuzzy_match", Score = 94%
```

### Scenario 4: No Match
```
Current System: Username = "John Doe"
Masterlist Current: Full Name = "Jane Smith"
Masterlist Resigned: Full Name = "Bob Johnson"
Result: PERNR = None, Match Type = "no_match", Score = 0%
```

---

## Key Features

### Multi-Source Lookup
1. Try Masterlist Current first (active employees)
2. Try Masterlist Resigned if not found (former employees)
3. Ensures complete coverage

### Flexible Column Detection
- Automatically finds columns with various names
- Case-insensitive matching
- Keyword-based detection

### Multiple Matching Strategies
1. **User ID Lookup**: Fastest, most accurate
2. **Exact Name Match**: 100% accuracy for identical names
3. **Fuzzy Name Match**: Handles variations, typos, formatting differences

### Validation
- Checks PERNK values are not "cant find", "unknown", etc.
- Converts to consistent string format
- Handles numeric and text PERNRs

### Tracking
- Records match type (user_id_match, exact_match, fuzzy_match, no_match)
- Stores match score (0-100%)
- Enables data quality analysis

---

## Performance Notes

- **User ID Lookup**: O(1) per row (direct dictionary-like lookup)
- **Exact Match**: O(n) per row (linear search through masterlist)
- **Fuzzy Match**: O(n) per row × similarity calculations
- **Overall**: Optimized for speed while maintaining accuracy

The system prioritizes speed by using the fastest method first (User ID lookup) and only falling back to slower methods (name matching) when necessary.

