from rest_framework.routers import DefaultRouter

from apps.masters.views.insurance import (
    CoverTypeViewSet,
    InsuranceCompanyViewSet,
    InsuranceTypeViewSet,
    PolicyTypeViewSet,
    PremiumFrequencyViewSet,
)

router = DefaultRouter()

router.register(r"policy-types", PolicyTypeViewSet, basename="policy-type")
router.register(r"insurance-types", InsuranceTypeViewSet, basename="insurance-type")
router.register(r"cover-types", CoverTypeViewSet, basename="cover-type")
router.register(
    r"premium-frequencies",
    PremiumFrequencyViewSet,
    basename="premium-frequency",
)
router.register(
    r"insurance-companies",
    InsuranceCompanyViewSet,
    basename="insurance-company",
)

urlpatterns = router.urls
