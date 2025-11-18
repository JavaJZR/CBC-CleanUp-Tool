# Employee Data Clean-Up Tool - Glossary of Terms

## Overview
This document defines key terms and concepts used in the Employee Data Clean-Up Tool to help users understand the application's functionality.

---

## Core Concepts

### **Lookup**
The process of finding matching employee records between different data sources (Current System Report, Previous Reference, and Masterlists) to retrieve missing information like PERNR, Full Names, and organizational data.

**Example:** When the app looks up a PERNR for an employee by matching their User ID from the Current System Report with the Previous Reference file.

---

### **Lookup Value / User ID**
A unique identifier **used to search for** employees across different data sources. This is the **input** or **search key** you use to find matching records.

**Examples:**
- Employee ID/Name
- User Abbreviation
- Username
- System ID (SysID)
- Any column that uniquely identifies an employee

**Role:** The lookup value is what you **USE** to find the PERNR.

**Note:** Different systems may use different column names for User IDs (e.g., "Employee Nbme", "User ID", "Abbreviation"). The Custom Column Selection feature allows you to specify which column to use.

---

### **PERNR (Personnel Number)**
A unique employee identification number assigned to each employee. This is the **target value** or **lookup result** you're trying to **retrieve**.

**Relationship to Lookup Value:**
- **Lookup Value (User ID)** = What you **USE** to search (the input)
- **PERNR** = What you're **LOOKING FOR** (the output/result)

**Once PERNR is found, it serves as the primary key to:**
- Retrieve Full Names from Masterlists
- Look up Resignation Dates
- Find Organizational Data (Position, Segment, Group, etc.)

**Format:** Typically an 8-digit number (e.g., 56003085), but can also be text values in some systems.

**Analogy:** Think of User ID as the "question" and PERNR as the "answer" - you use the User ID to find the corresponding PERNR.

---

## Data Sources

### **Current System Report**
The latest employee data file that needs to be enriched with PERNRs, Full Names, and other information. This is the primary file you're cleaning up.

**Required:** Yes  
**Purpose:** Contains the employee records that need PERNRs and additional data added to them.

---

### **Previous Reference**
A historical employee data file that contains User ID to PERNR mappings. This file is used for faster PERNR lookup when User IDs match between the Current System Report and Previous Reference.

**Required:** Optional (but recommended for faster processing)  
**Purpose:** Provides a mapping between User IDs and PERNRs to speed up the lookup process.

**How it works:** If an employee's User ID in the Current System Report matches their User ID in the Previous Reference, the app can immediately retrieve their PERNR without needing to search through Masterlists.

---

### **Masterlist – Current**
A reference file containing active employees with their PERNRs, Full Names, and organizational data.

**Required:** Yes  
**Purpose:** 
- Provides Full Names for employees when PERNR is found
- Supplies organizational data (Position, Segment, Group, Area/Division, Department/Branch)
- Used for name-based matching when User ID lookup fails

---

### **Masterlist – Resigned**
A reference file containing resigned employees with their PERNRs, Full Names, and Resignation Dates.

**Required:** Yes  
**Purpose:**
- Provides Full Names for resigned employees
- Contains Resignation Dates for employees who have left the company
- Used for name-based matching when User ID lookup fails

---

## Lookup Process

### **User ID Lookup**
The primary lookup method that matches employees by their User ID between the Current System Report and Previous Reference.

**Process:**
1. Extract User ID from Current System Report
2. Search for matching User ID in Previous Reference
3. If found, retrieve the corresponding PERNR
4. Use PERNR to get Full Name and other data from Masterlists

**Advantage:** Fast and accurate when User IDs are consistent across systems.

---

### **Name Matching (Fallback)**
A secondary lookup method used when User ID lookup fails or no Previous Reference is provided. Matches employees by comparing names between the Current System Report and Masterlists.

**Process:**
1. Extract Full Name/Username from Current System Report
2. Search for matching name in Masterlists (Current, then Resigned)
3. If found, retrieve PERNR and other associated data

**Types:**
- **Exact Match:** Names must match exactly
- **Fuzzy Match:** Names can have slight variations (typos, abbreviations, etc.)

---

### **Fuzzy Matching**
An intelligent matching algorithm that finds employees even when names have slight variations, typos, or formatting differences.

**How it works:**
- Compares names using similarity algorithms
- Assigns a match score (0-100%) indicating how similar names are
- Only matches if similarity is above the threshold (default: 80%)

