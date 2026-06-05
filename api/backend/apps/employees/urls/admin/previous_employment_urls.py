"""
URL routes for Previous Employment admin GET APIs.
"""

from django.urls import path

from apps.employees.views.admin.previous_employment_view import (
    PreviousEmploymentListView,
    PreviousEmploymentDetailView,
)

urlpatterns = [
    # List all previous employment records
    path(
        "<uuid:employee_id>/previous-employment/",
        PreviousEmploymentListView.as_view(),
        name="previous-employment-list",
    ),

    # Get single previous employment record
    path(
        "<uuid:employee_id>/previous-employment/<uuid:employment_id>/",
        PreviousEmploymentDetailView.as_view(),
        name="previous-employment-detail",
    ),
]