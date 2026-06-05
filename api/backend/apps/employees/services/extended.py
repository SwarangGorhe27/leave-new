import json

from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from apps.employees.constants import ChangeRequestStatus, ESSModule
from apps.employees.models import EmployeeChangeRequest
from apps.employees.utils import FileStorageHelper


def _json_safe(value):
    return json.loads(json.dumps(value, cls=DjangoJSONEncoder))


class ChangeRequestService:
    @staticmethod
    def create(employee, validated_data):
        module = validated_data["module"]
        old_data = validated_data.get("old_data")
        if old_data is None and module == ESSModule.PROFILE:
            from apps.employees.services.profile_section import build_profile_section

            old_data = build_profile_section(employee)
        if old_data is None and module == ESSModule.PERSONAL:
            from apps.employees.services.personal_details import build_personal_details

            old_data = build_personal_details(employee)
        if old_data is None and module == ESSModule.EMPLOYMENT:
            from apps.employees.services.employment_details import build_employment_details

            old_data = {"employment_details": build_employment_details(employee)}
        if old_data is None and module == ESSModule.FAMILY:
            from apps.employees.services.family_details import build_family_details

            old_data = {"family_details": build_family_details(employee)}
        if old_data is None and module == ESSModule.EDUCATION:
            from apps.employees.services.education_details import build_education_details

            old_data = {"education_details": build_education_details(employee)}
        if old_data is None and module == ESSModule.BANK:
            from apps.employees.services.bank_statutory_details import (
                build_bank_statutory_details,
            )

            old_data = build_bank_statutory_details(employee)
        if old_data is None and module == ESSModule.ADDRESS:
            from apps.employees.services.address_details import build_address_details

            old_data = build_address_details(employee)
        if old_data is None and module == ESSModule.NOMINEE:
            from apps.employees.services.nominee_details import build_nominee_details

            old_data = {"nominee_details": build_nominee_details(employee)}
        if old_data is None and module == ESSModule.LANGUAGE:
            from apps.employees.services.language_details import build_language_details

            old_data = {"language_details": build_language_details(employee)}
        if old_data is None and module == ESSModule.INSURANCE:
            from apps.employees.services.insurance_details import build_insurance_details

            old_data = {"insurance_details": build_insurance_details(employee)}
        if old_data is None and module == ESSModule.MEDICAL:
            from apps.employees.services.medical_details import build_medical_details

            old_data = {"medical_details": build_medical_details(employee)}
        if old_data is None and module == ESSModule.SOCIAL:
            from apps.employees.services.social_profile import build_social_profile

            old_data = {"social_profile": build_social_profile(employee)}
        if old_data is None and module == ESSModule.PASSPORT:
            from apps.employees.services.passport_visa_details import build_passport_visa_details

            old_data = {"passport_visa_records": build_passport_visa_details(employee)}

        return EmployeeChangeRequest.objects.create(
            employee=employee,
            module=module,
            action=validated_data.get("action", EmployeeChangeRequest.Action.UPDATE),
            request_data=_json_safe(validated_data.get("request_data", {})),
            old_data=_json_safe(old_data or {}),
            record_id=validated_data.get("record_id"),
            employee_remarks=validated_data.get("remarks", ""),
            requested_by=getattr(employee, "user", None),
        )

    @staticmethod
    def cancel(change_request, employee):
        if change_request.employee_id != employee.id:
            raise ValueError("You can cancel only your own request.")
        if change_request.status != ChangeRequestStatus.PENDING:
            raise ValueError("Only pending change requests can be cancelled.")
        change_request.status = ChangeRequestStatus.CANCELLED
        change_request.save(update_fields=["status", "updated_at"])
        return change_request


