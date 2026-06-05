"""
URL routes for Employee Filter admin APIs.

Mounted at:
  /api/admin/setup/   → urlpatterns  (filter CRUD + meta + actions)
  /api/admin/         → master_urlpatterns  (departments, designations, etc.)
"""

from django.urls import path

from apps.employees.views.admin.employee_filter_view import (
    AttendanceSchemeDropdownView,
    DepartmentDropdownView,
    DesignationDropdownView,
    EmployeeFilterAuditLogView,
    EmployeeFilterBulkDeleteView,
    EmployeeFilterCustomCreateView,
    EmployeeFilterDetailView,
    EmployeeFilterExecuteView,
    EmployeeFilterExportView,
    EmployeeFilterFavouriteView,
    EmployeeFilterListCreateView,
    EmployeeFilterPreviewView,
    EmployeeFilterSearchView,
    EmployeeFilterShareView,
    EmployeeFilterValidateView,
    FilterMetaCategoryTypesView,
    FilterMetaConditionsView,
    FilterMetaEmployeeStatusesView,
    FilterMetaEmployeeTypesView,
    FilterMetaFieldsView,
    GradeDropdownView,
    LocationDropdownView,
)

# ── /api/admin/setup/employee-filters/ ───────────────────────────────────
urlpatterns = [
    # ── Utility (must come BEFORE <uuid:filter_id> to avoid conflicts) ──
    path("employee-filters/custom/", EmployeeFilterCustomCreateView.as_view(), name="ef-custom-create"),
    path("employee-filters/preview/", EmployeeFilterPreviewView.as_view(), name="ef-preview"),
    path("employee-filters/validate/", EmployeeFilterValidateView.as_view(), name="ef-validate"),
    path("employee-filters/bulk-delete/", EmployeeFilterBulkDeleteView.as_view(), name="ef-bulk-delete"),
    path("employee-filters/search/", EmployeeFilterSearchView.as_view(), name="ef-search"),

    # ── Meta ─────────────────────────────────────────────────────────────
    path("employee-filters/meta/category-types/", FilterMetaCategoryTypesView.as_view(), name="ef-meta-category-types"),
    path("employee-filters/meta/employee-types/", FilterMetaEmployeeTypesView.as_view(), name="ef-meta-employee-types"),
    path("employee-filters/meta/employee-statuses/", FilterMetaEmployeeStatusesView.as_view(), name="ef-meta-employee-statuses"),
    path("employee-filters/meta/fields/", FilterMetaFieldsView.as_view(), name="ef-meta-fields"),
    path("employee-filters/meta/conditions/", FilterMetaConditionsView.as_view(), name="ef-meta-conditions"),

    # ── CRUD ─────────────────────────────────────────────────────────────
    path("employee-filters/", EmployeeFilterListCreateView.as_view(), name="ef-list-create"),
    path("employee-filters/<uuid:filter_id>/", EmployeeFilterDetailView.as_view(), name="ef-detail"),

    # ── Actions on a specific filter ─────────────────────────────────────
    path("employee-filters/<uuid:filter_id>/execute/", EmployeeFilterExecuteView.as_view(), name="ef-execute"),
    path("employee-filters/<uuid:filter_id>/export/", EmployeeFilterExportView.as_view(), name="ef-export"),
    path("employee-filters/<uuid:filter_id>/share/", EmployeeFilterShareView.as_view(), name="ef-share"),
    path("employee-filters/<uuid:filter_id>/favorite/", EmployeeFilterFavouriteView.as_view(), name="ef-favourite"),
    path("employee-filters/<uuid:filter_id>/audit-logs/", EmployeeFilterAuditLogView.as_view(), name="ef-audit-logs"),
]

# ── /api/admin/ master dropdowns ─────────────────────────────────────────
master_urlpatterns = [
    path("departments/dropdown/", DepartmentDropdownView.as_view(), name="dept-dropdown"),
    path("designations/dropdown/", DesignationDropdownView.as_view(), name="desig-dropdown"),
    path("grades/dropdown/", GradeDropdownView.as_view(), name="grade-dropdown"),
    path("locations/dropdown/", LocationDropdownView.as_view(), name="location-dropdown"),
    path("attendance-schemes/dropdown/", AttendanceSchemeDropdownView.as_view(), name="att-scheme-dropdown"),
]
