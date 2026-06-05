"""
Nominee Details Service for Admin Side — GET and PATCH.

Business logic for:
- Fetching all nominees for an employee (with related masters preloaded)
- Updating a single nominee record (including identity_proof document fields)

All queries use Django ORM for SQL injection protection.
"""

from typing import Any, Dict, Optional

from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.employees.models.employee import Employee
from apps.employees.models.nominees import EmployeeNominee


class NomineeService:
    """Service class for nominee GET and PATCH operations on admin side."""

    @staticmethod
    def get_all_nominees(employee_id: str) -> QuerySet:
        """
        Fetch all active nominees for the given employee.

        Args:
            employee_id (str): UUID of the employee.

        Returns:
            QuerySet: Active nominees with related master data preloaded
                      to prevent N+1 queries.

        Raises:
            Http404: If employee does not exist.
        """
        employee = get_object_or_404(Employee, id=employee_id)

        return (
            EmployeeNominee.objects.filter(
                employee=employee,
                is_active=True,
            )
            .select_related(
                "relation",
                "nominee_purpose",
                "family_member",
            )
            .order_by("created_at")
        )

    @staticmethod
    @transaction.atomic
    def update_nominee(
        employee_id: str,
        nominee_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeeNominee:
        """
        Partially update an existing nominee record.

        Handles both core nominee fields and the four identity_proof columns:
            identity_proof_url
            identity_proof_name
            identity_proof_size_bytes
            identity_proof_mime_type

        Args:
            employee_id (str):     UUID of the employee.
            nominee_id (str):      UUID of the nominee record.
            validated_data (dict): Serializer-validated payload.
            updated_by:            Request user (for audit trail if needed).

        Returns:
            EmployeeNominee: The saved nominee instance.

        Raises:
            Http404: If employee or nominee not found / inactive.
        """
        employee = get_object_or_404(Employee, id=employee_id)

        nominee = get_object_or_404(
            EmployeeNominee,
            id=nominee_id,
            employee=employee,
            is_active=True,
        )

        # Apply all validated fields (partial update — only keys present)
        for key, value in validated_data.items():
            setattr(nominee, key, value)

        nominee.save()

        # Reload related objects so the response serializer has fresh labels
        nominee.refresh_from_db()
        return nominee