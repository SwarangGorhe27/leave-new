"""URL routes for passport and visa master APIs."""

from rest_framework.routers import DefaultRouter

from apps.masters.views.passport_visa import (
    PassportCategoryViewSet,
    PassportStatusViewSet,
    VisaStatusViewSet,
    VisaTypeViewSet,
)

router = DefaultRouter()

router.register(
    r"passport-categories",
    PassportCategoryViewSet,
    basename="passport-category",
)
router.register(
    r"passport-statuses",
    PassportStatusViewSet,
    basename="passport-status",
)
router.register(r"visa-types", VisaTypeViewSet, basename="visa-type")
router.register(r"visa-statuses", VisaStatusViewSet, basename="visa-status")

urlpatterns = router.urls
