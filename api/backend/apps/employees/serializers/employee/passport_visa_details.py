"""Passport & Visa Details — submit serializer for change requests."""

from rest_framework import serializers


class PassportVisaRowSubmitSerializer(serializers.Serializer):
    """Single passport/visa record for submission."""

    id = serializers.UUIDField(required=False, allow_null=True)
    remove = serializers.BooleanField(required=False, default=False)
    delete = serializers.BooleanField(required=False, default=False)

    # Passport fields
    passport_number = serializers.CharField(max_length=30, required=False, allow_blank=True)
    passport_holder_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    issue_date = serializers.DateField(required=False, allow_null=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    issue_place = serializers.CharField(max_length=100, required=False, allow_blank=True)
    issue_country_id = serializers.IntegerField(required=False, allow_null=True)
    passport_category = serializers.CharField(max_length=50, required=False, allow_blank=True)
    passport_status = serializers.CharField(max_length=50, required=False, allow_blank=True)

    # Visa fields
    has_visa = serializers.BooleanField(required=False, default=False)
    visa_type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    visa_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    visa_expiry_date = serializers.DateField(required=False, allow_null=True)
    visa_issue_date = serializers.DateField(required=False, allow_null=True)
    visa_issue_country_id = serializers.IntegerField(required=False, allow_null=True)
    visa_country_id = serializers.IntegerField(required=False, allow_null=True)
    visa_sponsor = serializers.CharField(max_length=255, required=False, allow_blank=True)
    visa_status = serializers.CharField(max_length=50, required=False, allow_blank=True)

    # Document URLs
    passport_front_url = serializers.URLField(required=False, allow_blank=True)
    passport_back_url = serializers.URLField(required=False, allow_blank=True)
    visa_copy_url = serializers.URLField(required=False, allow_blank=True)


class PassportVisaDetailsSubmitSerializer(serializers.Serializer):
    """Passport & Visa Details submission (one or more records)."""

    passport_visa_records = PassportVisaRowSubmitSerializer(many=True)
    employee_remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )

    def validate(self, attrs):
        rows = attrs.get("passport_visa_records", [])
        if not rows:
            raise serializers.ValidationError(
                {"passport_visa_records": "Provide at least one passport/visa record."}
            )
        return attrs
