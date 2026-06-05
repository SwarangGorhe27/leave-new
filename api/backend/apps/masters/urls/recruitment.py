"""URL routes for recruitment master APIs."""

from rest_framework.routers import DefaultRouter

from apps.masters.views.recruitment import (
    CandidateSourceViewSet,
    InterviewRoundViewSet,
    JobFunctionViewSet,
    JobLevelViewSet,
    OfferStatusViewSet,
    PipelineStageViewSet,
    RejectionReasonViewSet,
)

router = DefaultRouter()

router.register(r"job-functions", JobFunctionViewSet, basename="job-function")
router.register(r"job-levels", JobLevelViewSet, basename="job-level")
router.register(r"interview-rounds", InterviewRoundViewSet, basename="interview-round")
router.register(
    r"candidate-sources",
    CandidateSourceViewSet,
    basename="candidate-source",
)
router.register(r"offer-statuses", OfferStatusViewSet, basename="offer-status")
router.register(
    r"rejection-reasons",
    RejectionReasonViewSet,
    basename="rejection-reason",
)
router.register(r"pipeline-stages", PipelineStageViewSet, basename="pipeline-stage")

urlpatterns = router.urls