**Example:** "John Smith" can match "John A. Smith" or "Jon Smith" if similarity is high enough.

**Settings:**
- **Threshold:** Adjustable from 0-100% (default: 80%)
- **Enable/Disable:** Can be turned off for exact matching only

---

## Column Selection

### **Header Row**
The row number in your Excel/CSV file that contains the column names (headers). Headers may not always be in the first row.

**Example:** If your file has company information in rows 1-2 and actual column headers in row 3, you would select "Row 3" as the header row.

---

### **Custom Column Selection**
A feature that allows you to manually specify which columns to use for User ID matching, instead of relying on automatic detection.

**When to use:**
- Your system uses non-standard column names (e.g., "Employee Nbme" instead of "User ID")
- Automatic detection selects the wrong columns
- You want precise control over the matching process

**Columns you can specify:**
- **Current System Report - User ID Column:** The column in your current report that contains employee identifiers
- **Previous Reference - User ID Column:** The column in the previous reference that contains matching identifiers
- **Previous Reference - PERNR Column:** The column in the previous reference that contains PERNR values

---

### **Full Name Column**
The column in the Current System Report that contains employee names. Used for name-based matching when User ID lookup fails.

**Common names:** "Full Name", "Name", "Username", "User Description", "Description"

---

## Match Results

### **Match Type**
Indicates how the PERNR was found for an employee record.

**Types:**
- **user_id_match:** Found via User ID lookup from Previous Reference
- **fuzzy_match:** Found via fuzzy name matching
- **exact_match:** Found via exact name matching
- **no_match:** PERNR could not be found

---

### **Match Score**
A percentage (0-100%) indicating how confident the match is. Higher scores indicate more reliable matches.

**Interpretation:**
- **100%:** Perfect match (usually from User ID lookup)
- **80-99%:** Very good match (fuzzy matching with high confidence)
- **50-79%:** Moderate match (may need review)
- **Below 50%:** Low confidence match (likely incorrect)

---

## Output Data

### **Enriched Data**
The final cleaned dataset with all available information added:
- PERNR (if found)
- Full Name (from Masterlist)
- Resignation Date (if applicable)
- Organizational Data (Position, Segment, Group, Area/Division, Department/Branch)
- Match Type and Match Score

---

### **Resigned Users**
Employees who have a valid Resignation Date in the output. These are separated into their own sheet in Excel exports.

**Note:** Only actual dates (MM/DD/YYYY format) are considered. Status values like "ACTIVE", "EXTENDED", or "WITH NEW PERNR" are not treated as resignation dates.

---

### **Current Users**
Active employees who do not have a Resignation Date. These are separated into their own sheet in Excel exports.

---

### **Missing PERNRs**
Employee records where no PERNR could be found through any lookup method. These require manual review or additional data sources.

---

## Organizational Data

Information about an employee's position and organizational structure, retrieved from the Current Masterlist:

- **Position Name:** Job title or position
- **Segment Name:** Business segment
- **Group Name:** Organizational group
- **Area/Division Name:** Area or division
- **Department/Branch:** Department or branch location

---

## Technical Terms

### **Data Persistence**
The ability of the app to remember uploaded Masterlist files between sessions. Once you upload Masterlists, they are saved and automatically loaded the next time you open the app.

**Location:** Stored in `%APPDATA%\CBCEmployeeCleanup\masterlist_config.json`

---

### **Cross-Session Persistence**
The feature that saves your Masterlist file paths so you don't need to re-upload them every time you use the app.

---

## Quick Reference

| Term | Definition |
|------|------------|
| **Lookup** | Finding matching records between data sources |
| **User ID (Lookup Value)** | Input/search key used to find employees (e.g., Employee ID, Username) |
| **PERNR (Lookup Result)** | Target value/result - Personnel Number retrieved from lookup |
| **Previous Reference** | Historical file with User ID → PERNR mappings |
| **Masterlist** | Reference file with employee details (Current or Resigned) |
| **Fuzzy Matching** | Matching names with slight variations |
| **Match Type** | How the PERNR was found (user_id_match, fuzzy_match, etc.) |
| **Match Score** | Confidence percentage of the match (0-100%) |
| **Custom Column Selection** | Manually specifying which columns to use for matching |
| **Header Row** | Row number containing column names in your file |

---

## Need Help?

If you encounter terms not defined here or need clarification, refer to the application's help documentation or contact your system administrator.

