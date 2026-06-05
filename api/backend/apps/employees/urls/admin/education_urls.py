"""
URL Configuration for Education Details API endpoints - Get and Edit.

Routes:
    GET  /employees/{employee_id}/education-details
    PATCH /employees/{employee_id}/education-details/{education_id}
"""

from django.urls import path

from apps.employees.views.admin.education_view import (
    EducationDetailsListView,
    EducationDetailView,
)

urlpatterns = [
    # Get all education records and create new one
    path(
        "<uuid:employee_id>/education-details/",
        EducationDetailsListView.as_view(),
        name="education_details_list"
    ),
    
    # Get, update specific education record
    path(
        "<uuid:employee_id>/education-details/<uuid:education_id>/",
        EducationDetailView.as_view(),
        name="education_details_detail"
    ),
]
