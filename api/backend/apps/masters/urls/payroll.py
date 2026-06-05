from rest_framework.routers import DefaultRouter

from apps.masters.views.payroll import (
    ArrearTypeViewSet,
    EsiSchemeViewSet,
    LabourRegisterTypeViewSet,
    LoanTypeViewSet,
    LwfSlabViewSet,
    PayComponentGroupViewSet,
    PayComponentViewSet,
    PayrollCycleViewSet,
    PfSchemeViewSet,
    PtStateSlabViewSet,
    ReimbursementTypeViewSet,
    SalaryStructureComponentViewSet,
    SalaryStructureViewSet,
    StatutoryComponentViewSet,
    TaxRegimeViewSet,
    TdsSectionViewSet,
)

router = DefaultRouter()

router.register(r"pay-component-groups", PayComponentGroupViewSet, basename="pay-component-group")
router.register(r"pay-components", PayComponentViewSet, basename="pay-component")
router.register(r"salary-structures", SalaryStructureViewSet, basename="salary-structure")
router.register(
    r"salary-structure-components",
    SalaryStructureComponentViewSet,
    basename="salary-structure-component",
)
router.register(r"reimbursement-types", ReimbursementTypeViewSet, basename="reimbursement-type")
router.register(r"loan-types", LoanTypeViewSet, basename="loan-type")
router.register(r"payroll-cycles", PayrollCycleViewSet, basename="payroll-cycle")
router.register(r"tax-regimes", TaxRegimeViewSet, basename="tax-regime")
router.register(r"tds-sections", TdsSectionViewSet, basename="tds-section")
router.register(r"arrear-types", ArrearTypeViewSet, basename="arrear-type")
router.register(r"statutory-components", StatutoryComponentViewSet, basename="statutory-component")
router.register(r"pf-schemes", PfSchemeViewSet, basename="pf-scheme")
router.register(r"esi-schemes", EsiSchemeViewSet, basename="esi-scheme")
router.register(r"pt-state-slabs", PtStateSlabViewSet, basename="pt-state-slab")
router.register(r"lwf-slabs", LwfSlabViewSet, basename="lwf-slab")
router.register(r"labour-register-types", LabourRegisterTypeViewSet, basename="labour-register-type")

urlpatterns = router.urls
