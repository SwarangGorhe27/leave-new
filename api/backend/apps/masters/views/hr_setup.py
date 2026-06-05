

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.employees.models.masters.hr_setup import (
    Band,
    Branch,
    BusinessUnit,
    CostCenter,
    Holiday,
    HolidayCalendar,
    HolidayGroup,
    ProfitCenter,
    Shift,
    ShiftType,
    WorkWeekPolicy,
)
from apps.masters.serializers.hr_setup import (
    BandListSerializer,
    BandSerializer,
    BranchListSerializer,
    BranchSerializer,
    BusinessUnitListSerializer,
    BusinessUnitSerializer,
    CostCenterListSerializer,
    CostCenterSerializer,
    HolidayCalendarListSerializer,
    HolidayCalendarSerializer,
    HolidayGroupListSerializer,
    HolidayGroupSerializer,
    HolidayListSerializer,
    HolidaySerializer,
    ProfitCenterListSerializer,
    ProfitCenterSerializer,
    ShiftListSerializer,
    ShiftSerializer,
    ShiftTypeListSerializer,
    ShiftTypeSerializer,
    WorkWeekPolicyListSerializer,
    WorkWeekPolicySerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class HRSetupMasterViewSet(ActiveMasterViewSet):
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    search_lookup_fields = ("code", "name")
    display_field = "name"


class BranchViewSet(HRSetupMasterViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    list_serializer_class = BranchListSerializer
    search_fields = ["code", "name", "gstin"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if branch_type := self.request.query_params.get("branch_type", "").upper():
            qs = qs.filter(branch_type=branch_type)
        if (v := self.request.query_params.get("is_payroll_entity", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(is_payroll_entity=(v == "true"))
        return qs


class BusinessUnitViewSet(HRSetupMasterViewSet):
    queryset = BusinessUnit.objects.all()
    serializer_class = BusinessUnitSerializer
    list_serializer_class = BusinessUnitListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        return qs


class CostCenterViewSet(HRSetupMasterViewSet):
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer
    list_serializer_class = CostCenterListSerializer
    search_fields = ["code", "name", "budget_code"]

    def get_queryset(self):
        qs = super().get_queryset()
        for param, field in [
            ("company_id", "company_id"),
            ("branch_id", "branch_id"),
            ("parent_cost_center_id", "parent_cost_center_id"),
        ]:
            if v := self.request.query_params.get(param):
                qs = qs.filter(**{field: v})
        if cct := self.request.query_params.get("cost_center_type", "").upper():
            qs = qs.filter(cost_center_type=cct)
        return qs


class ProfitCenterViewSet(HRSetupMasterViewSet):
    queryset = ProfitCenter.objects.all()
    serializer_class = ProfitCenterSerializer
    list_serializer_class = ProfitCenterListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        return qs


class BandViewSet(HRSetupMasterViewSet):
    queryset = Band.objects.all()
    serializer_class = BandSerializer
    list_serializer_class = BandListSerializer
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "min_ctc", "max_ctc"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if v := self.request.query_params.get("min_ctc_lte"):
            qs = qs.filter(min_ctc__lte=v)
        if v := self.request.query_params.get("max_ctc_gte"):
            qs = qs.filter(max_ctc__gte=v)
        return qs


class ShiftTypeViewSet(HRSetupMasterViewSet):
    queryset = ShiftType.objects.all()
    serializer_class = ShiftTypeSerializer
    list_serializer_class = ShiftTypeListSerializer
    search_fields = ["code", "name"]
    ordering = ["sort_order", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if v := self.request.query_params.get("sort_order"):
            qs = qs.filter(sort_order=v)
        return qs


class ShiftViewSet(HRSetupMasterViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    list_serializer_class = ShiftListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if v := self.request.query_params.get("shift_type_id"):
            qs = qs.filter(shift_type_id=v)
        for flag in ("is_overnight", "is_flexible", "ot_applicable"):
            if (v := self.request.query_params.get(flag, "").lower()) in (
                "true",
                "false",
            ):
                qs = qs.filter(**{flag: v == "true"})
        return qs


class WorkWeekPolicyViewSet(HRSetupMasterViewSet):
    queryset = WorkWeekPolicy.objects.all()
    serializer_class = WorkWeekPolicySerializer
    list_serializer_class = WorkWeekPolicyListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if v := self.request.query_params.get("working_days"):
            qs = qs.filter(working_days=v)
        return qs


class HolidayCalendarViewSet(HRSetupMasterViewSet):
    queryset = HolidayCalendar.objects.all()
    serializer_class = HolidayCalendarSerializer
    list_serializer_class = HolidayCalendarListSerializer
    search_fields = ["code", "name"]
    ordering_fields = ["calendar_year", "name", "code"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if v := self.request.query_params.get("calendar_year"):
            qs = qs.filter(calendar_year=v)
        if v := self.request.query_params.get("branch_id"):
            qs = qs.filter(branch_id=v)
        return qs


class HolidayViewSet(HRSetupMasterViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    list_serializer_class = HolidayListSerializer
    search_fields = ["name"]
    ordering_fields = ["holiday_date", "name"]
    ordering = ["holiday_date"]

    def get_queryset(self):
        qs = super().get_queryset()
        if v := self.request.query_params.get("holiday_calendar_id"):
            qs = qs.filter(holiday_calendar_id=v)
        if v := self.request.query_params.get("holiday_type", "").upper():
            qs = qs.filter(holiday_type=v)
        if v := self.request.query_params.get("date_from"):
            qs = qs.filter(holiday_date__gte=v)
        if v := self.request.query_params.get("date_to"):
            qs = qs.filter(holiday_date__lte=v)
        return qs

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request):
        qs = self.get_queryset()
        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(name__icontains=search)
        return Response(HolidayListSerializer(qs, many=True).data)


class HolidayGroupViewSet(HRSetupMasterViewSet):
    queryset = HolidayGroup.objects.all()
    serializer_class = HolidayGroupSerializer
    list_serializer_class = HolidayGroupListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        if v := self.request.query_params.get("holiday_calendar_id"):
            qs = qs.filter(holiday_calendar_id=v)
        return qs
