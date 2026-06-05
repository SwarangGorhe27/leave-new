"""ViewSets for recruitment master APIs."""

from apps.employees.models.masters.recruitment import (
    CandidateSource,
    InterviewRound,
    JobFunction,
    JobLevel,
    OfferStatus,
    PipelineStage,
    RejectionReason,
)
from apps.masters.serializers.recruitment import (
    CandidateSourceListSerializer,
    CandidateSourceSerializer,
    InterviewRoundListSerializer,
    InterviewRoundSerializer,
    JobFunctionListSerializer,
    JobFunctionSerializer,
    JobLevelListSerializer,
    JobLevelSerializer,
    OfferStatusListSerializer,
    OfferStatusSerializer,
    PipelineStageListSerializer,
    PipelineStageSerializer,
    RejectionReasonListSerializer,
    RejectionReasonSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


def _bool_param(request, name):
    value = request.query_params.get(name, "").lower()
    if value in ("true", "false"):
        return value == "true"
    return None


def _actor_employee_id(request):
    user = getattr(request, "user", None)
    employee = getattr(user, "employee_profile", None)
    return getattr(employee, "id", None)


class RecruitmentMasterViewSet(ActiveMasterViewSet):
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    search_lookup_fields = ("code", "name")
    display_field = "name"

    def perform_create(self, serializer):
        actor_id = _actor_employee_id(self.request)
        save_kwargs = {}
        if actor_id:
            save_kwargs["created_by"] = actor_id
            save_kwargs["updated_by"] = actor_id
        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        actor_id = _actor_employee_id(self.request)
        if actor_id:
            serializer.save(updated_by=actor_id)
            return
        serializer.save()


class CompanyFilteredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        return qs


class JobFunctionViewSet(RecruitmentMasterViewSet):
    queryset = JobFunction.objects.all()
    serializer_class = JobFunctionSerializer
    list_serializer_class = JobFunctionListSerializer


class JobLevelViewSet(RecruitmentMasterViewSet):
    queryset = JobLevel.objects.all()
    serializer_class = JobLevelSerializer
    list_serializer_class = JobLevelListSerializer
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if sort_order := self.request.query_params.get("sort_order"):
            qs = qs.filter(sort_order=sort_order)
        return qs


class InterviewRoundViewSet(RecruitmentMasterViewSet):
    queryset = InterviewRound.objects.all()
    serializer_class = InterviewRoundSerializer
    list_serializer_class = InterviewRoundListSerializer
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if sort_order := self.request.query_params.get("sort_order"):
            qs = qs.filter(sort_order=sort_order)
        return qs


class CandidateSourceViewSet(RecruitmentMasterViewSet):
    queryset = CandidateSource.objects.all()
    serializer_class = CandidateSourceSerializer
    list_serializer_class = CandidateSourceListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if source_category := self.request.query_params.get("source_category", "").upper():
            qs = qs.filter(source_category=source_category)
        return qs


class OfferStatusViewSet(RecruitmentMasterViewSet):
    queryset = OfferStatus.objects.all()
    serializer_class = OfferStatusSerializer
    list_serializer_class = OfferStatusListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        is_terminal = _bool_param(self.request, "is_terminal")
        if is_terminal is not None:
            qs = qs.filter(is_terminal=is_terminal)
        return qs


class RejectionReasonViewSet(CompanyFilteredMixin, RecruitmentMasterViewSet):
    queryset = RejectionReason.objects.all()
    serializer_class = RejectionReasonSerializer
    list_serializer_class = RejectionReasonListSerializer
    search_fields = ["code", "name", "rejection_stage"]

    def get_queryset(self):
        qs = super().get_queryset()
        if rejection_stage := self.request.query_params.get("rejection_stage"):
            qs = qs.filter(rejection_stage__iexact=rejection_stage)
        return qs


class PipelineStageViewSet(CompanyFilteredMixin, RecruitmentMasterViewSet):
    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer
    list_serializer_class = PipelineStageListSerializer
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if sort_order := self.request.query_params.get("sort_order"):
            qs = qs.filter(sort_order=sort_order)
        is_terminal = _bool_param(self.request, "is_terminal")
        if is_terminal is not None:
            qs = qs.filter(is_terminal=is_terminal)
        return qs
