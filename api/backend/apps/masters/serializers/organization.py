"""Serializers for organization master tables."""

from rest_framework import serializers

from apps.employees.models.masters.organization import (
    AccountType,
    Bank,
    BankStatus,
    Batch,
    Cab,
    Company,
    Department,
    DepartmentDivision,
    Designation,
    Extension,
    Grade,
    Team,
)


AUDIT_FIELDS = [
    "is_active",
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

READ_ONLY_AUDIT_FIELDS = ["id", "created_at", "updated_at", "deleted_at"]


def _validate_unique(value, model, field="code", instance=None, **scope):
    qs = model.objects.filter(**{f"{field}__iexact": value})
    for key, scope_value in scope.items():
        if scope_value:
            qs = qs.filter(**{key: scope_value})
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with {field} '{value}' already exists."
        )
    return value


class GlobalCodeMixin:
    code_field = "code"

    def validate_code(self, value):
        return _validate_unique(value, self.Meta.model, self.code_field, self.instance)


class CompanyScopedCodeMixin:
    code_field = "code"

    def validate_code(self, value):
        company = (
            self.initial_data.get("company_id")
            or getattr(self.instance, "company_id", None)
        )
        return _validate_unique(
            value,
            self.Meta.model,
            self.code_field,
            self.instance,
            company_id=company,
        )


class CompanySerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "code",
            "name",
            "pan",
            "gstin",
            "cin",
            "registered_address",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "code", "name", "pan", "gstin", "is_active"]


class DepartmentSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(
        source="company", queryset=Company.objects.all()
    )
    parent_department_id = serializers.PrimaryKeyRelatedField(
        source="parent_department",
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Department
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "parent_department_id",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class DepartmentListSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(source="company.id", read_only=True)
    parent_department_id = serializers.UUIDField(
        source="parent_department.id", read_only=True
    )

    class Meta:
        model = Department
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "parent_department_id",
            "is_active",
        ]


class TeamSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(
        source="company", queryset=Company.objects.all()
    )
    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Team
        fields = ["id", "company_id", "department_id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class TeamListSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(source="company.id", read_only=True)
    department_id = serializers.UUIDField(source="department.id", read_only=True)

    class Meta:
        model = Team
        fields = ["id", "company_id", "department_id", "code", "name", "is_active"]


class DesignationSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(
        source="company", queryset=Company.objects.all()
    )
    grade_id = serializers.PrimaryKeyRelatedField(
        source="grade", queryset=Grade.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Designation
        fields = ["id", "company_id", "code", "title", "grade_id", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class DesignationListSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(source="company.id", read_only=True)
    grade_id = serializers.UUIDField(source="grade.id", read_only=True)

    class Meta:
        model = Designation
        fields = ["id", "company_id", "code", "title", "grade_id", "is_active"]


class GradeSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(
        source="company", queryset=Company.objects.all()
    )

    class Meta:
        model = Grade
        fields = [
            "id",
            "company_id",
            "code",
            "label",
            "level_number",
            "seniority_level",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_level_number(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("level_number must be greater than 0.")
        return value


class GradeListSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(source="company.id", read_only=True)

    class Meta:
        model = Grade
        fields = [
            "id",
            "company_id",
            "code",
            "label",
            "level_number",
            "seniority_level",
            "is_active",
        ]


class BankSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            "id",
            "code",
            "name",
            "ifsc_prefix",
            "branch",
            "centre",
            "district",
            "state",
            "address",
            "contact",
            "city",
            "iso3166",
            "micr",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class BankListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            "id",
            "code",
            "name",
            "ifsc_prefix",
            "branch",
            "centre",
            "district",
            "state",
            "address",
            "contact",
            "city",
            "iso3166",
            "micr",
            "is_active",
        ]


class BankStatusSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = BankStatus
        fields = ["id", "code", "label", "is_terminal", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class BankStatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankStatus
        fields = ["id", "code", "label", "is_terminal", "is_active"]


class AccountTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = [
            "id",
            "code",
            "label",
            "description",
            "is_salary_allowed",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class AccountTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ["id", "code", "label", "description", "is_salary_allowed", "is_active"]


class DepartmentDivisionSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(
        source="department", queryset=Department.objects.all()
    )

    class Meta:
        model = DepartmentDivision
        fields = ["id", "department_id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_code(self, value):
        department = (
            self.initial_data.get("department_id")
            or getattr(self.instance, "department_id", None)
        )
        return _validate_unique(
            value,
            DepartmentDivision,
            "code",
            self.instance,
            department_id=department,
        )


class DepartmentDivisionListSerializer(serializers.ModelSerializer):
    department_id = serializers.UUIDField(source="department.id", read_only=True)

    class Meta:
        model = DepartmentDivision
        fields = ["id", "department_id", "code", "label", "is_active"]


class ExtensionSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Extension
        fields = ["id", "code", "label", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ExtensionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extension
        fields = ["id", "code", "label", "is_active"]


class BatchSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ["id", "code", "label", "start_year", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_start_year(self, value):
        if value is not None and value < 2000:
            raise serializers.ValidationError("start_year must be 2000 or later.")
        return value


class BatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ["id", "code", "label", "start_year", "is_active"]


class CabSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = Cab
        fields = ["id", "code", "label", "is_ac", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class CabListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cab
        fields = ["id", "code", "label", "is_ac", "is_active"]
