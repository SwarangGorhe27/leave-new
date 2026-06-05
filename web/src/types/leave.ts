// ─────────────────────────────────────────────────────────────────────────────
// Enums
// ─────────────────────────────────────────────────────────────────────────────

export enum LeaveStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
  CANCELLED = "cancelled",
}

export enum LeaveSession {
  FIRST_HALF = "first_half",
  SECOND_HALF = "second_half",
}

export enum WFHLocationType {
  HOME = "home",
  CLIENT_SITE = "client_site",
  CO_WORKING = "co_working",
}

export enum CompOffType {
  FULL_DAY = "full_day",
  HALF_DAY = "half_day",
}

export enum EarnedAgainstType {
  HOLIDAY = "holiday",
  WEEKEND = "weekend",
  OVERTIME = "overtime",
}

export enum GatePassMovementType {
  WITHIN_OFFICE = "within_office",
  OUTSIDE_OFFICE = "outside_office",
  CLIENT_LOCATION = "client_location",
}

export enum GatePassPassType {
  START_OF_DAY = "start_of_day",
  END_OF_DAY = "end_of_day",
  DURING_SHIFT = "during_shift",
}

export enum OutDutyTravelMode {
  OWN = "own",
  COMPANY_VEHICLE = "company_vehicle",
  PUBLIC = "public",
  AIR = "air",
}

export enum ShortLeaveTimeSlot {
  DAY_IN = "day_in",
  DAY_OUT = "day_out",
  IN_BETWEEN = "in_between",
}

export enum ApproverType {
  REPORTING_MANAGER = "REPORTING_MANAGER",
  SPECIFIC_USER = "SPECIFIC_USER",
  HR = "HR",
  DEPARTMENT_HEAD = "DEPARTMENT_HEAD",
}

export enum LedgerTransactionType {
  PENDING_APPLICATION = "pending_application",
  ALLOCATION = "allocation",
  OPENING_BALANCE = "opening_balance",
  ACCRUAL = "accrual",
  USAGE = "usage",
  CARRY_FORWARD = "carry_forward",
  ENCASHMENT = "encashment",
  LAPSE = "lapse",
  ADJUSTMENT = "adjustment",
  REVERSAL = "reversal",
}

// ─────────────────────────────────────────────────────────────────────────────
// Masters
// ─────────────────────────────────────────────────────────────────────────────

export interface LeaveType {
  id: string;
  name: string;
  code: string;
  leave_name?: string;
  max_days_per_year?: number;
  carry_forward?: boolean;
  max_carry_forward_days?: number;
  is_paid?: boolean;
  requires_document?: boolean;
  is_active: boolean;
}

export interface LeaveTypePayload {
  name: string;
  code: string;
  max_days_per_year?: number;
  carry_forward?: boolean;
  is_active?: boolean;
}

export interface LeaveMapping {
  id: string;
  role: string;
  leave_type: LeaveType;
  allowed_days: number;
}

export interface LeaveMappingPayload {
  role: string;
  leave_type_id: string;
  allowed_days: number;
}

export interface LeavePolicy {
  id: string;
  name: string;
  description?: string;
  leave_type?: LeaveType;
  applicable_roles?: string;
  days_per_year?: number;
  carry_forward_days?: number;
  max_consecutive_days?: number | null;
  min_notice_days?: number;
  allow_half_day?: boolean;
  allow_negative_balance?: boolean;
  is_active: boolean;
  effective_from: string;
  effective_to?: string | null;
}

export interface LeavePolicyPayload {
  name: string;
  leave_type_id?: string;
  applicable_roles?: string;
  days_per_year?: number;
  carry_forward_days?: number;
  max_consecutive_days?: number | null;
  min_notice_days?: number;
  allow_half_day?: boolean;
  allow_negative_balance?: boolean;
  effective_from: string;
  effective_to?: string | null;
}

export interface ApprovalWorkflowConfig {
  id: string;
  module?: string;
  workflow_name?: string;
  leave_type?: LeaveType;
  level?: number;
  approver_type?: ApproverType;
  specific_user?: string | null;
  sla_hours: number;
  is_active: boolean;
  steps?: WorkflowStep[];
}

