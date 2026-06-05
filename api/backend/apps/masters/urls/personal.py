

from rest_framework.routers import DefaultRouter

from apps.masters.views.personal import (
    BloodGroupViewSet,
    CasteCategoryViewSet,
    CasteViewSet,
    GenderViewSet,
    MaritalStatusViewSet,
    MotherTongueViewSet,
    NationalityViewSet,
    ReligionViewSet,
    SalutationViewSet,
)

router = DefaultRouter()

# ── Personal master routes ───────────────────────────────────────────────────
router.register(r"genders",        GenderViewSet,       basename="master-gender")
router.register(r"marital-statuses", MaritalStatusViewSet, basename="master-marital-status")
router.register(r"blood-groups",   BloodGroupViewSet,   basename="master-blood-group")

# ── Mutable tables ────────────────────────────────────────────────────────────
router.register(r"salutations",     SalutationViewSet,    basename="master-salutation")
router.register(r"religions",       ReligionViewSet,      basename="master-religion")
router.register(r"castes",          CasteViewSet,         basename="master-caste")
router.register(r"caste-categories", CasteCategoryViewSet, basename="master-caste-category")
router.register(r"mother-tongues",  MotherTongueViewSet,  basename="master-mother-tongue")
router.register(r"nationalities",   NationalityViewSet,   basename="master-nationality")

urlpatterns = router.urls
