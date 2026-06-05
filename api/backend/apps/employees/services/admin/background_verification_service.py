"""
Admin service for employee background verification.

All persistence uses Django ORM parameter binding; no raw SQL is used.
"""

from typing import Any, Dict

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.employees.models.background_verification import EmployeeBackgroundVerification
from apps.employees.models.employee import Employee
from apps.employees.models.masters.audit_additions import VerificationStatus



WRITE_FIELD_MAP = {
    "verification_status": "verification_status",
    "agencyName": "agency_name",
    "verifiedBy": "verified_by",
    "referenceNumber": "reference_number",
    "completionDate": "completion_date",
    "agencyRemarks": "agency_remarks",
}


class BackgroundVerificationService:
    @staticmethod
    def list_statuses():
        return VerificationStatus.objects.filter(is_active=True).order_by("sort_order", "name")

    @staticmethod
    def get_verification(employee_id: str) -> EmployeeBackgroundVerification:
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return get_object_or_404(
            EmployeeBackgroundVerification.objects.select_related("verification_status"),
            employee=employee,
            is_active=True,
        )

    @staticmethod
    def create_or_replace_verification(
        employee_id: str,
        validated_data: Dict[str, Any],
    ) -> EmployeeBackgroundVerification:
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        data = BackgroundVerificationService._map_fields(validated_data)

        with transaction.atomic():
            verification, _ = EmployeeBackgroundVerification.objects.get_or_create(
                employee=employee,
                defaults=data,
            )
            for field, value in data.items():
                setattr(verification, field, value)
            verification.is_active = True
            verification.save()
        return verification

    @staticmethod
    def update_verification(
        employee_id: str,
        validated_data: Dict[str, Any],
    ) -> EmployeeBackgroundVerification:
        verification = BackgroundVerificationService.get_verification(employee_id)
        data = BackgroundVerificationService._map_fields(validated_data)

        with transaction.atomic():
            for field, value in data.items():
                setattr(verification, field, value)
            verification.save()
        return verification

    @staticmethod
    def delete_verification(employee_id: str) -> None:
        verification = BackgroundVerificationService.get_verification(employee_id)
        with transaction.atomic():
            verification.delete()

    @staticmethod
    def _map_fields(validated_data: Dict[str, Any]) -> Dict[str, Any]:
        data = {}
        for source, target in WRITE_FIELD_MAP.items():
            if source in validated_data:
                data[target] = validated_data[source]
        return data
