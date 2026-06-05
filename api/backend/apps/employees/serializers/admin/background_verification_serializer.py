"""
Admin serializers for employee background verification.
"""

from django.utils import timezone
from rest_framework import serializers

from apps.employees.models.background_verification import EmployeeBackgroundVerification
from apps.employees.models.masters.audit_additions import VerificationStatus


COMPLETED_STATUS_CODES = {"VERIFIED", "COMPLETED", "CLEAR", "APPROVED"}


class VerificationStatusOptionSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = VerificationStatus
        fields = [
            "id",
            "code",
            "name",
            "label",
            "is_positive",
            "is_terminal",
            "sort_order",
        ]
        read_only_fields = fields


class BackgroundVerificationSerializer(serializers.ModelSerializer):
    verificationStatusId = serializers.UUIDField(source="verification_status_id", read_only=True)
    verificationStatus = serializers.CharField(source="verification_status.name", read_only=True)
    verificationStatusCode = serializers.CharField(source="verification_status.code", read_only=True)
    agencyName = serializers.CharField(source="agency_name", read_only=True)
    verifiedBy = serializers.CharField(source="verified_by", read_only=True)
    referenceNumber = serializers.CharField(source="reference_number", read_only=True)
    completionDate = serializers.DateField(source="completion_date", read_only=True)
    agencyRemarks = serializers.CharField(source="agency_remarks", read_only=True)
    header = serializers.SerializerMethodField()
    fieldsView = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeBackgroundVerification
        fields = [
            "id",
            "employee",
            "verificationStatusId",
            "verificationStatus",
            "verificationStatusCode",
            "agencyName",
            "verifiedBy",
            "referenceNumber",
            "completionDate",
            "agencyRemarks",
            "header",
            "fieldsView",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_header(self, obj):
        return {
            "title": "Verification Status",
            "value": obj.verification_status.name,
            "code": obj.verification_status.code,
        }

    def get_fieldsView(self, obj):
        return [
            {"key": "verificationStatus", "label": "Verification Status", "value": obj.verification_status.name},
            {"key": "agencyName", "label": "Agency Name", "value": obj.agency_name},
            {"key": "verifiedBy", "label": "Verified By", "value": obj.verified_by},
            {"key": "referenceNumber", "label": "Reference Number", "value": obj.reference_number},
            {"key": "completionDate", "label": "Completion Date", "value": obj.completion_date},
            {"key": "agencyRemarks", "label": "Agency Remarks", "value": obj.agency_remarks},
        ]


class BackgroundVerificationWriteSerializer(serializers.Serializer):
    verificationStatus = serializers.UUIDField(required=False)
    verificationStatusId = serializers.UUIDField(required=False)
    agencyName = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    verifiedBy = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    referenceNumber = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    completionDate = serializers.DateField(required=False, allow_null=True)
    agencyRemarks = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=2000)

    def validate(self, attrs):
        status_id = attrs.get("verificationStatusId") or attrs.get("verificationStatus")
        instance = self.context.get("instance")

        if not self.partial and not status_id:
            raise serializers.ValidationError({
                "verificationStatus": "Verification status is required."
            })

        if status_id:
            try:
                status = VerificationStatus.objects.get(id=status_id, is_active=True)
            except VerificationStatus.DoesNotExist:
                raise serializers.ValidationError({
                    "verificationStatus": "Select a valid active verification status."
                })
            attrs["verification_status"] = status
        elif instance:
            status = instance.verification_status
        else:
            status = None

        for field in ("agencyName", "verifiedBy", "referenceNumber", "agencyRemarks"):
            if field in attrs and isinstance(attrs[field], str):
                attrs[field] = attrs[field].strip() or None

        completion_date = attrs.get("completionDate")
        if instance and "completionDate" not in attrs:
            completion_date = instance.completion_date

        if completion_date and completion_date > timezone.localdate():
            raise serializers.ValidationError({
                "completionDate": "Completion date cannot be in the future."
            })

        if status and status.code.upper() in COMPLETED_STATUS_CODES:
            verified_by = attrs.get("verifiedBy")
            if instance and "verifiedBy" not in attrs:
                verified_by = instance.verified_by
            if not verified_by:
                raise serializers.ValidationError({
                    "verifiedBy": "Verified by is required for a completed verification status."
                })
            if not completion_date:
                raise serializers.ValidationError({
                    "completionDate": "Completion date is required for a completed verification status."
                })

        return attrs
