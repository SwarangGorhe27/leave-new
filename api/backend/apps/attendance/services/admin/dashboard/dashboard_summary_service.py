"""Dashboard Summary Service - Analytics metrics calculation."""

import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Any, Optional

from django.db.models import (
    Count,
    Q,
    Sum,
    F,
    DecimalField,
    Value,
    Case,
    When,
    ExpressionWrapper,
)
from django.utils import timezone

from apps.attendance.models import DailyAttendance, AttendanceStatus
from apps.employees.models import Employee

logger = logging.getLogger(__name__)


class DashboardSummaryService:
    """
    Business logic for dashboard summary calculations.
    
    Handles:
    - Average work hours calculation
    - Attendance stats (present, absent, holidays, late, half-days)
    - Monthly aggregations
    - Efficient querying with aggregations
    """

    @staticmethod
    def get_dashboard_summary(
        employee: Employee,
        month: int = None,
        year: int = None,
    ) -> Dict[str, Any]:
        """
        Calculate dashboard summary metrics for an employee.

        Args:
            employee: Employee instance
            month: Month number (1-12). Defaults to current month.
            year: Year. Defaults to current year.

        Returns:
            Dictionary containing summary metrics:
            {
                'avg_work_hours': Decimal,
                'total_present': int,
                'total_absent': int,
                'total_holidays': int,
                'total_late_logins': int,
                'total_half_days': int,
                'period_start_date': date,
                'period_end_date': date,
                'generated_at': datetime,
            }

        Raises:
            ValueError: If invalid month/year provided
        """
        try:
            # Use current date if not provided
            now = timezone.now()
            if month is None:
                month = now.month
            if year is None:
                year = now.year

            # Validate month/year
            if not (1 <= month <= 12 and 2000 <= year <= 2100):
                logger.warning(
                    f"Invalid month/year for dashboard summary: month={month}, year={year}",
                    extra={"employee_id": str(employee.id), "month": month, "year": year},
                )
                raise ValueError("Invalid month or year provided")

            # Calculate period dates
            period_start = date(year, month, 1)
            # Get last day of month
            next_month = period_start.replace(day=28) + timedelta(days=4)
            period_end = (next_month - timedelta(days=next_month.day)).replace(day=1) + \
                        timedelta(days=32)
            period_end = period_end.replace(day=1) - timedelta(days=1)

            # Fetch attendance records for the period
            attendance_records = DailyAttendance.objects.filter(
                employee=employee,
                attendance_date__year=year,
                attendance_date__month=month,
                deleted_at__isnull=True,
            ).select_related("status")

            # Calculate metrics using aggregation
            summary = attendance_records.aggregate(
                # Average work hours
                avg_work_hours=ExpressionWrapper(
                    Sum("actual_work_mins") / (Count("id", filter=Q(actual_work_mins__gt=0)) or 1),
                    output_field=DecimalField(),
                ),
                # Count by status
                total_present=Count(
                    "id",
                    filter=Q(status__name__iexact="present")
                ),
                total_absent=Count(
                    "id",
                    filter=Q(status__name__iexact="absent")
                ),
                total_holidays=Count(
                    "id",
                    filter=Q(status__name__iexact="holiday")
                ),
                total_late_logins=Count(
                    "id",
                    filter=Q(is_late=True)
                ),
                total_half_days=Count(
                    "id",
                    filter=Q(lop_days__gt=0) & Q(lop_days__lt=1)
                ),
            )

            # Convert minutes to hours (actual_work_mins is in minutes)
            avg_work_mins = summary.get("avg_work_hours") or 0
            if avg_work_mins:
                avg_work_hours = Decimal(str(avg_work_mins / 60))
            else:
                avg_work_hours = Decimal("0.00")

            result = {
                "avg_work_hours": round(avg_work_hours, 2),
                "total_present": summary.get("total_present", 0),
                "total_absent": summary.get("total_absent", 0),
                "total_holidays": summary.get("total_holidays", 0),
                "total_late_logins": summary.get("total_late_logins", 0),
                "total_half_days": summary.get("total_half_days", 0),
                "period_start_date": period_start,
                "period_end_date": period_end,
                "generated_at": timezone.now(),
            }

            logger.info(
                f"Dashboard summary calculated for employee {employee.employee_code}",
                extra={
                    "employee_id": str(employee.id),
                    "month": month,
                    "year": year,
                },
            )

            return result

        except Exception as e:
            logger.error(
                f"Error calculating dashboard summary: {str(e)}",
                exc_info=True,
                extra={
                    "employee_id": str(employee.id),
                    "month": month,
                    "year": year,
                },
            )
            raise

    @staticmethod
    def validate_period(month: int, year: int) -> bool:
        """
        Validate month and year parameters.

        Args:
            month: Month number (1-12)
            year: Year number

        Returns:
            True if valid, False otherwise
        """
        try:
            date(year, month, 1)
            return True
        except ValueError:
            return False
