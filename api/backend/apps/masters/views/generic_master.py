"""
Generic Master ViewSet Router

This module provides a unified endpoint for accessing all master data dynamically.
Maps master names (e.g., 'Gender', 'Department') to their actual viewsets.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import Http404

# ──────────────────────────────────────────────────────────────────────────────
# MASTER VIEWSET REGISTRY
# ──────────────────────────────────────────────────────────────────────────────

# Import all viewsets
from apps.employees.models.employee import Employee
from apps.masters.views.personal import (
    GenderViewSet,
    MaritalStatusViewSet,
    BloodGroupViewSet,
    SalutationViewSet,
    ReligionViewSet,
    CasteViewSet,
    CasteCategoryViewSet,
    MotherTongueViewSet,
    NationalityViewSet,
)

from apps.masters.views.employment import (
    EmployeeTypeViewSet,
    EmployeeCategoryViewSet,
    SourceOfHireViewSet,
    SourceOfHireTypeViewSet,
    PayrollStatusViewSet,
    PayrollModeViewSet,
    PayrollGroupViewSet,
    TransportTypeViewSet,
    EmployeeStatusViewSet,
    WorkExperienceRangeViewSet,
    RelevantExperienceRangeViewSet,
)

from apps.masters.views.organization import (
    CompanyViewSet,
    DepartmentViewSet,
    TeamViewSet,
    DesignationViewSet,
    GradeViewSet,
    BankViewSet,
    BankStatusViewSet,
    AccountTypeViewSet,
    DepartmentDivisionViewSet,
    ExtensionViewSet,
    BatchViewSet,
    CabViewSet,
)

from apps.masters.views.hr_setup import (
    BranchViewSet,
    BusinessUnitViewSet,
    CostCenterViewSet,
    ProfitCenterViewSet,
    BandViewSet,
    ShiftTypeViewSet,
    ShiftViewSet,
    WorkWeekPolicyViewSet,
    HolidayCalendarViewSet,
    HolidayViewSet,
    HolidayGroupViewSet,
)

from apps.masters.views.education import (
    QualificationViewSet,
    SpecializationViewSet,
    EducationLevelViewSet,
    EducationStatusViewSet,
    UniversityViewSet,
    BoardViewSet,
    InstitutionViewSet,
    StudyModeViewSet,
    PassingYearViewSet,
)

from apps.masters.views.payroll import (
    PayComponentViewSet,
    SalaryStructureViewSet,
    PayComponentGroupViewSet,
    SalaryStructureComponentViewSet,
    ReimbursementTypeViewSet,
    LoanTypeViewSet,
    PayrollCycleViewSet,
    TaxRegimeViewSet,
    TdsSectionViewSet,
    ArrearTypeViewSet,
    StatutoryComponentViewSet,
    PfSchemeViewSet,
    EsiSchemeViewSet,
    PtStateSlabViewSet,
    LwfSlabViewSet,
    LabourRegisterTypeViewSet,
)

from apps.masters.views.insurance import (
    PolicyTypeViewSet,
    InsuranceTypeViewSet,
    CoverTypeViewSet,
    PremiumFrequencyViewSet,
    InsuranceCompanyViewSet,
)

from apps.masters.views.performance_training import (
    AppraisalCycleViewSet,
    RatingScaleViewSet,
    GoalCategoryViewSet,
    KpiLibraryViewSet,
    KraLibraryViewSet,
    CompetencyGroupViewSet,
    CompetencyViewSet,
    TrainingCategoryViewSet,
    TrainingModeViewSet,
    CourseViewSet,
    CertificationBodyViewSet,
    AssetCategoryViewSet,
    AssetConditionViewSet,
    AssetTypeViewSet,
    VendorViewSet,
)

from apps.masters.views.location_and_misc import (
    CountryViewSet,
    StateViewSet,
    CityViewSet,
    OfficeLocationViewSet,
    LanguageViewSet,
    ProficiencyLevelViewSet,
    RelationViewSet,
    OccupationViewSet,
    ProfessionViewSet,
)

from apps.masters.views.audit_additions import (
    VerificationStatusViewSet,
)

from apps.masters.views.attendance import (
    AttendanceTrackingModeViewSet,
)

from apps.masters.views.passport_visa import (
    PassportCategoryViewSet,
    PassportStatusViewSet,
)

from apps.masters.views.leave import (
    LeavePolicyRuleViewSet,
    LeavePolicyViewSet,
    LeaveTypeViewSet,
)
from apps.masters.views.workflow_security import (
    ApprovalActionViewSet,
    AuditEventTypeViewSet,
    EscalationTypeViewSet,
    NotificationChannelViewSet,
    NotificationTemplateViewSet,
    NotificationTriggerViewSet,
    PasswordPolicyViewSet,
    SessionPolicyViewSet,
    WorkflowTypeViewSet,
)

from apps.masters.views.weekly_off_days import (
    WeeklyOffDaysViewSet,
)


# ──────────────────────────────────────────────────────────────────────────────
# NON-MASTER DROPDOWN ADAPTERS
# ──────────────────────────────────────────────────────────────────────────────

class EmployeeDropdownViewSet(viewsets.ViewSet):
    """Read-only adapter for employee dropdowns used by manager/referrer fields."""

    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = Employee.objects.all().only(
            "id",
            "employee_code",
            "first_name",
            "middle_name",
            "last_name",
            "is_active",
        )

        is_active = request.query_params.get("is_active")
        if is_active == "true":
            qs = qs.filter(is_active=True)
        elif is_active == "false":
            qs = qs.filter(is_active=False)

        search = (request.query_params.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(employee_code__icontains=search)
                | Q(first_name__icontains=search)
                | Q(middle_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        results = [
            {
                "id": employee.id,
                "code": employee.employee_code,
                "label": f"{employee.full_name} ({employee.employee_code})",
                "name": employee.full_name,
                "is_active": employee.is_active,
            }
            for employee in qs.order_by("first_name", "last_name", "employee_code")[:100]
        ]

        return Response({
            "count": len(results),
            "next": None,
            "previous": None,
            "results": results,
        })


# ──────────────────────────────────────────────────────────────────────────────
# MASTER NAME TO VIEWSET MAPPING
# ──────────────────────────────────────────────────────────────────────────────

MASTER_REGISTRY = {
    # Personal Masters
    "Gender": GenderViewSet,
    "MaritalStatus": MaritalStatusViewSet,
    "BloodGroup": BloodGroupViewSet,
    "Salutation": SalutationViewSet,
    "Religion": ReligionViewSet,
    "Caste": CasteViewSet,
    "CasteCategory": CasteCategoryViewSet,
    "MotherTongue": MotherTongueViewSet,
    "Nationality": NationalityViewSet,
    
    # Employment Masters
    "EmployeeType": EmployeeTypeViewSet,
    "EmployeeCategory": EmployeeCategoryViewSet,
    "SourceOfHire": SourceOfHireViewSet,
    "SourceOfHireType": SourceOfHireTypeViewSet,
    "PayrollStatus": PayrollStatusViewSet,
    "PayrollMode": PayrollModeViewSet,
    "PayrollGroup": PayrollGroupViewSet,
    "TransportType": TransportTypeViewSet,
    "EmployeeStatus": EmployeeStatusViewSet,
    "WorkExperienceRange": WorkExperienceRangeViewSet,
    "RelevantExperienceRange": RelevantExperienceRangeViewSet,
    
    # Organization Masters
    "Company": CompanyViewSet,
    "Department": DepartmentViewSet,
    "Team": TeamViewSet,
    "Designation": DesignationViewSet,
    "Grade": GradeViewSet,
    "Bank": BankViewSet,
    "BankStatus": BankStatusViewSet,
    "AccountType": AccountTypeViewSet,
    "DepartmentDivision": DepartmentDivisionViewSet,
    "Extension": ExtensionViewSet,
    "Batch": BatchViewSet,
    "Cab": CabViewSet,
    
    # HR Setup Masters
    "Branch": BranchViewSet,
    "BusinessUnit": BusinessUnitViewSet,
    "CostCenter": CostCenterViewSet,
    "ProfitCenter": ProfitCenterViewSet,
    "Band": BandViewSet,
    "ShiftType": ShiftTypeViewSet,
    "ShiftGroup": ShiftViewSet,
    "Shift": ShiftViewSet,  # Alias
    "WorkWeekPolicy": WorkWeekPolicyViewSet,
    "HolidayCalendar": HolidayCalendarViewSet,
    "Holiday": HolidayViewSet,
    "HolidayGroup": HolidayGroupViewSet,
    
    # Education Masters
    "Qualification": QualificationViewSet,
    "Specialization": SpecializationViewSet,
    "EducationLevel": EducationLevelViewSet,
    "EducationStatus": EducationStatusViewSet,
    "University": UniversityViewSet,
    "Board": BoardViewSet,
    "Institution": InstitutionViewSet,
    "StudyMode": StudyModeViewSet,
    "PassingYear": PassingYearViewSet,
    
    # Payroll Masters
    "PayComponent": PayComponentViewSet,
    "EarningComponent": PayComponentViewSet,  # Alias
    "SalaryStructure": SalaryStructureViewSet,
    "PayComponentGroup": PayComponentGroupViewSet,
    "SalaryStructureComponent": SalaryStructureComponentViewSet,
    "ReimbursementType": ReimbursementTypeViewSet,
    "LoanType": LoanTypeViewSet,
    "PayrollCycle": PayrollCycleViewSet,
    "TaxRegime": TaxRegimeViewSet,
    "TdsSection": TdsSectionViewSet,
    "ArrearType": ArrearTypeViewSet,
    "StatutoryComponent": StatutoryComponentViewSet,
    "DeductionComponent": StatutoryComponentViewSet,  # Alias
    "PfScheme": PfSchemeViewSet,
    "EsiScheme": EsiSchemeViewSet,
    "PtStateSlab": PtStateSlabViewSet,
    "LwfSlab": LwfSlabViewSet,
    "LabourRegisterType": LabourRegisterTypeViewSet,
    
    # Insurance Masters
    "PolicyType": PolicyTypeViewSet,
    "InsuranceType": InsuranceTypeViewSet,
    "CoverType": CoverTypeViewSet,
    "PremiumFrequency": PremiumFrequencyViewSet,
    "InsuranceCompany": InsuranceCompanyViewSet,
    "InsuranceProvider": InsuranceCompanyViewSet,  # Alias
    
    # Performance & Training Masters
    "AppraisalCycle": AppraisalCycleViewSet,
    "RatingScale": RatingScaleViewSet,
    "GoalCategory": GoalCategoryViewSet,
    "KpiLibrary": KpiLibraryViewSet,
    "KraLibrary": KraLibraryViewSet,
    "CompetencyGroup": CompetencyGroupViewSet,
    "Competency": CompetencyViewSet,
    "TrainingCategory": TrainingCategoryViewSet,
    "TrainingMode": TrainingModeViewSet,
    "Course": CourseViewSet,
    "CertificationBody": CertificationBodyViewSet,
    "AssetCategory": AssetCategoryViewSet,
    "AssetCondition": AssetConditionViewSet,
    "AssetType": AssetTypeViewSet,
    "Vendor": VendorViewSet,
    "TrainingType": TrainingCategoryViewSet,  # Alias
    
    # Attendance Masters
    "AttendanceTrackingMode": AttendanceTrackingModeViewSet,
    
    # Leave Masters
    "LeaveType": LeaveTypeViewSet,
    "LeavePolicy": LeavePolicyViewSet,
    "LeavePolicyRule": LeavePolicyRuleViewSet,
    "WeeklyOffDays": WeeklyOffDaysViewSet,

    # Workflow & Security Masters
    "WorkflowType": WorkflowTypeViewSet,
    "ApprovalAction": ApprovalActionViewSet,
    "EscalationType": EscalationTypeViewSet,
    "AuditEventType": AuditEventTypeViewSet,
    "PasswordPolicy": PasswordPolicyViewSet,
    "SessionPolicy": SessionPolicyViewSet,
    "NotificationChannel": NotificationChannelViewSet,
    "NotificationTemplate": NotificationTemplateViewSet,
    "NotificationTrigger": NotificationTriggerViewSet,
    
    # Passport & Visa Masters
    "PassportCategory": PassportCategoryViewSet,
    "PassportStatus": PassportStatusViewSet,

    # Location Masters
    "Country": CountryViewSet,
    "State": StateViewSet,
    "City": CityViewSet,
    "OfficeLocation": OfficeLocationViewSet,
    
    # Miscellaneous Masters
    "Language": LanguageViewSet,
    "ProficiencyLevel": ProficiencyLevelViewSet,
    "Relation": RelationViewSet,
    "Occupation": OccupationViewSet,
    "Profession": ProfessionViewSet,
    "VerificationStatus": VerificationStatusViewSet,
    "EmployeeNumberSeries": CompanyViewSet,  # Alias for employee series/company
    "Employee": EmployeeDropdownViewSet,
}


# ──────────────────────────────────────────────────────────────────────────────
# GENERIC MASTER ROUTER CLASS
# ──────────────────────────────────────────────────────────────────────────────

class GenericMasterViewSet(viewsets.ViewSet):
    """
    A dynamic ViewSet that routes requests to appropriate master viewsets.
    
    Usage:
        GET /api/masters/{master_name}/ - List all records for a master
        POST /api/masters/{master_name}/ - Create a new record
        GET /api/masters/{master_name}/{id}/ - Retrieve a specific record
        PUT/PATCH /api/masters/{master_name}/{id}/ - Update a record
        DELETE /api/masters/{master_name}/{id}/ - Delete a record
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_viewset_class(self, master_name: str):
        """Get the ViewSet class for a given master name."""
        viewset_class = MASTER_REGISTRY.get(master_name)
        if not viewset_class:
            raise Http404(
                f"Master '{master_name}' not found. "
                f"Available masters: {', '.join(sorted(MASTER_REGISTRY.keys()))}"
            )
        return viewset_class
    
    def get_viewset_instance(self, master_name: str):
        """Create and return a configured ViewSet instance."""
        viewset_class = self.get_viewset_class(master_name)
        instance = viewset_class()
        instance.request = self.request
        instance.format_kwarg = self.format_kwarg
        return instance
    
    def list(self, request, master_name=None):
        """List all records for a master."""
        if not master_name:
            return Response(
                {"error": "Master name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            viewset = self.get_viewset_instance(master_name)
            viewset.action = "list"
            return viewset.list(request)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, master_name=None):
        """Create a new record for a master."""
        if not master_name:
            return Response(
                {"error": "Master name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            viewset = self.get_viewset_instance(master_name)
            viewset.action = "create"
            return viewset.create(request)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, master_name=None, pk=None):
        """Retrieve a specific record."""
        if not master_name:
            return Response(
                {"error": "Master name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            viewset = self.get_viewset_instance(master_name)
            viewset.kwargs = {"pk": pk}
            viewset.action = "retrieve"
            return viewset.retrieve(request, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, master_name=None, pk=None):
        """Update a record (full update)."""
        if not master_name:
            return Response(
                {"error": "Master name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            viewset = self.get_viewset_instance(master_name)
            viewset.kwargs = {"pk": pk}
            viewset.action = "update"
            return viewset.update(request, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, master_name=None, pk=None):
        """Partial update a record."""
        if not master_name:
            return Response(
                {"error": "Master name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            viewset = self.get_viewset_instance(master_name)
            viewset.kwargs = {"pk": pk}
            viewset.action = "partial_update"
            return viewset.partial_update(request, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, master_name=None, pk=None):
        """Delete a record."""
        if not master_name:
            return Response(
                {"error": "Master name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            viewset = self.get_viewset_instance(master_name)
            viewset.kwargs = {"pk": pk}
            viewset.action = "destroy"
            return viewset.destroy(request, pk=pk)
        except Http404 as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=["get"])
    def list_all_masters(self, request):
        """List all available masters."""
        return Response({
            "masters": sorted(MASTER_REGISTRY.keys()),
            "count": len(MASTER_REGISTRY)
        })
