"""
Bank, PF, and ESI serializers for the admin employee details page.
"""

import re
from decimal import Decimal

from rest_framework import serializers

from apps.employees.models.masters.organization import AccountType, Bank, BankStatus
from apps.employees.models.masters.payroll import TaxRegime


IFSC_PATTERN = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")
ACCOUNT_NUMBER_PATTERN = re.compile(r"^[0-9]{6,30}$")
ACCOUNT_HOLDER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,148}$")
BANK_CODE_PATTERN = re.compile(r"^[A-Z0-9_-]{2,20}$")
BANK_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .,&()'/-]{1,198}$")
BRANCH_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .,&()'/-]{1,148}$")
PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
PF_ACCOUNT_PATTERN = re.compile(r"^[A-Z]{2}/[A-Z]{3}/[0-9]{7}/[0-9]{3}/[0-9]{7}$")
ESIC_PATTERN = re.compile(r"^[0-9]{17}$")
LIN_PATTERN = re.compile(r"^[A-Z0-9/-]{6,30}$")
LABEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .,&()'/-]{1,98}$")


def mask_account_number(value):
    if value in ("", None):
        return None
    value = str(value)
    return f"XXXX XXXX {value[-4:]}"


class MaskedAccountNumberField(serializers.CharField):
    def to_representation(self, value):
        return mask_account_number(value)


