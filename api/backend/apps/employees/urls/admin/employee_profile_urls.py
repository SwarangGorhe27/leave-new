from django.urls import path

from apps.employees.views.admin.employee_profile_view import (
    EmployeeProfileView,
)
from apps.employees.views.admin.profile_section_view import (
    EmployeeProfileSectionAdminView,
)
from apps.employees.views.admin.profile_detail_section_views import (
    EmployeeAddressDetailsAdminView,
    EmployeeEmploymentDetailsAdminView,
    EmployeeInsuranceDetailsAdminView,
    EmployeeInsurancePolicyAdminView,
    EmployeeLanguageDetailsAdminView,
    EmployeeMedicalDetailsAdminView,
    EmployeePersonalDetailsAdminView,
)

app_name = "ess_admin_employee"

urlpatterns = [
    path(
        "<uuid:employee_id>/profile/",
        EmployeeProfileView.as_view(),
        name="admin_employee_profile",
    ),
    path(
        "<uuid:employee_id>/profile-section/",
        EmployeeProfileSectionAdminView.as_view(),
        name="admin_employee_profile_section",
    ),
    path(
        "<uuid:employee_id>/personal-details/",
        EmployeePersonalDetailsAdminView.as_view(),
        name="admin_employee_personal_details",
    ),
    path(
        "<uuid:employee_id>/address-details/",
        EmployeeAddressDetailsAdminView.as_view(),
        name="admin_employee_address_details",
    ),
    path(
        "<uuid:employee_id>/employment-details/",
        EmployeeEmploymentDetailsAdminView.as_view(),
        name="admin_employee_employment_details",
    ),
    path(
        "<uuid:employee_id>/language-details/",
        EmployeeLanguageDetailsAdminView.as_view(),
        name="admin_employee_language_details",
    ),
    path(
        "<uuid:employee_id>/medical-details/",
        EmployeeMedicalDetailsAdminView.as_view(),
        name="admin_employee_medical_details",
    ),
    path(
        "<uuid:employee_id>/insurance-details/",
        EmployeeInsuranceDetailsAdminView.as_view(),
        name="admin_employee_insurance_details",
    ),
    path(
        "<uuid:employee_id>/insurance-details",
        EmployeeInsuranceDetailsAdminView.as_view(),
        name="admin_employee_insurance_details_no_slash",
    ),
    path(
        "<uuid:employee_id>/insurance-details/<uuid:policy_id>/",
        EmployeeInsurancePolicyAdminView.as_view(),
        name="admin_employee_insurance_policy",
    ),
    path(
        "<uuid:employee_id>/insurance-details/<uuid:policy_id>",
        EmployeeInsurancePolicyAdminView.as_view(),
        name="admin_employee_insurance_policy_no_slash",
    ),
]
