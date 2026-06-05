"""
Previous Employment service for admin employee details.

All database access uses Django ORM query parameters; no raw SQL is used.
This ensures SQL injection prevention throughout the service layer.
"""

from typing import Any, Dict, Optional

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.models.employee import Employee
from apps.employees.models.previous_employment import EmployeePreviousEmployment


PREVIOUS_EMPLOYMENT_RELATED_FIELDS = (
    "employee",
    "verified_by",
)


def _actor_employee(actor: Optional[Any]) -> Optional[Employee]:
    """Extract authenticated employee from request user."""
    if actor is None or not getattr(actor, "is_authenticated", True):
        return None
    return getattr(actor, "employee_profile", None)


class PreviousEmploymentService:
    """
    Service layer for Previous Employment management.
    Handles all business logic and database operations.
    """

    @staticmethod
    def list_employments(employee_id: str):
        """
        List all previous employment records for an employee.
        Uses parameterized queries to prevent SQL injection.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return (
            EmployeePreviousEmployment.objects.filter(
                employee=employee,
                is_active=True
            )
            .select_related(*PREVIOUS_EMPLOYMENT_RELATED_FIELDS)
            .order_by("-date_to", "-date_from", "-created_at")
        )

    @staticmethod
    def get_employment(employee_id: str, employment_id: str) -> EmployeePreviousEmployment:
        """
        Retrieve a specific previous employment record.
        Uses parameterized queries to prevent SQL injection.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return get_object_or_404(
            EmployeePreviousEmployment.objects.select_related(*PREVIOUS_EMPLOYMENT_RELATED_FIELDS),
            id=employment_id,
            employee=employee,
            is_active=True,
        )

    @staticmethod
    def _check_duplicate(
        employee: Employee,
        organization_name: str,
        date_from,
        date_to,
        exclude_id=None,
    ) -> None:
        """
        Check for duplicate employment records.
        Prevents adding duplicate records for the same organization/date range.
        Uses parameterized queries to prevent SQL injection.
        """
        # Check for exact duplicate (same org, dates)
        duplicates = EmployeePreviousEmployment.objects.filter(
            employee=employee,
            organization_name__iexact=organization_name.strip(),  # Case-insensitive
            date_from=date_from,
            date_to=date_to,
            is_active=True,
        )
        
        if exclude_id:
            duplicates = duplicates.exclude(id=exclude_id)

        if duplicates.exists():
            raise ValidationError({
                "organization_name": (
                    "A previous employment record for this organization with the same dates "
                    "already exists for this employee."
                )
            })

    @staticmethod
    def create_employment(
        employee_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeePreviousEmployment:
        """
        Create a new previous employment record.
        Uses transaction to ensure data integrity.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)

        # Check for duplicates
        PreviousEmploymentService._check_duplicate(
            employee,
            validated_data.get("organization_name", ""),
            validated_data.get("date_from"),
            validated_data.get("date_to"),
        )

        with transaction.atomic():
            actor_emp = _actor_employee(updated_by)
            
            employment = EmployeePreviousEmployment(
                employee=employee,
                **validated_data,
                created_by=actor_emp,
                updated_by=actor_emp,
            )
            employment.save()

        return employment

    @staticmethod
    def update_employment(
        employee_id: str,
        employment_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeePreviousEmployment:
        """
        Update an existing previous employment record.
        Uses transaction to ensure data integrity.
        """
        employment = PreviousEmploymentService.get_employment(
            employee_id,
            employment_id,
        )

        # Check for duplicates (excluding current record)
        if "organization_name" in validated_data or "date_from" in validated_data or "date_to" in validated_data:
            org_name = validated_data.get("organization_name", employment.organization_name)
            date_from = validated_data.get("date_from", employment.date_from)
            date_to = validated_data.get("date_to", employment.date_to)
            
            PreviousEmploymentService._check_duplicate(
                employment.employee,
                org_name,
                date_from,
                date_to,
                exclude_id=employment_id,
            )

        with transaction.atomic():
            actor_emp = _actor_employee(updated_by)
            
            for field, value in validated_data.items():
                setattr(employment, field, value)
            
            employment.updated_by = actor_emp
            employment.save()

        return employment

    @staticmethod
    def verify_employment(
        employee_id: str,
        employment_id: str,
        updated_by: Optional[Any] = None,
    ) -> EmployeePreviousEmployment:
        """
        Mark a previous employment record as verified.
        """
        employment = PreviousEmploymentService.get_employment(
            employee_id,
            employment_id,
        )

        actor_emp = _actor_employee(updated_by)
        
        with transaction.atomic():
            employment.is_verified = True
            employment.verified_by = actor_emp
            employment.updated_by = actor_emp
            employment.save()

        return employment

    @staticmethod
    def delete_employment(
        employee_id: str,
        employment_id: str,
        updated_by: Optional[Any] = None,
    ) -> None:
        """
        Soft-delete a previous employment record.
        """
        employment = PreviousEmploymentService.get_employment(
            employee_id,
            employment_id,
        )

        actor_emp = _actor_employee(updated_by)
        
        with transaction.atomic():
            employment.is_active = False
            employment.updated_by = actor_emp
            employment.save()

    @staticmethod
    def get_verified_employments(employee_id: str):
        """
        Get only verified previous employment records for an employee.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return (
            EmployeePreviousEmployment.objects.filter(
                employee=employee,
                is_active=True,
                is_verified=True,
            )
            .select_related(*PREVIOUS_EMPLOYMENT_RELATED_FIELDS)
            .order_by("-date_to", "-date_from")
        )

    @staticmethod
    def get_unverified_employments(employee_id: str):
        """
        Get only unverified previous employment records for an employee.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return (
            EmployeePreviousEmployment.objects.filter(
                employee=employee,
                is_active=True,
                is_verified=False,
            )
            .select_related(*PREVIOUS_EMPLOYMENT_RELATED_FIELDS)
            .order_by("-date_to", "-date_from")
        )

    @staticmethod
    def bulk_verify_employments(employee_id: str, updated_by: Optional[Any] = None) -> int:
        """
        Verify all unverified employment records for an employee.
        Returns the count of records updated.
        """
        actor_emp = _actor_employee(updated_by)
        
        count = EmployeePreviousEmployment.objects.filter(
            employee_id=employee_id,
            is_active=True,
            is_verified=False,
        ).update(
            is_verified=True,
            verified_by=actor_emp,
            updated_by=actor_emp,
        )
        
        return count
