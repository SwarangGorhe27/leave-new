"""Service for Shift Roster Summary and Analytics."""

import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from calendar import monthrange

from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone

from apps.attendance.models import EmployeeShiftRoster, ShiftDefinition
from apps.employees.models import Company
from apps.attendance.models.enums import ShiftFamily

logger = logging.getLogger(__name__)


class RosterSummaryService:
    """
    Service for roster analytics and summary generation.
    
    Handles:
    - Monthly analytics
    - Department distribution
    - Shift type distribution
    - Employee summaries
    """

    @staticmethod
    def get_roster_summary(
        company: Company,
        month: int,
        year: int,
        department_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive roster summary for a month.
        
        Args:
            company: Company instance
            month: Month number (1-12)
            year: Year
            department_id: Filter by department (optional)
            
        Returns:
            Dictionary with roster statistics
        """
        try:
            logger.info(
                f"Generating roster summary for {month}/{year}",
                extra={
                    "company_id": str(company.id),
                    "month": month,
                    "year": year,
                },
            )

            # Get date range for month
            first_day = date(year, month, 1)
            last_day = date(year, month, monthrange(year, month)[1])

            # Build base queryset
            queryset = EmployeeShiftRoster.objects.filter(
                company=company,
                roster_date__gte=first_day,
                roster_date__lte=last_day,
                deleted_at__isnull=True,
            ).select_related("employee", "shift", "employee__department")

            if department_id:
                queryset = queryset.filter(employee__department_id=department_id)

            # Count metrics by shift type
            shift_metrics = queryset.values("shift__shift_type").annotate(
                count=Count("id")
            )

            shift_counts = {}
            for metric in shift_metrics:
                shift_type = metric["shift__shift_type"]
                shift_counts[shift_type] = metric["count"]

            # Calculate totals
            total_rosters = queryset.count()
            total_employees = queryset.values("employee").distinct().count()
            total_week_offs = queryset.filter(is_week_off=True).count()
            total_working_days = total_rosters - total_week_offs

            # Department distribution
            dept_distribution = {}
            dept_data = (
                queryset
                .values("employee__department__name")
                .annotate(count=Count("id"))
                .order_by("employee__department__name")
            )
            for item in dept_data:
                dept_name = item["employee__department__name"] or "Unassigned"
                dept_distribution[dept_name] = item["count"]

            # Shift distribution
            shift_distribution = {}
            for shift_type in ShiftFamily.choices:
                shift_code = shift_type[0]
                shift_distribution[shift_code] = shift_counts.get(shift_code, 0)

            summary = {
                "company_id": str(company.id),
                "period": f"{year}-{month:02d}",
                "date_range": {
                    "from_date": first_day.isoformat(),
                    "to_date": last_day.isoformat(),
                    "days": (last_day - first_day).days + 1,
                },
                "total_employees": total_employees,
                "night_shift_count": shift_counts.get(ShiftFamily.NIGHT, 0),
                "rotational_count": shift_counts.get(ShiftFamily.ROTATIONAL, 0),
                "flexible_count": shift_counts.get(ShiftFamily.FLEXIBLE, 0),
                "split_shift_count": shift_counts.get(ShiftFamily.SPLIT, 0),
                "fixed_shift_count": shift_counts.get(ShiftFamily.FIXED, 0),
                "total_rosters": total_rosters,
                "total_working_days": total_working_days,
                "total_week_offs": total_week_offs,
                "department_distribution": dept_distribution,
                "shift_distribution": shift_distribution,
            }

            logger.debug(
                f"Roster summary generated for {month}/{year}",
                extra={
                    "company_id": str(company.id),
                    "total_rosters": total_rosters,
                    "total_employees": total_employees,
                },
            )

            return summary

        except Exception as e:
            logger.error(
                f"Error generating roster summary: {str(e)}",
                extra={"company_id": str(company.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def get_department_summary(
        company: Company,
        month: int,
        year: int,
    ) -> List[Dict[str, Any]]:
        """
        Get department-wise roster summary.
        
        Args:
            company: Company instance
            month: Month number
            year: Year
            
        Returns:
            List of department summaries
        """
        try:
            logger.info(
                f"Generating department summary for {month}/{year}",
                extra={
                    "company_id": str(company.id),
                    "month": month,
                    "year": year,
                },
            )

            first_day = date(year, month, 1)
            last_day = date(year, month, monthrange(year, month)[1])

            dept_data = (
                EmployeeShiftRoster.objects
                .filter(
                    company=company,
                    roster_date__gte=first_day,
                    roster_date__lte=last_day,
                    deleted_at__isnull=True,
                )
                .values(
                    "employee__department__id",
                    "employee__department__name",
                )
                .annotate(
                    total_employees=Count("employee", distinct=True),
                    working_days=Count(
                        Case(
                            When(is_week_off=False, then=1),
                            output_field=IntegerField(),
                        )
                    ),
                    week_offs=Count(
                        Case(
                            When(is_week_off=True, then=1),
                            output_field=IntegerField(),
                        )
                    ),
                    night_shifts=Count(
                        Case(
                            When(shift__shift_type=ShiftFamily.NIGHT, then=1),
                            output_field=IntegerField(),
                        )
                    ),
                )
                .order_by("employee__department__name")
            )

            summaries = []
            for dept in dept_data:
                summaries.append({
                    "department_id": str(dept["employee__department__id"]) if dept["employee__department__id"] else "unassigned",
                    "department_name": dept["employee__department__name"] or "Unassigned",
                    "total_employees": dept["total_employees"],
                    "working_days": dept["working_days"],
                    "week_offs": dept["week_offs"],
                    "night_shifts": dept["night_shifts"],
                })

            return summaries

        except Exception as e:
            logger.error(
                f"Error generating department summary: {str(e)}",
                extra={"company_id": str(company.id)},
                exc_info=True,
            )
            raise

    @staticmethod
    def get_employee_roster_summary(
        company: Company,
        employee_id: str,
        month: int,
        year: int,
    ) -> Dict[str, Any]:
        """
        Get employee-specific roster summary.
        
        Args:
            company: Company instance
            employee_id: Employee UUID
            month: Month number
            year: Year
            
        Returns:
            Employee roster summary
        """
        try:
            logger.info(
                f"Generating employee roster summary for {month}/{year}",
                extra={
                    "company_id": str(company.id),
                    "employee_id": employee_id,
                    "month": month,
                    "year": year,
                },
            )

            first_day = date(year, month, 1)
            last_day = date(year, month, monthrange(year, month)[1])

            rosters = (
                EmployeeShiftRoster.objects
                .filter(
                    company=company,
                    employee_id=employee_id,
                    roster_date__gte=first_day,
                    roster_date__lte=last_day,
                    deleted_at__isnull=True,
                )
                .select_related("employee", "shift")
            )

            total_rosters = rosters.count()
            working_days = rosters.filter(is_week_off=False).count()
            week_offs = rosters.filter(is_week_off=True).count()

            # Get latest shift
            latest_roster = rosters.order_by("-roster_date").first()
            current_shift = latest_roster.shift.code if latest_roster else None

            summary = {
                "employee_id": employee_id,
                "month": f"{year}-{month:02d}",
                "total_rosters": total_rosters,
                "working_days": working_days,
                "week_offs": week_offs,
                "current_shift": current_shift,
            }

            return summary

        except Exception as e:
            logger.error(
                f"Error generating employee roster summary: {str(e)}",
                extra={
                    "company_id": str(company.id),
                    "employee_id": employee_id,
                },
                exc_info=True,
            )
            raise
