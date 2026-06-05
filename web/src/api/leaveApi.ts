/**
 * Leave module API client.
 * All paths are relative to /api/v1/leave/ (mounted in tenant_urls.py).
 */

import api, { unwrap } from "@api/client";
import type {
  ActionRemarks,
  ApprovalWorkflowConfig,
  AuditLog,
  CompOffRequest,
  CompOffRequestPayload,
  GatePassRequest,
  GatePassRequestPayload,
  LeaveBalance,
  LeaveBalanceProjection,
  LeaveMapping,
  LeaveMappingPayload,
  LeavePolicy,
  LeavePolicyPayload,
  LeaveReportParams,
  LeaveRequest,
  LeaveRequestPayload,
  LeaveRequestUpdatePayload,
  LeaveType,
  LeaveTypePayload,
  NotificationTemplate,
  NotificationTemplatePayload,
  OutDutyRequest,
  OutDutyRequestPayload,
  OvertimeRequest,
  OvertimeRequestPayload,
  PaginatedResponse,
  ShortLeaveRequest,
  ShortLeaveRequestPayload,
  WFHRequest,
  WFHRequestPayload,
  WeeklyOffShufflePayload,
  WeeklyOffShuffleRequest,
  WorkflowConfigPayload,
} from "@/types/leave";

const BASE = "/v1/leave";

// ─────────────────────────────────────────────────────────────────────────────
// ESS — Core Leave
// ─────────────────────────────────────────────────────────────────────────────

export const applyLeave = (payload: LeaveRequestPayload) =>
  api.post(`${BASE}/ess/apply`, payload).then((r) => unwrap<{ application_id: string }>(r));

export const fetchMyLeaveApplications = (params?: { status?: string; year?: number }) =>
  api.get(`${BASE}/ess/applications`, { params }).then((r) => unwrap<PaginatedResponse<LeaveRequest>>(r));

export const fetchLeaveApplicationDetail = (id: string) =>
  api.get(`${BASE}/ess/applications/${id}`).then((r) => unwrap<LeaveRequest>(r));

export const updateLeaveApplication = (id: string, payload: LeaveRequestUpdatePayload) =>
  api.patch(`${BASE}/ess/applications/${id}/update/`, payload).then((r) => unwrap<{ application_id: string }>(r));

export const cancelLeaveApplication = (id: string, reason: string) =>
  api.patch(`${BASE}/ess/applications/${id}/cancel`, { reason }).then((r) => unwrap(r));

export const resubmitLeaveApplication = (id: string, payload: Partial<LeaveRequestUpdatePayload>) =>
  api.post(`${BASE}/ess/applications/${id}/resubmit/`, payload).then((r) => unwrap<{ application_id: string }>(r));

export const addLeaveComment = (id: string, comment: string) =>
  api.post(`${BASE}/ess/applications/${id}/comments/`, { comment }).then((r) => unwrap<{ comment_id: string }>(r));

export const fetchMyLeaveBalance = (params?: { year?: number }) =>
  api.get(`${BASE}/ess/balance`, { params }).then((r) => unwrap<LeaveBalance[]>(r));

export const fetchLeaveBalanceProjection = (params?: { leave_type_id?: string; project_until?: string }) =>
  api.get(`${BASE}/balances/projection/`, { params }).then((r) => unwrap<LeaveBalanceProjection>(r));

export const fetchLeaveTypes = () =>
  api.get(`${BASE}/ess/leave-types`).then((r) => unwrap<LeaveType[]>(r));

export const fetchEmployeeLeaveTypes = () =>
  api.get(`${BASE}/types/`).then((r) => unwrap<LeaveType[]>(r));

export const fetchLeaveReasons = (category?: string) =>
  api.get(`${BASE}/ess/applications/reasons/`, { params: { category } }).then((r) => unwrap<{ id: string; label: string }[]>(r));

export const fetchHolidayCalendar = (params?: { year?: number }) =>
  api.get(`${BASE}/ess/holidays`, { params }).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// ESS — v2 endpoints
// ─────────────────────────────────────────────────────────────────────────────

