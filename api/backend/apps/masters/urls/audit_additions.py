"""URL routes for audit-addition master APIs."""

from rest_framework.routers import DefaultRouter

from apps.masters.views.audit_additions import (
    AuthorizedSignatoryViewSet,
    BulletinCategoryViewSet,
    ClearanceItemTypeViewSet,
    ContractStatusViewSet,
    CounterPartyViewSet,
    EmployeeFilterViewSet,
    FormCategoryViewSet,
    ImportTypeViewSet,
    LetterApprovalTypeViewSet,
    PaymentTypeViewSet,
    PolicyCategoryViewSet,
    PositionChangeReasonViewSet,
    ReportingManagerViewSet,
    ResidentialStatusViewSet,
    SeparationModeViewSet,
    VerificationStatusViewSet,
)

router = DefaultRouter()

router.register(r"separation-modes", SeparationModeViewSet, basename="separation-mode")
router.register(r"contract-statuses", ContractStatusViewSet, basename="contract-status")
router.register(
    r"verification-statuses",
    VerificationStatusViewSet,
    basename="verification-status",
)
router.register(
    r"residential-statuses",
    ResidentialStatusViewSet,
    basename="residential-status",
)
router.register(r"payment-types", PaymentTypeViewSet, basename="payment-type")
router.register(r"employee-filters", EmployeeFilterViewSet, basename="employee-filter")
router.register(
    r"bulletin-categories",
    BulletinCategoryViewSet,
    basename="bulletin-category",
)
router.register(r"policy-categories", PolicyCategoryViewSet, basename="policy-category")
router.register(r"form-categories", FormCategoryViewSet, basename="form-category")
router.register(r"import-types", ImportTypeViewSet, basename="import-type")
router.register(
    r"letter-approval-types",
    LetterApprovalTypeViewSet,
    basename="letter-approval-type",
)
router.register(
    r"clearance-item-types",
    ClearanceItemTypeViewSet,
    basename="clearance-item-type",
)
router.register(
    r"position-change-reasons",
    PositionChangeReasonViewSet,
    basename="position-change-reason",
)
router.register(r"counter-parties", CounterPartyViewSet, basename="counter-party")
router.register(
    r"authorized-signatories",
    AuthorizedSignatoryViewSet,
    basename="authorized-signatory",
)
router.register(
    r"reporting-managers",
    ReportingManagerViewSet,
    basename="reporting-manager",
)

urlpatterns = router.urls
