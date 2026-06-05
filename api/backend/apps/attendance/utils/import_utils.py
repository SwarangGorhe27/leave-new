"""
attendance/utils/import_utils.py

Handles parsing and validation of the Attendance Matrix Excel/CSV import file.

Actual file format (from Attendance_Matrix_May_2026.xlsx)
----------------------------------------------------------
Row 1 (header):
    Col 1: Employee          — employee full name
    Col 2: ID                — employee_code (EMP001, EMP002 …)
    Col 3: Dept              — department name
    Col 4 onward: date cols  — headers are "DD-MM-YYYY" strings
                               each cell contains a status cell_code:
                               P, A, WO, WFH, L, WFH, HD, HO, CL, SL …

Row 2+ (data):
    Col 1: full name
    Col 2: employee_code
    Col 3: department
    Col 4 onward: cell_code per date matching header

This is the OPPOSITE of a flat/normalized format — it is a wide matrix.
The import parser unpivots it into flat records:
    (employee_code, date, cell_code) per non-None cell.

Exported by this code
---------------------
List of dicts:
    {
        "employee_code": "EMP001",
        "full_name":     "Amit Sharma",
        "department":    "Engineering",
        "date":          date(2026, 5, 1),
        "cell_code":     "P",
    }

Valid cell codes accepted on import
------------------------------------
P, A, WO, WFH, L, HD, HO, CL, SL, EL, ML
(any unrecognised code is flagged as a validation error per row)

Validation performed here (structural only)
--------------------------------------------
- Row 1 must have Employee, ID, Dept as first 3 cols (case-insensitive)
- Row 1 must have at least one parseable date column after col 3
- employee_code (col 2) must be non-empty for every data row
- Each date header must be parseable as DD-MM-YYYY or YYYY-MM-DD
- Each cell value must be in VALID_CELL_CODES or blank (blank = skip)

Deep per-record validation (employee exists, date in cycle, locked etc.)
is done by the async Celery worker — not here.
"""

from __future__ import annotations

import csv
from datetime import date, datetime
from typing import Optional

VALID_CELL_CODES = {
    "P", "A", "WO", "WFH", "L",
    "HD", "HO", "CL", "SL", "EL", "ML",
}

# Map cell_code → mst_attendance_status.code
# WFH is status=PRESENT + work_mode=REMOTE (resolved by the worker)
CELL_CODE_TO_STATUS = {
    "P":   "PRESENT",
    "A":   "ABSENT",
    "WO":  "WEEK_OFF",
    "WFH": "PRESENT",   # worker sets work_mode=REMOTE
    "L":   "LEAVE",
    "HD":  "HALF_DAY",
    "HO":  "HOLIDAY",
    "CL":  "LEAVE",     # worker resolves leave_type by code
    "SL":  "LEAVE",
    "EL":  "LEAVE",
    "ML":  "LEAVE",
}

CELL_CODE_TO_WORK_MODE = {
    "WFH": "REMOTE",
}

# leave_type_code when cell_code implies a specific leave type
CELL_CODE_TO_LEAVE_TYPE = {
    "CL": "CL",
    "SL": "SL",
    "EL": "EL",
    "ML": "ML",
}


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def parse_import_file(
    path: str,
    suffix: str,
) -> tuple[list[dict], list[dict]]:
    """
    Parse the attendance matrix import file into flat records.

    Parameters
    ----------
    path   : str  Absolute path to the saved temp file.
    suffix : str  File extension: .xlsx / .xls / .csv

    Returns
    -------
    (records, errors)
        records : list of dicts — one per (employee, date) cell
        errors  : list of dicts — structural/cell validation errors

    Each record dict:
        employee_code   : str
        full_name       : str
        department      : str | None
        date            : date
        cell_code       : str   normalised uppercase
        status_code     : str   resolved from CELL_CODE_TO_STATUS
        work_mode       : str | None
        leave_type_code : str | None
    """
    if suffix in (".xlsx", ".xls"):
        return _parse_excel(path)
    else:
        return _parse_csv(path)


# ---------------------------------------------------------------------------
# Excel parser
# ---------------------------------------------------------------------------

def _parse_excel(path: str) -> tuple[list[dict], list[dict]]:
    import openpyxl

    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as exc:
        return [], [{"row": "file", "error": f"Cannot open Excel file: {exc}"}]

    ws = wb.active
    all_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not all_rows:
        return [], [{"row": "file", "error": "File is empty."}]

    header_row = [str(v).strip() if v is not None else "" for v in all_rows[0]]
    return _process_rows(header_row, all_rows[1:])


# ---------------------------------------------------------------------------
# CSV parser
# ---------------------------------------------------------------------------

def _parse_csv(path: str) -> tuple[list[dict], list[dict]]:
    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.reader(f)
            all_rows_raw = list(reader)
    except Exception as exc:
        return [], [{"row": "file", "error": f"Cannot open CSV file: {exc}"}]

    if not all_rows_raw:
        return [], [{"row": "file", "error": "File is empty."}]

    header_row = [str(v).strip() for v in all_rows_raw[0]]
    # Pad data rows to same length as header
    data_rows = []
    for raw in all_rows_raw[1:]:
        padded = list(raw) + [None] * (len(header_row) - len(raw))
        data_rows.append(tuple(padded))

    return _process_rows(header_row, data_rows)


