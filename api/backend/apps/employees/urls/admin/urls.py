"""
Admin URLs for Employee ESS

Base URL: /api/admin/

Endpoints for HR/Admin to manage change requests and employee profiles.
"""

from django.urls import path, include

from apps.employees.views.admin import (
    ChangeRequestApproveAdminView,
    ChangeRequestDetailAdminView,
    ChangeRequestListAdminView,
    ChangeRequestRejectAdminView,
)

app_name = "ess_admin"

urlpatterns = [
    # ═════════════════════════════════════════════════════════════════════
    # ADD EMPLOYEE  (must be before generic employees/ includes)
    # ═════════════════════════════════════════════════════════════════════
    path("employees/", include("apps.employees.urls.admin.add_employee_urls")),

    # ═════════════════════════════════════════════════════════════════════
    # CHANGE REQUEST APPROVAL WORKFLOW
    # ═════════════════════════════════════════════════════════════════════
    path("change-requests/", ChangeRequestListAdminView.as_view(), name="change-requests-list"),
    # GET  — List all change requests (paginated, filterable by status/module/employee)
    
    path("change-request/<uuid:pk>/", ChangeRequestDetailAdminView.as_view(), name="change-request-detail"),
    # GET  — View change request with diff (old_data vs request_data)
    
    path("change-request/<uuid:pk>/approve/", ChangeRequestApproveAdminView.as_view(), name="change-request-approve"),
    # POST — Approve change request (apply changes to employee profile)
    #   Body: { "admin_remarks": "optional reason" }
    
    path("change-request/<uuid:pk>/reject/", ChangeRequestRejectAdminView.as_view(), name="change-request-reject"),
    # POST — Reject change request (no changes applied)
    #   Body: { "admin_remarks": "rejection reason (required)" }
    
    # ═════════════════════════════════════════════════════════════════════
    # EMPLOYEE PROFILE MANAGEMENT
    # ═════════════════════════════════════════════════════════════════════
    path("employees/", include("apps.employees.urls.admin.employee_profile_urls")),
    path("employees/", include("apps.employees.urls.admin.document_urls")),
    path("", include("apps.employees.urls.admin.policies_forms_urls")),
    path("employees/<uuid:employee_id>/", include("apps.employees.urls.admin.policies_forms_urls")),
    path("", include("apps.employees.urls.admin.segment_urls")),
    path("employees/<uuid:employee_id>/", include("apps.employees.urls.admin.segment_urls")),
    path("", include("apps.employees.urls.admin.role_mapping_urls")),
    path("employees/<uuid:employee_id>/", include("apps.employees.urls.admin.role_mapping_urls")),
    path("employees/", include("apps.employees.urls.admin.salary_urls")),
    path("employees/", include("apps.employees.urls.admin.background_verification_urls")),
]

