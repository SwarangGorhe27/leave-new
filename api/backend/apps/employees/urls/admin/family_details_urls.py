"""
URL Configuration for Family Details API endpoints - Get and Edit Only.

Routes:
    GET  /employees/{employee_id}/family-details
    PATCH /employees/{employee_id}/family-details/{family_member_id}
"""

from django.urls import path

from apps.employees.views.admin.family_details_view import (
    FamilyDetailsListView,
    FamilyMemberDetailView,
)

urlpatterns = [
    # Get all family members
    path(
        "<uuid:employee_id>/family-details",
        FamilyDetailsListView.as_view(),
        name="family_details_list"
    ),
    
    # Update specific family member
    path(
        "<uuid:employee_id>/family-details/<uuid:family_member_id>",
        FamilyMemberDetailView.as_view(),
        name="family_member_detail"
    ),
]