export const fetchMyLeaveRequests = (params?: { status?: string; year?: number }) =>
  api.get(`${BASE}/requests/`, { params }).then((r) => unwrap<PaginatedResponse<LeaveRequest>>(r));

export const cancelLeaveRequest = (id: string) =>
  api.post(`${BASE}/requests/${id}/cancel/`).then((r) => unwrap(r));

export const fetchMyLeaveBalances = (params?: { year?: number }) =>
  api.get(`${BASE}/balances/`, { params }).then((r) => unwrap<LeaveBalance[]>(r));

// ─────────────────────────────────────────────────────────────────────────────
// ESS — WFH
// ─────────────────────────────────────────────────────────────────────────────

export const fetchMyWFHRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/ess/wfh/`, { params }).then((r) => unwrap<PaginatedResponse<WFHRequest>>(r));

export const createWFHRequest = (payload: WFHRequestPayload) =>
  api.post(`${BASE}/ess/wfh/`, payload).then((r) => unwrap<{ id: string }>(r));

export const cancelWFHRequest = (id: string) =>
  api.patch(`${BASE}/ess/wfh/${id}/cancel/`).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// ESS — CompOff
// ─────────────────────────────────────────────────────────────────────────────

export const fetchMyCompOffRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/ess/comp-off/`, { params }).then((r) => unwrap<PaginatedResponse<CompOffRequest>>(r));

export const createCompOffRequest = (payload: CompOffRequestPayload) =>
  api.post(`${BASE}/ess/comp-off/`, payload).then((r) => unwrap<{ id: string }>(r));

// ─────────────────────────────────────────────────────────────────────────────
// ESS — GatePass
// ─────────────────────────────────────────────────────────────────────────────

export const fetchMyGatePassRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/ess/gate-pass/`, { params }).then((r) => unwrap<PaginatedResponse<GatePassRequest>>(r));

export const createGatePassRequest = (payload: GatePassRequestPayload) =>
  api.post(`${BASE}/ess/gate-pass/`, payload).then((r) => unwrap<{ id: string }>(r));

// ─────────────────────────────────────────────────────────────────────────────
// ESS — OutDuty
// ─────────────────────────────────────────────────────────────────────────────

export const fetchMyOutDutyRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/ess/out-duty/`, { params }).then((r) => unwrap<PaginatedResponse<OutDutyRequest>>(r));

export const createOutDutyRequest = (payload: OutDutyRequestPayload) =>
  api.post(`${BASE}/ess/out-duty/`, payload).then((r) => unwrap<{ id: string }>(r));

// ─────────────────────────────────────────────────────────────────────────────
// ESS — ShortLeave
// ─────────────────────────────────────────────────────────────────────────────

export const fetchMyShortLeaveRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/ess/short-leave/`, { params }).then((r) => unwrap<PaginatedResponse<ShortLeaveRequest>>(r));

export const createShortLeaveRequest = (payload: ShortLeaveRequestPayload) =>
  api.post(`${BASE}/ess/short-leave/`, payload).then((r) => unwrap<{ id: string }>(r));

// ─────────────────────────────────────────────────────────────────────────────
// ESS — Overtime
// ─────────────────────────────────────────────────────────────────────────────

export const fetchMyOvertimeRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/ess/overtime/`, { params }).then((r) => unwrap<PaginatedResponse<OvertimeRequest>>(r));

export const createOvertimeRequest = (payload: OvertimeRequestPayload) =>
  api.post(`${BASE}/ess/overtime/`, payload).then((r) => unwrap<{ id: string }>(r));

// ─────────────────────────────────────────────────────────────────────────────
// ESS — WeeklyOffShuffle
// ─────────────────────────────────────────────────────────────────────────────

export const fetchMyWeeklyOffShuffleRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/ess/week-off-shuffle/`, { params }).then((r) => unwrap<PaginatedResponse<WeeklyOffShuffleRequest>>(r));

export const createWeeklyOffShuffleRequest = (payload: WeeklyOffShufflePayload) =>
  api.post(`${BASE}/ess/week-off-shuffle/`, payload).then((r) => unwrap<{ id: string }>(r));

// ─────────────────────────────────────────────────────────────────────────────
// Manager — Core Leave
// ─────────────────────────────────────────────────────────────────────────────

export const fetchTeamLeaveApplications = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/team-applications`, { params }).then((r) => unwrap<PaginatedResponse<LeaveRequest>>(r));

