from rest_framework.routers import DefaultRouter

from apps.masters.views.organization import (
    AccountTypeViewSet,
    BankStatusViewSet,
    BankViewSet,
    BatchViewSet,
    CabViewSet,
    CompanyViewSet,
    DepartmentDivisionViewSet,
    DepartmentViewSet,
    DesignationViewSet,
    ExtensionViewSet,
    GradeViewSet,
    TeamViewSet,
)

router = DefaultRouter()

router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"designations", DesignationViewSet, basename="designation")
router.register(r"grades", GradeViewSet, basename="grade")
router.register(r"banks", BankViewSet, basename="bank")
router.register(r"bank-statuses", BankStatusViewSet, basename="bank-status")
router.register(r"account-types", AccountTypeViewSet, basename="account-type")
router.register(
    r"department-divisions",
    DepartmentDivisionViewSet,
    basename="department-division",
)
router.register(r"extensions", ExtensionViewSet, basename="extension")
router.register(r"batches", BatchViewSet, basename="batch")
router.register(r"cabs", CabViewSet, basename="cab")

urlpatterns = router.urls
