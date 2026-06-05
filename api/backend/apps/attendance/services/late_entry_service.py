"""
Late Entry Service Layer.

Provides business logic for late login cycle tracking, leaderboard calculation,
late entry listings, and summary analytics.
"""

import logging
from datetime import datetime, date
from uuid import UUID
from typing import Optional, Dict, Any, List

from django.db import transaction
from django.db.models import Q, Count, Avg, Max, F
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.employees.models import Employee
from apps.attendance.models import (
    DailyAttendance,
    LateLoginCycleTracker,
    AttendancePolicy,
)

logger = logging.getLogger(__name__)


class LateEntryService:
    """Service for late entry analytics and tracking."""

    @staticmethod
    def get_late_entries(
        company_id: UUID,
        from_date: date,
        to_date: date,
        department_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None,
        min_late_mins: Optional[int] = None,
        max_late_mins: Optional[int] = None,
        grace_consumed: Optional[bool] = None,
    ):
        """
        Query late daily attendance records with policy context.
        """
        try:
            # Query DailyAttendance records that are late (is_late=True)
            queryset = DailyAttendance.objects.filter(
                company_id=company_id,
                attendance_date__range=[from_date, to_date],
                is_late=True
            )
            from apps.attendance.utils.employee_relations import defer_employment_team

            queryset = defer_employment_team(
                queryset.select_related(
                    "employee",
                    "employee__employment_details",
                    "employee__employment_details__department",
                    "shift",
                    "policy",
                )
            )

            # Apply optional filters
            if department_id:
                queryset = queryset.filter(
                    employee__employment_details__department_id=department_id
                )

            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)

            if min_late_mins is not None:
                queryset = queryset.filter(late_in_mins__gte=min_late_mins)

            if max_late_mins is not None:
                queryset = queryset.filter(late_in_mins__lte=max_late_mins)

            if grace_consumed is not None:
                queryset = queryset.filter(is_grace=grace_consumed)

            # Order by attendance date descending and employee name
            queryset = queryset.order_by("-attendance_date", "employee__first_name")

            return queryset
        except Exception as e:
            logger.error(f"Error fetching late entries: {str(e)}", exc_info=True)
            raise ValidationError(f"Error retrieving late entries: {str(e)}")

    @staticmethod
    def get_late_entries_summary(
        company_id: UUID,
        date_val: Optional[date] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        department_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Get summary analytics for late entries.
        """
        try:
            # Resolve date range
            if from_date and to_date:
                start_date = from_date
                end_date = to_date
            elif date_val:
                start_date = date_val
                end_date = date_val
            else:
                # Default to current month's start date and today
                end_date = timezone.now().date()
                start_date = end_date.replace(day=1)

            # Base query on DailyAttendance
            base_records = DailyAttendance.objects.filter(
                company_id=company_id,
                attendance_date__range=[start_date, end_date]
            )

            if department_id:
                base_records = base_records.filter(
                    employee__employment_details__department_id=department_id
                )

            # Late records subset
            late_records = base_records.filter(is_late=True)

            total_late = late_records.count()
            avg_late_mins = late_records.aggregate(avg=Avg("late_in_mins"))["avg"] or 0
            max_late_mins = late_records.aggregate(max=Max("late_in_mins"))["max"] or 0
            grace_consumed_count = base_records.filter(is_grace=True).count()

            # Half day triggered count from tracker in this range
            tracker_qs = LateLoginCycleTracker.objects.filter(
                employee__company_id=company_id,
                half_day_triggered_date__range=[start_date, end_date]
            )
            if department_id:
                tracker_qs = tracker_qs.filter(
                    employee__employment_details__department_id=department_id
                )
            half_day_triggered_count = tracker_qs.count()

            # Group late records by department
            dept_counts = (
                late_records.values(
                    dept_name=F("employee__employment_details__department__name")
                )
                .annotate(late_count=Count("id"))
                .order_by("-late_count")
            )

            by_department = []
            for item in dept_counts:
                dept_name = item.get("dept_name") or "Unknown"
                by_department.append({
                    "dept": dept_name,
                    "late_count": item.get("late_count", 0)
                })

            return {
                "total_late": total_late,
                "avg_late_mins": round(float(avg_late_mins), 2),
                "max_late_mins": max_late_mins,
                "grace_consumed_count": grace_consumed_count,
                "half_day_triggered_count": half_day_triggered_count,
                "by_department": by_department,
            }
        except Exception as e:
            logger.error(f"Error generating late entries summary: {str(e)}", exc_info=True)
            raise ValidationError(f"Error generating late entry summary: {str(e)}")

    @staticmethod
    def get_late_cycle_tracker(
        employee_id: UUID,
        company_id: UUID,
        cycle_month_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get late cycle tracker state for an employee.
        """
        try:
            # Parse cycle month
            if cycle_month_str:
                try:
                    dt = datetime.strptime(cycle_month_str, "%Y-%m")
                    cycle_month = dt.date()
                except ValueError:
                    raise ValidationError("cycle_month must be in YYYY-MM format.")
            else:
                cycle_month = timezone.now().date().replace(day=1)

            # Check if employee exists and belongs to company
            employee = Employee.objects.filter(id=employee_id, company_id=company_id).first()
            if not employee:
                raise ValidationError("Employee not found or does not belong to the requested company.")

            # Look up tracker
            tracker = LateLoginCycleTracker.objects.filter(
                employee_id=employee_id,
                cycle_month=cycle_month
            ).select_related("policy").first()

            if not tracker:
                # Fallback to active policy values
                policy = AttendancePolicy.objects.filter(
                    company_id=company_id,
                    is_current=True,
                    is_active=True
                ).first()

                return {
                    "employee_id": employee_id,
                    "policy_id": policy.id if policy else None,
                    "cycle_month": cycle_month.strftime("%Y-%m"),
                    "cycle_number": 1,
                    "late_count": 0,
                    "cycle_limit": policy.late_login_cycle_limit if policy else 3,
                    "is_cycle_closed": False,
                    "half_day_triggered_date": None,
                }

            return {
                "employee_id": tracker.employee_id,
                "policy_id": tracker.policy_id,
                "cycle_month": tracker.cycle_month.strftime("%Y-%m"),
                "cycle_number": tracker.cycle_number,
                "late_count": tracker.late_count,
                "cycle_limit": tracker.policy.late_login_cycle_limit if tracker.policy else 3,
                "is_cycle_closed": tracker.is_cycle_closed,
                "half_day_triggered_date": tracker.half_day_triggered_date,
            }
        except ValidationError as ve:
            raise ve
        except Exception as e:
            logger.error(f"Error fetching late cycle tracker: {str(e)}", exc_info=True)
            raise ValidationError(f"Error retrieving cycle tracker: {str(e)}")

    @staticmethod
    def get_leaderboard(
        company_id: UUID,
        from_date: date,
        to_date: date,
        department_id: Optional[UUID] = None,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get late entry leaderboard for management.
        """
        try:
            # Query late records
            late_records = DailyAttendance.objects.filter(
                company_id=company_id,
                attendance_date__range=[from_date, to_date],
                is_late=True
            )

            if department_id:
                late_records = late_records.filter(
                    employee__employment_details__department_id=department_id
                )

            # Group by employee
            grouped = (
                late_records.values("employee_id")
                .annotate(
                    total_late_days=Count("id"),
                    avg_late_mins=Avg("late_in_mins")
                )
                .order_by("-total_late_days", "-avg_late_mins")
            )

            # Retrieve only top N IDs to optimize employee fetching
            top_groups = list(grouped[:top_n])
            employee_ids = [item["employee_id"] for item in top_groups]

            # Fetch employee names in bulk
            employees = Employee.objects.filter(id__in=employee_ids).only(
                "id", "first_name", "last_name"
            )
            employee_map = {
                emp.id: f"{emp.first_name} {emp.last_name}".strip()
                for emp in employees
            }

            # Fetch half days triggered in bulk in this range
            half_days = LateLoginCycleTracker.objects.filter(
                employee_id__in=employee_ids,
                half_day_triggered_date__range=[from_date, to_date]
            ).values("employee_id").annotate(count=Count("id"))

            half_days_map = {item["employee_id"]: item["count"] for item in half_days}

            leaderboard = []
            for item in top_groups:
                emp_id = item["employee_id"]
                leaderboard.append({
                    "employee_id": emp_id,
                    "employee_name": employee_map.get(emp_id, "Unknown Employee"),
                    "total_late_days": item["total_late_days"],
                    "avg_late_mins": round(float(item["avg_late_mins"] or 0), 2),
                    "half_days_triggered": half_days_map.get(emp_id, 0),
                })

            return leaderboard
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {str(e)}", exc_info=True)
            raise ValidationError(f"Error generating leaderboard: {str(e)}")
