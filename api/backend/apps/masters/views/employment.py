"""ViewSets for employment master APIs."""

from apps.employees.models.masters.employment import (
    EmployeeCategory,
    EmployeeStatus,
    EmployeeType,
    PayrollGroup,
    PayrollMode,
    PayrollStatus,
    RelevantExperienceRange,
    SourceOfHire,
    SourceOfHireType,
    TransportType,
    WorkExperienceRange,
)
from apps.masters.serializers.employment import (
    EmployeeCategoryListSerializer,
    EmployeeCategorySerializer,
    EmployeeStatusListSerializer,
    EmployeeStatusSerializer,
    EmployeeTypeListSerializer,
    EmployeeTypeSerializer,
    PayrollGroupListSerializer,
    PayrollGroupSerializer,
    PayrollModeListSerializer,
    PayrollModeSerializer,
    PayrollStatusListSerializer,
    PayrollStatusSerializer,
    RelevantExperienceRangeListSerializer,
    RelevantExperienceRangeSerializer,
    SourceOfHireListSerializer,
    SourceOfHireSerializer,
    SourceOfHireTypeListSerializer,
    SourceOfHireTypeSerializer,
    TransportTypeListSerializer,
    TransportTypeSerializer,
    WorkExperienceRangeListSerializer,
    WorkExperienceRangeSerializer,
)
from apps.masters.views.base import DeletedAtMasterViewSet


class EmploymentMasterViewSet(DeletedAtMasterViewSet):


    search_fields = ["code", "label"]


class EmployeeTypeViewSet(EmploymentMasterViewSet):
    queryset = EmployeeType.objects.all()
    serializer_class = EmployeeTypeSerializer
    list_serializer_class = EmployeeTypeListSerializer


class EmployeeCategoryViewSet(EmploymentMasterViewSet):
    queryset = EmployeeCategory.objects.all()
    serializer_class = EmployeeCategorySerializer
    list_serializer_class = EmployeeCategoryListSerializer


class SourceOfHireViewSet(EmploymentMasterViewSet):
    queryset = SourceOfHire.objects.all()
    serializer_class = SourceOfHireSerializer
    list_serializer_class = SourceOfHireListSerializer


class SourceOfHireTypeViewSet(EmploymentMasterViewSet):
    queryset = SourceOfHireType.objects.all()
    serializer_class = SourceOfHireTypeSerializer
    list_serializer_class = SourceOfHireTypeListSerializer
    ordering_fields = ["id", "code", "label", "is_internal", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        is_internal = self.request.query_params.get("is_internal", "").lower()
        if is_internal in ("true", "false"):
            qs = qs.filter(is_internal=is_internal == "true")
        return qs


class PayrollStatusViewSet(EmploymentMasterViewSet):
    queryset = PayrollStatus.objects.all()
    serializer_class = PayrollStatusSerializer
    list_serializer_class = PayrollStatusListSerializer
    search_fields = ["code", "label", "description"]


class PayrollModeViewSet(EmploymentMasterViewSet):
    queryset = PayrollMode.objects.all()
    serializer_class = PayrollModeSerializer
    list_serializer_class = PayrollModeListSerializer


class PayrollGroupViewSet(EmploymentMasterViewSet):
    queryset = PayrollGroup.objects.all()
    serializer_class = PayrollGroupSerializer
    list_serializer_class = PayrollGroupListSerializer


class TransportTypeViewSet(EmploymentMasterViewSet):
    queryset = TransportType.objects.all()
    serializer_class = TransportTypeSerializer
    list_serializer_class = TransportTypeListSerializer


class EmployeeStatusViewSet(EmploymentMasterViewSet):
    queryset = EmployeeStatus.objects.all()
    serializer_class = EmployeeStatusSerializer
    list_serializer_class = EmployeeStatusListSerializer
    ordering_fields = ["id", "code", "label", "is_terminal", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        is_terminal = self.request.query_params.get("is_terminal", "").lower()
        if is_terminal in ("true", "false"):
            qs = qs.filter(is_terminal=is_terminal == "true")
        return qs


class WorkExperienceRangeViewSet(EmploymentMasterViewSet):
    queryset = WorkExperienceRange.objects.all()
    serializer_class = WorkExperienceRangeSerializer
    list_serializer_class = WorkExperienceRangeListSerializer
    ordering_fields = ["id", "code", "label", "min_months", "max_months"]
    ordering = ["min_months", "label"]


class RelevantExperienceRangeViewSet(EmploymentMasterViewSet):
    queryset = RelevantExperienceRange.objects.all()
    serializer_class = RelevantExperienceRangeSerializer
    list_serializer_class = RelevantExperienceRangeListSerializer
    ordering_fields = ["id", "code", "label", "min_months", "max_months"]
    ordering = ["min_months", "label"]
