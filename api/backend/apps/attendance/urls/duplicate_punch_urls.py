"""
Duplicate Punch URL Routing.

Registers all duplicate punch endpoints under the swipe-logs prefix:
    GET  swipe-logs/duplicates/                  - List duplicates
    GET  swipe-logs/duplicates/summary/          - Analytics summary
    POST swipe-logs/<id>/flag-duplicate/          - Flag as duplicate
    POST swipe-logs/<id>/unflag-duplicate/        - Remove duplicate flag
    POST swipe-logs/duplicates/bulk-dismiss/      - Bulk dismiss
"""

from django.urls import path
from apps.attendance.views.admin.swipe_logs.duplicate_punch_views import (
    DuplicatePunchAPI,
)

urlpatterns = [
    # List duplicate swipe logs
    path(
        "swipe-logs/duplicates/",
        DuplicatePunchAPI.list_duplicates,
        name="duplicate-punches-list",
    ),

    # Duplicate analytics summary
    path(
        "swipe-logs/duplicates/summary/",
        DuplicatePunchAPI.get_summary,
        name="duplicate-punches-summary",
    ),

    # Bulk dismiss duplicate flags
    path(
        "swipe-logs/duplicates/bulk-dismiss/",
        DuplicatePunchAPI.bulk_dismiss,
        name="duplicate-punches-bulk-dismiss",
    ),

    # Manually flag a swipe as duplicate
    path(
        "swipe-logs/<int:id>/flag-duplicate/",
        DuplicatePunchAPI.flag_duplicate,
        name="duplicate-punch-flag",
    ),

    # Remove duplicate flag
    path(
        "swipe-logs/<int:id>/unflag-duplicate/",
        DuplicatePunchAPI.unflag_duplicate,
        name="duplicate-punch-unflag",
    ),
]
