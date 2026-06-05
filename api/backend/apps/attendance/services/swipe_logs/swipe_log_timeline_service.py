"""
Swipe Log Timeline Service - Employee punch history and daily timeline computation.

Provides:
- Employee punch history
- Daily timeline with work duration, late arrival, etc.
- First IN / Last OUT calculation
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from decimal import Decimal

from django.db.models import QuerySet
# from django.utils import timezone

from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.models.enums import PunchType

logger = logging.getLogger(__name__)


class SwipeLogTimelineService:
    """
    Service for computing employee punch timelines and history.
    
    Provides:
    - Punch history for date range
    - Daily timeline with computed metrics
    - Work duration calculation
    - Late arrival detection
    - Shift conformance checking
    """



    # ─────────────────────────────────────────────────────────────
    # Daily Timeline
    # ─────────────────────────────────────────────────────────────

    def get_employee_daily_timeline(
        self,
        employee_id: str,
        timeline_date: date,
    ) -> Dict[str, Any]:
        """
        Get employee's daily timeline with computed metrics.
        
        Includes:
        - All punches for the day
        - First IN / Last OUT
        - Total work minutes
        - Attendance status
        - Shift conformance
        - Sequence validation
        
        Args:
            employee_id: Employee UUID
            timeline_date: Date to get timeline for (default today)
        
        Returns:
            Dictionary with daily timeline data
        """
        from apps.employees.models import Employee

        # Get employee
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            raise ValueError(f"Employee {employee_id} not found.")

        # Get punches for the day
        day_start = datetime.combine(timeline_date, datetime.min.time())
        day_end = datetime.combine(timeline_date, datetime.max.time())

        punches = list(
            PunchLog.objects.filter(
                employee_id=employee_id,
                punch_time__gte=day_start,
                punch_time__lte=day_end,
            ).order_by("punch_time")
        )

        if not punches:
            return self._empty_timeline(employee, timeline_date)

        # Compute timeline metrics
        first_in = self._get_first_punch_of_type(punches, PunchType.IN)
        last_out = self._get_last_punch_of_type(punches, PunchType.OUT)

        total_work_minutes = self._calculate_work_duration(first_in, last_out)

        is_present = first_in is not None
        is_late = False
        late_by_minutes = None

        # Check if late (would require shift assignment)
        employment_details = getattr(employee, 'employment_details', None)
        if first_in and employment_details and employment_details.department:
            is_late, late_by_minutes = self._check_late_arrival(
                first_in.punch_time,
                timeline_date,
                employee,
            )

        # Analyze sequence
        is_invalid_sequence, sequence_issues = self._validate_punch_sequence(punches)

        timeline = {
            "date": timeline_date.isoformat(),
            "employee_id": str(employee_id),
            "employee_code": employee.employee_code,
            "employee_name": employee.full_name,
            "department_name": employment_details.department.name if employment_details and employment_details.department else None,
            "shift_name": None,  # Would need shift roster query
            "shift_start_time": None,
            "shift_end_time": None,
            "punches": [
                {
                    "id": str(p.id),
                    "punch_time": p.punch_time.isoformat(),
                    "punch_type": p.punch_type,
                    "punch_source": p.punch_source,
                    "device_id": p.device_id,
                    "punch_mode": p.punch_mode,
                    "is_trusted": p.is_trusted,
                }
                for p in punches
            ],
            "first_in": {
                "id": str(first_in.id),
                "punch_time": first_in.punch_time.isoformat(),
                "punch_type": first_in.punch_type,
            } if first_in else None,
            "last_out": {
                "id": str(last_out.id),
                "punch_time": last_out.punch_time.isoformat(),
                "punch_type": last_out.punch_type,
            } if last_out else None,
            "total_work_minutes": total_work_minutes,
            "net_work_minutes": total_work_minutes,
            "is_present": is_present,
            "is_late": is_late,
            "late_by_minutes": late_by_minutes,
            "shift_hours_required": None,  # Would need shift query
            "shift_hours_worked": round(total_work_minutes / 60, 2),
            "invalid_sequence_detected": is_invalid_sequence,
            "sequence_issues": sequence_issues,
            "created_at": datetime.now().isoformat(),
        }

        return timeline

    # ─────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────

    def _empty_timeline(self, employee, timeline_date: date) -> Dict[str, Any]:
        """
        Return empty timeline for a day with no punches.
        
        Args:
            employee: Employee instance
            timeline_date: Date
        
        Returns:
            Empty timeline dictionary
        """
        employment_details = getattr(employee, 'employment_details', None)
        return {
            "date": timeline_date.isoformat(),
            "employee_id": str(employee.id),
            "employee_code": employee.employee_code,
            "employee_name": employee.full_name,
            "department_name": employment_details.department.name if employment_details and employment_details.department else None,
            "shift_name": None,
            "shift_start_time": None,
            "shift_end_time": None,
            "punches": [],
            "first_in": None,
            "last_out": None,
            "total_work_minutes": 0,
            "net_work_minutes": 0,
            "is_present": False,
            "is_late": False,
            "late_by_minutes": None,
            "shift_hours_required": None,
            "shift_hours_worked": 0.0,
            "invalid_sequence_detected": False,
            "sequence_issues": [],
            "created_at": datetime.now().isoformat(),
        }

    def _get_first_punch_of_type(
        self,
        punches: List[PunchLog],
        punch_type: str,
    ) -> Optional[PunchLog]:
        """Get first punch of given type from list."""
        for punch in punches:
            if punch.punch_type == punch_type:
                return punch
        return None

    def _get_last_punch_of_type(
        self,
        punches: List[PunchLog],
        punch_type: str,
    ) -> Optional[PunchLog]:
        """Get last punch of given type from list."""
        for punch in reversed(punches):
            if punch.punch_type == punch_type:
                return punch
        return None

    def _calculate_work_duration(
        self,
        first_in: Optional[PunchLog],
        last_out: Optional[PunchLog],
    ) -> int:
        """
        Calculate total work duration in minutes.
        
        Args:
            first_in: First IN punch
            last_out: Last OUT punch
        
        Returns:
            Work duration in minutes
        """
        if not first_in or not last_out:
            return 0

        duration = last_out.punch_time - first_in.punch_time
        return int(duration.total_seconds() / 60)

    def _check_late_arrival(
        self,
        first_in_time: datetime,
        attendance_date: date,
        employee,
    ) -> tuple[bool, Optional[int]]:
        """
        Check if employee arrived late.
        
        Args:
            first_in_time: First IN punch time
            attendance_date: Date of attendance
            employee: Employee instance
        
        Returns:
            Tuple of (is_late: bool, late_by_minutes: int or None)
        """
        # Would need to query shift assignment for this date
        # For now, returning default
        return False, None

    def _validate_punch_sequence(
        self,
        punches: List[PunchLog],
    ) -> tuple[bool, List[str]]:
        """
        Validate punch sequence for the day.
        
        Args:
            punches: List of punches ordered by time
        
        Returns:
            Tuple of (is_invalid: bool, issues: list of issue descriptions)
        """
        issues = []

        if not punches:
            return False, issues

        # First punch should be IN
        if punches[0].punch_type != PunchType.IN:
            issues.append("first_punch_not_in")

        # Validate sequence
        valid_sequences = {
            PunchType.IN: [PunchType.OUT],
            PunchType.OUT: [PunchType.IN],
        }

        for i in range(len(punches) - 1):
            current = punches[i].punch_type
            next_punch = punches[i + 1].punch_type

            valid_next = valid_sequences.get(current, [])

            if next_punch not in valid_next:
                issues.append(f"invalid_transition_{current}_to_{next_punch}")

        return len(issues) > 0, issues