export const approveLeaveApplication = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/applications/${id}/approve`, payload).then((r) => unwrap(r));

export const rejectLeaveApplication = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/applications/${id}/reject`, payload).then((r) => unwrap(r));

export const fetchTeamLeaveBalances = (params?: { year?: number }) =>
  api.get(`${BASE}/manager/team-balances`, { params }).then((r) => unwrap<LeaveBalance[]>(r));

// v2
export const fetchTeamLeaveRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/requests/`, { params }).then((r) => unwrap<PaginatedResponse<LeaveRequest>>(r));

export const approveLeaveRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/requests/${id}/approve/`, payload).then((r) => unwrap(r));

export const rejectLeaveRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/requests/${id}/reject/`, payload).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Manager — Other Request Types
// ─────────────────────────────────────────────────────────────────────────────

export const fetchTeamWFHRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/wfh/`, { params }).then((r) => unwrap<PaginatedResponse<WFHRequest>>(r));
export const approveWFHRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/wfh/${id}/approve/`, payload).then((r) => unwrap(r));
export const rejectWFHRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/wfh/${id}/reject/`, payload).then((r) => unwrap(r));

export const fetchTeamCompOffRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/comp-off/`, { params }).then((r) => unwrap<PaginatedResponse<CompOffRequest>>(r));
export const approveCompOffRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/comp-off/${id}/approve/`, payload).then((r) => unwrap(r));
export const rejectCompOffRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/comp-off/${id}/reject/`, payload).then((r) => unwrap(r));

export const fetchTeamGatePassRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/gate-pass/`, { params }).then((r) => unwrap<PaginatedResponse<GatePassRequest>>(r));
export const approveGatePassRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/gate-pass/${id}/approve/`, payload).then((r) => unwrap(r));
export const rejectGatePassRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/gate-pass/${id}/reject/`, payload).then((r) => unwrap(r));

export const fetchTeamOutDutyRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/out-duty/`, { params }).then((r) => unwrap<PaginatedResponse<OutDutyRequest>>(r));
export const approveOutDutyRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/out-duty/${id}/approve/`, payload).then((r) => unwrap(r));
export const rejectOutDutyRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/out-duty/${id}/reject/`, payload).then((r) => unwrap(r));

export const fetchTeamShortLeaveRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/short-leave/`, { params }).then((r) => unwrap<PaginatedResponse<ShortLeaveRequest>>(r));
export const approveShortLeaveRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/short-leave/${id}/approve/`, payload).then((r) => unwrap(r));
export const rejectShortLeaveRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/short-leave/${id}/reject/`, payload).then((r) => unwrap(r));

export const fetchTeamOvertimeRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/overtime/`, { params }).then((r) => unwrap<PaginatedResponse<OvertimeRequest>>(r));
export const approveOvertimeRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/overtime/${id}/approve/`, payload).then((r) => unwrap(r));
export const rejectOvertimeRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/overtime/${id}/reject/`, payload).then((r) => unwrap(r));

export const fetchTeamWeeklyOffShuffleRequests = (params?: { status?: string }) =>
  api.get(`${BASE}/manager/week-off-shuffle/`, { params }).then((r) => unwrap<PaginatedResponse<WeeklyOffShuffleRequest>>(r));
export const approveWeeklyOffShuffleRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/week-off-shuffle/${id}/approve/`, payload).then((r) => unwrap(r));
export const rejectWeeklyOffShuffleRequest = (id: string, payload?: ActionRemarks) =>
  api.post(`${BASE}/manager/week-off-shuffle/${id}/reject/`, payload).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Leave Types (ViewSet)
// ─────────────────────────────────────────────────────────────────────────────

export const adminFetchLeaveTypes = () =>
  api.get(`${BASE}/admin/leave-types-v2/`).then((r) => unwrap<LeaveType[]>(r));

