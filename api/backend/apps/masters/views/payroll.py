
from django.db.models import Q

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
from apps.masters.serializers.payroll import (
    ArrearTypeListSerializer,
    ArrearTypeSerializer,
    EsiSchemeListSerializer,
    EsiSchemeSerializer,
    LabourRegisterTypeListSerializer,
    LabourRegisterTypeSerializer,
    LoanTypeListSerializer,
    LoanTypeSerializer,
    LwfSlabListSerializer,
    LwfSlabSerializer,
    PayComponentGroupListSerializer,
    PayComponentGroupSerializer,
    PayComponentListSerializer,
    PayComponentSerializer,
    PayrollCycleListSerializer,
    PayrollCycleSerializer,
    PfSchemeListSerializer,
    PfSchemeSerializer,
    PtStateSlabListSerializer,
    PtStateSlabSerializer,
    ReimbursementTypeListSerializer,
    ReimbursementTypeSerializer,
    SalaryStructureComponentListSerializer,
    SalaryStructureComponentSerializer,
    SalaryStructureListSerializer,
    SalaryStructureSerializer,
    StatutoryComponentListSerializer,
    StatutoryComponentSerializer,
    TaxRegimeListSerializer,
    TaxRegimeSerializer,
    TdsSectionListSerializer,
    TdsSectionSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class PayrollMasterViewSet(ActiveMasterViewSet):
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    search_lookup_fields = ("code", "name")
    display_field = "name"


class PayComponentGroupViewSet(PayrollMasterViewSet):
    queryset = PayComponentGroup.objects.all()
    serializer_class = PayComponentGroupSerializer
    list_serializer_class = PayComponentGroupListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if (v := self.request.query_params.get("is_earning", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_earning=(v == "true"))
        return qs


class PayComponentViewSet(PayrollMasterViewSet):
    queryset = PayComponent.objects.all()
    serializer_class = PayComponentSerializer
    list_serializer_class = PayComponentListSerializer
    search_fields = ["code", "name"]
    ordering = ["sort_order", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        for param in ("company_id", "component_group_id", "component_type", "formula_type"):
            if v := self.request.query_params.get(param):
                qs = qs.filter(**{param: v})
        return qs


class SalaryStructureViewSet(PayrollMasterViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    list_serializer_class = SalaryStructureListSerializer
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "effective_from", "min_ctc", "max_ctc"]

    def get_queryset(self):
        qs = super().get_queryset()
        for param in ("company_id", "grade_id", "band_id"):
            if v := self.request.query_params.get(param):
                qs = qs.filter(**{param: v})
        if v := self.request.query_params.get("effective_on"):
            qs = qs.filter(effective_from__lte=v).filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=v)
            )
        return qs


class SalaryStructureComponentViewSet(ActiveMasterViewSet):
    queryset = SalaryStructureComponent.objects.all()
    serializer_class = SalaryStructureComponentSerializer
    list_serializer_class = SalaryStructureComponentListSerializer
    search_fields = []
    search_lookup_fields = ()
    ordering_fields = ["calculation_order", "created_at"]
    ordering = ["calculation_order"]

    def get_queryset(self):
        qs = super().get_queryset()
        for param in ("salary_structure_id", "pay_component_id"):
            if v := self.request.query_params.get(param):
                qs = qs.filter(**{param: v})
        if (v := self.request.query_params.get("is_mandatory", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_mandatory=(v == "true"))
        return qs


class ReimbursementTypeViewSet(PayrollMasterViewSet):
    queryset = ReimbursementType.objects.all()
    serializer_class = ReimbursementTypeSerializer
    list_serializer_class = ReimbursementTypeListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if (v := self.request.query_params.get("requires_receipt", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(requires_receipt=(v == "true"))
        if (v := self.request.query_params.get("taxable", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(taxable=(v == "true"))
        return qs


class LoanTypeViewSet(PayrollMasterViewSet):
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer
    list_serializer_class = LoanTypeListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if (v := self.request.query_params.get("requires_approval", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(requires_approval=(v == "true"))
        return qs


class PayrollCycleViewSet(PayrollMasterViewSet):
    queryset = PayrollCycle.objects.all()
    serializer_class = PayrollCycleSerializer
    list_serializer_class = PayrollCycleListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if frequency := self.request.query_params.get("frequency"):
            qs = qs.filter(frequency=frequency)
        return qs


class TaxRegimeViewSet(PayrollMasterViewSet):
    queryset = TaxRegime.objects.all()
    serializer_class = TaxRegimeSerializer
    list_serializer_class = TaxRegimeListSerializer
    search_fields = ["code", "name", "financial_year"]

    def get_queryset(self):
        qs = super().get_queryset()
        if financial_year := self.request.query_params.get("financial_year"):
            qs = qs.filter(financial_year=financial_year)
        return qs


class TdsSectionViewSet(ActiveMasterViewSet):
    queryset = TdsSection.objects.all()
    serializer_class = TdsSectionSerializer
    list_serializer_class = TdsSectionListSerializer
    search_fields = ["section_code", "description", "category"]
    search_lookup_fields = ("section_code", "description", "category")
    display_field = "section_code"
    ordering_fields = ["section_code", "category", "created_at"]
    ordering = ["section_code"]

    def get_queryset(self):
        qs = super().get_queryset()
        if category := self.request.query_params.get("category"):
            qs = qs.filter(category__iexact=category)
        return qs


class ArrearTypeViewSet(PayrollMasterViewSet):
    queryset = ArrearType.objects.all()
    serializer_class = ArrearTypeSerializer
    list_serializer_class = ArrearTypeListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        return qs


class StatutoryComponentViewSet(PayrollMasterViewSet):
    queryset = StatutoryComponent.objects.all()
    serializer_class = StatutoryComponentSerializer
    list_serializer_class = StatutoryComponentListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (v := self.request.query_params.get("is_employee_contribution", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_employee_contribution=(v == "true"))
        if (v := self.request.query_params.get("is_employer_contribution", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_employer_contribution=(v == "true"))
        return qs


class PfSchemeViewSet(PayrollMasterViewSet):
    queryset = PfScheme.objects.all()
    serializer_class = PfSchemeSerializer
    list_serializer_class = PfSchemeListSerializer
    search_fields = ["code", "name"]


class EsiSchemeViewSet(ActiveMasterViewSet):
    queryset = EsiScheme.objects.all()
    serializer_class = EsiSchemeSerializer
    list_serializer_class = EsiSchemeListSerializer
    search_fields = ["code"]
    search_lookup_fields = ("code",)
    display_field = "code"
    ordering_fields = ["code", "created_at"]
    ordering = ["code"]


class PtStateSlabViewSet(ActiveMasterViewSet):
    queryset = PtStateSlab.objects.all()
    serializer_class = PtStateSlabSerializer
    list_serializer_class = PtStateSlabListSerializer
    search_fields = ["financial_year"]
    search_lookup_fields = ("financial_year",)
    display_field = "financial_year"
    ordering_fields = ["state_id", "financial_year", "income_from"]
    ordering = ["state_id", "income_from"]

    def get_queryset(self):
        qs = super().get_queryset()
        for param in ("state_id", "financial_year"):
            if v := self.request.query_params.get(param):
                qs = qs.filter(**{param: v})
        return qs


class LwfSlabViewSet(ActiveMasterViewSet):
    queryset = LwfSlab.objects.all()
    serializer_class = LwfSlabSerializer
    list_serializer_class = LwfSlabListSerializer
    search_fields = ["frequency"]
    search_lookup_fields = ("frequency",)
    display_field = "frequency"
    ordering_fields = ["state_id", "frequency", "created_at"]
    ordering = ["state_id", "frequency"]

    def get_queryset(self):
        qs = super().get_queryset()
        if state_id := self.request.query_params.get("state_id"):
            qs = qs.filter(state_id=state_id)
        if frequency := self.request.query_params.get("frequency"):
            qs = qs.filter(frequency=frequency)
        return qs


class LabourRegisterTypeViewSet(PayrollMasterViewSet):
    queryset = LabourRegisterType.objects.all()
    serializer_class = LabourRegisterTypeSerializer
    list_serializer_class = LabourRegisterTypeListSerializer
    search_fields = ["code", "name", "statutory_form_ref"]
