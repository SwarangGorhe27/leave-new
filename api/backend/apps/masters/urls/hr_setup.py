from rest_framework.routers import DefaultRouter

from apps.masters.views.hr_setup import (
    BandViewSet,
    BranchViewSet,
    BusinessUnitViewSet,
    CostCenterViewSet,
    HolidayCalendarViewSet,
    HolidayGroupViewSet,
    HolidayViewSet,
    ProfitCenterViewSet,
    ShiftTypeViewSet,
    ShiftViewSet,
    WorkWeekPolicyViewSet,
)

router = DefaultRouter()

router.register(r"branches", BranchViewSet, basename="branch")
router.register(r"business-units", BusinessUnitViewSet, basename="business-unit")
router.register(r"cost-centers", CostCenterViewSet, basename="cost-center")
router.register(r"profit-centers", ProfitCenterViewSet, basename="profit-center")
router.register(r"bands", BandViewSet, basename="band")
router.register(r"shift-types", ShiftTypeViewSet, basename="shift-type")
router.register(r"shifts", ShiftViewSet, basename="shift")
router.register(
    r"work-week-policies",
    WorkWeekPolicyViewSet,
    basename="work-week-policy",
)
router.register(
    r"holiday-calendars",
    HolidayCalendarViewSet,
    basename="holiday-calendar",
)
router.register(r"holidays", HolidayViewSet, basename="holiday")
router.register(r"holiday-groups", HolidayGroupViewSet, basename="holiday-group")

urlpatterns = router.urls
