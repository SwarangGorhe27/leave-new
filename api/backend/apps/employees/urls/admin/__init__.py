"""Admin / HR URLconf — aggregates employee admin route modules."""

from django.urls import include, path

from .urls import urlpatterns as change_request_urlpatterns

urlpatterns = [
    *change_request_urlpatterns,
    path("", include("apps.employees.urls.admin.employee_profile_urls")),
    path("", include("apps.employees.urls.admin.family_details_urls")),
    path("", include("apps.employees.urls.admin.work_experience_urls")),
    path("", include("apps.employees.urls.admin.passport_urls")),
    path("", include("apps.employees.urls.admin.bank_statutory_urls")),
    path("", include("apps.employees.urls.admin.position_history_urls")),
    path("", include("apps.employees.urls.admin.previous_employment_urls")),
    path("", include("apps.employees.urls.admin.education_urls")),
    path("", include("apps.employees.urls.admin.nominee_urls")),
    path("", include("apps.employees.urls.admin.document_urls")),
    path("employees/", include("apps.employees.urls.admin.document_urls")),
    path("", include("apps.employees.urls.admin.policies_forms_urls")),
    path("<uuid:employee_id>/", include("apps.employees.urls.admin.policies_forms_urls")),
    path("employees/<uuid:employee_id>/", include("apps.employees.urls.admin.policies_forms_urls")),
    path("", include("apps.employees.urls.admin.segment_urls")),
    path("<uuid:employee_id>/", include("apps.employees.urls.admin.segment_urls")),
    path("employees/<uuid:employee_id>/", include("apps.employees.urls.admin.segment_urls")),
    path("", include("apps.employees.urls.admin.role_mapping_urls")),
    path("<uuid:employee_id>/", include("apps.employees.urls.admin.role_mapping_urls")),
    path("employees/<uuid:employee_id>/", include("apps.employees.urls.admin.role_mapping_urls")),
    path("", include("apps.employees.urls.admin.salary_urls")),
    path("employees/", include("apps.employees.urls.admin.salary_urls")),
    path("", include("apps.employees.urls.admin.background_verification_urls")),
    path("employees/", include("apps.employees.urls.admin.background_verification_urls")),
    path("", include("apps.employees.urls.admin.asset_urls")),
    path("", include("apps.employees.urls.admin.access_card_urls")),
    # ── Fines & Damages (Setup section) ─────────────────────────────────
    path("setup/", include("apps.employees.urls.admin.fines_damages_urls")),
    # ── Employee Filter (Setup section) ─────────────────────────────────
    path("setup/", include("apps.employees.urls.admin.employee_filter_urls")),
    path("", include("apps.employees.urls.admin.org_chart_urls")),
    path("employees/", include("apps.employees.urls.admin.org_chart_urls")),
]
