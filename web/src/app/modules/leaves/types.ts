// ─────────────────────────────────────────────────────────────────────────────
// types.ts  –  Leave module shared types
// Aligned with Django REST serializers in leave_types.py, leave_balances.py,
// leave_requests.py, leave_holidays.py, leave_policies.py
// ─────────────────────────────────────────────────────────────────────────────

// ── Leave type (LeaveTypeSerializer) ─────────────────────────────────────────
export interface LeaveTypeRef {
  /** UUID – maps to leave_type_id in the serializer */
  id: string;
  code: string;
  name: string;
  /** max_days_per_year exposed as max_days */
  max_days: number;
  /** carry_forward_enabled exposed as carry_forward */
  carry_forward: boolean;
  /** Derived client-side from leave policy rules; not returned by the type
   *  endpoint directly but included when embedded inside balance rows */
  is_paid?: boolean;
  color_code?: string;
}

// ── Leave balance (EmployeeLeaveBalanceSerializer) ───────────────────────────
export interface LeaveBalanceAPI {
  /** leave_type.id */
  leave_type_id: string;
  /** leave_type.name */
  leave_type: string;
  /** allocated_days + carried_forward */
  opening: number;
  /** accrued_days */
  accrued: number;
  /** used_days */
  taken: number;
  /** total_available_balance */
  balance: number;
  year: number;

  // ── Extended fields returned by AdminLeaveBalanceSerializer (admin views) ──
  id?: string;
  employee_id?: string;
  allocated_days?: number;
  accrued_days?: number;
  carried_forward?: number;
  used_days?: number;
  pending_days?: number;
  encashed_days?: number;
  lapsed_days?: number;
  leave_year_start?: string;
  leave_year_end?: string;

  // ── Client-side convenience fields populated after fetch ─────────────────
  /** Populated client-side from leave type metadata */
  leave_type_detail?: LeaveTypeRef;
  /** period_start / period_end filled from leave_year_start / leave_year_end */
  period_start?: string;
  period_end?: string;
  /** Alias: balance */
  available?: number;
  /** Alias: taken */
  used?: number;
  /** Alias: pending_days */
  pending_approval?: number;
  /** Alias: opening + accrued */
  total_allocated?: number;
}

// ── Leave application status ──────────────────────────────────────────────────
export type LeaveApplicationStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "PENDING"
  | "APPROVED"
  | "REJECTED"
  | "CANCELLED"
  | "REVOKED"
  | "WITHDRAWN"
  | "ESCALATED"
  | "AUTO_APPROVED";

// ── Leave approval (LeaveApprovalSerializer) ──────────────────────────────────
export interface LeaveApprovalAPI {
  id: string;
  approval_level: number;
  status: string;
  remarks: string | null;
  approver_id: string;
  approver_name: string;
  actioned_at: string | null;
  created_at: string;
}

// ── Leave application summary (LeaveApplicationSummarySerializer) ─────────────
export interface LeaveApplicationAPI {
  id: string;
  /** leave_type.id */
  leave_type_id: string;
  /** leave_type.name  – exposed as "leave_type" in the serializer */
  leave_type_name: string;
  leave_type_code: string;
  from_date: string;
  to_date: string;
  from_session: "first_half" | "second_half";
  to_session: "first_half" | "second_half";
  total_days: number | string;
  /** Backend field name is leave_status (source="status") */
  leave_status: LeaveApplicationStatus;
  /** applied_at in the serializer */
  applied_at: string;

  // ── Detail fields (LeaveApplicationDetailSerializer) ─────────────────────
  reason?: string;
  /** status field from the full detail serializer */
  status?: LeaveApplicationStatus;
  approvals?: LeaveApprovalAPI[];

  // ── Client-side fields populated after fetch ──────────────────────────────
  /** Populated client-side from leave type lookup */
  leave_type_detail?: LeaveTypeRef;
  /** Legacy alias kept for component compatibility → maps to applied_at */
  applied_on?: string;
  /** Legacy alias kept for component compatibility → maps to leave_type_id */
  leave_type?: string;
  employee_code?: string;
  employee_name?: string;
  approved_at?: string | null;
  contact_number?: string;
  mode_of_work?: string | null;
  notify_team?: boolean;
  documents?: Array<{
    id: string;
    file_name: string;
    file_url: string;
    file_type?: string | null;
    file_size_kb?: number | null;
    uploaded_by?: string;
    uploaded_at?: string;
  }>;
  leave_days?: Array<{
    id: string;
    leave_date: string;
    session: "first_half" | "second_half";
    day_value: string;
    is_weekend: boolean;
    is_holiday: boolean;
    is_counted: boolean;
  }>;
  is_half_day?: boolean;
}

// ── Create payload (LeaveApplicationCreateSerializer) ─────────────────────────
export interface ApplyLeavePayload {
  /** UUID of the leave type */
  leave_type_id: string;
  from_date: string;
  to_date: string;
  reason?: string;
  /** Backend uses is_half_day (bool) – no from_half / to_half fields */
  is_half_day: boolean;
}

// ── Update payload (LeaveApplicationUpdateSerializer) ─────────────────────────
export interface UpdateLeavePayload {
  leave_type_id?: string;
  from_date?: string;
  to_date?: string;
  is_half_day?: boolean;
  reason?: string;
}

// ── Cancel payload (LeaveApplicationCancelSerializer) ─────────────────────────
export interface CancelLeavePayload {
  reason: string;
}

// ── Holiday (AdminHolidayListItemSerializer / HolidayCalendarSerializer) ───────
export interface HolidayAPI {
  id: string;
  name: string;
  /** ISO date string YYYY-MM-DD */
  date: string;
  /** Maps to holiday_type */
  holiday_type: string;
  is_optional: boolean;
  is_active?: boolean;
  holiday_calendar_id?: string;
}

// ── Leave balance summary (aggregated on client from balance rows) ─────────────
export interface LeaveBalanceSummaryAPI {
  employee_id: string;
  total_allocated: number;
  total_accrued: number;
  total_available: number;
  total_used: number;
  total_pending: number;
  balances: LeaveBalanceAPI[];
}