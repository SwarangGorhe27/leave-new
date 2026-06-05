"""Profile Section serializers — screenshot fields only."""

from rest_framework import serializers

from apps.employees.constants.profile_section import (
    PROFILE_SECTION_EMPLOYEE_EDITABLE,
    PROFILE_SECTION_FIELDS,
)


class ProfileSectionSerializer(serializers.Serializer):
    """Read / response — all screenshot fields."""

    employee_id = serializers.UUIDField(read_only=True)
    employee_code = serializers.CharField(read_only=True)
    salutation = serializers.CharField(allow_null=True, required=False)
    middle_name = serializers.CharField(allow_null=True, required=False)
    preferred_name = serializers.CharField(allow_null=True, required=False)
    personal_email = serializers.EmailField(allow_null=True, required=False)
    personal_mobile = serializers.CharField(allow_null=True, required=False)
    extension_number = serializers.CharField(allow_null=True, required=False)
    bio_about = serializers.CharField(allow_null=True, required=False)
    profile_photo = serializers.CharField(allow_null=True, required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    official_email = serializers.EmailField(allow_null=True, required=False)
    work_mobile = serializers.CharField(allow_null=True, required=False)
    alternate_mobile_number = serializers.CharField(allow_null=True, required=False)
    username = serializers.CharField(allow_null=True, required=False, max_length=150)
    signature_upload = serializers.CharField(allow_null=True, required=False)


class ProfileSectionEmployeeSubmitSerializer(serializers.Serializer):
    """
    Employee Submit — only editable profile fields.
    Creates a PROFILE change request for admin approval.
    """

    salutation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preferred_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    personal_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    personal_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    extension_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio_about = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_photo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    alternate_mobile_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    signature_upload = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        remarks = attrs.pop("remarks", "")
        self._remarks = remarks
        unknown = set(attrs.keys()) - PROFILE_SECTION_EMPLOYEE_EDITABLE
        if unknown:
            raise serializers.ValidationError(
                {"non_field_errors": f"Fields not allowed: {', '.join(sorted(unknown))}"}
            )
        if not attrs:
            raise serializers.ValidationError(
                {"non_field_errors": "Provide at least one field to update."}
            )
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")


class ProfileSectionAdminUpdateSerializer(serializers.Serializer):
    """Admin PATCH — screenshot fields (includes official_email)."""

    salutation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preferred_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    personal_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    personal_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    extension_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio_about = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_photo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    official_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    work_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    alternate_mobile_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    signature_upload = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        from apps.employees.constants.profile_section import PROFILE_SECTION_ADMIN_EDITABLE

        unknown = set(attrs.keys()) - PROFILE_SECTION_ADMIN_EDITABLE
        if unknown:
            raise serializers.ValidationError(
                {k: "Field not allowed in profile section." for k in unknown}
            )
        if not attrs:
            raise serializers.ValidationError(
                {"non_field_errors": "Provide at least one field to update."}
            )
        return attrs
