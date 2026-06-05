"""
URL routes for Employee Asset admin APIs.
"""

from django.urls import path

from apps.employees.views.admin.asset_view import (
    EmployeeAssetListView,
    EmployeeAssetDetailView,
)

urlpatterns = [
    # List and Create asset assignments
    path(
        "<uuid:employee_id>/asset-details/",
        EmployeeAssetListView.as_view(),
        name="employee-asset-list",
    ),

    # Get, Update, and Delete single asset assignment
    path(
        "<uuid:employee_id>/asset-details/<uuid:asset_id>/",
        EmployeeAssetDetailView.as_view(),
        name="employee-asset-detail",
    ),
]
