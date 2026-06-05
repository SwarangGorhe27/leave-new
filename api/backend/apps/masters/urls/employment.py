"""URL routes for employment master APIs."""

from rest_framework.routers import DefaultRouter

from apps.masters.views.employment import (
    EmployeeCategoryViewSet,
    EmployeeStatusViewSet,
    EmployeeTypeViewSet,
    PayrollGroupViewSet,
    PayrollModeViewSet,
    PayrollStatusViewSet,
    RelevantExperienceRangeViewSet,
    SourceOfHireTypeViewSet,
    SourceOfHireViewSet,
    TransportTypeViewSet,
    WorkExperienceRangeViewSet,
)

router = DefaultRouter()

router.register(r"employee-types", EmployeeTypeViewSet, basename="employment-employee-type")
router.register(
    r"employee-categories",
    EmployeeCategoryViewSet,
    basename="employment-employee-category",
)
router.register(r"sources-of-hire", SourceOfHireViewSet, basename="employment-source-of-hire")
router.register(
    r"source-of-hire-types",
    SourceOfHireTypeViewSet,
    basename="employment-source-of-hire-type",
)
router.register(r"payroll-statuses", PayrollStatusViewSet, basename="employment-payroll-status")
router.register(r"payroll-modes", PayrollModeViewSet, basename="employment-payroll-mode")
router.register(r"payroll-groups", PayrollGroupViewSet, basename="employment-payroll-group")
router.register(r"transport-types", TransportTypeViewSet, basename="employment-transport-type")
router.register(r"employee-statuses", EmployeeStatusViewSet, basename="employment-employee-status")
router.register(
    r"work-experience-ranges",
    WorkExperienceRangeViewSet,
    basename="employment-work-experience-range",
)
router.register(
    r"relevant-experience-ranges",
    RelevantExperienceRangeViewSet,
    basename="employment-relevant-experience-range",
)

urlpatterns = router.urls
