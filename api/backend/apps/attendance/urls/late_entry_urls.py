"""
Late Entry URL Routing.
"""

from django.urls import path
from apps.attendance.views.admin.swipe_logs.late_entry_views import LateEntryAPI

urlpatterns = [
    # Swipe Logs Late Entry endpoints
    path(
        "swipe-logs/late-entries",
        LateEntryAPI.list_late_entries,
        name="late-entries-list",
    ),
    path(
        "swipe-logs/late-entries/summary",
        LateEntryAPI.get_summary,
        name="late-entries-summary",
    ),

    # Attendance Late Cycle tracker and leaderboard endpoints
    path(
        "attendance/late-cycle/<uuid:employee_id>",
        LateEntryAPI.get_late_cycle_tracker,
        name="late-cycle-tracker",
    ),
    path(
        "attendance/late-entries/leaderboard",
        LateEntryAPI.get_leaderboard,
        name="late-entries-leaderboard",
    ),
]
