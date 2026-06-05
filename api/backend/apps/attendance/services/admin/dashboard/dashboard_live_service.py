"""Dashboard Live Service - Lightweight live polling endpoint."""

import logging
from datetime import date
from typing import Dict, Any

from django.db.models import Count, Q
from django.utils import timezone

from apps.attendance.models import DailyAttendance, PunchLog
from apps.employees.models import Employee

logger = logging.getLogger(__name__)


class DashboardLiveService:
    """
    Business logic for live polling dashboard counts.
    
    Optimized for:
    - Lightweight queries
    - Minimal DB load
    - Fast response times
    - Real-time count updates
    """

    @staticmethod
    def get_live_dashboard_counts(company) -> Dict[str, Any]:
        """
        Get lightweight live dashboard counts.

        Args:
            company: Company instance

        Returns:
            Dictionary containing:
            {
                'present_count': int,
                'late_count': int,
                'not_yet_in_count': int,
                'total_count': int,
                'generated_at': datetime,
            }
        """
        try:
            today = date.today()

            # Get count of employees with punch-in today
            punch_ins_today = PunchLog.objects.filter(
                company=company,
                punch_time__date=today,
                punch_type="IN",
            ).values("employee_id").distinct().count()

            # Get count of late employees from daily attendance
            late_count = DailyAttendance.objects.filter(
                company_id=company.id,
                attendance_date=today,
                is_late=True,
                deleted_at__isnull=True,
            ).count()

            # Get count of active employees
            total_employee_count = Employee.objects.filter(
                company=company,
                status=Employee.StatusChoices.ACTIVE,
                deleted_at__isnull=True,
            ).count()

            # On-time count = punch-ins - late
            on_time_count = punch_ins_today - late_count
            if on_time_count < 0:
                on_time_count = 0

            # Not yet in = total - checked in
            not_yet_in_count = total_employee_count - punch_ins_today

            result = {
                "present_count": on_time_count,
                "late_count": late_count,
                "not_yet_in_count": not_yet_in_count,
                "total_count": total_employee_count,
                "generated_at": timezone.now(),
            }

            logger.debug(
                f"Live dashboard counts calculated for company {company.code}",
                extra={
                    "company_id": str(company.id),
                    "on_time": on_time_count,
                    "late": late_count,
                    "not_yet_in": not_yet_in_count,
                },
            )

            return result

        except Exception as e:
            logger.error(
                f"Error calculating live dashboard counts: {str(e)}",
                exc_info=True,
                extra={"company_id": str(company.id)},
            )
            raise
