from django.urls import path

from apps.employees.views.admin.segment_view import (
    EmployeeFilterListCreateView,
    EmployeeFilterPreviewView,
    PredefinedFiltersView,
    SegmentDashboardView,
    SegmentDetailView,
    SegmentDuplicateView,
    SegmentEmployeeSearchView,
    SegmentMembersView,
)

urlpatterns = [
    path("segments/", SegmentDashboardView.as_view(), name="admin-segment-list"),
    path("segments/<uuid:segment_id>/", SegmentDetailView.as_view(), name="admin-segment-detail"),
    path("segments/<uuid:segment_id>/duplicate/", SegmentDuplicateView.as_view(), name="admin-segment-duplicate"),
    path("segments/<uuid:segment_id>/members/", SegmentMembersView.as_view(), name="admin-segment-members"),
    path("segments/employees/", SegmentEmployeeSearchView.as_view(), name="admin-segment-employee-search"),
    path("segments/filters/", EmployeeFilterListCreateView.as_view(), name="admin-employee-filter-list"),
    path("segments/filters/preview/", EmployeeFilterPreviewView.as_view(), name="admin-employee-filter-preview"),
    path("segments/predefined-filters/", PredefinedFiltersView.as_view(), name="admin-segment-predefined-filters"),
]
