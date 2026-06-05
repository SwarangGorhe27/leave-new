"""
URL routes for Employee Background Verification admin APIs.
"""

from django.urls import path

from apps.employees.views.admin.background_verification_view import (
    BackgroundVerificationStatusListView,
    EmployeeBackgroundVerificationView,
)

urlpatterns = [
    path(
        "background-verification/statuses/",
        BackgroundVerificationStatusListView.as_view(),
        name="background-verification-statuses",
    ),
    path(
        "<uuid:employee_id>/background-verification/statuses/",
        BackgroundVerificationStatusListView.as_view(),
        name="employee-background-verification-statuses",
    ),
    path(
        "<uuid:employee_id>/background-verification/",
        EmployeeBackgroundVerificationView.as_view(),
        name="employee-background-verification",
    ),
]
