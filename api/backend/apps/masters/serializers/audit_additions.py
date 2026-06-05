"""Serializers for audit-addition master APIs."""

from rest_framework import serializers

from apps.employees.models.employee import Employee
from apps.employees.models.masters.audit_additions import (
    AuthorizedSignatory,
    BulletinCategory,
    ClearanceItemType,
    ContractStatus,
    CounterParty,
    EmployeeFilter,
    FormCategory,
    ImportType,
    LetterApprovalType,
    PaymentType,
    PolicyCategory,
    PositionChangeReason,
    ReportingManager,
    ResidentialStatus,
    SeparationMode,
    VerificationStatus,
)
from apps.employees.models.masters.organization import Department, Designation


AUDIT_FIELDS = [
    "is_active",
    "created_by",
    "updated_by",
    "created_at",
    "updated_at",
    "deleted_at",
    "meta_data",
    "meta_version",
    "created_by_system",
    "updated_by_system",
    "created_source",
    "updated_source",
    "meta_tags",
    "extra_attributes",
]

READ_ONLY_AUDIT_FIELDS = [
    "id",
    "created_by",
    "updated_by",
    "created_at",
    "updated_at",
    "deleted_at",
]


def _validate_unique_code(value, model, instance=None, company_id=None):
    value = value.strip().upper()
    qs = model.objects.filter(code__iexact=value)
    if company_id:
        qs = qs.filter(company_id=company_id)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with code '{value}' already exists."
        )
    return value


class GlobalCodeMixin:
    def validate_code(self, value):
        return _validate_unique_code(value, self.Meta.model, self.instance)


class CompanyScopedCodeMixin:
    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or getattr(self.instance, "company_id", None)
        )
        return _validate_unique_code(
            value,
            self.Meta.model,
            self.instance,
            company_id=company_id,
        )


class _NameMasterListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "code", "name", "is_active"]


class SeparationModeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = SeparationMode
        fields = [
            "id",
            "code",
            "name",
            "is_voluntary",
            "is_terminal",
            "sort_order",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class SeparationModeListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = SeparationMode
        fields = [
            "id",
            "code",
            "name",
            "is_voluntary",
            "is_terminal",
            "sort_order",
            "is_active",
        ]


class ContractStatusSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = ContractStatus
        fields = [
            "id",
            "code",
            "name",
            "display_color",
            "is_terminal",
            "sort_order",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ContractStatusListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = ContractStatus
        fields = [
            "id",
            "code",
            "name",
            "display_color",
            "is_terminal",
            "sort_order",
            "is_active",
        ]


class VerificationStatusSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = VerificationStatus
        fields = [
            "id",
            "code",
            "name",
            "is_positive",
            "is_terminal",
            "sort_order",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class VerificationStatusListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = VerificationStatus
        fields = [
            "id",
            "code",
            "name",
            "is_positive",
            "is_terminal",
            "sort_order",
            "is_active",
        ]


class ResidentialStatusSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = ResidentialStatus
        fields = ["id", "code", "name", "tax_regime_note", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ResidentialStatusListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = ResidentialStatus
        fields = ["id", "code", "name", "tax_regime_note", "is_active"]


class PaymentTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = [
            "id",
            "code",
            "name",
            "requires_bank_account",
            "requires_ifsc",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class PaymentTypeListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = PaymentType
        fields = [
            "id",
            "code",
            "name",
            "requires_bank_account",
            "requires_ifsc",
            "is_active",
        ]


class EmployeeFilterSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = EmployeeFilter
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "filter_type",
            "description",
            "is_system",
            "member_count",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class EmployeeFilterListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = EmployeeFilter
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "filter_type",
            "is_system",
            "member_count",
            "is_active",
        ]


class BulletinCategorySerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = BulletinCategory
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "context_type",
            "icon_url",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class BulletinCategoryListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = BulletinCategory
        fields = ["id", "company_id", "code", "name", "context_type", "is_active"]


class PolicyCategorySerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = PolicyCategory
        fields = ["id", "company_id", "code", "name", "sort_order", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class PolicyCategoryListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = PolicyCategory
        fields = ["id", "company_id", "code", "name", "sort_order", "is_active"]


class FormCategorySerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = FormCategory
        fields = ["id", "company_id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class FormCategoryListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = FormCategory
        fields = ["id", "company_id", "code", "name", "is_active"]


class ImportTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = ImportType
        fields = [
            "id",
            "code",
            "name",
            "module_category",
            "template_schema",
            "requires_effective_date",
            "sample_file_url",
            "sort_order",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ImportTypeListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = ImportType
        fields = [
            "id",
            "code",
            "name",
            "module_category",
            "requires_effective_date",
            "sort_order",
            "is_active",
        ]


class LetterApprovalTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = LetterApprovalType
        fields = [
            "id",
            "code",
            "name",
            "requires_digital_signature",
            "requires_approver",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class LetterApprovalTypeListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = LetterApprovalType
        fields = [
            "id",
            "code",
            "name",
            "requires_digital_signature",
            "requires_approver",
            "is_active",
        ]


class ClearanceItemTypeSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = ClearanceItemType
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "responsible_department_id",
            "sort_order",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ClearanceItemTypeListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = ClearanceItemType
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "responsible_department_id",
            "sort_order",
            "is_active",
        ]


class PositionChangeReasonSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = PositionChangeReason
        fields = ["id", "code", "name", "change_type", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class PositionChangeReasonListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = PositionChangeReason
        fields = ["id", "code", "name", "change_type", "is_active"]


class CounterPartySerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = CounterParty
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "counter_party_type",
            "gstin",
            "pan",
            "contact_email",
            "contact_phone",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CounterPartyListSerializer(_NameMasterListSerializer):
    class Meta(_NameMasterListSerializer.Meta):
        model = CounterParty
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "counter_party_type",
            "gstin",
            "pan",
            "is_active",
        ]


class AuthorizedSignatorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizedSignatory
        fields = [
            "id",
            "company_id",
            "employee_id",
            "signatory_name",
            "signatory_title",
            "digital_signature_file",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class AuthorizedSignatoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizedSignatory
        fields = [
            "id",
            "company_id",
            "employee_id",
            "signatory_name",
            "signatory_title",
            "is_active",
        ]


class ReportingManagerSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        source="employee",
        queryset=Employee.objects.filter(is_active=True),
    )
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    designation_id = serializers.PrimaryKeyRelatedField(
        source="designation",
        queryset=Designation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    designation_title = serializers.CharField(source="designation.title", read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = ReportingManager
        fields = [
            "id",
            "company_id",
            "employee_id",
            "employee_code",
            "employee_name",
            "designation_id",
            "designation_title",
            "department_id",
            "department_name",
            "is_primary",
            "sort_order",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ReportingManagerListSerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    designation_id = serializers.UUIDField(source="designation.id", read_only=True)
    designation_title = serializers.CharField(source="designation.title", read_only=True)
    department_id = serializers.UUIDField(source="department.id", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = ReportingManager
        fields = [
            "id",
            "company_id",
            "employee_id",
            "employee_code",
            "employee_name",
            "designation_id",
            "designation_title",
            "department_id",
            "department_name",
            "is_primary",
            "sort_order",
            "is_active",
        ]
