import type { LeaveCategory, LeaveRequestStatus } from "../../modules/adminLeave/types";

export type FilterOption<Value extends string = string> = {
  value: Value;
  label: string;
};

export const LEAVE_CATEGORY_OPTIONS: FilterOption<LeaveCategory | "ALL">[] = [
  { value: "ALL", label: "All Categories" },
  { value: "LEAVE", label: "Casual Leave" },
  { value: "SICK_LEAVE", label: "Sick Leave" },
  { value: "EARNED_LEAVE", label: "Earned Leave" },
  { value: "COMP_OFF", label: "Comp Off" },
  { value: "WFH", label: "WFH" },
  { value: "OUT_DUTY", label: "Out Duty" },
  { value: "SHORT_LEAVE", label: "Short Leave" },
  { value: "GATE_PASS", label: "Gate Pass" },
  { value: "OVERTIME", label: "Overtime" },
  { value: "OPTIONAL_HOLIDAY", label: "Optional Holiday" },
];

export const LEAVE_STATUS_OPTIONS: FilterOption<LeaveRequestStatus | "ALL">[] = [
  { value: "ALL", label: "All Status" },
  { value: "DRAFT", label: "Draft" },
  { value: "SUBMITTED", label: "Submitted" },
  { value: "PENDING", label: "Pending" },
  { value: "APPROVED", label: "Approved" },
  { value: "REJECTED", label: "Rejected" },
  { value: "CANCELLED", label: "Cancelled" },
  { value: "REVOKED", label: "Revoked" },
];

export const STATUS_BADGE_STYLES: Record<string, string> = {
  APPROVED: "text-emerald-300 bg-emerald-500/10",
  REJECTED: "text-rose-300 bg-rose-500/10",
  PENDING: "text-amber-300 bg-amber-500/10",
  SUBMITTED: "text-slate-300 bg-slate-600/20",
  CANCELLED: "text-slate-300 bg-slate-600/20",
  REVOKED: "text-slate-300 bg-slate-600/20",
  DRAFT: "text-slate-300 bg-slate-600/20",
};

export const DEFAULT_ADVANCED_FILTERS = {
  dateFrom: "",
  dateTo: "",
  department: "ALL",
  employee: "ALL",
  workflowLevel: "ALL",
  payrollLock: "ALL",
  location: "ALL",
  businessUnit: "ALL",
  balanceImpact: "ALL",
  approvalSla: "ALL",
  escalationStatus: "ALL",
} as const;

export type AdvancedLeaveFilters = typeof DEFAULT_ADVANCED_FILTERS;
