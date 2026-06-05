"""Employee views for attendance module."""

from apps.attendance.views.employee.shift_assignment_view import (
    ShiftAssignmentViewSet,
)
from apps.attendance.views.employee.shift_assignment_bulk_view import (
    BulkShiftAssignmentCreateView,
    BulkShiftAssignmentValidateView,
    BulkShiftAssignmentStatusView,
    BulkShiftAssignmentRetryView,
)
from apps.attendance.views.employee.rotation_weekly_off_view import (
    ShiftRotationRuleViewSet,
    WeeklyOffViewSet,
    WeekendOverrideViewSet,
)
from apps.attendance.views.employee.shift_swap_view import ShiftSwapViewSet
from apps.attendance.views.employee.shift_swap_workflow_view import (
    accept_shift_swap,
    approve_shift_swap,
    reject_shift_swap,
    cancel_shift_swap,
)
from apps.attendance.views.employee.roster_publish_view import (
    publish_roster,
    unpublish_roster,
    get_publish_status,
    get_publish_history,
)

# Roster Lock Views
from apps.attendance.views.employee.roster_lock_views import (
    lock_roster,
    unlock_roster,
    get_lock_config,
    set_lock_config,
    get_lock_status,
)

# Roster Calendar Views
from apps.attendance.views.employee.roster_calendar_views import (
    get_monthly_calendar,
    get_day_calendar,
    detect_conflicts,
)

# Employee Shift History Views
from apps.attendance.views.employee.employee_shift_history_views import (
    get_shift_history,
    get_current_shift,
    get_shift_config,
    update_shift_config,
    get_bulk_history,
)

# Roster Audit Views
from apps.attendance.views.employee.roster_audit_views import (
    get_audit_logs,
    get_audit_detail,
    get_entity_audit_history,
    get_entity_change_summary,
)
from apps.attendance.views.employee.request_views import (
    EmployeeOTViewSet,
    EmployeeRegularizationViewSet,
)
__all__ = [
    # Shift Assignment
    "ShiftAssignmentViewSet",
    # Bulk Shift Assignment
    "BulkShiftAssignmentCreateView",
    "BulkShiftAssignmentValidateView",
    "BulkShiftAssignmentStatusView",
    "BulkShiftAssignmentRetryView",
    # Rotation, Weekly Off, Weekend Override
    "ShiftRotationRuleViewSet",
    "WeeklyOffViewSet",
    "WeekendOverrideViewSet",
    # Shift Swap
    "ShiftSwapViewSet",
    # Shift Swap Workflow
    "accept_shift_swap",
    "approve_shift_swap",
    "reject_shift_swap",
    "cancel_shift_swap",
    # Roster Publish
    "publish_roster",
    "unpublish_roster",
    "get_publish_status",
    "get_publish_history",
    # Roster Lock
    "lock_roster",
    "unlock_roster",
    "get_lock_config",
    "set_lock_config",
    "get_lock_status",
    # Roster Calendar
    "get_monthly_calendar",
    "get_day_calendar",
    "detect_conflicts",
    # Employee Shift History
    "get_shift_history",
    "get_current_shift",
    "get_shift_config",
    "update_shift_config",
    "get_bulk_history",
    # Roster Audit
    "get_audit_logs",
    "get_audit_detail",
    "get_entity_audit_history",
    "get_entity_change_summary",
    "EmployeeOTViewSet",
    "EmployeeRegularizationViewSet",
]
