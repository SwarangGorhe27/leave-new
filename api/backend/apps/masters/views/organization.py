"""ViewSets for organization master tables."""

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
from apps.masters.serializers.organization import (
    AccountTypeListSerializer,
    AccountTypeSerializer,
    BankListSerializer,
    BankSerializer,
    BankStatusListSerializer,
    BankStatusSerializer,
    BatchListSerializer,
    BatchSerializer,
    CabListSerializer,
    CabSerializer,
    CompanyListSerializer,
    CompanySerializer,
    DepartmentDivisionListSerializer,
    DepartmentDivisionSerializer,
    DepartmentListSerializer,
    DepartmentSerializer,
    DesignationListSerializer,
    DesignationSerializer,
    ExtensionListSerializer,
    ExtensionSerializer,
    GradeListSerializer,
    GradeSerializer,
    TeamListSerializer,
    TeamSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class OrganizationNameViewSet(ActiveMasterViewSet):
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    search_lookup_fields = ("code", "name")
    display_field = "name"


class OrganizationLabelViewSet(ActiveMasterViewSet):
    ordering_fields = ["code", "label", "created_at"]
    ordering = ["label"]
    search_lookup_fields = ("code", "label")
    display_field = "label"


class CompanyFilteredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        return qs


class CompanyViewSet(OrganizationNameViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    list_serializer_class = CompanyListSerializer
    search_fields = ["code", "name", "pan", "gstin", "cin"]


class DepartmentViewSet(CompanyFilteredMixin, OrganizationNameViewSet):
    queryset = Department.objects.select_related("company", "parent_department")
    serializer_class = DepartmentSerializer
    list_serializer_class = DepartmentListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if parent_department_id := self.request.query_params.get("parent_department_id"):
            qs = qs.filter(parent_department_id=parent_department_id)
        if self.request.query_params.get("top_level", "").lower() == "true":
            qs = qs.filter(parent_department__isnull=True)
        return qs


class TeamViewSet(CompanyFilteredMixin, OrganizationNameViewSet):
    queryset = Team.objects.select_related("company", "department")
    serializer_class = TeamSerializer
    list_serializer_class = TeamListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if department_id := self.request.query_params.get("department_id"):
            qs = qs.filter(department_id=department_id)
        return qs


class DesignationViewSet(CompanyFilteredMixin, ActiveMasterViewSet):
    queryset = Designation.objects.select_related("company", "grade")
    serializer_class = DesignationSerializer
    list_serializer_class = DesignationListSerializer
    search_fields = ["code", "title"]
    ordering_fields = ["code", "title", "created_at"]
    ordering = ["title"]
    search_lookup_fields = ("code", "title")
    display_field = "title"

    def get_queryset(self):
        qs = super().get_queryset()
        if grade_id := self.request.query_params.get("grade_id"):
            qs = qs.filter(grade_id=grade_id)
        return qs


class GradeViewSet(CompanyFilteredMixin, OrganizationLabelViewSet):
    queryset = Grade.objects.select_related("company")
    serializer_class = GradeSerializer
    list_serializer_class = GradeListSerializer
    search_fields = ["code", "label", "seniority_level"]
    ordering_fields = ["code", "label", "level_number", "seniority_level", "created_at"]
    ordering = ["level_number", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        if seniority_level := self.request.query_params.get("seniority_level"):
            qs = qs.filter(seniority_level__iexact=seniority_level)
        if level_number := self.request.query_params.get("level_number"):
            qs = qs.filter(level_number=level_number)
        return qs


class BankViewSet(OrganizationNameViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    list_serializer_class = BankListSerializer
    ordering_fields = [
        "code",
        "name",
        "ifsc_prefix",
        "branch",
        "centre",
        "district",
        "state",
        "city",
        "micr",
        "created_at",
    ]
    search_fields = [
        "code",
        "name",
        "ifsc_prefix",
        "branch",
        "centre",
        "district",
        "state",
        "city",
        "iso3166",
        "micr",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        if ifsc := self.request.query_params.get("ifsc"):
            qs = qs.filter(code__iexact=ifsc)
        if code := self.request.query_params.get("code"):
            qs = qs.filter(code__iexact=code)
        if ifsc_prefix := self.request.query_params.get("ifsc_prefix"):
            qs = qs.filter(ifsc_prefix__iexact=ifsc_prefix)
        if branch := self.request.query_params.get("branch"):
            qs = qs.filter(branch__icontains=branch)
        if district := self.request.query_params.get("district"):
            qs = qs.filter(district__iexact=district)
        if state := self.request.query_params.get("state"):
            qs = qs.filter(state__iexact=state)
        if city := self.request.query_params.get("city"):
            qs = qs.filter(city__iexact=city)
        if iso3166 := self.request.query_params.get("iso3166"):
            qs = qs.filter(iso3166__iexact=iso3166)
        if micr := self.request.query_params.get("micr"):
            qs = qs.filter(micr__iexact=micr)
        return qs


class BankStatusViewSet(OrganizationLabelViewSet):
    queryset = BankStatus.objects.all()
    serializer_class = BankStatusSerializer
    list_serializer_class = BankStatusListSerializer
    search_fields = ["code", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (value := self.request.query_params.get("is_terminal", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_terminal=(value == "true"))
        return qs


class AccountTypeViewSet(OrganizationLabelViewSet):
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer
    list_serializer_class = AccountTypeListSerializer
    search_fields = ["code", "label", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (value := self.request.query_params.get("is_salary_allowed", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_salary_allowed=(value == "true"))
        return qs


class DepartmentDivisionViewSet(OrganizationLabelViewSet):
    queryset = DepartmentDivision.objects.select_related("department")
    serializer_class = DepartmentDivisionSerializer
    list_serializer_class = DepartmentDivisionListSerializer
    search_fields = ["code", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        if department_id := self.request.query_params.get("department_id"):
            qs = qs.filter(department_id=department_id)
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(department__company_id=company_id)
        return qs


class ExtensionViewSet(OrganizationLabelViewSet):
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer
    list_serializer_class = ExtensionListSerializer
    search_fields = ["code", "label"]


class BatchViewSet(OrganizationLabelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    list_serializer_class = BatchListSerializer
    search_fields = ["code", "label"]
    ordering_fields = ["code", "label", "start_year", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if start_year := self.request.query_params.get("start_year"):
            qs = qs.filter(start_year=start_year)
        return qs


class CabViewSet(OrganizationLabelViewSet):
    queryset = Cab.objects.all()
    serializer_class = CabSerializer
    list_serializer_class = CabListSerializer
    search_fields = ["code", "label"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (value := self.request.query_params.get("is_ac", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_ac=(value == "true"))
        return qs
