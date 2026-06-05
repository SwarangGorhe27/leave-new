

from rest_framework.routers import DefaultRouter

from apps.masters.views.education import (
    BoardViewSet,
    EducationLevelViewSet,
    EducationStatusViewSet,
    InstitutionViewSet,
    PassingYearViewSet,
    QualificationViewSet,
    SpecializationViewSet,
    StudyModeViewSet,
    UniversityViewSet,
)

router = DefaultRouter()

router.register(r"levels",          EducationLevelViewSet,  basename="education-level")
router.register(r"statuses",        EducationStatusViewSet, basename="education-status")
router.register(r"specializations", SpecializationViewSet,  basename="specialization")
router.register(r"boards",          BoardViewSet,           basename="board")
router.register(r"qualifications",  QualificationViewSet,   basename="qualification")
router.register(r"study-modes",     StudyModeViewSet,       basename="study-mode")
router.register(r"institutions",    InstitutionViewSet,     basename="institution")
router.register(r"universities",    UniversityViewSet,      basename="university")
router.register(r"passing-years",   PassingYearViewSet,     basename="passing-year")

urlpatterns = router.urls
