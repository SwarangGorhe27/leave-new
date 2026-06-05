"""
Admin views for employees app.
"""
"""Admin / HR views for employee ESS."""

from .change_request_approval_view import (
    ChangeRequestApproveAdminView,
    ChangeRequestDetailAdminView,
    ChangeRequestListAdminView,
    ChangeRequestRejectAdminView,
)
from .employee_profile_view import (
    EmployeeProfileView,
)
from .profile_detail_section_views import (
    EmployeeAddressDetailsAdminView,
    EmployeeEmploymentDetailsAdminView,
    EmployeeInsuranceDetailsAdminView,
    EmployeeInsurancePolicyAdminView,
    EmployeeLanguageDetailsAdminView,
    EmployeeMedicalDetailsAdminView,
    EmployeePersonalDetailsAdminView,
)
from .profile_section_view import EmployeeProfileSectionAdminView
from .fines_damages_view import (
    FineListCreateView,
    FineDetailView,
    FineStatusView,
    FineStatsView,
    FineExportView,
    DamageListCreateView,
    DamageDetailView,
    DamageStatsView,
    DamageExportView,
    EmployeeDropdownView,
    EmployeeSearchView,
)
from .employee_filter_view import (
    EmployeeFilterListCreateView,
    EmployeeFilterCustomCreateView,
    EmployeeFilterDetailView,
    EmployeeFilterExecuteView,
    EmployeeFilterPreviewView,
    EmployeeFilterShareView,
    EmployeeFilterFavouriteView,
    EmployeeFilterExportView,
    EmployeeFilterAuditLogView,
    EmployeeFilterValidateView,
    EmployeeFilterBulkDeleteView,
    EmployeeFilterSearchView,
    FilterMetaCategoryTypesView,
    FilterMetaEmployeeTypesView,
    FilterMetaEmployeeStatusesView,
    FilterMetaFieldsView,
    FilterMetaConditionsView,
    DepartmentDropdownView,
    DesignationDropdownView,
    GradeDropdownView,
    LocationDropdownView,
    AttendanceSchemeDropdownView,
)

# Swagger / legacy aliases
AdminChangeRequestListView = ChangeRequestListAdminView
AdminChangeRequestDetailView = ChangeRequestDetailAdminView
AdminApproveChangeRequestView = ChangeRequestApproveAdminView
AdminRejectChangeRequestView = ChangeRequestRejectAdminView

__all__ = [
    "AdminApproveChangeRequestView",
    "AdminChangeRequestDetailView",
    "AdminChangeRequestListView",
    "AdminRejectChangeRequestView",
    "ChangeRequestApproveAdminView",
    "ChangeRequestDetailAdminView",
    "ChangeRequestListAdminView",
    "ChangeRequestRejectAdminView",
    "EmployeeAddressDetailsAdminView",
    "EmployeeEmploymentDetailsAdminView",
    "EmployeeInsuranceDetailsAdminView",
    "EmployeeInsurancePolicyAdminView",
    "EmployeeLanguageDetailsAdminView",
    "EmployeeMedicalDetailsAdminView",
    "EmployeePersonalDetailsAdminView",
    "EmployeeProfileSectionAdminView",
    "EmployeeProfileView",
    # ── Fines & Damages ───────────────────────────────────────────────────
    "FineListCreateView",
    "FineDetailView",
    "FineStatusView",
    "FineStatsView",
    "FineExportView",
    "DamageListCreateView",
    "DamageDetailView",
    "DamageStatsView",
    "DamageExportView",
    "EmployeeDropdownView",
    "EmployeeSearchView",
]
