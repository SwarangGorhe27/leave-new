export type LeaveDuration = "FULL" | "HALF" | "HOURLY";

export type PayrollLockStatus = "Unlocked" | "Locked";
export type LeavePriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type LeaveCategory = "LEAVE" | "COMP_OFF" | "SHORT_LEAVE" | "OUT_DUTY" | "WFH" | "GATE_PASS" | "OVERTIME";
export type AdminActorRole = "employee" | "manager" | "HR" | "admin" | "superadmin";

export type LeaveRequestStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "APPROVED"
  | "PENDING"
  | "REJECTED"
  | "CANCELLED"
  | "REVOKED";

export interface AdminLeaveEmployeeRef {
  employee_code: string;
  employee_name: string;
  department: string;
  designation?: string;
  avatarColor?: string;
  initials?: string;
}

export interface AdminLeaveTypeRef {
  id: string;
  code: string;
  name: string;
  color_code?: string;
  is_paid: boolean;
  is_active: boolean;
}

export interface LeaveApprovalStep {
  level: number;
  approver: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "SKIPPED";
  acted_at?: string;
  remarks?: string;
}

export interface LeaveComment {
  id: string;
  author: string;
  created_at: string;
  message: string;
}

export interface LeaveAttachment {
  id: string;
  name: string;
  url: string;
  type: "pdf" | "image" | "link";
}

export interface LeaveAuditEvent {
  id: string;
  at: string;
  actor: string;
  actor_role?: AdminActorRole;
  action: string;
  meta?: string;
  previous_value?: string;
  new_value?: string;
  ip_address?: string;
  device_info?: string;
}

export interface LeaveLedgerImpactLine {
  id: string;
  leave_type_code: string;
  effect: "DEBIT" | "CREDIT";
  days: number;
  note?: string;
}

export interface AdminLeaveRequestRow {
  id: string;
  employee: AdminLeaveEmployeeRef;
  leave_type: AdminLeaveTypeRef;
  from_date: string;
  to_date: string;
  total_days: number;
  duration: LeaveDuration;
  applied_on: string;
  reason: string;
  backup_employee?: string;
  status: LeaveRequestStatus;
  priority?: LeavePriority;
  workflow_stage?: string;
  category?: LeaveCategory;
  current_approver?: string;
  payroll_lock: PayrollLockStatus;
  workflow_level: number;
  deleted_at?: string | null;

  approval_history: LeaveApprovalStep[];
  comments: LeaveComment[];
  attachments: LeaveAttachment[];
  audit: LeaveAuditEvent[];
  ledger_impact: LeaveLedgerImpactLine[];
}

export interface LeaveTypeMasterRecord extends AdminLeaveTypeRef {
  description?: string;
  color_code?: string;
  max_yearly_allocation: number;
  carry_forward: boolean;
  encashment: boolean;
  attachment_required: boolean;
  gender_applicability: "ALL" | "MALE" | "FEMALE" | "OTHER";
  half_day_support: boolean;
  hourly_leave_support: boolean;
  clubbing_restrictions?: string;
  future_apply_caps_days?: number;
  backdate_limits_days?: number;
  leave_year_type: "CALENDAR" | "FINANCIAL";
}

