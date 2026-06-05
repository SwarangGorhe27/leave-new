"""
URL Configuration for Nominee Details API endpoints — Admin Side.

Routes:
    GET   /employees/{employee_id}/nominee-details
    PATCH /employees/{employee_id}/nominee-details/{nominee_id}

Registration in config/tenant_urls.py:
    path(
        "employees/",
        include("apps.employees.urls.admin.nominee_urls"),
    ),
"""

from django.urls import path

from apps.employees.views.admin.nominee_view import (
    NomineeDetailView,
    NomineeListView,
)

urlpatterns = [
    # GET  — all nominees for an employee
    path(
        "<uuid:employee_id>/nominee-details",
        NomineeListView.as_view(),
        name="nominee_list",
    ),
    # PATCH — update a specific nominee
    path(
        "<uuid:employee_id>/nominee-details/<uuid:nominee_id>",
        NomineeDetailView.as_view(),
        name="nominee_detail",
    ),
]