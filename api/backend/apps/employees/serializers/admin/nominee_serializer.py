"""
Nominee Details serializers for admin APIs.

The admin UI uses a few display names that differ from the model names:
- contact_number -> mobile_no
- nominee_type -> nominee_purpose
- epf_percentage -> nominee_percentage
- relationship_with_minor -> guardian_relation
- guardian_contact_number -> guardian_mobile_no

The serializer accepts both naming styles and persists only validated model
fields through Django ORM.
"""

import re
from datetime import date

from rest_framework import serializers

from apps.employees.models.nominees import EmployeeNominee


_MOBILE_RE = re.compile(r"^\+?[\d\s\-\(\)]+$")
_ALLOWED_PROOF_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}


class NomineeDetailSerializer(serializers.ModelSerializer):
    relation_label = serializers.CharField(
        source="relation.label",
        read_only=True,
        allow_null=True,
    )
    nominee_purpose_label = serializers.CharField(
        source="nominee_purpose.label",
        read_only=True,
    )
    full_name = serializers.SerializerMethodField()

    contact_number = serializers.CharField(source="mobile_no", read_only=True)
    nominee_type = serializers.ReadOnlyField(source="nominee_purpose_id")
    nominee_type_label = serializers.CharField(
        source="nominee_purpose.label",
        read_only=True,
    )
    epf_percentage = serializers.DecimalField(
        source="nominee_percentage",
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    relationship_with_minor = serializers.CharField(
        source="guardian_relation",
        read_only=True,
    )
    guardian_contact_number = serializers.CharField(
        source="guardian_mobile_no",
        read_only=True,
    )

    class Meta:
        model = EmployeeNominee
        fields = [
            "id",
            "employee",
            "first_name",
            "last_name",
            "full_name",
            "nominee_email",
            "date_of_birth",
            "relation",
            "relation_label",
            "nominee_purpose",
            "nominee_purpose_label",
            "nominee_type",
            "nominee_type_label",
            "nominee_percentage",
            "epf_percentage",
            "mobile_no",
            "contact_number",
            "address",
            "is_minor_nominee",
            "guardian_name",
            "guardian_relation",
            "relationship_with_minor",
            "guardian_mobile_no",
            "guardian_contact_number",
            "guardian_address",
            "identity_proof_url",
            "identity_proof_name",
            "identity_proof_size_bytes",
            "identity_proof_mime_type",
            "guardian_identity_proof_url",
            "guardian_identity_proof_name",
            "guardian_identity_proof_size_bytes",
            "guardian_identity_proof_mime_type",
            "is_active",
        ]
        read_only_fields = ["id", "employee", "full_name"]

    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.first_name or ""


class NomineeUpdateSerializer(serializers.ModelSerializer):
    mobile_no = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )
    guardian_mobile_no = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )

    class Meta:
        model = EmployeeNominee
        fields = [
            "first_name",
            "last_name",
            "nominee_email",
            "date_of_birth",
            "relation",
            "nominee_purpose",
            "nominee_percentage",
            "mobile_no",
            "address",
            "is_minor_nominee",
            "guardian_name",
            "guardian_relation",
            "guardian_mobile_no",
            "guardian_address",
            "identity_proof_url",
            "identity_proof_name",
            "identity_proof_size_bytes",
            "identity_proof_mime_type",
            "guardian_identity_proof_url",
            "guardian_identity_proof_name",
            "guardian_identity_proof_size_bytes",
            "guardian_identity_proof_mime_type",
            "is_active",
        ]

    def to_internal_value(self, data):
        data = data.copy()
        aliases = {
            "contact_number": "mobile_no",
            "nominee_type": "nominee_purpose",
            "epf_percentage": "nominee_percentage",
            "relationship_with_minor": "guardian_relation",
            "guardian_contact_number": "guardian_mobile_no",
        }
        for alias, field in aliases.items():
            if alias in data and field not in data:
                data[field] = data[alias]
            data.pop(alias, None)
        return super().to_internal_value(data)

    def _validate_phone_number(self, value):
        if value is None:
            return value

        value = value.strip()
        if value == "":
            return value

        if not _MOBILE_RE.match(value):
            raise serializers.ValidationError("Enter a valid phone number.")

        if value.count("+") > 1:
            raise serializers.ValidationError(
                "Phone number cannot contain multiple '+' symbols."
            )

        if "+" in value and not value.startswith("+"):
            raise serializers.ValidationError(
                "'+' symbol is only allowed at the beginning."
            )

        digits = re.sub(r"\D", "", value)
        if digits.startswith("91"):
            if len(digits) != 12:
                raise serializers.ValidationError(
                    "Mobile number with country code must contain exactly 12 digits."
                )
            mobile_number = digits[2:]
        else:
            if len(digits) != 10:
                raise serializers.ValidationError(
                    "Mobile number must contain exactly 10 digits."
                )
            mobile_number = digits

        if mobile_number[0] not in ["6", "7", "8", "9"]:
            raise serializers.ValidationError("Enter a valid Indian mobile number.")

        return value

    def _validate_mime_type(self, value):
        if value in (None, ""):
            return value
        normalized = value.strip().lower()
        if normalized not in _ALLOWED_PROOF_MIME_TYPES:
            raise serializers.ValidationError(
                "Only PDF, JPEG, PNG, or WEBP files are allowed."
            )
        return normalized

    def validate_mobile_no(self, value):
        return self._validate_phone_number(value)

    def validate_guardian_mobile_no(self, value):
        return self._validate_phone_number(value)

    def validate_nominee_percentage(self, value):
        if value is not None and (value <= 0 or value > 100):
            raise serializers.ValidationError(
                "Nominee percentage must be between 0.01 and 100."
            )
        return value

    def validate_identity_proof_size_bytes(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("File size cannot be negative.")
        return value

    def validate_guardian_identity_proof_size_bytes(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("File size cannot be negative.")
        return value

    def validate_identity_proof_mime_type(self, value):
        return self._validate_mime_type(value)

    def validate_guardian_identity_proof_mime_type(self, value):
        return self._validate_mime_type(value)

    def validate(self, data):
        if data.get("identity_proof_url") == "":
            data["identity_proof_url"] = None
            data.setdefault("identity_proof_name", None)
            data.setdefault("identity_proof_size_bytes", None)
            data.setdefault("identity_proof_mime_type", None)

        if data.get("guardian_identity_proof_url") == "":
            data["guardian_identity_proof_url"] = None
            data.setdefault("guardian_identity_proof_name", None)
            data.setdefault("guardian_identity_proof_size_bytes", None)
            data.setdefault("guardian_identity_proof_mime_type", None)

        if data.get("date_of_birth") and data["date_of_birth"] > date.today():
            raise serializers.ValidationError(
                {"date_of_birth": "Date of birth cannot be in the future."}
            )

        if data.get("is_minor_nominee") is True:
            required_guardian_fields = {
                "guardian_name": "Guardian name is required for a minor nominee.",
                "guardian_relation": "Relationship with minor is required.",
                "guardian_mobile_no": "Guardian contact number is required.",
                "guardian_address": "Guardian address is required.",
            }
            errors = {
                field: message
                for field, message in required_guardian_fields.items()
                if not data.get(field)
            }
            if errors:
                raise serializers.ValidationError(errors)

        if data.get("is_minor_nominee") is False:
            for field in (
                "guardian_name",
                "guardian_relation",
                "guardian_mobile_no",
                "guardian_address",
                "guardian_identity_proof_url",
                "guardian_identity_proof_name",
                "guardian_identity_proof_size_bytes",
                "guardian_identity_proof_mime_type",
            ):
                data.setdefault(field, None)

        return data
