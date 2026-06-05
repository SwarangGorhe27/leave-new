"""Validators for the Attendance module."""

from apps.attendance.validators.swipe_logs.swipe_log_validator import SwipeLogValidator
from apps.attendance.validators.swipe_logs.swipe_live_sync_validators import (
    SwipeLiveValidator,
    SwipeSyncValidator,
)

from apps.attendance.validators.shift_roster.shift_validator import ShiftValidator
from apps.attendance.validators.shift_roster.roster_validator import RosterValidator
from apps.attendance.validators.admin.dashboard.dashboard_validator import DashboardValidator

# Shift Swap Validators
from apps.attendance.validators.shift_swap_validators import (
    validate_different_employees,
    validate_employees_exist,
    validate_shifts_exist,
    validate_swap_date,
    validate_shift_ownership,
    validate_no_duplicate_swap,
    validate_no_pending_opposite_swap,
)

# Roster Publish Validators
from apps.attendance.validators.roster_publish_validators import (
    validate_publish_period,
    validate_departments_exist,
    validate_publisher_exists,
    validate_no_duplicate_publish,
    validate_rosters_exist,
    validate_publish_exists,
    validate_roster_not_locked,
)

# Roster Lock Validators
from apps.attendance.validators.roster_lock_validators import (
    validate_lock_month_year,
    validate_departments_exist as validate_lock_departments,
    validate_not_already_locked,
    validate_roster_locked,
)

# Roster Calendar Validators
from apps.attendance.validators.roster_calendar_validators import (
    validate_employee_exists as validate_calendar_employee,
    validate_department_exists as validate_calendar_department,
    validate_calendar_period,
    validate_date_range as validate_calendar_date_range,
    validate_calendar_date,
)

# Employee Shift History Validators
from apps.attendance.validators.employee_shift_history_validators import (
    validate_employee_exists as validate_history_employee,
    validate_shift_exists,
    validate_date_range as validate_history_date_range,
    validate_employee_ids_not_empty,
    validate_no_overlapping_config,
)

# Roster Audit Validators
from apps.attendance.validators.roster_audit_validators import (
    validate_audit_log_exists,
    validate_date_range as validate_audit_date_range,
    validate_employee_exists as validate_audit_employee,
    validate_entity_type_valid,
)
from apps.attendance.validators.exception_validators import (
    get_actor_employee_id,
    get_company_id_from_request,
    parse_company_id,
    validate_company_access,
    validate_exception_is_resolvable,
)
from apps.attendance.validators.audit_log_validators import (
    get_attendance_table_names,
    normalize_table_name,
    validate_action,
    validate_action_source,
    validate_company_and_employee_scope,
)
from apps.attendance.validators.notification_validators import (
    validate_notification_type,
    validate_recipient,
    validate_triggered_by,
    validate_recipient_ownership,
    validate_reference_table,
    validate_recipient_ids,
)


__all__ = [
    "ShiftValidator",
    "RosterValidator",
    "SwipeLogValidator",
    "SwipeLiveValidator",
    "SwipeSyncValidator",
    "DashboardValidator",
    # Shift Swap
    "validate_different_employees",
    "validate_employees_exist",
    "validate_shifts_exist",
    "validate_swap_date",
    "validate_shift_ownership",
    "validate_no_duplicate_swap",
    "validate_no_pending_opposite_swap",
    # Roster Publish
    "validate_publish_period",
    "validate_departments_exist",
    "validate_publisher_exists",
    "validate_no_duplicate_publish",
    "validate_rosters_exist",
    "validate_publish_exists",
    "validate_roster_not_locked",
    # Roster Lock
    "validate_lock_month_year",
    "validate_lock_departments",
    "validate_not_already_locked",
    "validate_roster_locked",
    # Roster Calendar
    "validate_calendar_employee",
    "validate_calendar_department",
    "validate_calendar_period",
    "validate_calendar_date_range",
    "validate_calendar_date",
    # Employee Shift History
    "validate_history_employee",
    "validate_shift_exists",
    "validate_history_date_range",
    "validate_employee_ids_not_empty",
    "validate_no_overlapping_config",
    # Roster Audit
    "validate_audit_log_exists",
    "validate_audit_date_range",
    "validate_audit_employee",
    "validate_entity_type_valid",
    "get_actor_employee_id",
    "get_company_id_from_request",
    "parse_company_id",
    "validate_company_access",
    "validate_exception_is_resolvable",
    "get_attendance_table_names",
    "normalize_table_name",
    "validate_action",
    "validate_action_source",
    "validate_company_and_employee_scope",
    "validate_notification_type",
    "validate_recipient",
    "validate_triggered_by",
    "validate_recipient_ownership",
    "validate_reference_table",
    "validate_recipient_ids",
]
