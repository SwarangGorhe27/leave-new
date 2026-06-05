

from rest_framework import serializers

from apps.employees.models.masters.payroll import (
    ArrearType,
    EsiScheme,
    LabourRegisterType,
    LoanType,
    LwfSlab,
    PayComponent,
    PayComponentGroup,
    PayrollCycle,
    PfScheme,
    PtStateSlab,
    ReimbursementType,
    SalaryStructure,
    SalaryStructureComponent,
    StatutoryComponent,
    TaxRegime,
    TdsSection,
)


AUDIT_FIELDS = [
    "is_active",
    "created_at",
    "updated_at",
    "deleted_at",
    "created_by",
    "updated_by",
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
    "created_at",
    "updated_at",
    "deleted_at",
]


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


class CompanyScopedCodeMixin:
    code_field = "code"

    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or (self.instance.company_id if self.instance else None)
        )
        return _validate_unique(
            value,
            self.Meta.model,
            self.code_field,
            self.instance,
            company_id=company_id,
        )


class GlobalCodeMixin:
    code_field = "code"

    def validate_code(self, value):
        return _validate_unique(value, self.Meta.model, self.code_field, self.instance)


class PayComponentGroupSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = PayComponentGroup
        fields = ["id", "company_id", "code", "name", "is_earning", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class PayComponentGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayComponentGroup
        fields = ["id", "company_id", "code", "name", "is_earning", "is_active"]


class PayComponentSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = PayComponent
        fields = [
            "id",
            "company_id",
            "component_group_id",
            "code",
            "name",
            "component_type",
            "is_taxable",
            "is_pf_applicable",
            "is_esi_applicable",
            "is_pt_applicable",
            "is_lwf_applicable",
            "is_bonus_applicable",
            "formula_type",
            "formula_value",
            "formula_expression",
            "sort_order",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class PayComponentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayComponent
        fields = [
            "id",
            "company_id",
            "component_group_id",
            "code",
            "name",
            "component_type",
            "sort_order",
            "is_active",
        ]


class SalaryStructureSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "grade_id",
            "band_id",
            "min_ctc",
            "max_ctc",
            "currency_code",
            "effective_from",
            "effective_to",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate(self, attrs):
        min_ctc = attrs.get("min_ctc", getattr(self.instance, "min_ctc", None))
        max_ctc = attrs.get("max_ctc", getattr(self.instance, "max_ctc", None))
        if min_ctc is not None and max_ctc is not None and max_ctc < min_ctc:
            raise serializers.ValidationError(
                {"max_ctc": "max_ctc must be greater than or equal to min_ctc."}
            )
        return attrs


class SalaryStructureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "grade_id",
            "band_id",
            "effective_from",
            "effective_to",
            "is_active",
        ]


class SalaryStructureComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructureComponent
        fields = [
            "id",
            "salary_structure_id",
            "pay_component_id",
            "calculation_order",
            "min_amount",
            "max_amount",
            "formula_override",
            "is_mandatory",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate(self, attrs):
        min_amount = attrs.get("min_amount", getattr(self.instance, "min_amount", None))
        max_amount = attrs.get("max_amount", getattr(self.instance, "max_amount", None))
        if min_amount is not None and max_amount is not None and max_amount < min_amount:
            raise serializers.ValidationError(
                {"max_amount": "max_amount must be greater than or equal to min_amount."}
            )
        return attrs


class SalaryStructureComponentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructureComponent
        fields = [
            "id",
            "salary_structure_id",
            "pay_component_id",
            "calculation_order",
            "is_mandatory",
            "is_active",
        ]


class ReimbursementTypeSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = ReimbursementType
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "max_per_month",
            "requires_receipt",
            "taxable",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ReimbursementTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReimbursementType
        fields = ["id", "company_id", "code", "name", "max_per_month", "is_active"]


class LoanTypeSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "max_amount",
            "max_installments",
            "default_interest_rate",
            "requires_approval",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class LoanTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = ["id", "company_id", "code", "name", "max_amount", "is_active"]


class PayrollCycleSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = PayrollCycle
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "frequency",
            "pay_date_day",
            "cut_off_day",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class PayrollCycleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollCycle
        fields = ["id", "company_id", "code", "name", "frequency", "is_active"]


class TaxRegimeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = TaxRegime
        fields = [
            "id",
            "code",
            "name",
            "financial_year",
            "standard_deduction",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class TaxRegimeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRegime
        fields = ["id", "code", "name", "financial_year", "is_active"]


class TdsSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TdsSection
        fields = [
            "id",
            "section_code",
            "description",
            "max_deduction",
            "category",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate_section_code(self, value):
        return _validate_unique(value, TdsSection, "section_code", self.instance)


class TdsSectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TdsSection
        fields = ["id", "section_code", "description", "category", "is_active"]


class ArrearTypeSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = ArrearType
        fields = ["id", "company_id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ArrearTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArrearType
        fields = ["id", "company_id", "code", "name", "is_active"]


class StatutoryComponentSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = StatutoryComponent
        fields = [
            "id",
            "code",
            "name",
            "is_employee_contribution",
            "is_employer_contribution",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class StatutoryComponentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatutoryComponent
        fields = [
            "id",
            "code",
            "name",
            "is_employee_contribution",
            "is_employer_contribution",
            "is_active",
        ]


class PfSchemeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = PfScheme
        fields = [
            "id",
            "code",
            "name",
            "employee_rate",
            "employer_rate",
            "wage_ceiling",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class PfSchemeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PfScheme
        fields = ["id", "code", "name", "employee_rate", "employer_rate", "is_active"]


class EsiSchemeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = EsiScheme
        fields = [
            "id",
            "code",
            "employee_rate",
            "employer_rate",
            "wage_ceiling",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class EsiSchemeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EsiScheme
        fields = ["id", "code", "employee_rate", "employer_rate", "is_active"]


class PtStateSlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = PtStateSlab
        fields = [
            "id",
            "state_id",
            "income_from",
            "income_to",
            "annual_tax",
            "financial_year",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class PtStateSlabListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PtStateSlab
        fields = ["id", "state_id", "financial_year", "income_from", "income_to", "annual_tax", "is_active"]


class LwfSlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = LwfSlab
        fields = [
            "id",
            "state_id",
            "employee_contribution",
            "employer_contribution",
            "frequency",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class LwfSlabListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LwfSlab
        fields = ["id", "state_id", "frequency", "employee_contribution", "employer_contribution", "is_active"]


class LabourRegisterTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = LabourRegisterType
        fields = ["id", "code", "name", "statutory_form_ref", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class LabourRegisterTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabourRegisterType
        fields = ["id", "code", "name", "statutory_form_ref", "is_active"]
