"""
Org chart admin URL routes.

Base: /api/employees/

Routes:
    GET  employees/search/
    GET  org-chart/tree/
    POST org-chart/top-level-manager/
    POST org-chart/assign-manager/
    POST org-chart/mass-transfer/
    GET  org-chart/unassigned/
    POST org-chart/export/
"""

from django.urls import path

from apps.employees.views.admin.org_chart_view import (
    EmployeeSearchView,
    OrgChartAssignManagerView,
    OrgChartExportView,
    OrgChartMassTransferView,
    OrgChartTopLevelManagerView,
    OrgChartTreeView,
    OrgChartUnassignedView,
)

urlpatterns = [
    path("employees/search/", EmployeeSearchView.as_view(), name="employee-search"),
    path("org-chart/tree/", OrgChartTreeView.as_view(), name="org-chart-tree"),
    path(
        "org-chart/top-level-manager/",
        OrgChartTopLevelManagerView.as_view(),
        name="org-chart-top-level-manager",
    ),
    path(
        "org-chart/assign-manager/",
        OrgChartAssignManagerView.as_view(),
        name="org-chart-assign-manager",
    ),
    path(
        "org-chart/mass-transfer/",
        OrgChartMassTransferView.as_view(),
        name="org-chart-mass-transfer",
    ),
    path(
        "org-chart/unassigned/",
        OrgChartUnassignedView.as_view(),
        name="org-chart-unassigned",
    ),
    path("org-chart/export/", OrgChartExportView.as_view(), name="org-chart-export"),
]
