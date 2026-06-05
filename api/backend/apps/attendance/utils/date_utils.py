"""
attendance/utils/date_utils.py

Shared date helpers for the Attendance Matrix sub-module.

Functions
---------
get_cycle_bounds          — resolve cycle start/end for a given year+month
build_date_headers        — ordered date header list for the grid
resolve_cell_code         — compute display cell code from status/work_mode/leave_type
get_month_display_label   — "MAY 2026" label for month nav
is_weekend                — check if a date is a weekend per company config
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Optional

from apps.attendance.models import AttendanceCycle, EmployeeAttendanceConfig


# ---------------------------------------------------------------------------
# Cycle Bounds
# ---------------------------------------------------------------------------

def get_cycle_bounds(company_id: str, year: int, month: int) -> tuple[date, date]:
    """
    Return (cycle_start, cycle_end) for the given company / year / month.

    Resolution order:
    1. Company-level default cycle from AttendanceCompanyConfig.
    2. If no config exists, fall back to calendar month (1st to last day).

    The cycle_start_day tells us which day of the month the cycle opens.
    Example: cycle_start_day=26 → cycle runs 26-Mar to 25-Apr for "April".

    Parameters
    ----------
    company_id : str  UUID of the tenant company.
    year       : int  Calendar year (e.g. 2026).
    month      : int  Month number 1–12.

    Returns
    -------
    (cycle_start, cycle_end) as date objects.
    """
    # Try to get the default cycle for this company
    cycle = (
        AttendanceCycle.objects
        .filter(company_id=company_id, is_default=True, is_active=True)
        .first()
    )

    if not cycle:
        # Fallback: try any active cycle for this company
        cycle = (
            AttendanceCycle.objects
            .filter(company_id=company_id, is_active=True)
            .first()
        )

    if not cycle or cycle.cycle_start_day == 1:
        # Standard calendar month
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, 1), date(year, month, last_day)

    start_day = cycle.cycle_start_day

    # Cycle opens on start_day of the PREVIOUS month and closes on
    # (start_day - 1) of the CURRENT month.
    # e.g. start_day=26, month=May → cycle_start=26-Apr, cycle_end=25-May

    # Compute cycle_start: start_day of (month - 1)
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    # Clamp start_day to valid days in prev_month
    max_days_prev = calendar.monthrange(prev_year, prev_month)[1]
    clamped_start = min(start_day, max_days_prev)
    cycle_start = date(prev_year, prev_month, clamped_start)

    # cycle_end: (start_day - 1) of current month
    max_days_curr = calendar.monthrange(year, month)[1]
    end_day = min(start_day - 1, max_days_curr)
    if end_day < 1:
        # edge: start_day=1 handled above; this shouldn't happen
        end_day = max_days_curr
    cycle_end = date(year, month, end_day)

    return cycle_start, cycle_end


# ---------------------------------------------------------------------------
# Date Headers
# ---------------------------------------------------------------------------

DAY_LABELS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]


def build_date_headers(
    cycle_start: date,
    cycle_end: date,
    week_start_day: int,
    holiday_dates: set[date],
) -> list[dict]:
    """
    Build the ordered list of date objects for the matrix grid header row.

    Each dict contains:
        date        : ISO date string "YYYY-MM-DD"
        day_label   : "MON" … "SUN"
        is_weekend  : True if the day is a configured weekend day
        is_holiday  : True if the date is in holiday_dates

    Parameters
    ----------
    cycle_start    : date   First date of the cycle.
    cycle_end      : date   Last date of the cycle.
    week_start_day : int    0=Sunday … 6=Saturday (from AttendanceCompanyConfig).
    holiday_dates  : set    Set of holiday date objects for quick lookup.

    Returns
    -------
    List of dicts, one per calendar date in [cycle_start, cycle_end].
    """
    headers = []
    current = cycle_start

    # weekend_days: the two days that are off — derived from week_start_day.
    # Typical: week_start_day=1 (Mon) → weekends are Sat(6) and Sun(0).
    # We treat days where Python weekday() maps to Sat or Sun as weekend
    # regardless of week_start_day, but honour the company's week definition.
    # Standard approach: the two days BEFORE week_start_day (mod 7) are off.
    # For most Indian companies week_start_day=1 → Sat, Sun are weekend.
    # We compute: off_days = {(week_start_day - 1) % 7, (week_start_day - 2) % 7}
    # Mapping to Python's weekday(): Mon=0 … Sun=6
    # Our config: 0=Sun … 6=Sat → Python weekday: Mon=0,Tue=1,...,Sat=5,Sun=6
    # Convert: python_weekday = (config_day - 1) % 7  (0=Sun in config → 6=Sun in python)
    def config_to_python_weekday(config_day: int) -> int:
        # config: 0=Sun,1=Mon,...,6=Sat → python: Mon=0,...,Sat=5,Sun=6
        mapping = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
        return mapping[config_day]

    # Work week runs week_start_day through week_start_day+4 (5 working days)
    # Weekend = the remaining 2 days
    work_start_py = config_to_python_weekday(week_start_day)
    working_days_py = {(work_start_py + i) % 7 for i in range(5)}
    weekend_days_py = set(range(7)) - working_days_py

    while current <= cycle_end:
        py_wd = current.weekday()  # Mon=0 … Sun=6
        headers.append({
            "date": current.isoformat(),
            "day_label": DAY_LABELS[current.weekday() - 0],
            # Fix: Python weekday Mon=0,Sun=6; our DAY_LABELS are Sun=0,Mon=1
            # Rebuild correctly:
            "day_label": _python_weekday_to_label(py_wd),
            "is_weekend": py_wd in weekend_days_py,
            "is_holiday": current in holiday_dates,
        })
        current += timedelta(days=1)

    return headers


def _python_weekday_to_label(py_wd: int) -> str:
    """Convert Python weekday (Mon=0 … Sun=6) to 3-letter label."""
    labels = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    return labels[py_wd]


# ---------------------------------------------------------------------------
# Cell Code Resolution
# ---------------------------------------------------------------------------

def resolve_cell_code(
    status_code: str,
    work_mode: str,
    leave_type_code: Optional[str] = None,
) -> str:
    """
    Compute the display cell code shown in the Attendance Matrix grid.

    This is a VIEW-LAYER computation — never stored in the database.

    Rules (evaluated in order):
    1. PRESENT + work_mode=REMOTE  → "WFH"
    2. LEAVE + leave_type_code set → leave_type_code  (CL, SL, EL, ML …)
    3. LEAVE + no leave_type_code  → "L"
    4. ABSENT                      → "A"
    5. HALF_DAY                    → "HD"
    6. HOLIDAY                     → "HO"
    7. WEEK_OFF                    → "WO"
    8. PRESENT (office/other)      → "P"
    9. Fallback                    → first char of status_code

    Parameters
    ----------
    status_code     : str  mst_attendance_status.code
    work_mode       : str  emp_daily_attendance.work_mode
    leave_type_code : str  mst_leave_type.code (CL/SL/EL…); None if not on leave

    Returns
    -------
    Single display code string.
    """
    if status_code == "PRESENT":
        if work_mode == "REMOTE":
            return "WFH"
        return "P"

    if status_code == "LEAVE":
        if leave_type_code:
            return leave_type_code  # CL, SL, EL, ML etc.
        return "L"

    if status_code == "ABSENT":
        return "A"

    if status_code == "HALF_DAY":
        return "HD"

    if status_code == "HOLIDAY":
        return "HO"

    if status_code == "WEEK_OFF":
        return "WO"

    # Fallback for any future status codes
    return status_code[0] if status_code else "?"


# ---------------------------------------------------------------------------
# Display Label
# ---------------------------------------------------------------------------

def get_month_display_label(year: int, month: int) -> str:
    """Return "MAY 2026" style label for the month navigation header."""
    return date(year, month, 1).strftime("%B %Y").upper()


# ---------------------------------------------------------------------------
# Weekend Check
# ---------------------------------------------------------------------------

def is_weekend(d: date, week_start_day: int) -> bool:
    """
    Return True if the given date falls on a weekend day per company config.

    Parameters
    ----------
    d              : date   Date to check.
    week_start_day : int    0=Sunday … 6=Saturday (company config).
    """
    py_wd = d.weekday()
    mapping = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
    work_start_py = mapping[week_start_day]
    working_days_py = {(work_start_py + i) % 7 for i in range(5)}
    return py_wd not in working_days_py
