"""
URL configuration for admin position history APIs.
"""

from django.urls import path

from apps.employees.views.admin.position_history_view import (
    PositionHistoryDetailView,
    PositionHistoryListCreateView,
)


urlpatterns = [
    path(
        "<uuid:employee_id>/position-history",
        PositionHistoryListCreateView.as_view(),
        name="admin_position_history_list_create",
    ),
    path(
        "<uuid:employee_id>/position-history/",
        PositionHistoryListCreateView.as_view(),
        name="admin_position_history_list_create_slash",
    ),
    path(
        "<uuid:employee_id>/position-history/<uuid:position_history_id>",
        PositionHistoryDetailView.as_view(),
        name="admin_position_history_detail",
    ),
    path(
        "<uuid:employee_id>/position-history/<uuid:position_history_id>/",
        PositionHistoryDetailView.as_view(),
        name="admin_position_history_detail_slash",
    ),
]