export const adminCreateLeaveType = (payload: LeaveTypePayload) =>
  api.post(`${BASE}/admin/leave-types-v2/`, payload).then((r) => unwrap<LeaveType>(r));

export const adminUpdateLeaveType = (id: string, payload: Partial<LeaveTypePayload>) =>
  api.put(`${BASE}/admin/leave-types-v2/${id}/`, payload).then((r) => unwrap<LeaveType>(r));

export const adminDeleteLeaveType = (id: string) =>
  api.delete(`${BASE}/admin/leave-types-v2/${id}/`).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Leave Mappings (ViewSet)
// ─────────────────────────────────────────────────────────────────────────────

export const fetchLeaveMappings = (params?: { role?: string }) =>
  api.get(`${BASE}/admin/leave-mappings/`, { params }).then((r) => unwrap<LeaveMapping[]>(r));

export const createLeaveMapping = (payload: LeaveMappingPayload) =>
  api.post(`${BASE}/admin/leave-mappings/`, payload).then((r) => unwrap<LeaveMapping>(r));

export const updateLeaveMapping = (id: string, payload: Partial<LeaveMappingPayload>) =>
  api.put(`${BASE}/admin/leave-mappings/${id}/`, payload).then((r) => unwrap<LeaveMapping>(r));

export const deleteLeaveMapping = (id: string) =>
  api.delete(`${BASE}/admin/leave-mappings/${id}/`).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Policies
// ─────────────────────────────────────────────────────────────────────────────

export const adminFetchPolicies = () =>
  api.get(`${BASE}/admin/policies`).then((r) => unwrap<LeavePolicy[]>(r));

export const adminCreatePolicy = (payload: LeavePolicyPayload) =>
  api.post(`${BASE}/admin/policies`, payload).then((r) => unwrap<LeavePolicy>(r));

export const adminUpdatePolicy = (id: string, payload: Partial<LeavePolicyPayload>) =>
  api.patch(`${BASE}/admin/policies/${id}/`, payload).then((r) => unwrap<LeavePolicy>(r));

export const adminAssignPolicy = (payload: { policy_id: string; employee_ids: string[] }) =>
  api.post(`${BASE}/admin/policies/assign`, payload).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Balances
// ─────────────────────────────────────────────────────────────────────────────

export const adminFetchLeaveBalances = (params?: { employee_id?: string; year?: number }) =>
  api.get(`${BASE}/admin/balances`, { params }).then((r) => unwrap<PaginatedResponse<LeaveBalance>>(r));

export const adminCreditLeaveBalance = (payload: { employee_id: string; leave_type_id: string; days: number; remarks?: string }) =>
  api.post(`${BASE}/admin/balances/credit`, payload).then((r) => unwrap(r));

export const adminDebitLeaveBalance = (payload: { employee_id: string; leave_type_id: string; days: number; remarks?: string }) =>
  api.post(`${BASE}/admin/balances/debit`, payload).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Applications
// ─────────────────────────────────────────────────────────────────────────────

