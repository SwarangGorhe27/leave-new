from django.urls import path

from apps.employees.views.admin.role_mapping_view import (
    EmployeeRoleDetailView,
    RoleAssignmentRevokeView,
    RoleDashboardView,
    RoleDetailView,
    RoleEmployeeListView,
    RoleListCreateView,
    RoleMappingOptionsView,
)

urlpatterns = [
    path("roles-mapping/", RoleDashboardView.as_view(), name="admin-role-dashboard"),
    path("roles-mapping/options/", RoleMappingOptionsView.as_view(), name="admin-role-options"),
    path("roles-mapping/roles/", RoleListCreateView.as_view(), name="admin-role-list"),
    path("roles-mapping/roles/<uuid:role_id>/", RoleDetailView.as_view(), name="admin-role-detail"),
    path("roles-mapping/employees/search/", RoleEmployeeListView.as_view(), name="admin-role-employee-search"),
    path("roles-mapping/employees/", RoleEmployeeListView.as_view(), name="admin-role-employees"),
    path("roles-mapping/employees/<uuid:target_employee_id>/roles/", EmployeeRoleDetailView.as_view(), name="admin-employee-role-detail"),
    path("roles-mapping/assignments/<uuid:assignment_id>/", RoleAssignmentRevokeView.as_view(), name="admin-role-assignment-revoke"),
]