class ApprovalService:
    @staticmethod
    def approve(change_request, reviewed_by=None, remarks=""):
        if change_request.status != ChangeRequestStatus.PENDING:
            raise ValueError(
                f"Can only approve PENDING requests. Current status: {change_request.status}"
            )

        change_request.status = ChangeRequestStatus.APPROVED
        change_request.reviewed_by = reviewed_by
        change_request.reviewed_at = timezone.now()
        change_request.admin_remarks = remarks
        change_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "admin_remarks",
                "updated_at",
            ]
        )

        ApprovalService._apply_approved_changes(change_request)
        return change_request

    @staticmethod
    def _apply_approved_changes(change_request):
        """Persist approved request_data to the employee record."""
        module = change_request.module
        data = change_request.request_data or {}
        employee = change_request.employee

        if data.get("_request_only") is True:
            return

        if module == ESSModule.PROFILE and data:
            from apps.employees.services.profile_section import apply_profile_section

            apply_profile_section(employee, data)
        elif module == ESSModule.PERSONAL and data:
            from apps.employees.services.personal_details import apply_personal_details

            apply_personal_details(employee, data)
        elif module == ESSModule.EMPLOYMENT and data:
            from apps.employees.services.employment_details import apply_employment_details

            apply_employment_details(employee, data)
        elif module == ESSModule.FAMILY and data:
            from apps.employees.services.family_details import apply_family_details

            apply_family_details(employee, data)
        elif module == ESSModule.EDUCATION and data:
            from apps.employees.services.education_details import apply_education_details

            apply_education_details(employee, data)
        elif module == ESSModule.BANK and data:
            from apps.employees.services.bank_statutory_details import (
                apply_bank_statutory_details,
            )

            apply_bank_statutory_details(employee, data)
        elif module == ESSModule.ADDRESS and data:
            from apps.employees.services.address_details import apply_address_details

            apply_address_details(employee, data)
        elif module == ESSModule.NOMINEE and data:
            from apps.employees.services.nominee_details import apply_nominee_details

            apply_nominee_details(employee, data)
        elif module == ESSModule.LANGUAGE and data:
            from apps.employees.services.language_details import apply_language_details

            apply_language_details(employee, data)
        elif module == ESSModule.INSURANCE and data:
            from apps.employees.services.insurance_details import apply_insurance_details

            apply_insurance_details(employee, data)
        elif module == ESSModule.MEDICAL and data:
            from apps.employees.services.medical_details import apply_medical_details

            apply_medical_details(employee, data)
        elif module == ESSModule.SOCIAL and data:
            from apps.employees.services.social_profile import apply_social_profile

            apply_social_profile(employee, data)
        elif module == ESSModule.PASSPORT and data:
            from apps.employees.services.passport_visa_details import apply_passport_visa_details

            apply_passport_visa_details(employee, data)

    @staticmethod
    def reject(change_request, reviewed_by=None, remarks=""):
        change_request.status = ChangeRequestStatus.REJECTED
        change_request.reviewed_by = reviewed_by
        change_request.reviewed_at = timezone.now()
        change_request.admin_remarks = remarks
        change_request.save(update_fields=["status", "reviewed_by", "reviewed_at", "admin_remarks", "updated_at"])
        return change_request


class ProfilePictureService:
    @staticmethod
    def upload(employee, file):
        url = FileStorageHelper.save(employee.employee_code, "profile_picture", file)
        employee.profile_picture_url = url
        employee.save(update_fields=["profile_picture_url", "updated_at"])
        return url


class SignatureUploadService:
    @staticmethod
    def upload(employee, file):
        url = FileStorageHelper.save(employee.employee_code, "signature", file)
        employee.signature_url = url
        employee.save(update_fields=["signature_url", "updated_at"])
        return url


class ESSDocumentUploadService:
    @staticmethod
    def upload_document(employee, file, document_name="", remarks=""):
        return FileStorageHelper.save(employee.employee_code, "document", file)

    @staticmethod
    def upload_passport_doc(employee, file, kind="passport", record_id=None):
        category = "visa" if kind == "visa" else "passport"
        return FileStorageHelper.save(employee.employee_code, category, file)

    @staticmethod
    def upload_certificate(employee, file, record_id=None):
        return FileStorageHelper.save(employee.employee_code, "certificate", file)