class BankAccountUpdateSerializer(serializers.Serializer):
    bank = serializers.PrimaryKeyRelatedField(
        queryset=Bank.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    bank_code = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    bank_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    account_type = serializers.PrimaryKeyRelatedField(
        queryset=AccountType.objects.filter(is_active=True)
    )
    account_number = serializers.CharField(max_length=40)
    ifsc_code = serializers.CharField(max_length=11, required=False, allow_blank=True, allow_null=True)
    micr_code = serializers.CharField(max_length=9, required=False, allow_blank=True, allow_null=True)
    branch_name = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    branch_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    account_holder_name = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    bank_status = serializers.PrimaryKeyRelatedField(
        queryset=BankStatus.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    is_primary = serializers.BooleanField(required=False)
    is_salary_account = serializers.BooleanField(required=False)
    payment_type_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_account_number(self, value):
        cleaned_value = value.replace(" ", "")
        if not ACCOUNT_NUMBER_PATTERN.match(cleaned_value):
            raise serializers.ValidationError(
                "Account number must contain 6 to 30 digits."
            )
        return cleaned_value

    def validate_bank_code(self, value):
        if value in ("", None):
            return None
        normalized_value = value.strip().upper()
        if not BANK_CODE_PATTERN.match(normalized_value):
            raise serializers.ValidationError(
                "Bank code must be 2 to 20 characters and contain only letters, numbers, underscores, or hyphens."
            )
        return normalized_value

    def validate_bank_name(self, value):
        if value in ("", None):
            return None
        normalized_value = " ".join(value.split())
        if not BANK_NAME_PATTERN.match(normalized_value):
            raise serializers.ValidationError(
                "Bank name must be 2 to 200 characters and contain only valid bank name characters."
            )
        return normalized_value

    def validate_ifsc_code(self, value):
        if value in ("", None):
            return None
        normalized_value = value.upper()
        if not IFSC_PATTERN.match(normalized_value):
            raise serializers.ValidationError(
                "IFSC code must be 11 characters, like HDFC0001234."
            )
        return normalized_value

    def validate_micr_code(self, value):
        if value in ("", None):
            return None
        value = value.strip()
        if not value.isdigit() or len(value) != 9:
            raise serializers.ValidationError("MICR code must contain exactly 9 digits.")
        return value

    def validate_branch_name(self, value):
        if value in ("", None):
            return None
        normalized_value = " ".join(value.split())
        if not BRANCH_NAME_PATTERN.match(normalized_value):
            raise serializers.ValidationError(
                "Branch name must be 2 to 150 characters and contain only valid branch name characters."
            )
        return normalized_value

    def validate_branch_address(self, value):
        if value in ("", None):
            return None
        normalized_value = " ".join(value.split())
        if len(normalized_value) > 500:
            raise serializers.ValidationError("Branch address cannot exceed 500 characters.")
        return normalized_value

    def validate_account_holder_name(self, value):
        if value in ("", None):
            return None
        normalized_value = " ".join(value.split())
        if not ACCOUNT_HOLDER_PATTERN.match(normalized_value):
            raise serializers.ValidationError(
                "Account holder name can contain letters, spaces, dots, apostrophes, and hyphens."
            )
        return normalized_value

    def validate(self, attrs):
        account_type = attrs.get("account_type")
        is_salary_account = attrs.get("is_salary_account", True)

        if (
            not self.partial
            and attrs.get("bank") is None
            and not attrs.get("bank_name")
        ):
            raise serializers.ValidationError(
                {"bank": "Provide an existing bank UUID or bank_name to create/reuse a bank."}
            )
        if not self.partial:
            required_fields = ("account_holder_name", "ifsc_code")
            missing_fields = [
                field for field in required_fields if attrs.get(field) in ("", None)
            ]
            if missing_fields:
                raise serializers.ValidationError(
                    {
                        field: "This field is required for bank account creation."
                        for field in missing_fields
                    }
                )

        bank = attrs.get("bank")
        bank_name = attrs.get("bank_name")
        bank_code = attrs.get("bank_code")
        if bank is not None and (bank_name or bank_code):
            raise serializers.ValidationError(
                {"bank": "Provide either bank UUID or bank_name/bank_code, not both."}
            )

        ifsc_code = attrs.get("ifsc_code")
        if bank is not None and ifsc_code and bank.ifsc_prefix:
            if not ifsc_code.startswith(bank.ifsc_prefix.upper()):
                raise serializers.ValidationError(
                    {"ifsc_code": "IFSC code prefix does not match the selected bank."}
                )

        if account_type and is_salary_account and not account_type.is_salary_allowed:
            raise serializers.ValidationError(
                {"account_type": "This account type is not allowed for salary credit."}
            )

        return attrs


class PfDetailsUpdateSerializer(serializers.Serializer):
    is_pf_covered = serializers.BooleanField(required=False)
    uan = serializers.CharField(max_length=14, required=False, allow_blank=True, allow_null=True)
    pf_account_no = serializers.CharField(max_length=26, required=False, allow_blank=True, allow_null=True)
    pf_type = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    pf_monthly_contribution = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
        required=False,
        allow_null=True,
    )
    pf_employee_share = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal("0.00"),
        max_value=Decimal("100.00"),
        required=False,
        allow_null=True,
    )
    pf_employer_share = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal("0.00"),
        max_value=Decimal("100.00"),
        required=False,
        allow_null=True,
    )
    pf_joining_date = serializers.DateField(required=False, allow_null=True)
    pf_exit_date = serializers.DateField(required=False, allow_null=True)
    pf_status = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    is_higher_pension_wages = serializers.BooleanField(required=False)
    earlier_member_of_pension_on_higher_wages = serializers.BooleanField(required=False, write_only=True)

    def validate_uan(self, value):
        if value in ("", None):
            return None
        cleaned_value = re.sub(r"[\s-]", "", value)
        if not cleaned_value.isdigit() or len(cleaned_value) != 12:
            raise serializers.ValidationError("UAN must contain exactly 12 digits.")
        return cleaned_value

    def validate_pf_status(self, value):
        if value in ("", None):
            return None
        return value.strip()

    def validate_pf_account_no(self, value):
        if value in ("", None):
            return None
        normalized_value = value.strip().upper().replace(" ", "")
        if not PF_ACCOUNT_PATTERN.match(normalized_value):
            raise serializers.ValidationError(
                "PF number must follow region/office/registration/extension/member format, e.g. MH/BAN/0000064/000/0000123."
            )
        return normalized_value

    def validate_pf_type(self, value):
        if value in ("", None):
            return None
        normalized_value = " ".join(value.split())
        if not LABEL_PATTERN.match(normalized_value):
            raise serializers.ValidationError("PF type contains invalid characters.")
        return normalized_value

    def validate(self, attrs):
        if "earlier_member_of_pension_on_higher_wages" in attrs:
            attrs["is_higher_pension_wages"] = attrs.pop(
                "earlier_member_of_pension_on_higher_wages"
            )
        is_pf_covered = attrs.get("is_pf_covered")
        if (
            is_pf_covered is True
            and not attrs.get("pf_account_no")
            and self.context.get("require_coverage_identifiers")
        ):
            raise serializers.ValidationError(
                {"pf_account_no": "PF number is required when PF coverage is selected."}
            )
        if attrs.get("pf_joining_date") and attrs.get("pf_exit_date"):
            if attrs["pf_exit_date"] < attrs["pf_joining_date"]:
                raise serializers.ValidationError(
                    {"pf_exit_date": "PF exit date cannot be before PF joining date."}
                )
        return attrs


