"""Validators for shift assignment operations."""

import logging
from typing import List, Dict, Tuple
from datetime import date, datetime, timedelta
from uuid import UUID

from django.db.models import Q, Count
from django.contrib.auth.models import User

from apps.attendance.models import (
    EmployeeShiftRoster,
    ShiftDefinition,
    AttendanceCycle,
    AttendanceJob,
)
from apps.employees.models import Employee, Company, Department

logger = logging.getLogger(__name__)


class ShiftAssignmentValidator:
    """Validator for shift assignment operations."""

    def __init__(self, company_id: UUID = None):
        """Initialize validator with optional company context."""
        self.company_id = company_id
        self.errors = []
        self.warnings = []

    def validate_employee(self, employee_id: UUID) -> Tuple[bool, Employee]:
        """Validate employee exists and is active."""
        try:
            employee = Employee.objects.get(
                id=employee_id,
                deleted_at__isnull=True,
            )
            if not employee.is_active:
                self.warnings.append(
                    f"Employee {employee.employee_code} is inactive."
                )
            if employee.status != "ACTIVE":
                self.warnings.append(
                    f"Employee {employee.employee_code} status is {employee.status}."
                )
            return True, employee
        except Employee.DoesNotExist:
            self.errors.append(f"Employee {employee_id} not found.")
            return False, None

    def validate_shift(self, shift_id: UUID) -> Tuple[bool, ShiftDefinition]:
        """Validate shift exists and is active."""
        try:
            shift = ShiftDefinition.objects.get(
                id=shift_id,
                deleted_at__isnull=True,
            )
            if not shift.is_active:
                self.warnings.append(f"Shift {shift.code} is inactive.")
            return True, shift
        except ShiftDefinition.DoesNotExist:
            self.errors.append(f"Shift {shift_id} not found.")
            return False, None

    def validate_cycle(self, cycle_id: UUID) -> Tuple[bool, AttendanceCycle]:
        """Validate cycle exists and is active."""
        try:
            cycle = AttendanceCycle.objects.get(
                id=cycle_id,
                deleted_at__isnull=True,
            )
            if not cycle.is_active:
                self.warnings.append(f"Cycle {cycle.name} is inactive.")
            return True, cycle
        except AttendanceCycle.DoesNotExist:
            self.errors.append(f"Cycle {cycle_id} not found.")
            return False, None

    def validate_roster_date_in_cycle(
        self,
        roster_date: date,
        cycle: AttendanceCycle,
    ) -> bool:
        """Validate roster date falls within cycle dates."""
        if not (cycle.start_date <= roster_date <= cycle.end_date):
            self.errors.append(
                f"Roster date {roster_date} is outside cycle range "
                f"({cycle.start_date} - {cycle.end_date})."
            )
            return False
        return True

    def check_duplicate_assignment(
        self,
        employee_id: UUID,
        roster_date: date,
        exclude_id: UUID = None,
    ) -> bool:
        """Check if assignment already exists for employee on that date."""
        query = EmployeeShiftRoster.objects.filter(
            employee_id=employee_id,
            roster_date=roster_date,
            deleted_at__isnull=True,
        )
        if exclude_id:
            query = query.exclude(id=exclude_id)

        if query.exists():
            self.errors.append(
                f"Assignment already exists for employee {employee_id} on {roster_date}."
            )
            return True  # Duplicate found
        return False  # No duplicate

    def check_overlapping_shifts(
        self,
        employee_id: UUID,
        shift_id: UUID,
        roster_date: date,
        exclude_id: UUID = None,
    ) -> bool:
        """Check for overlapping shifts on the same date."""
        # For now, we enforce one shift per day, so this is same as duplicate check
        return self.check_duplicate_assignment(
            employee_id,
            roster_date,
            exclude_id,
        )

    def validate_date_range(
        self,
        date_from: date,
        date_to: date,
    ) -> bool:
        """Validate date range is valid."""
        if date_from > date_to:
            self.errors.append("Start date cannot be after end date.")
            return False

        if date_from < date.today():
            self.warnings.append("Start date is in the past.")

        # Check max 90 days
        date_diff = (date_to - date_from).days
        if date_diff > 90:
            self.errors.append("Date range cannot exceed 90 days.")
            return False

        return True

    def validate_bulk_assignment_data(
        self,
        assignments: List[Dict],
        cycle_id: UUID,
        date_from: date,
        date_to: date,
    ) -> Tuple[bool, Dict]:
        """Validate all bulk assignment data."""
        results = {
            "valid": [],
            "invalid": [],
            "warnings": [],
            "errors": [],
        }

        # Validate date range
        if not self.validate_date_range(date_from, date_to):
            results["errors"].extend(self.errors)
            return False, results

        # Validate cycle
        is_valid, cycle = self.validate_cycle(cycle_id)
        if not is_valid:
            results["errors"].extend(self.errors)
            return False, results

        # Validate each assignment
        checked_combinations = set()

        for idx, assignment in enumerate(assignments):
            assignment_errors = []
            employee_id = assignment.get("employee_id")
            shift_id = assignment.get("shift_id")

            # Validate employee
            is_valid, employee = self.validate_employee(employee_id)
            if not is_valid:
                assignment_errors.extend(self.errors)
                self.errors = []
            else:
                assignment_errors.extend(self.warnings)
                self.warnings = []

            # Validate shift
            if not assignment_errors:
                is_valid, shift = self.validate_shift(shift_id)
                if not is_valid:
                    assignment_errors.extend(self.errors)
                    self.errors = []
                else:
                    assignment_errors.extend(self.warnings)
                    self.warnings = []

            if assignment_errors:
                results["invalid"].append({
                    "index": idx,
                    "employee_id": employee_id,
                    "shift_id": shift_id,
                    "errors": assignment_errors,
                })
            else:
                # Check for duplicate combinations
                combo_key = f"{employee_id}_{shift_id}"
                if combo_key in checked_combinations:
                    results["invalid"].append({
                        "index": idx,
                        "employee_id": employee_id,
                        "shift_id": shift_id,
                        "errors": ["Duplicate employee-shift combination in bulk data."],
                    })
                else:
                    results["valid"].append({
                        "index": idx,
                        "employee_id": employee_id,
                        "shift_id": shift_id,
                        "employee": employee,
                        "shift": shift,
                    })
                    checked_combinations.add(combo_key)

        return len(results["invalid"]) == 0, results

    def check_existing_assignments_in_range(
        self,
        employee_id: UUID,
        date_from: date,
        date_to: date,
    ) -> List[EmployeeShiftRoster]:
        """Get existing assignments in date range."""
        return EmployeeShiftRoster.objects.filter(
            employee_id=employee_id,
            roster_date__range=[date_from, date_to],
            deleted_at__isnull=True,
        ).select_related("shift")

    def generate_dates_for_bulk(
        self,
        assignment_type: str,
        date_from: date = None,
        date_to: date = None,
        recurring_days: List[int] = None,
        start_date: date = None,
        weeks: int = 4,
    ) -> List[date]:
        """Generate dates based on assignment type."""
        dates = []

        if assignment_type == "single_date":
            dates = [date_from]

        elif assignment_type == "date_range":
            current = date_from
            while current <= date_to:
                dates.append(current)
                current += timedelta(days=1)

        elif assignment_type == "recurring":
            current = start_date
            end_date = start_date + timedelta(weeks=weeks)
            while current <= end_date:
                if current.weekday() in recurring_days:
                    dates.append(current)
                current += timedelta(days=1)

        return dates

    def get_validation_errors(self) -> List[str]:
        """Get all validation errors."""
        return self.errors

    def get_validation_warnings(self) -> List[str]:
        """Get all validation warnings."""
        return self.warnings

    def clear(self):
        """Clear errors and warnings."""
        self.errors = []
        self.warnings = []
