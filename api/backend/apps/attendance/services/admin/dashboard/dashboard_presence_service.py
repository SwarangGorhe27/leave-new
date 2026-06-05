"""Dashboard Presence Service - Live employee presence tracking."""

import logging
from datetime import date, datetime, timedelta, time
from decimal import Decimal
from typing import Dict, Any, List
from datetime import datetime as dt

from django.db.models import Q, Case, When, Value, CharField, F
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.attendance.models import DailyAttendance, PunchLog
from apps.employees.models import Employee, EmployeeEmploymentDetails

logger = logging.getLogger(__name__)


class DashboardPresenceService:
    """
    Business logic for live employee presence.
    
    Handles:
    - Today's employee presence detection
    - Check-in time tracking
    - Work hours calculation
    - Late arrival flagging
    - Pagination
    """

    @staticmethod
    def get_whos_in_today(company) -> Dict[str, Any]:
        """
        Get who's in today widget data.

        Args:
            company: Company instance

        Returns:
            Dictionary containing:
            {
                'on_time_count': int,
                'late_in_count': int,
                'not_yet_in_count': int,
                'total_employee_count': int,
                'employee_list': [...],
                'generated_at': datetime,
            }
        """
        try:
            today = date.today()
            now = timezone.now()

            # Get all active employees in the company
            active_employees = Employee.objects.filter(
                company=company,
                status=Employee.StatusChoices.ACTIVE,
                deleted_at__isnull=True,
            )
            from apps.attendance.utils.employee_relations import with_employee_org

            active_employees = with_employee_org(active_employees)

            employee_list = []
            on_time_count = 0
            late_in_count = 0
            not_yet_in_count = 0

            for emp in active_employees:
                # Try to get today's attendance
                try:
                    attendance = DailyAttendance.objects.get(
                        employee=emp,
                        attendance_date=today,
                        deleted_at__isnull=True,
                    )

                    # Get latest punch-in for today
                    first_punch = PunchLog.objects.filter(
                        employee=emp,
                        punch_time__date=today,
                        punch_type="IN",
                    ).order_by("punch_time").first()

                    if first_punch:
                        check_in_time = first_punch.punch_time.time()
                        is_late = attendance.is_late
                        status = "Late" if is_late else "On Time"
                        
                        if is_late:
                            late_in_count += 1
                        else:
                            on_time_count += 1

                        # Calculate work hours so far
                        work_hours = Decimal(str(attendance.actual_work_mins / 60)) \
                            if attendance.actual_work_mins else Decimal("0.00")
                    else:
                        check_in_time = None
                        status = "Not Yet In"
                        work_hours = Decimal("0.00")
                        not_yet_in_count += 1

                except DailyAttendance.DoesNotExist:
                    # No attendance record, check punches
                    first_punch = PunchLog.objects.filter(
                        employee=emp,
                        punch_time__date=today,
                        punch_type="IN",
                    ).order_by("punch_time").first()

                    if first_punch:
                        check_in_time = first_punch.punch_time.time()
                        status = "Checked In"
                        work_hours = Decimal("0.00")
                        on_time_count += 1
                    else:
                        check_in_time = None
                        status = "Not Yet In"
                        work_hours = Decimal("0.00")
                        not_yet_in_count += 1

                # Build employee presence item
                try:
                    emp_details = emp.employment_details
                except Exception:
                    emp_details = None
                employee_list.append({
                    "employee_id": emp.id,
                    "employee_code": emp.employee_code,
                    "employee_name": f"{emp.first_name} {emp.last_name}",
                    "designation": (
                        emp_details.designation.title
                        if emp_details and emp_details.designation
                        else "N/A"
                    ),
                    "department": (
                        emp_details.department.name
                        if emp_details and emp_details.department
                        else "N/A"
                    ),
                    "check_in_time": check_in_time,
                    "status": status,
                    "work_hours": round(work_hours, 2),
                    "is_late": status == "Late",
                })

            result = {
                "on_time_count": on_time_count,
                "late_in_count": late_in_count,
                "not_yet_in_count": not_yet_in_count,
                "total_employee_count": on_time_count + late_in_count + not_yet_in_count,
                "employee_list": employee_list,
                "generated_at": timezone.now(),
            }

            logger.info(
                f"Who's in today calculated for company {company.code}",
                extra={
                    "company_id": str(company.id),
                    "total_count": result["total_employee_count"],
                },
            )

            return result

        except Exception as e:
            logger.error(
                f"Error calculating who's in today: {str(e)}",
                exc_info=True,
                extra={"company_id": str(company.id)},
            )
            raise

    @staticmethod
    def get_employee_presence(
        company,
    ) -> Dict[str, Any]:
        """
        Get employee presence list without pagination.

        Args:
            company: Company instance

        Returns:
            Dictionary containing presence list
        """
        try:
            today = date.today()

            # Get all active employees
            active_employees = Employee.objects.filter(
                company=company,
                status=Employee.StatusChoices.ACTIVE,
                deleted_at__isnull=True,
            )
            from apps.attendance.utils.employee_relations import with_employee_org

            active_employees = with_employee_org(active_employees).order_by("employee_code")

            employee_list = []

            for emp in active_employees:
                # Get today's attendance
                try:
                    attendance = DailyAttendance.objects.get(
                        employee=emp,
                        attendance_date=today,
                        deleted_at__isnull=True,
                    )

                    first_punch = PunchLog.objects.filter(
                        employee=emp,
                        punch_time__date=today,
                        punch_type="IN",
                    ).order_by("punch_time").first()

                    check_in_time = first_punch.punch_time.time() if first_punch else None
                    is_late = attendance.is_late
                    status = "Late" if is_late else "On Time" if check_in_time else "Not Yet In"
                    work_hours = Decimal(str(attendance.actual_work_mins / 60)) \
                        if attendance.actual_work_mins else Decimal("0.00")

                except DailyAttendance.DoesNotExist:
                    first_punch = PunchLog.objects.filter(
                        employee=emp,
                        punch_time__date=today,
                        punch_type="IN",
                    ).order_by("punch_time").first()

                    check_in_time = first_punch.punch_time.time() if first_punch else None
                    status = "Checked In" if first_punch else "Not Yet In"
                    work_hours = Decimal("0.00")
                    is_late = False

                emp_details = emp.employment_details
                employee_list.append({
                    "employee_id": emp.id,
                    "employee_code": emp.employee_code,
                    "employee_name": f"{emp.first_name} {emp.last_name}",
                    "designation": emp_details.designation.title if emp_details.designation else "N/A",
                    "department": emp_details.department.name if emp_details.department else "N/A",
                    "check_in_time": check_in_time,
                    "status": status,
                    "work_hours": round(work_hours, 2),
                    "is_late": is_late,
                })

            result = {
                "results": employee_list,
                "generated_at": timezone.now(),
            }

            logger.info(
                f"Employee presence retrieved for company {company.code}",
                extra={
                    "company_id": str(company.id),
                },
            )

            return result

        except Exception as e:
            logger.error(
                f"Error fetching employee presence: {str(e)}",
                exc_info=True,
                extra={
                    "company_id": str(company.id),
                    "page": page,
                },
            )
            raise
