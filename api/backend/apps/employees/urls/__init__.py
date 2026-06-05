"""
HRMS ESS — Root URL dispatcher.

Include from project urls.py:

    path("", include("apps.employees.urls")),

Routes:
    /api/employee/   — Employee self-service (ESS)
    /api/admin/      — HR / admin (change requests, profiles)
"""

from django.urls import include, path

app_name = "employees"

urlpatterns = [
    path(
        "api/employee/",
        include("apps.employees.urls.employee"),
    ),
    path(
        "api/admin/",
        include("apps.employees.urls.admin"),
    ),
    # Backwards-compatible admin path used by some clients: /api/admin/employees/
    path(
        "api/admin/employees/",
        include(
            (
                "apps.employees.urls.admin.employee_profile_urls",
                "ess_admin_employee",
            ),
            namespace="ess_admin_employee_direct",
        ),
    ),
    # Legacy admin profile base path (kept for existing clients)
    path(
        "api/employees/",
        include(
            (
                "apps.employees.urls.admin.employee_profile_urls",
                "ess_admin_employee",
            ),
            namespace="ess_admin_employee_legacy",
        ),
    ),
]

# Backward-compatible alias used in documentation
ess_urlpatterns = urlpatterns
"""Employee app URLs package."""