export interface WorkflowStep {
  level: number;
  approver_type: string;
  approver_id: string | null;
  fallback_type?: string;
  sla_hours: number;
  auto_approve_on_timeout: boolean;
}

export interface WorkflowConfigPayload {
  module?: string;
  workflow_name?: string;
  leave_type_id?: string;
  level?: number;
  approver_type?: ApproverType;
  specific_user_id?: string | null;
  sla_hours?: number;
  steps?: WorkflowStep[];
}

// ─────────────────────────────────────────────────────────────────────────────
// Leave Balance & Ledger
// ─────────────────────────────────────────────────────────────────────────────

export interface LeaveBalance {
  id: string;
  leave_type: LeaveType;
  year: number;
  allocated_days: number;
  accrued_days: number;
  carried_forward: number;
  used_days: number;
  pending_days: number;
  encashed_days: number;
  lapsed_days: number;
  available_days: number;
  leave_year_start?: string;
  leave_year_end?: string;
}

export interface LeaveBalanceProjection {
  current_balance: number;
  projected_balance: number;
}

export interface LeaveBalanceLedgerEntry {
  id: string;
  transaction_type: LedgerTransactionType;
  days: number;
  balance_before: number;
  balance_after: number;
  remarks?: string;
  created_at: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Leave Request
// ─────────────────────────────────────────────────────────────────────────────

export interface LeaveApproval {
  id: string;
  approval_level: number;
  status: string;
  remarks?: string;
  approver_id: string;
  approver_name: string;
  actioned_at?: string;
  actioned_on?: string;
  created_at: string;
}

export interface LeaveRequest {
  id: string;
  employee?: string;
  leave_type_id?: string;
  leave_type: string;
  leave_type_code?: string;
  from_date: string;
  to_date: string;
  from_session?: LeaveSession;
  to_session?: LeaveSession;
  total_days: number;
  leave_year?: number;
  reason?: string;
  contact_number?: string;
  mode_of_work?: string;
  notify_team?: boolean;
  leave_status: LeaveStatus;
  status?: LeaveStatus;
  applied_at: string;
  approvals?: LeaveApproval[];
}

export interface LeaveRequestPayload {
  leave_type_id: string;
  from_date: string;
  to_date: string;
  from_session?: LeaveSession;
  to_session?: LeaveSession;
  reason?: string;
  contact_during_leave?: string;
}

export interface LeaveRequestUpdatePayload {
  leave_type_id?: string;
  from_date?: string;
  to_date?: string;
  from_session?: LeaveSession;
  to_session?: LeaveSession;
  reason?: string;
  contact_number?: string;
}

export interface LeaveStatusHistory {
  id: string;
  from_status?: string;
  to_status: string;
  old_status?: string;
  new_status?: string;
  changed_by?: string;
  remarks?: string;
  changed_at: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Other Request Types
// ─────────────────────────────────────────────────────────────────────────────

export interface WFHRequest {
  id: string;
  employee_id?: string;
  employee_name?: string;
  from_date: string;
  to_date: string;
  total_days: number;
  work_location_type: WFHLocationType;
  vpn_confirmed: boolean;
  connectivity_confirmed: boolean;
  reason?: string;
  status: LeaveStatus;
  actioned_at?: string;
  created_at: string;
}

export interface WFHRequestPayload {
  from_date: string;
  to_date: string;
  total_days: number;
  work_location_type: WFHLocationType;
  vpn_confirmed?: boolean;
  connectivity_confirmed?: boolean;
  reason?: string;
}

export interface CompOffRequest {
  id: string;
  employee_id?: string;
  employee_name?: string;
  worked_date: string;
  comp_off_type: CompOffType;
  earned_against_date_type: EarnedAgainstType;
  earned_days: number;
  used_days: number;
  expiry_date?: string | null;
  reason?: string;
  status: string;
  actioned_at?: string;
  created_at: string;
}

export interface CompOffRequestPayload {
  worked_date: string;
  comp_off_type: CompOffType;
  earned_against_date_type: EarnedAgainstType;
  earned_days?: number;
  expiry_date?: string | null;
  reason?: string;
  proof_url?: string;
}

export interface GatePassRequest {
  id: string;
  employee_id?: string;
  employee_name?: string;
  request_date?: string;
  purpose: string;
  movement_type: GatePassMovementType;
  pass_type: GatePassPassType;
  from_location?: string;
  to_location?: string;
  start_time: string;
  expected_return_time?: string | null;
  actual_departure_time?: string | null;
  actual_return_time?: string | null;
  duration_minutes: number;
  reason?: string;
  status: string;
  actioned_at?: string;
  created_at: string;
}

export interface GatePassRequestPayload {
  purpose: string;
  purpose_type_id: string;
  movement_type: GatePassMovementType;
  pass_type: GatePassPassType;
  from_location?: string;
  to_location?: string;
  start_time: string;
  expected_return_time?: string | null;
  duration_minutes: number;
  reason?: string;
}

export interface OutDutyRequest {
  id: string;
  employee_id?: string;
  employee_name?: string;
  from_date: string;
  to_date: string;
  actual_return_date?: string | null;
  from_location?: string;
  to_location?: string;
  reason?: string;
  travel_mode?: OutDutyTravelMode | null;
  status: string;
  advance_approved?: boolean;
  travel_expense_submitted?: boolean;
  actioned_at?: string;
  created_at: string;
}

export interface OutDutyRequestPayload {
  from_date: string;
  to_date: string;
  from_location?: string;
  to_location?: string;
  purpose_type_id: string;
  reason?: string;
  travel_mode?: OutDutyTravelMode | null;
  cc_manager_id?: string | null;
  advance_amount?: number | null;
}

export interface ShortLeaveRequest {
  id: string;
  employee_id?: string;
  employee_name?: string;
  leave_date: string;
  time_slot: ShortLeaveTimeSlot;
  start_time?: string | null;
  end_time?: string | null;
  duration_hours: number;
  reason?: string;
  status: string;
  actioned_at?: string;
  created_at: string;
}

export interface ShortLeaveRequestPayload {
  policy_id: string;
  leave_date: string;
  time_slot: ShortLeaveTimeSlot;
  start_time?: string | null;
  end_time?: string | null;
  duration_hours: number;
  reason?: string;
}

export interface OvertimeRequest {
  id: string;
  employee_id?: string;
  employee_name?: string;
  ot_date: string;
  ot_hours: number;
  reason?: string;
  grant_comp_off?: boolean;
  status: string;
  actioned_at?: string;
  created_at: string;
}

export interface OvertimeRequestPayload {
  ot_date: string;
  ot_hours: number;
  reason?: string;
  grant_comp_off?: boolean;
}

export interface WeeklyOffShuffleRequest {
  id: string;
  employee_id?: string;
  employee_name?: string;
  week_start_date: string;
  current_off_date: string;
  requested_off_date: string;
  reason?: string;
  impact_on_shift?: string;
  status: string;
  actioned_at?: string;
  created_at: string;
}

export interface WeeklyOffShufflePayload {
  week_start_date: string;
  current_off_date: string;
  requested_off_date: string;
  reason?: string;
  impact_on_shift?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Admin / Reports
// ─────────────────────────────────────────────────────────────────────────────

export interface LeaveReportParams {
  from_date?: string;
  to_date?: string;
  department_id?: string;
  employee_id?: string;
  leave_type_id?: string;
  page?: number;
  page_size?: number;
}

export interface AuditLog {
  id: string;
  action: string;
  model: string;
  object_id?: string;
  changes?: Record<string, unknown>;
  performed_by?: string;
  created_at: string;
}

export interface NotificationTemplate {
  id: string;
  event_type: string;
  channel: string;
  subject?: string;
  body: string;
  is_active: boolean;
}

export interface NotificationTemplatePayload {
  subject?: string;
  body: string;
  is_active?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Paginated response wrapper
// ─────────────────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

export interface ActionRemarks {
  remarks?: string;
}
