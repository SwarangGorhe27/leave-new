"""Dashboard Trend Service - Work hours trend aggregation."""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
import calendar

from django.db.models import Sum, Q
from django.utils import timezone

from apps.attendance.models import DailyAttendance, AttendanceStatus
from apps.employees.models import Employee

logger = logging.getLogger(__name__)


class DashboardTrendService:
    """
    Business logic for dashboard work-hours trend.
    
    Handles:
    - Daily work hours aggregation
    - Monthly trend calculation
    - Holiday and weekend flagging
    - Chart data formatting
    """

    # Day names mapping
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @staticmethod
    def get_work_hours_trend(
        employee: Employee,
        month: int = None,
        year: int = None,
    ) -> Dict[str, Any]:
        """
        Get work-hours trend data for the month.

        Args:
            employee: Employee instance
            month: Month number (1-12). Defaults to current month.
            year: Year. Defaults to current year.

        Returns:
            Dictionary containing trend data:
            {
                'month': int,
                'year': int,
                'trend_data': [
                    {
                        'date': date,
                        'day_name': str,
                        'work_hours': Decimal,
                        'is_holiday': bool,
                        'is_weekend': bool,
                        'status': str,
                    },
                    ...
                ],
                'total_work_hours': Decimal,
                'average_daily_hours': Decimal,
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
                    f"Invalid month/year for trend: month={month}, year={year}",
                    extra={"employee_id": str(employee.id)},
                )
                raise ValueError("Invalid month or year provided")

            # Get all days in the month
            num_days = calendar.monthrange(year, month)[1]
            period_start = date(year, month, 1)
            period_end = date(year, month, num_days)

            # Fetch attendance records for the month
            attendance_records = DailyAttendance.objects.filter(
                employee=employee,
                attendance_date__year=year,
                attendance_date__month=month,
                deleted_at__isnull=True,
            ).select_related("status")

            # Create dict for quick lookup
            attendance_dict = {
                record.attendance_date: record
                for record in attendance_records
            }

            # Build trend data
            trend_data = []
            total_work_mins = 0
            working_days = 0

            for day in range(1, num_days + 1):
                current_date = date(year, month, day)
                weekday = current_date.weekday()  # 0=Monday, 6=Sunday
                is_weekend = weekday >= 5  # Saturday=5, Sunday=6

                # Check if date is a holiday (can be extended with Holiday model query)
                is_holiday = False  # Can be enhanced with Holiday model lookup

                if current_date in attendance_dict:
                    record = attendance_dict[current_date]
                    # Convert minutes to hours
                    work_hours = Decimal(str(record.actual_work_mins / 60)) if record.actual_work_mins else Decimal("0.00")
                    status_name = record.status.name if record.status else "Unknown"
                    
                    if record.actual_work_mins > 0:
                        total_work_mins += record.actual_work_mins
                        working_days += 1
                else:
                    # No attendance record for this date
                    work_hours = Decimal("0.00")
                    status_name = "Absent"

                trend_item = {
                    "date": current_date,
                    "day_name": DashboardTrendService.DAY_NAMES[weekday],
                    "work_hours": round(work_hours, 2),
                    "is_holiday": is_holiday,
                    "is_weekend": is_weekend,
                    "status": status_name,
                }

                trend_data.append(trend_item)

            # Calculate aggregates
            total_work_hours = Decimal(str(total_work_mins / 60)) if total_work_mins else Decimal("0.00")
            avg_daily_hours = Decimal(
                str(total_work_mins / (working_days * 60))
            ) if working_days > 0 else Decimal("0.00")

            result = {
                "month": month,
                "year": year,
                "trend_data": trend_data,
                "total_work_hours": round(total_work_hours, 2),
                "average_daily_hours": round(avg_daily_hours, 2),
                "generated_at": timezone.now(),
            }

            logger.info(
                f"Trend data calculated for employee {employee.employee_code}",
                extra={
                    "employee_id": str(employee.id),
                    "month": month,
                    "year": year,
                },
            )

            return result

        except Exception as e:
            logger.error(
                f"Error calculating trend data: {str(e)}",
                exc_info=True,
                extra={
                    "employee_id": str(employee.id),
                    "month": month,
                    "year": year,
                },
            )
            raise
