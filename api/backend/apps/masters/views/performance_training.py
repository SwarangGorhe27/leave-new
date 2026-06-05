

from apps.employees.models.masters.performance_training import (
    AppraisalCycle,
    AssetCategory,
    AssetCondition,
    AssetType,
    CertificationBody,
    Competency,
    CompetencyGroup,
    Course,
    GoalCategory,
    KpiLibrary,
    KraLibrary,
    RatingScale,
    TrainingCategory,
    TrainingMode,
    Vendor,
)
from apps.masters.serializers.performance_training import (
    AppraisalCycleListSerializer,
    AppraisalCycleSerializer,
    AssetCategoryListSerializer,
    AssetCategorySerializer,
    AssetConditionListSerializer,
    AssetConditionSerializer,
    AssetTypeListSerializer,
    AssetTypeSerializer,
    CertificationBodyListSerializer,
    CertificationBodySerializer,
    CompetencyGroupListSerializer,
    CompetencyGroupSerializer,
    CompetencyListSerializer,
    CompetencySerializer,
    CourseListSerializer,
    CourseSerializer,
    GoalCategoryListSerializer,
    GoalCategorySerializer,
    KpiLibraryListSerializer,
    KpiLibrarySerializer,
    KraLibraryListSerializer,
    KraLibrarySerializer,
    RatingScaleListSerializer,
    RatingScaleSerializer,
    TrainingCategoryListSerializer,
    TrainingCategorySerializer,
    TrainingModeListSerializer,
    TrainingModeSerializer,
    VendorListSerializer,
    VendorSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


class PerformanceTrainingMasterViewSet(ActiveMasterViewSet):
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    search_lookup_fields = ("code", "name")
    display_field = "name"


class CompanyFilteredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        return qs


class AppraisalCycleViewSet(PerformanceTrainingMasterViewSet):
    queryset = AppraisalCycle.objects.all()
    serializer_class = AppraisalCycleSerializer
    list_serializer_class = AppraisalCycleListSerializer
    search_fields = ["code", "name"]


class RatingScaleViewSet(CompanyFilteredMixin, ActiveMasterViewSet):
    queryset = RatingScale.objects.all()
    serializer_class = RatingScaleSerializer
    list_serializer_class = RatingScaleListSerializer
    search_fields = ["code"]
    search_lookup_fields = ("code",)
    display_field = "code"
    ordering_fields = ["code", "min_value", "max_value", "created_at"]
    ordering = ["code"]


class GoalCategoryViewSet(PerformanceTrainingMasterViewSet):
    queryset = GoalCategory.objects.all()
    serializer_class = GoalCategorySerializer
    list_serializer_class = GoalCategoryListSerializer
    search_fields = ["code", "name"]


class KpiLibraryViewSet(CompanyFilteredMixin, PerformanceTrainingMasterViewSet):
    queryset = KpiLibrary.objects.all()
    serializer_class = KpiLibrarySerializer
    list_serializer_class = KpiLibraryListSerializer
    search_fields = ["code", "name", "unit_of_measure"]

    def get_queryset(self):
        qs = super().get_queryset()
        if goal_category_id := self.request.query_params.get("goal_category_id"):
            qs = qs.filter(goal_category_id=goal_category_id)
        return qs


class KraLibraryViewSet(CompanyFilteredMixin, PerformanceTrainingMasterViewSet):
    queryset = KraLibrary.objects.all()
    serializer_class = KraLibrarySerializer
    list_serializer_class = KraLibraryListSerializer
    search_fields = ["code", "name", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        if goal_category_id := self.request.query_params.get("goal_category_id"):
            qs = qs.filter(goal_category_id=goal_category_id)
        return qs


class CompetencyGroupViewSet(CompanyFilteredMixin, PerformanceTrainingMasterViewSet):
    queryset = CompetencyGroup.objects.all()
    serializer_class = CompetencyGroupSerializer
    list_serializer_class = CompetencyGroupListSerializer
    search_fields = ["code", "name", "description"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]
    ordering = ["sort_order", "name"]


class CompetencyViewSet(CompanyFilteredMixin, PerformanceTrainingMasterViewSet):
    queryset = Competency.objects.all()
    serializer_class = CompetencySerializer
    list_serializer_class = CompetencyListSerializer
    search_fields = ["code", "name", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        for param in ("competency_group_id", "rating_scale_id"):
            if value := self.request.query_params.get(param):
                qs = qs.filter(**{param: value})
        return qs


class TrainingCategoryViewSet(PerformanceTrainingMasterViewSet):
    queryset = TrainingCategory.objects.all()
    serializer_class = TrainingCategorySerializer
    list_serializer_class = TrainingCategoryListSerializer
    search_fields = ["code", "name"]


class TrainingModeViewSet(PerformanceTrainingMasterViewSet):
    queryset = TrainingMode.objects.all()
    serializer_class = TrainingModeSerializer
    list_serializer_class = TrainingModeListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if (value := self.request.query_params.get("requires_venue", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(requires_venue=(value == "true"))
        return qs


class CourseViewSet(CompanyFilteredMixin, PerformanceTrainingMasterViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    list_serializer_class = CourseListSerializer
    search_fields = ["code", "name", "provider"]
    ordering_fields = ["code", "name", "duration_hours", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if training_category_id := self.request.query_params.get("training_category_id"):
            qs = qs.filter(training_category_id=training_category_id)
        if provider := self.request.query_params.get("provider"):
            qs = qs.filter(provider__icontains=provider)
        return qs


class CertificationBodyViewSet(PerformanceTrainingMasterViewSet):
    queryset = CertificationBody.objects.all()
    serializer_class = CertificationBodySerializer
    list_serializer_class = CertificationBodyListSerializer
    search_fields = ["code", "name"]


class AssetCategoryViewSet(PerformanceTrainingMasterViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    list_serializer_class = AssetCategoryListSerializer
    search_fields = ["code", "name"]


class AssetConditionViewSet(PerformanceTrainingMasterViewSet):
    queryset = AssetCondition.objects.all()
    serializer_class = AssetConditionSerializer
    list_serializer_class = AssetConditionListSerializer
    search_fields = ["code", "name"]


class AssetTypeViewSet(PerformanceTrainingMasterViewSet):
    queryset = AssetType.objects.all()
    serializer_class = AssetTypeSerializer
    list_serializer_class = AssetTypeListSerializer
    search_fields = ["code", "name"]

    def get_queryset(self):
        qs = super().get_queryset()
        if asset_category_id := self.request.query_params.get("asset_category_id"):
            qs = qs.filter(asset_category_id=asset_category_id)
        if (value := self.request.query_params.get("requires_serial_no", "").lower()) in (
            "true",
            "false",
        ):
            qs = qs.filter(requires_serial_no=(value == "true"))
        return qs


class VendorViewSet(CompanyFilteredMixin, PerformanceTrainingMasterViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    list_serializer_class = VendorListSerializer
    search_fields = ["code", "name", "gstin", "pan"]

    def get_queryset(self):
        qs = super().get_queryset()
        if vendor_type := self.request.query_params.get("vendor_type"):
            qs = qs.filter(vendor_type=vendor_type)
        return qs
