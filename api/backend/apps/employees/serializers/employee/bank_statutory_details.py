"""Serializers for employee Bank / PF / ESI details."""

from rest_framework import serializers

from apps.employees.services.validators import (
    validate_aadhaar_number,
    validate_ifsc_code,
    validate_pan_number,
)


class BankAccountDetailsRowSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    bank = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bank_id = serializers.UUIDField(required=False, allow_null=True)
    account_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    account_no_masked = serializers.CharField(read_only=True, allow_null=True)
    ifsc = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    account_type_id = serializers.IntegerField(required=False, allow_null=True)
    primary = serializers.BooleanField(required=False)
    account_holder_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    branch_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payment_type_id = serializers.UUIDField(required=False, allow_null=True)
    remove = serializers.BooleanField(required=False)
    delete = serializers.BooleanField(required=False)

    def validate_ifsc(self, value):
        if value in ("", None):
            return value
        return validate_ifsc_code(value)

    def validate_account_no(self, value):
        if value in ("", None):
            return value
        cleaned = str(value).replace(" ", "")
        if not cleaned.isdigit() or len(cleaned) < 6 or len(cleaned) > 30:
            raise serializers.ValidationError(
                "Account number must contain 6 to 30 digits."
            )
        return cleaned


class StatutoryDetailsSerializer(serializers.Serializer):
    pan_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pan_number_masked = serializers.CharField(read_only=True, allow_null=True)
    aadhaar_number = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    aadhaar_number_masked = serializers.CharField(read_only=True, allow_null=True)
    uan_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pf_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    esic_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    professional_tax_no = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    tax_regime = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tax_regime_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_pan_number(self, value):
        if value in ("", None):
            return value
        return validate_pan_number(value)

    def validate_aadhaar_number(self, value):
        if value in ("", None):
            return value
        return validate_aadhaar_number(value)


class BankStatutoryDetailsSerializer(serializers.Serializer):
    bank_accounts = BankAccountDetailsRowSerializer(many=True)
    statutory_details = StatutoryDetailsSerializer()


class BankStatutoryDetailsSubmitSerializer(serializers.Serializer):
    bank_accounts = BankAccountDetailsRowSerializer(required=False, many=True)
    statutory_details = StatutoryDetailsSerializer(required=False)
    employee_remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    @property
    def remarks(self):
        return self.validated_data.get("employee_remarks", "")
