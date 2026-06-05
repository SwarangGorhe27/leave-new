"""Service for shift rotation preview and employee assignment."""

import logging
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from uuid import UUID

from django.utils import timezone

from apps.attendance.models import ShiftMaster, EmployeeShiftRoster
from apps.employees.models import Employee

logger = logging.getLogger(__name__)


class ShiftRotationPreviewService:
    """
    Service for previewing shift rotations and employee assignments.

    Handles:
    - Fetching employees assigned to a shift
    - Filtering assignments by date range
    - Generating rotation preview data
    - Handling cross-midnight shifts
    """

    @staticmethod
    def get_rotation_preview(
        shift: ShiftMaster,
        from_date: date,
        to_date: date,
    ) -> Dict[str, Any]:
        """
        Get preview of employees assigned to a shift within date range.

        Args:
            shift: ShiftMaster instance
            from_date: Start date for preview
            to_date: End date for preview

        Returns:
            Dictionary with shift and employee assignment preview

        Raises:
            ValueError: If date range is invalid
        """
        try:
            logger.info(
                f"Generating rotation preview for shift {shift.id}",
                extra={
                    "shift_id": str(shift.id),
                    "from_date": str(from_date),
                    "to_date": str(to_date),
                },
            )

            # Validate date range
            if from_date > to_date:
                raise ValueError("from_date must be less than or equal to to_date")

            if (to_date - from_date).days > 365:
                raise ValueError("Date range cannot exceed 365 days")

            # Fetch active employee shift roster assignments
            assignments = EmployeeShiftRoster.objects.filter(
                shift=shift,
                employee__company=shift.company,
                shift_from__date__lte=to_date,
                shift_till__date__gte=from_date,
                deleted_at__isnull=True,
                employee__is_active=True,
            ).select_related("employee").distinct("employee_id")

            # Build employee list with assignment details
            employees = []
            for assignment in assignments:
                employees.append(
                    {
                        "id": str(assignment.employee.id),
                        "employee_code": assignment.employee.employee_code,
                        "first_name": assignment.employee.first_name,
                        "last_name": assignment.employee.last_name,
                        "full_name": assignment.employee.get_full_name(),
                        "shift_from": assignment.shift_from.isoformat(),
                        "shift_till": assignment.shift_till.isoformat(),
                    }
                )

            # Count unique employees
            employee_count = len(employees)

            logger.info(
                f"Rotation preview generated: {employee_count} employees",
                extra={
                    "shift_id": str(shift.id),
                    "employee_count": employee_count,
                },
            )

            return {
                "shift_id": str(shift.id),
                "shift_code": shift.code,
                "shift_name": shift.name,
                "start_time": shift.start_time.isoformat(),
                "end_time": shift.end_time.isoformat(),
                "cross_midnight": shift.cross_midnight,
                "date_range": {
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat(),
                    "days": (to_date - from_date).days + 1,
                },
                "employee_count": employee_count,
                "employees": employees,
            }

        except ValueError as e:
            logger.error(
                f"Invalid parameters for rotation preview: {str(e)}",
                extra={"shift_id": str(shift.id)},
            )
            raise
        except Exception as e:
            logger.error(
                f"Error generating rotation preview: {str(e)}",
                extra={"shift_id": str(shift.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def get_employees_by_shift_and_date(
        shift: ShiftMaster,
        target_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Get employees assigned to shift on a specific date.

        Args:
            shift: ShiftMaster instance
            target_date: Specific date to check

        Returns:
            List of employees assigned to shift on that date
        """
        try:
            logger.info(
                f"Fetching employees for shift {shift.id} on {target_date}",
                extra={
                    "shift_id": str(shift.id),
                    "target_date": str(target_date),
                },
            )

            assignments = EmployeeShiftRoster.objects.filter(
                shift=shift,
                employee__company=shift.company,
                shift_from__date__lte=target_date,
                shift_till__date__gte=target_date,
                deleted_at__isnull=True,
                employee__is_active=True,
            ).select_related("employee")

            employees = []
            for assignment in assignments:
                employees.append(
                    {
                        "id": str(assignment.employee.id),
                        "employee_code": assignment.employee.employee_code,
                        "name": assignment.employee.get_full_name(),
                        "department": assignment.employee.department.name
                        if assignment.employee.department
                        else None,
                    }
                )

            return employees

        except Exception as e:
            logger.error(
                f"Error fetching employees by shift and date: {str(e)}",
                extra={"shift_id": str(shift.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def get_shift_assignments_summary(
        shift: ShiftMaster,
        from_date: date,
        to_date: date,
    ) -> Dict[str, Any]:
        """
        Get summary of shift assignments within date range.

        Args:
            shift: ShiftMaster instance
            from_date: Start date
            to_date: End date

        Returns:
            Summary dictionary with assignment statistics
        """
        try:
            logger.info(
                f"Generating assignment summary for shift {shift.id}",
                extra={
                    "shift_id": str(shift.id),
                    "from_date": str(from_date),
                    "to_date": str(to_date),
                },
            )

            assignments = EmployeeShiftRoster.objects.filter(
                shift=shift,
                shift_from__date__lte=to_date,
                shift_till__date__gte=from_date,
                deleted_at__isnull=True,
            )

            total_assignments = assignments.count()
            unique_employees = assignments.values("employee").distinct().count()

            # Group by department if available
            department_summary = {}
            for assignment in assignments:
                dept = (
                    assignment.employee.department.name
                    if assignment.employee.department
                    else "Unassigned"
                )
                if dept not in department_summary:
                    department_summary[dept] = 0
                department_summary[dept] += 1

            return {
                "shift_id": str(shift.id),
                "shift_code": shift.code,
                "date_range": {
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat(),
                },
                "total_assignments": total_assignments,
                "unique_employees": unique_employees,
                "department_summary": department_summary,
            }

        except Exception as e:
            logger.error(
                f"Error generating assignment summary: {str(e)}",
                extra={"shift_id": str(shift.id)},
                exc_info=True,
            )
            raise
