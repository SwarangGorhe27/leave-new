"""API routes for the Leave module — prefix /api/v1/leave/"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# ── ViewSets (router) ─────────────────────────────────────────────────────────
from .views.admin_views import LeaveMappingViewSet, LeaveTypeViewSet

# ── Balance views ─────────────────────────────────────────────────────────────
from .views.leave_balances import (
    AdminLeaveBalanceCreditView,
    AdminLeaveBalanceDebitView,
    AdminLeaveBalanceListView,
    EmployeeLeaveBalanceProjectionView,
    EmployeeLeaveBalanceView,
    ManagerTeamLeaveBalanceView,
)
from .views.employee_views import (
    EmployeeLeaveBalanceListView,
    EmployeeLeaveCancelView,
    EmployeeLeaveRequestListCreateView,
)

# ── Manager views (v2) ────────────────────────────────────────────────────────
from .views.manager_views import (
    ManagerApproveRequestView,
    ManagerRejectRequestView,
    ManagerTeamRequestListView,
)

# ── Approval / workflow ───────────────────────────────────────────────────────
from .views.approvals import (
    ApprovalsBulkActionView,
    ApprovalsDelegateView,
    WorkflowConfigView,
)
from .views.admin_reports import (
    AdminApprovalTATReportView,
    AdminLeaveEncashmentReportView,
    AdminLeavePatternAnalyticsView,
    AdminLeaveSummaryReportView,
    AdminWorkflowConfigCreateView,
)

# ── ESS / core leave ──────────────────────────────────────────────────────────
from .views.leave_requests import (
    AdminLeaveApplicationListView,
    EmployeeLeaveApplicationCancelView,
    EmployeeLeaveApplicationCommentView,
    EmployeeLeaveApplicationCreateView,
    EmployeeLeaveApplicationDetailView,
    EmployeeLeaveApplicationListView,
    EmployeeLeaveApplicationResubmitView,
    EmployeeLeaveApplicationUpdateView,
    ManagerLeaveApplicationApproveView,
    ManagerLeaveApplicationRejectView,
    ManagerTeamLeaveApplicationListView,
    ReasonListView,
)

# ── Masters ───────────────────────────────────────────────────────────────────
from .views.leave_types import (
    AdminLeaveTypeDeleteView,
    AdminLeaveTypeListCreateView,
    AdminLeaveTypeUpdateView,
    EmployeeLeaveTypeListView,
)
from .views.leave_policies import (
    AdminLeavePolicyAssignView,
    AdminLeavePolicyListCreateView,
    AdminLeavePolicyUpdateView,
    EmployeePolicyAssignView,
)
from .views.leave_holidays import (
    AdminHolidayListView,
    AdminHolidayGroupAssignmentView,
    AdminLeaveCarryForwardView,
    EmployeeHolidayCalendarView,
)
from .views.accrual_schedules import AccrualScheduleListView
from .views.calendar_periods import CalendarPeriodListCreateView
from .views.weekends_config import WeekendConfigDetailView, WeekendConfigView

# ── Audit / templates / encashment ────────────────────────────────────────────
from .views.admin_audit_logs import AdminAuditLogsListView
from .views.admin_notification_templates import (
    AdminNotificationTemplateListView,
    AdminNotificationTemplateUpdateView,
)
from .views.leave_encashment import AdminLeaveEncashmentProcessView

# ── Other request types ───────────────────────────────────────────────────────
from .views.other_requests import (
    # WFH
    WFHRequestListCreateView,
    WFHRequestCancelView,
    ManagerWFHListView,
    ManagerWFHApproveView,
    ManagerWFHRejectView,
    # CompOff
    CompOffRequestListCreateView,
    ManagerCompOffListView,
    ManagerCompOffApproveView,
    ManagerCompOffRejectView,
    # GatePass
    GatePassRequestListCreateView,
    ManagerGatePassListView,
    ManagerGatePassApproveView,
    ManagerGatePassRejectView,
    # OutDuty
    OutDutyRequestListCreateView,
    ManagerOutDutyListView,
    ManagerOutDutyApproveView,
    ManagerOutDutyRejectView,
    # ShortLeave
    ShortLeaveRequestListCreateView,
    ManagerShortLeaveListView,
    ManagerShortLeaveApproveView,
    ManagerShortLeaveRejectView,
    # Overtime
    OvertimeRequestListCreateView,
    ManagerOvertimeListView,
    ManagerOvertimeApproveView,
    ManagerOvertimeRejectView,
    # WeeklyOffShuffle
    WeeklyOffShuffleListCreateView,
    ManagerWeeklyOffShuffleListView,
    ManagerWeeklyOffShuffleApproveView,
    ManagerWeeklyOffShuffleRejectView,
)

# ─────────────────────────────────────────────────────────────────────────────
# Router (ViewSets)
# ─────────────────────────────────────────────────────────────────────────────

router = DefaultRouter()
router.register(r"admin/leave-types-v2", LeaveTypeViewSet, basename="leave-type-v2")
router.register(r"admin/leave-mappings", LeaveMappingViewSet, basename="leave-mapping")

# ─────────────────────────────────────────────────────────────────────────────
# URL patterns
# ─────────────────────────────────────────────────────────────────────────────

urlpatterns = [
    path("", include(router.urls)),

    # ── v2 Employee endpoints ─────────────────────────────────────────────────
    path("types/", EmployeeLeaveTypeListView.as_view(), name="leave_types_v2"),
    path("requests/", EmployeeLeaveRequestListCreateView.as_view(), name="leave_requests_v2"),
    path("requests/<uuid:id>/cancel/", EmployeeLeaveCancelView.as_view(), name="leave_request_cancel_v2"),
    path("balances/", EmployeeLeaveBalanceListView.as_view(), name="leave_balances_v2"),
    path("balances/projection/", EmployeeLeaveBalanceProjectionView.as_view(), name="leave_balance_projection"),

    # ── v2 Manager endpoints ──────────────────────────────────────────────────
    path("manager/requests/", ManagerTeamRequestListView.as_view(), name="manager_leave_requests_v2"),
    path("manager/requests/<uuid:id>/approve/", ManagerApproveRequestView.as_view(), name="manager_leave_approve_v2"),
    path("manager/requests/<uuid:id>/reject/", ManagerRejectRequestView.as_view(), name="manager_leave_reject_v2"),

    # ── ESS — core leave ──────────────────────────────────────────────────────
    path("ess/applications/reasons/", ReasonListView.as_view(), name="reason-list"),
    path("ess/apply", EmployeeLeaveApplicationCreateView.as_view(), name="leave_apply"),
    path("ess/applications", EmployeeLeaveApplicationListView.as_view(), name="leave_applications"),
    path("ess/applications/<uuid:id>", EmployeeLeaveApplicationDetailView.as_view(), name="leave_application_detail"),
    path("ess/applications/<uuid:id>/update/", EmployeeLeaveApplicationUpdateView.as_view(), name="employee-leave-application-update"),
    path("ess/applications/<uuid:id>/cancel", EmployeeLeaveApplicationCancelView.as_view(), name="leave_application_cancel"),
    path("ess/applications/<uuid:id>/resubmit/", EmployeeLeaveApplicationResubmitView.as_view(), name="employee-leave-application-resubmit"),
    path("ess/applications/<uuid:id>/comments/", EmployeeLeaveApplicationCommentView.as_view(), name="employee-leave-application-comment"),
    path("ess/balance", EmployeeLeaveBalanceView.as_view(), name="leave_balance"),
    path("ess/leave-types", EmployeeLeaveTypeListView.as_view(), name="leave_types"),
    path("ess/holidays", EmployeeHolidayCalendarView.as_view(), name="leave_holidays"),

    # ── ESS — other request types ─────────────────────────────────────────────
    path("ess/wfh/", WFHRequestListCreateView.as_view(), name="ess_wfh"),
    path("ess/wfh/<uuid:id>/cancel/", WFHRequestCancelView.as_view(), name="ess_wfh_cancel"),

    path("ess/comp-off/", CompOffRequestListCreateView.as_view(), name="ess_comp_off"),

    path("ess/gate-pass/", GatePassRequestListCreateView.as_view(), name="ess_gate_pass"),

    path("ess/out-duty/", OutDutyRequestListCreateView.as_view(), name="ess_out_duty"),

    path("ess/short-leave/", ShortLeaveRequestListCreateView.as_view(), name="ess_short_leave"),

    path("ess/overtime/", OvertimeRequestListCreateView.as_view(), name="ess_overtime"),

    path("ess/week-off-shuffle/", WeeklyOffShuffleListCreateView.as_view(), name="ess_week_off_shuffle"),

    # ── Manager — core leave ──────────────────────────────────────────────────
    path("manager/team-applications", ManagerTeamLeaveApplicationListView.as_view(), name="manager_team_leave_applications"),
    path("manager/applications/<uuid:id>/approve", ManagerLeaveApplicationApproveView.as_view(), name="manager_leave_application_approve"),
    path("manager/applications/<uuid:id>/reject", ManagerLeaveApplicationRejectView.as_view(), name="manager_leave_application_reject"),
    path("manager/team-balances", ManagerTeamLeaveBalanceView.as_view(), name="manager_team_leave_balances"),

    # ── Manager — other request types ─────────────────────────────────────────
    path("manager/wfh/", ManagerWFHListView.as_view(), name="manager_wfh"),
    path("manager/wfh/<uuid:id>/approve/", ManagerWFHApproveView.as_view(), name="manager_wfh_approve"),
    path("manager/wfh/<uuid:id>/reject/", ManagerWFHRejectView.as_view(), name="manager_wfh_reject"),

    path("manager/comp-off/", ManagerCompOffListView.as_view(), name="manager_comp_off"),
    path("manager/comp-off/<uuid:id>/approve/", ManagerCompOffApproveView.as_view(), name="manager_comp_off_approve"),
    path("manager/comp-off/<uuid:id>/reject/", ManagerCompOffRejectView.as_view(), name="manager_comp_off_reject"),

    path("manager/gate-pass/", ManagerGatePassListView.as_view(), name="manager_gate_pass"),
    path("manager/gate-pass/<uuid:id>/approve/", ManagerGatePassApproveView.as_view(), name="manager_gate_pass_approve"),
    path("manager/gate-pass/<uuid:id>/reject/", ManagerGatePassRejectView.as_view(), name="manager_gate_pass_reject"),

    path("manager/out-duty/", ManagerOutDutyListView.as_view(), name="manager_out_duty"),
    path("manager/out-duty/<uuid:id>/approve/", ManagerOutDutyApproveView.as_view(), name="manager_out_duty_approve"),
    path("manager/out-duty/<uuid:id>/reject/", ManagerOutDutyRejectView.as_view(), name="manager_out_duty_reject"),

    path("manager/short-leave/", ManagerShortLeaveListView.as_view(), name="manager_short_leave"),
    path("manager/short-leave/<uuid:id>/approve/", ManagerShortLeaveApproveView.as_view(), name="manager_short_leave_approve"),
    path("manager/short-leave/<uuid:id>/reject/", ManagerShortLeaveRejectView.as_view(), name="manager_short_leave_reject"),

    path("manager/overtime/", ManagerOvertimeListView.as_view(), name="manager_overtime"),
    path("manager/overtime/<uuid:id>/approve/", ManagerOvertimeApproveView.as_view(), name="manager_overtime_approve"),
    path("manager/overtime/<uuid:id>/reject/", ManagerOvertimeRejectView.as_view(), name="manager_overtime_reject"),

    path("manager/week-off-shuffle/", ManagerWeeklyOffShuffleListView.as_view(), name="manager_week_off_shuffle"),
    path("manager/week-off-shuffle/<uuid:id>/approve/", ManagerWeeklyOffShuffleApproveView.as_view(), name="manager_week_off_shuffle_approve"),
    path("manager/week-off-shuffle/<uuid:id>/reject/", ManagerWeeklyOffShuffleRejectView.as_view(), name="manager_week_off_shuffle_reject"),

    # ── Admin — balances ──────────────────────────────────────────────────────
    path("admin/balances", AdminLeaveBalanceListView.as_view(), name="admin_leave_balances"),
    path("admin/balances/credit", AdminLeaveBalanceCreditView.as_view(), name="admin_leave_balance_credit"),
    path("admin/balances/debit", AdminLeaveBalanceDebitView.as_view(), name="admin_leave_balance_debit"),

    # ── Admin — applications ──────────────────────────────────────────────────
    path("admin/applications", AdminLeaveApplicationListView.as_view(), name="admin_leave_applications"),

    # ── Admin — leave types ───────────────────────────────────────────────────
    path("admin/leave-types", AdminLeaveTypeListCreateView.as_view(), name="admin_leave_types"),
    path("admin/leave-types/<uuid:id>", AdminLeaveTypeUpdateView.as_view(), name="admin_leave_type_update"),
    path("admin/leave-types/<uuid:id>/delete/", AdminLeaveTypeDeleteView.as_view(), name="admin-leave-type-delete"),

    # ── Admin — policies ──────────────────────────────────────────────────────
    path("admin/policies", AdminLeavePolicyListCreateView.as_view(), name="admin_leave_policies"),
    path("admin/policies/assign", AdminLeavePolicyAssignView.as_view(), name="admin_leave_policy_assign"),
    path("admin/policies/<uuid:id>/", AdminLeavePolicyUpdateView.as_view(), name="update_leave_policy"),
    path("admin/employee-policy/assign/", EmployeePolicyAssignView.as_view(), name="admin_employee_policy_assign"),

    # ── Admin — holidays ──────────────────────────────────────────────────────
    path("admin/holidays", AdminHolidayListView.as_view(), name="admin_holidays"),
    path("admin/holiday-groups/assign", AdminHolidayGroupAssignmentView.as_view(), name="admin_leave_holiday_group_assign"),
    path("admin/carry-forward", AdminLeaveCarryForwardView.as_view(), name="admin_leave_carry_forward"),

    # ── Admin — configuration ─────────────────────────────────────────────────
    path("admin/accrual-schedules/", AccrualScheduleListView.as_view(), name="admin_accrual_schedules"),
    path("admin/calendar-periods/", CalendarPeriodListCreateView.as_view(), name="calendar_periods"),
    path("admin/weekends/config/", WeekendConfigView.as_view(), name="admin_weekend_config"),
    path("admin/weekends/config/<uuid:config_id>/", WeekendConfigDetailView.as_view(), name="admin_weekend_config_detail"),

    # ── Admin — audit / templates / encashment ────────────────────────────────
    path("admin/audit-logs/", AdminAuditLogsListView.as_view(), name="admin_audit_logs"),
    path("admin/notification-templates/", AdminNotificationTemplateListView.as_view(), name="admin_notification_templates"),
    path("admin/notification-templates/<uuid:id>/", AdminNotificationTemplateUpdateView.as_view(), name="admin_notification_template_update"),
    path("admin/leave-encashment/process/", AdminLeaveEncashmentProcessView.as_view(), name="admin_leave_encashment_process"),

    # ── Approvals ─────────────────────────────────────────────────────────────
    path("approvals/bulk-action/", ApprovalsBulkActionView.as_view(), name="approvals_bulk_action"),
    path("approvals/delegate/", ApprovalsDelegateView.as_view(), name="approvals_delegate"),

    # ── Workflow configuration ────────────────────────────────────────────────
    path("workflow/config/", WorkflowConfigView.as_view(), name="workflow_config"),
    path("workflow/config/create/", AdminWorkflowConfigCreateView.as_view(), name="admin_workflow_config_create"),

    # ── Reports & analytics ───────────────────────────────────────────────────
    path("reports/leave-summary/", AdminLeaveSummaryReportView.as_view(), name="admin_leave_summary_report"),
    path("reports/leave-encashment/", AdminLeaveEncashmentReportView.as_view(), name="admin_leave_encashment_report"),
    path("reports/approval-tat/", AdminApprovalTATReportView.as_view(), name="admin_approval_tat_report"),
    path("analytics/leave-patterns/", AdminLeavePatternAnalyticsView.as_view(), name="admin_leave_patterns_analytics"),
]
