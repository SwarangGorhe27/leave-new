from typing import Any, Dict, List

from django.apps import apps
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .base_service import BaseLeaveService


class HolidayService(BaseLeaveService):
    @staticmethod
    def list_admin_holidays(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        holiday_calendar_model = apps.get_model("employees", "HolidayCalendar")
        holiday_model = apps.get_model("employees", "Holiday")

        calendar_queryset = holiday_calendar_model.objects.filter(is_active=True)

        if filters.get("branch_id"):
            calendar_queryset = calendar_queryset.filter(branch_id=filters["branch_id"])

        if filters.get("year"):
            calendar_queryset = calendar_queryset.filter(calendar_year=filters["year"])

        calendars = {
            calendar.id: calendar
            for calendar in calendar_queryset.order_by("calendar_year", "name")
        }

        if not calendars:
            return []

        holiday_queryset = holiday_model.objects.filter(
            is_active=True,
            holiday_calendar_id__in=list(calendars.keys()),
        ).order_by("holiday_date", "name")

        if filters.get("year"):
            holiday_queryset = holiday_queryset.filter(
                holiday_date__year=filters["year"]
            )

        holidays = []
        for holiday in holiday_queryset:
            calendar = calendars.get(holiday.holiday_calendar_id)
            if not calendar:
                continue

            holidays.append(
                {
                    "id": holiday.id,
                    "holiday_calendar_id": holiday.holiday_calendar_id,
                    "calendar": {
                        "id": calendar.id,
                        "code": calendar.code,
                        "name": calendar.name,
                        "calendar_year": calendar.calendar_year,
                        "branch_id": calendar.branch_id,
                    },
                    "holiday_date": holiday.holiday_date,
                    "name": holiday.name,
                    "holiday_type": holiday.holiday_type,
                    "is_active": holiday.is_active,
                }
            )

        return holidays

    @staticmethod
    @transaction.atomic
    def create_admin_holiday(
        data: Dict[str, Any],
        company_id,
        user_id=None,
    ) -> List[Dict[str, Any]]:
        if not company_id:
            raise ValidationError({"company_id": "Unable to resolve company_id."})

        branch_model = apps.get_model("employees", "Branch")
        holiday_calendar_model = apps.get_model("employees", "HolidayCalendar")
        holiday_model = apps.get_model("employees", "Holiday")
        holiday_branch_map_model = apps.get_model("leave", "HolidayBranchMap")

        branch_ids = data["branch_ids"]
        branches = {
            branch.id: branch
            for branch in branch_model.objects.filter(
                id__in=branch_ids,
                company_id=company_id,
                is_active=True,
            )
        }

        missing_branch_ids = [
            str(branch_id) for branch_id in branch_ids if branch_id not in branches
        ]
        if missing_branch_ids:
            raise ValidationError(
                {
                    "branch_ids": (
                        "Invalid or inactive branch IDs for this company: "
                        + ", ".join(missing_branch_ids)
                    )
                }
            )

        holiday_date = data["date"]
        year = holiday_date.year
        created_holidays = []

        for branch_id in branch_ids:
            branch = branches[branch_id]
            calendar = HolidayService._get_or_create_branch_calendar(
                holiday_calendar_model,
                company_id,
                year,
                branch,
                user_id,
            )

            holiday, _ = holiday_model.objects.update_or_create(
                holiday_calendar_id=calendar.id,
                holiday_date=holiday_date,
                defaults={
                    "name": data["name"],
                    "holiday_type": data["type"],
                    "is_active": True,
                    "updated_by": user_id,
                },
            )

            if user_id and not holiday.created_by:
                holiday.created_by = user_id
                holiday.save(update_fields=["created_by", "updated_at"])

            holiday_branch_map_model.objects.get_or_create(
                holiday=calendar,
                branch=branch,
            )

            created_holidays.append(
                {
                    "id": str(holiday.id),
                    "holiday_calendar_id": str(calendar.id),
                    "branch_id": str(branch.id),
                    "holiday_date": holiday.holiday_date,
                    "name": holiday.name,
                    "holiday_type": holiday.holiday_type,
                }
            )

        return created_holidays

    @staticmethod
    def _get_or_create_branch_calendar(
        holiday_calendar_model,
        company_id,
        year,
        branch,
        user_id=None,
    ):
        calendar = (
            holiday_calendar_model.objects.filter(
                company_id=company_id,
                calendar_year=year,
                branch_id=branch.id,
                is_active=True,
            )
            .order_by("name")
            .first()
        )

        if calendar:
            return calendar

        return holiday_calendar_model.objects.create(
            company_id=company_id,
            code=f"HCAL-{year}-{str(branch.id)[:8]}",
            name=f"{branch.name} Holiday Calendar {year}",
            calendar_year=year,
            branch_id=branch.id,
            is_active=True,
            created_by=user_id,
            updated_by=user_id,
        )
