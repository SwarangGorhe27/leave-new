"""
Position history service for admin employee details.

All database access uses Django ORM query parameters; no raw SQL is used.
"""

from datetime import timedelta
from typing import Any, Dict, Optional

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.models.employee import Employee
from apps.employees.models.position_history import EmployeePositionHistory


POSITION_HISTORY_RELATED_FIELDS = (
    "designation",
    "department",
    "grade",
    "branch",
    "reporting_to",
    "reporting_to__employee",
    "reporting_to__designation",
)


def _actor_employee(actor: Optional[Any]) -> Optional[Employee]:
    if actor is None or not getattr(actor, "is_authenticated", True):
        return None
    return getattr(actor, "employee_profile", None)


class PositionHistoryService:
    @staticmethod
    def list_positions(employee_id: str):
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return (
            EmployeePositionHistory.objects.filter(employee=employee, is_active=True)
            .select_related(*POSITION_HISTORY_RELATED_FIELDS)
            .order_by("-effective_from", "-created_at")
        )

    @staticmethod
    def get_position(employee_id: str, position_history_id: str) -> EmployeePositionHistory:
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return get_object_or_404(
            EmployeePositionHistory.objects.select_related(*POSITION_HISTORY_RELATED_FIELDS),
            id=position_history_id,
            employee=employee,
            is_active=True,
        )

    @staticmethod
    def _ensure_no_overlap(
        employee: Employee,
        effective_from,
        effective_to,
        exclude_id=None,
    ) -> None:
        requested_end = effective_to
        overlapping = EmployeePositionHistory.objects.filter(
            employee=employee,
            is_active=True,
        )
        if exclude_id:
            overlapping = overlapping.exclude(id=exclude_id)

        if requested_end is None:
            overlapping = overlapping.filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=effective_from)
            )
        else:
            overlapping = overlapping.filter(effective_from__lte=requested_end).filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=effective_from)
            )

        if overlapping.exists():
            raise ValidationError(
                {
                    "effective_from": (
                        "Position period overlaps with an existing position history row "
                        "for this employee."
                    )
                }
            )

    @staticmethod
    def _close_previous_current(employee: Employee, effective_from, exclude_id=None) -> None:
        previous_current = EmployeePositionHistory.objects.filter(
            employee=employee,
            effective_to__isnull=True,
            is_active=True,
        )
        if exclude_id:
            previous_current = previous_current.exclude(id=exclude_id)

        close_date = effective_from - timedelta(days=1)
        previous_current.filter(effective_from__lt=effective_from).update(
            effective_to=close_date
        )

    @staticmethod
    @transaction.atomic
    def create_position(
        employee_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeePositionHistory:
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        effective_from = validated_data["effective_from"]
        effective_to = validated_data.get("effective_to")

        if effective_to is None:
            PositionHistoryService._close_previous_current(employee, effective_from)

        PositionHistoryService._ensure_no_overlap(employee, effective_from, effective_to)

        position = EmployeePositionHistory(employee=employee, **validated_data)
        actor_employee = _actor_employee(updated_by)
        if actor_employee is not None:
            position.changed_by = actor_employee

        position.save()
        return PositionHistoryService.get_position(employee_id, position.id)

    @staticmethod
    @transaction.atomic
    def update_position(
        employee_id: str,
        position_history_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeePositionHistory:
        position = PositionHistoryService.get_position(employee_id, position_history_id)
        effective_from = validated_data.get("effective_from", position.effective_from)
        effective_to = (
            validated_data["effective_to"]
            if "effective_to" in validated_data
            else position.effective_to
        )

        if effective_to is None:
            PositionHistoryService._close_previous_current(
                position.employee,
                effective_from,
                exclude_id=position.id,
            )

        PositionHistoryService._ensure_no_overlap(
            position.employee,
            effective_from,
            effective_to,
            exclude_id=position.id,
        )

        for field, value in validated_data.items():
            setattr(position, field, value)

        actor_employee = _actor_employee(updated_by)
        if actor_employee is not None:
            position.changed_by = actor_employee

        position.save()
        return PositionHistoryService.get_position(employee_id, position.id)