export const adminFetchLeaveApplications = (params?: { employee_id?: string; status?: string; from_date?: string; to_date?: string }) =>
  api.get(`${BASE}/admin/applications`, { params }).then((r) => unwrap<PaginatedResponse<LeaveRequest>>(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Holidays
// ─────────────────────────────────────────────────────────────────────────────

export const adminFetchHolidays = (params?: { year?: number }) =>
  api.get(`${BASE}/admin/holidays`, { params }).then((r) => unwrap(r));

export interface CreateAdminHolidayPayload {
  date: string;
  name: string;
  type: "NATIONAL" | "RESTRICTED" | "OPTIONAL" | "COMPANY";
  branch_ids: string[];
}

export const adminCreateHoliday = (payload: CreateAdminHolidayPayload) =>
  api.post("/leave/admin/holidays", payload).then((r) => unwrap(r));

export const adminAssignHolidayGroup = (payload: unknown) =>
  api.post(`${BASE}/admin/holiday-groups/assign`, payload).then((r) => unwrap(r));

export const adminTriggerCarryForward = (payload: unknown) =>
  api.post(`${BASE}/admin/carry-forward`, payload).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Workflow Configuration
// ─────────────────────────────────────────────────────────────────────────────

export const fetchWorkflowConfig = () =>
  api.get(`${BASE}/workflow/config/`).then((r) => unwrap<ApprovalWorkflowConfig[]>(r));

export const updateWorkflowConfig = (payload: WorkflowConfigPayload) =>
  api.put(`${BASE}/workflow/config/`, payload).then((r) => unwrap<ApprovalWorkflowConfig>(r));

export const createWorkflowConfig = (payload: WorkflowConfigPayload) =>
  api.post(`${BASE}/workflow/config/create/`, payload).then((r) => unwrap<ApprovalWorkflowConfig>(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Bulk Approvals / Delegate
// ─────────────────────────────────────────────────────────────────────────────

export const bulkApproveLeave = (payload: { application_ids: string[]; action: "approve" | "reject"; remarks?: string }) =>
  api.post(`${BASE}/approvals/bulk-action/`, payload).then((r) => unwrap(r));

export const delegateApproval = (payload: { application_id: string; delegate_to_id: string; reason?: string }) =>
  api.post(`${BASE}/approvals/delegate/`, payload).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Reports & Analytics
// ─────────────────────────────────────────────────────────────────────────────

export const fetchLeaveSummaryReport = (params?: LeaveReportParams) =>
  api.get(`${BASE}/reports/leave-summary/`, { params }).then((r) => unwrap(r));

export const fetchLeaveEncashmentReport = (params?: LeaveReportParams) =>
  api.get(`${BASE}/reports/leave-encashment/`, { params }).then((r) => unwrap(r));

export const fetchApprovalTATReport = (params?: LeaveReportParams) =>
  api.get(`${BASE}/reports/approval-tat/`, { params }).then((r) => unwrap(r));

export const fetchLeavePatternAnalytics = (params?: LeaveReportParams) =>
  api.get(`${BASE}/analytics/leave-patterns/`, { params }).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Audit Logs & Notification Templates
// ─────────────────────────────────────────────────────────────────────────────

export const fetchAuditLogs = (params?: { page?: number; page_size?: number; model?: string }) =>
  api.get(`${BASE}/admin/audit-logs/`, { params }).then((r) => unwrap<PaginatedResponse<AuditLog>>(r));

export const fetchNotificationTemplates = () =>
  api.get(`${BASE}/admin/notification-templates/`).then((r) => unwrap<NotificationTemplate[]>(r));

export const updateNotificationTemplate = (id: string, payload: NotificationTemplatePayload) =>
  api.patch(`${BASE}/admin/notification-templates/${id}/`, payload).then((r) => unwrap<NotificationTemplate>(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Encashment
// ─────────────────────────────────────────────────────────────────────────────

export const processLeaveEncashment = (payload: { employee_id: string; leave_type_id: string; days: number }) =>
  api.post(`${BASE}/admin/leave-encashment/process/`, payload).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Accrual Schedules & Calendar Periods
// ─────────────────────────────────────────────────────────────────────────────

export const fetchAccrualSchedules = () =>
  api.get(`${BASE}/admin/accrual-schedules/`).then((r) => unwrap(r));

export const fetchCalendarPeriods = () =>
  api.get(`${BASE}/admin/calendar-periods/`).then((r) => unwrap(r));

export const createCalendarPeriod = (payload: unknown) =>
  api.post(`${BASE}/admin/calendar-periods/`, payload).then((r) => unwrap(r));

// ─────────────────────────────────────────────────────────────────────────────
// Admin — Weekends Config
// ─────────────────────────────────────────────────────────────────────────────

export const fetchWeekendsConfig = () =>
  api.get(`${BASE}/admin/weekends/config/`).then((r) => unwrap(r));

export const createWeekendsConfig = (payload: unknown) =>
  api.post(`${BASE}/admin/weekends/config/`, payload).then((r) => unwrap(r));

export const updateWeekendsConfig = (configId: string, payload: unknown) =>
  api.patch(`${BASE}/admin/weekends/config/${configId}/`, payload).then((r) => unwrap(r));
