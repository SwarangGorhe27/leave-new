"""
Shift Window Builder
====================
Constructs the punch acceptance window for a given shift and attendance date.

Handles:
- Normal shifts (09:00 - 18:00)
- Cross-midnight shifts (22:00 - 06:00)
- Early punch buffer (before shift start)
- Late punch buffer (after shift end)

The window determines which punches belong to a given attendance date.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pytz
from django.utils import timezone


@dataclass
class ShiftWindow:
    """
    Represents the full punch acceptance window for a shift on a specific date.

    Attributes:
        attendance_date:  The canonical date this window belongs to.
        shift_start:      Exact shift start datetime (no buffer).
        shift_end:        Exact shift end datetime (no buffer).
        window_start:     Earliest punch accepted (shift_start - early_buffer).
        window_end:       Latest punch accepted (shift_end + late_buffer).
        cross_midnight:   Whether the shift crosses midnight.
    """

    attendance_date: date
    shift_start: datetime
    shift_end: datetime
    window_start: datetime
    window_end: datetime
    cross_midnight: bool


def build_shift_window(shift, attendance_date: date, tz_name: str = "Asia/Kolkata") -> ShiftWindow:
    """
    Build the punch acceptance window for a shift on a given attendance date.

    Args:
        shift:            ShiftDefinition instance (must have start_time, end_time,
                          cross_midnight, early_punch_buffer_mins, late_punch_buffer_mins).
        attendance_date:  The date we are computing attendance for.
        tz_name:          IANA timezone string. Defaults to Asia/Kolkata.
                          Should come from AttendanceOfficeLocation.timezone when available.

    Returns:
        ShiftWindow dataclass with all window boundaries as timezone-aware datetimes.

    Example (normal shift):
        Shift 09:00 - 18:00, buffer 60/120 mins
        window_start = 08:00, window_end = 20:00 — same calendar day.

    Example (cross-midnight shift):
        Shift 22:00 - 06:00, buffer 60/120 mins
        shift_start  = date 15th 22:00
        shift_end    = date 16th 06:00
        window_start = date 15th 21:00
        window_end   = date 16th 08:00
    """
    tz = pytz.timezone(tz_name)

    # --- Shift start datetime (anchored to attendance_date) ---
    shift_start = tz.localize(
        datetime.combine(attendance_date, shift.start_time)
    )

    # --- Shift end datetime ---
    if shift.cross_midnight:
        # End time is on the NEXT calendar day
        shift_end = tz.localize(
            datetime.combine(attendance_date + timedelta(days=1), shift.end_time)
        )
    else:
        shift_end = tz.localize(
            datetime.combine(attendance_date, shift.end_time)
        )

    # --- Apply buffers ---
    window_start = shift_start - timedelta(minutes=shift.early_punch_buffer_mins)
    window_end = shift_end + timedelta(minutes=shift.late_punch_buffer_mins)

    return ShiftWindow(
        attendance_date=attendance_date,
        shift_start=shift_start,
        shift_end=shift_end,
        window_start=window_start,
        window_end=window_end,
        cross_midnight=shift.cross_midnight,
    )


def get_attendance_date_for_punch(punch_time: datetime, shift, candidate_date: date, tz_name: str = "Asia/Kolkata") -> date | None:
    """
    Given a raw punch timestamp, determine which attendance date it belongs to.

    Used during backfill or when processing punches that may span midnight.

    Args:
        punch_time:     Timezone-aware punch datetime.
        shift:          ShiftDefinition instance.
        candidate_date: The date to test (typically punch_time.date() or day before).
        tz_name:        IANA timezone string.

    Returns:
        The attendance date if punch falls within the window, else None.
    """
    window = build_shift_window(shift, candidate_date, tz_name)
    if window.window_start <= punch_time <= window.window_end:
        return candidate_date
    return None