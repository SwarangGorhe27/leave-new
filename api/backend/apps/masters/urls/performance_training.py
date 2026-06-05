from rest_framework.routers import DefaultRouter

from apps.masters.views.performance_training import (
    AppraisalCycleViewSet,
    AssetCategoryViewSet,
    AssetConditionViewSet,
    AssetTypeViewSet,
    CertificationBodyViewSet,
    CompetencyGroupViewSet,
    CompetencyViewSet,
    CourseViewSet,
    GoalCategoryViewSet,
    KpiLibraryViewSet,
    KraLibraryViewSet,
    RatingScaleViewSet,
    TrainingCategoryViewSet,
    TrainingModeViewSet,
    VendorViewSet,
)

router = DefaultRouter()

router.register(r"appraisal-cycles", AppraisalCycleViewSet, basename="appraisal-cycle")
router.register(r"rating-scales", RatingScaleViewSet, basename="rating-scale")
router.register(r"goal-categories", GoalCategoryViewSet, basename="goal-category")
router.register(r"kpi-library", KpiLibraryViewSet, basename="kpi-library")
router.register(r"kra-library", KraLibraryViewSet, basename="kra-library")
router.register(r"competency-groups", CompetencyGroupViewSet, basename="competency-group")
router.register(r"competencies", CompetencyViewSet, basename="competency")
router.register(r"training-categories", TrainingCategoryViewSet, basename="training-category")
router.register(r"training-modes", TrainingModeViewSet, basename="training-mode")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"certification-bodies", CertificationBodyViewSet, basename="certification-body")
router.register(r"asset-categories", AssetCategoryViewSet, basename="asset-category")
router.register(r"asset-conditions", AssetConditionViewSet, basename="asset-condition")
router.register(r"asset-types", AssetTypeViewSet, basename="asset-type")
router.register(r"vendors", VendorViewSet, basename="vendor")

urlpatterns = router.urls
