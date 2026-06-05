"""
Employee Asset service for admin employee details.

All database access uses Django ORM query parameters; no raw SQL is used.
This ensures SQL injection prevention throughout the service layer.
"""

from typing import Any, Dict, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.models.employee import Employee
from apps.employees.models.assets import EmployeeAsset


ASSET_RELATED_FIELDS = (
    "employee",
    "asset_category",
    "asset_condition",
)


def _actor_employee(actor: Optional[Any]) -> Optional[Employee]:
    """Extract authenticated employee from request user."""
    if actor is None or not getattr(actor, "is_authenticated", True):
        return None
    return getattr(actor, "employee_profile", None)


class EmployeeAssetService:
    """
    Service layer for Employee Asset management.
    Handles all business logic and database operations.
    """

    @staticmethod
    def list_assets(employee_id: str):
        """
        List all active asset assignments for an employee.
        Uses parameterized queries to prevent SQL injection.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return (
            EmployeeAsset.objects.filter(
                employee=employee,
                is_active=True
            )
            .select_related(*ASSET_RELATED_FIELDS)
            .order_by("-assign_date", "-created_at")
        )

    @staticmethod
    def get_asset(employee_id: str, asset_id: str) -> EmployeeAsset:
        """
        Retrieve a specific asset assignment record.
        Uses parameterized queries to prevent SQL injection.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return get_object_or_404(
            EmployeeAsset.objects.select_related(*ASSET_RELATED_FIELDS),
            id=asset_id,
            employee=employee,
            is_active=True,
        )

    @staticmethod
    def _check_duplicate(
        employee: Employee,
        asset_code: str,
        exclude_id=None,
    ) -> None:
        """
        Check for duplicate asset assignment by asset_code.
        Prevents duplicate active assignments of the same asset code.
        Uses parameterized queries to prevent SQL injection.
        """
        if not asset_code:
            return
            
        duplicates = EmployeeAsset.objects.filter(
            employee=employee,
            asset_code__iexact=asset_code.strip(),
            is_active=True,
        )
        
        if exclude_id:
            duplicates = duplicates.exclude(id=exclude_id)

        if duplicates.exists():
            raise ValidationError({
                "assetId": (
                    "An active asset assignment with this Asset ID "
                    "already exists for this employee."
                )
            })

    @staticmethod
    def create_asset(
        employee_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeeAsset:
        """
        Create a new employee asset assignment.
        Uses database transaction to ensure data integrity.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)

        # Check for duplicates
        EmployeeAssetService._check_duplicate(
            employee,
            validated_data.get("asset_code", ""),
        )

        if not validated_data.get("status"):
            validated_data["status"] = EmployeeAsset.StatusChoices.ASSIGNED

        with transaction.atomic():
            asset = EmployeeAsset(
                employee=employee,
                **validated_data,
            )
            asset.save()

        # Reload related fields for representation
        return EmployeeAssetService.get_asset(employee_id, asset.id)

    @staticmethod
    def update_asset(
        employee_id: str,
        asset_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> EmployeeAsset:
        """
        Update an existing asset assignment record.
        Uses database transaction to ensure data integrity.
        """
        asset = EmployeeAssetService.get_asset(
            employee_id,
            asset_id,
        )

        # Check for duplicates (excluding current record)
        if "asset_code" in validated_data:
            EmployeeAssetService._check_duplicate(
                asset.employee,
                validated_data.get("asset_code"),
                exclude_id=asset_id,
            )

        with transaction.atomic():
            for field, value in validated_data.items():
                setattr(asset, field, value)
            
            asset.save()

        # Reload related fields for representation
        return EmployeeAssetService.get_asset(employee_id, asset.id)

    @staticmethod
    def delete_asset(
        employee_id: str,
        asset_id: str,
        updated_by: Optional[Any] = None,
    ) -> None:
        """
        Permanently delete an asset assignment record.
        """
        asset = EmployeeAssetService.get_asset(
            employee_id,
            asset_id,
        )

        with transaction.atomic():
            asset.delete()