class EsiDetailsUpdateSerializer(serializers.Serializer):
    is_esi_covered = serializers.BooleanField(required=False)
    esic_no = serializers.CharField(max_length=23, required=False, allow_blank=True, allow_null=True)
    esic_type = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    esic_employee_contribution = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal("0.00"),
        max_value=Decimal("100.00"),
        required=False,
        allow_null=True,
    )
    esic_employer_contribution = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal("0.00"),
        max_value=Decimal("100.00"),
        required=False,
        allow_null=True,
    )
    esic_joining_date = serializers.DateField(required=False, allow_null=True)
    esic_dispensary = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)
    esic_status = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)

    def validate_esic_no(self, value):
        if value in ("", None):
            return None
        normalized_value = re.sub(r"[\s-]", "", value.strip())
        if not ESIC_PATTERN.match(normalized_value):
            raise serializers.ValidationError(
                "ESI number must contain exactly 17 digits."
            )
        return normalized_value

    def validate_esic_status(self, value):
        if value in ("", None):
            return None
        return value.strip()

    def validate_esic_type(self, value):
        if value in ("", None):
            return None
        normalized_value = " ".join(value.split())
        if not LABEL_PATTERN.match(normalized_value):
            raise serializers.ValidationError("ESI type contains invalid characters.")
        return normalized_value

    def validate_esic_dispensary(self, value):
        if value in ("", None):
            return None
        normalized_value = " ".join(value.split())
        if len(normalized_value) > 150:
            raise serializers.ValidationError("ESI dispensary cannot exceed 150 characters.")
        return normalized_value

    def validate(self, attrs):
        if (
            attrs.get("is_esi_covered") is True
            and not attrs.get("esic_no")
            and self.context.get("require_coverage_identifiers")
        ):
            raise serializers.ValidationError(
                {"esic_no": "ESI number is required when ESI coverage is selected."}
            )
        return attrs


class LwfDetailsUpdateSerializer(serializers.Serializer):
    is_lwf_covered = serializers.BooleanField(required=False)
    lin_number = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)

    def validate_lin_number(self, value):
        if value in ("", None):
            return None
        normalized_value = value.strip().upper().replace(" ", "")
        if not LIN_PATTERN.match(normalized_value):
            raise serializers.ValidationError(
                "LIN number must be 6 to 30 characters and contain only letters, numbers, slash, or hyphen."
            )
        return normalized_value

    def validate(self, attrs):
        if (
            attrs.get("is_lwf_covered") is True
            and not attrs.get("lin_number")
            and self.context.get("require_coverage_identifiers")
        ):
            raise serializers.ValidationError(
                {"lin_number": "LIN number is required when LWF coverage is selected."}
            )
        return attrs