# ---------------------------------------------------------------------------
# Core processing — shared by Excel and CSV
# ---------------------------------------------------------------------------

def _process_rows(
    header_row: list[str],
    data_rows: list[tuple],
) -> tuple[list[dict], list[dict]]:
    errors: list[dict] = []
    records: list[dict] = []

    # ── Validate first 3 header columns ──────────────────────────────────────
    expected_fixed = ["employee", "id", "dept"]
    actual_fixed = [h.lower() for h in header_row[:3]]

    for i, (exp, act) in enumerate(zip(expected_fixed, actual_fixed)):
        if exp not in act:
            errors.append({
                "row": "header",
                "col": i + 1,
                "error": (
                    f"Expected column {i+1} header to contain '{exp}', "
                    f"got '{header_row[i]}'."
                ),
            })

    if errors:
        # Can't continue — column structure is wrong
        return [], errors

    # ── Parse date columns (col 4 onward) ────────────────────────────────────
    date_cols: list[tuple[int, date]] = []   # (col_index, date)

    for col_idx, header_val in enumerate(header_row[3:], start=3):
        if not header_val:
            continue
        parsed_date = _parse_date_header(header_val)
        if parsed_date is None:
            errors.append({
                "row": "header",
                "col": col_idx + 1,
                "error": f"Cannot parse date header '{header_val}'. Use DD-MM-YYYY.",
            })
        else:
            date_cols.append((col_idx, parsed_date))

    if not date_cols:
        errors.append({
            "row": "header",
            "error": "No parseable date columns found after column 3.",
        })
        return [], errors

    # ── Process data rows ─────────────────────────────────────────────────────
    for row_num, row in enumerate(data_rows, start=2):  # row_num is Excel row number
        # Skip fully empty rows
        if all(v is None or str(v).strip() == "" for v in row):
            continue

        full_name     = str(row[0]).strip() if row[0] is not None else ""
        employee_code = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ""
        department    = str(row[2]).strip() if len(row) > 2 and row[2] is not None else None

        if not employee_code:
            errors.append({
                "row": row_num,
                "error": "Employee ID (column 2) is empty.",
            })
            continue

        # Process each date cell
        for col_idx, col_date in date_cols:
            raw_val = row[col_idx] if col_idx < len(row) else None

            if raw_val is None or str(raw_val).strip() == "":
                # Blank cell — skip (not an error, means no data for this date)
                continue

            cell_code = str(raw_val).strip().upper()

            if cell_code not in VALID_CELL_CODES:
                errors.append({
                    "row": row_num,
                    "col": col_idx + 1,
                    "employee_code": employee_code,
                    "date": col_date.isoformat(),
                    "error": (
                        f"Invalid cell code '{cell_code}'. "
                        f"Accepted: {', '.join(sorted(VALID_CELL_CODES))}."
                    ),
                })
                continue

            records.append({
                "employee_code":   employee_code,
                "full_name":       full_name,
                "department":      department or None,
                "date":            col_date,
                "cell_code":       cell_code,
                "status_code":     CELL_CODE_TO_STATUS[cell_code],
                "work_mode":       CELL_CODE_TO_WORK_MODE.get(cell_code),
                "leave_type_code": CELL_CODE_TO_LEAVE_TYPE.get(cell_code),
            })

    return records, errors


# ---------------------------------------------------------------------------
# Date header parser
# ---------------------------------------------------------------------------

def _parse_date_header(value: str) -> Optional[date]:
    """
    Parse a date column header. Accepts:
        DD-MM-YYYY  (file format: 01-05-2026)
        YYYY-MM-DD  (ISO format)
        DD/MM/YYYY
        MM/DD/YYYY  (US format — tried last)
    Returns None if unparseable.
    """
    value = value.strip()
    formats = [
        "%d-%m-%Y",   # 01-05-2026  ← primary (matches actual file)
        "%Y-%m-%d",   # 2026-05-01
        "%d/%m/%Y",   # 01/05/2026
        "%m/%d/%Y",   # 05/01/2026
        "%d-%m-%y",   # 01-05-26
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Summary helper (used by view to build the response)
# ---------------------------------------------------------------------------

def summarise_import(
    records: list[dict],
    errors: list[dict],
) -> dict:
    """
    Build the summary dict returned in the import API response.

    Returns
    -------
    {
        rows_received      : int   — employee rows parsed (unique employee_codes)
        records_parsed     : int   — total (employee, date) cells parsed
        validation_errors  : list  — structural errors found
        is_valid           : bool  — True if no errors
    }
    """
    unique_employees = len({r["employee_code"] for r in records})
    return {
        "rows_received":     unique_employees,
        "records_parsed":    len(records),
        "validation_errors": errors,
        "is_valid":          len(errors) == 0,
    }
