"""
Passport and Visa serializers for the admin employee details page.
"""

from django.db.models import Q
from rest_framework import serializers

from apps.employees.models.masters.location import Country


class PassportIssuingCountryField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None

        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            if not isinstance(data, str):
                raise exc

            value = data.strip()
            if not value:
                return None

            country = self.get_queryset().filter(
                Q(label__iexact=value) | Q(code__iexact=value) | Q(iso3_code__iexact=value)
            ).first()
            if country is None:
                raise serializers.ValidationError(
                    "Country of issue must be an active country id, ISO code, or country name."
                )
            return country


class PassportDetailsUpdateSerializer(serializers.Serializer):
    passport_no = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )

    passport_issue_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    passport_expiry = serializers.DateField(
        required=False,
        allow_null=True,
    )

    passport_place_of_issue = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=150,
    )

    passport_category = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )

    passport_status = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )

    passport_issuing_country = PassportIssuingCountryField(
        queryset=Country.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    passport_country_of_issue = PassportIssuingCountryField(
        source="passport_issuing_country",
        queryset=Country.objects.filter(is_active=True),
        required=False,
        allow_null=True,
        write_only=True,
    )


class VisaDetailsUpdateSerializer(serializers.Serializer):
    visa_country = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )

    visa_type = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )

    visa_number = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=50,
    )

    visa_sponsor = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=150,
    )

    visa_status = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=50,
    )

    visa_issue_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    visa_expiry = serializers.DateField(
        required=False,
        allow_null=True,
    )

    visaCountry = serializers.CharField(
        source="visa_country",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
        write_only=True,
    )

    visaType = serializers.CharField(
        source="visa_type",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
        write_only=True,
    )

    visaNumber = serializers.CharField(
        source="visa_number",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=50,
        write_only=True,
    )

    visaSponsor = serializers.CharField(
        source="visa_sponsor",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=150,
        write_only=True,
    )

    visaStatus = serializers.CharField(
        source="visa_status",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=50,
        write_only=True,
    )

    visaIssueDate = serializers.DateField(
        source="visa_issue_date",
        required=False,
        allow_null=True,
        write_only=True,
    )

    visaExpiry = serializers.DateField(
        source="visa_expiry",
        required=False,
        allow_null=True,
        write_only=True,
    )


class PassportVisaUpdateSerializer(serializers.Serializer):
    passport_details = PassportDetailsUpdateSerializer(required=False)
    visa_details = VisaDetailsUpdateSerializer(required=False)


class EmployeeSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    employee_code = serializers.CharField()
    full_name = serializers.CharField()
    status = serializers.CharField()


class PassportDetailsSerializer(serializers.Serializer):
    holder_name = serializers.CharField(allow_null=True)
    passport_no = serializers.CharField(allow_null=True)
    passport_issue_date = serializers.DateField(allow_null=True)
    passport_expiry = serializers.DateField(allow_null=True)
    passport_place_of_issue = serializers.CharField(allow_null=True)
    passport_category = serializers.CharField(allow_null=True)
    passport_status = serializers.CharField(allow_null=True)
    passport_status_label = serializers.CharField(allow_null=True, required=False)
    passport_issuing_country = serializers.IntegerField(allow_null=True)
    passport_issuing_country_label = serializers.CharField(allow_null=True)
    passport_country_of_issue = serializers.CharField(
        source="passport_issuing_country_label",
        allow_null=True,
    )
    nationality = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    record_id = serializers.CharField(allow_null=True, required=False)


class VisaDetailsSerializer(serializers.Serializer):
    visa_country = serializers.CharField(allow_null=True)
    visa_type = serializers.CharField(allow_null=True)
    visa_number = serializers.CharField(allow_null=True)
    visa_sponsor = serializers.CharField(allow_null=True)
    visa_status = serializers.CharField(allow_null=True)
    visa_issue_date = serializers.DateField(allow_null=True)
    visa_expiry = serializers.DateField(allow_null=True)
    visaCountry = serializers.CharField(source="visa_country", allow_null=True)
    visaType = serializers.CharField(source="visa_type", allow_null=True)
    visaNumber = serializers.CharField(source="visa_number", allow_null=True)
    visaSponsor = serializers.CharField(source="visa_sponsor", allow_null=True)
    visaStatus = serializers.CharField(source="visa_status", allow_null=True)
    visaIssueDate = serializers.DateField(source="visa_issue_date", allow_null=True)
    visaExpiry = serializers.DateField(source="visa_expiry", allow_null=True)
    status = serializers.CharField()


class AuditUserSerializer(serializers.Serializer):
    id = serializers.CharField(allow_null=True)
    name = serializers.CharField(allow_null=True)


class AuditSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)
    created_by = AuditUserSerializer(allow_null=True)
    updated_by = AuditUserSerializer(allow_null=True)


class PassportVisaDetailsSerializer(serializers.Serializer):
    employee = EmployeeSummarySerializer()
    passport_details = PassportDetailsSerializer()
    visa_details = VisaDetailsSerializer()
    audit = AuditSerializer()
