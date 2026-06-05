"""Emergency & Medical Information serializers."""

from rest_framework import serializers

from apps.employees.services.validators.common import validate_mobile_number


class MedicalDetailsPayloadSerializer(serializers.Serializer):
    """Screenshot fields for Employee - Emergency & Medical Information."""

    emergency_contact_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    emergency_contact_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    emergency_contact_relationship = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    relationship = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    medical_conditions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    any_disease = serializers.BooleanField(required=False, allow_null=True)
    has_disease = serializers.BooleanField(required=False, allow_null=True)
    disease_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pre_existing_diseases = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    undergone_major_surgery = serializers.BooleanField(required=False, allow_null=True)
    any_surgery_operation_done = serializers.BooleanField(required=False, allow_null=True)
    surgery_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    surgery_operation_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    allergies = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    doctor_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_emergency_contact_number(self, value):
        return validate_mobile_number(value)

    def validate(self, attrs):
        if "relationship" in attrs and "emergency_contact_relationship" not in attrs:
            attrs["emergency_contact_relationship"] = attrs.pop("relationship")

        if "disease_description" in attrs and "pre_existing_diseases" not in attrs:
            attrs["pre_existing_diseases"] = attrs["disease_description"]
        if attrs.get("has_disease") is None and attrs.get("any_disease") is not None:
            attrs["has_disease"] = attrs["any_disease"]

        if "surgery_operation_description" in attrs and "surgery_details" not in attrs:
            attrs["surgery_details"] = attrs["surgery_operation_description"]
        if attrs.get("undergone_major_surgery") is None and attrs.get("any_surgery_operation_done") is not None:
            attrs["undergone_major_surgery"] = attrs["any_surgery_operation_done"]

        return attrs


class MedicalDetailsSubmitSerializer(serializers.Serializer):
    """Employee PATCH body for Emergency & Medical Information approval request."""

    medical_details = MedicalDetailsPayloadSerializer()
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        self._remarks = attrs.pop("remarks", "")
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