class StatutoryDocumentsUpdateSerializer(serializers.Serializer):
    pan = serializers.CharField(max_length=10, required=False, allow_blank=True, allow_null=True)
    aadhaar_no = serializers.CharField(max_length=14, required=False, allow_blank=True, allow_null=True)
    tax_regime = serializers.PrimaryKeyRelatedField(
        queryset=TaxRegime.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    def validate_pan(self, value):
        if value in ("", None):
            return None
        normalized_value = value.strip().upper()
        if not PAN_PATTERN.match(normalized_value):
            raise serializers.ValidationError("PAN must follow AAAAA9999A format.")
        return normalized_value

    def validate_aadhaar_no(self, value):
        if value in ("", None):
            return None
        cleaned_value = re.sub(r"[\s-]", "", value)
        if not cleaned_value.isdigit() or len(cleaned_value) != 12:
            raise serializers.ValidationError("Aadhaar number must contain exactly 12 digits.")
        return cleaned_value


class StatutoryContributionsUpdateSerializer(serializers.Serializer):
    statutory_documents = StatutoryDocumentsUpdateSerializer(required=False)
    pf_details = PfDetailsUpdateSerializer(required=False)
    esi_details = EsiDetailsUpdateSerializer(required=False)
    lwf_details = LwfDetailsUpdateSerializer(required=False)

    def validate(self, attrs):
        if (
            "statutory_documents" not in attrs
            and "pf_details" not in attrs
            and "esi_details" not in attrs
            and "lwf_details" not in attrs
        ):
            raise serializers.ValidationError(
                "Provide statutory_documents, pf_details, esi_details, lwf_details, or any combination."
            )
        return attrs


class BankStatutoryCreateSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField(required=False)
    bank_account = BankAccountUpdateSerializer(required=False)
    statutory_documents = StatutoryDocumentsUpdateSerializer(required=False)
    pf_details = PfDetailsUpdateSerializer(required=False)
    esi_details = EsiDetailsUpdateSerializer(required=False)
    lwf_details = LwfDetailsUpdateSerializer(required=False)

    def validate(self, attrs):
        if (
            "bank_account" not in attrs
            and "statutory_documents" not in attrs
            and "pf_details" not in attrs
            and "esi_details" not in attrs
            and "lwf_details" not in attrs
        ):
            raise serializers.ValidationError(
                "Provide bank_account, statutory_documents, pf_details, esi_details, lwf_details, or any combination."
            )
        return attrs


class BankStatutoryCreateWithEmployeeSerializer(BankStatutoryCreateSerializer):
    employee_id = serializers.UUIDField(required=True)


class EmployeeSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    employee_code = serializers.CharField()
    full_name = serializers.CharField()
    status = serializers.CharField()


class BankAccountSerializer(serializers.Serializer):
    id = serializers.UUIDField(allow_null=True)
    bank = serializers.UUIDField(allow_null=True)
    bank_name = serializers.CharField(allow_null=True)
    account_type = serializers.IntegerField(allow_null=True)
    account_type_label = serializers.CharField(allow_null=True)
    account_holder_name = serializers.CharField(allow_null=True)
    account_number = MaskedAccountNumberField(allow_null=True)
    masked_account_number = MaskedAccountNumberField(allow_null=True)
    account_number_last4 = serializers.CharField(allow_null=True)
    ifsc_code = serializers.CharField(allow_null=True)
    micr_code = serializers.CharField(allow_null=True)
    branch_name = serializers.CharField(allow_null=True)
    branch_address = serializers.CharField(allow_null=True)
    bank_status = serializers.IntegerField(allow_null=True)
    bank_status_label = serializers.CharField(allow_null=True)
    is_primary = serializers.BooleanField(allow_null=True)
    is_salary_account = serializers.BooleanField(allow_null=True)
    is_verified = serializers.BooleanField(allow_null=True)
    payment_type_id = serializers.UUIDField(allow_null=True)
    payment_type_label = serializers.CharField(allow_null=True)
    payment_type_name = serializers.CharField(allow_null=True, required=False)


class PfDetailsSerializer(serializers.Serializer):
    is_pf_covered = serializers.BooleanField(allow_null=True)
    uan = serializers.CharField(allow_null=True)
    pf_account_no = serializers.CharField(allow_null=True)
    uan_last4 = serializers.CharField(allow_null=True)
    pf_account_no_last4 = serializers.CharField(allow_null=True)
    pf_type = serializers.CharField(allow_null=True)
    pf_monthly_contribution = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    pf_employee_share = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    pf_employer_share = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    pf_joining_date = serializers.DateField(allow_null=True)
    pf_exit_date = serializers.DateField(allow_null=True)
    pf_status = serializers.CharField(allow_null=True)
    is_higher_pension_wages = serializers.BooleanField(allow_null=True)
    earlier_member_of_pension_on_higher_wages = serializers.BooleanField(allow_null=True)


class EsiDetailsSerializer(serializers.Serializer):
    is_esi_covered = serializers.BooleanField(allow_null=True)
    esic_no = serializers.CharField(allow_null=True)
    esic_no_last4 = serializers.CharField(allow_null=True)
    esic_type = serializers.CharField(allow_null=True)
    esic_employee_contribution = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    esic_employer_contribution = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    esic_joining_date = serializers.DateField(allow_null=True)
    esic_dispensary = serializers.CharField(allow_null=True)
    esic_status = serializers.CharField(allow_null=True)


class LwfDetailsSerializer(serializers.Serializer):
    is_lwf_covered = serializers.BooleanField(allow_null=True)
    lin_number = serializers.CharField(allow_null=True)
    lin_number_last4 = serializers.CharField(allow_null=True)


class AuditUserSerializer(serializers.Serializer):
    id = serializers.CharField(allow_null=True)
    name = serializers.CharField(allow_null=True)


class StatutoryDocumentsSerializer(serializers.Serializer):
    pan = serializers.CharField(allow_null=True)
    pan_last4 = serializers.CharField(allow_null=True)
    pan_verified = serializers.BooleanField(allow_null=True)
    pan_verified_at = serializers.DateTimeField(allow_null=True)
    aadhaar_no = serializers.CharField(allow_null=True)
    aadhaar_last4 = serializers.CharField(allow_null=True)
    aadhaar_linked = serializers.BooleanField(allow_null=True)
    tax_regime_id = serializers.UUIDField(allow_null=True)
    tax_regime_name = serializers.CharField(allow_null=True)
    tax_regime_code = serializers.CharField(allow_null=True)


class AuditSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)
    created_by = AuditUserSerializer(allow_null=True)
    updated_by = AuditUserSerializer(allow_null=True)


class BankStatutoryDetailsSerializer(serializers.Serializer):
    employee = EmployeeSummarySerializer()
    bank_account = BankAccountSerializer(allow_null=True)
    bank_accounts = BankAccountSerializer(many=True, required=False)
    statutory_documents = StatutoryDocumentsSerializer()
    pf_details = PfDetailsSerializer()
    esi_details = EsiDetailsSerializer()
    lwf_details = LwfDetailsSerializer()
    audit = AuditSerializer()
