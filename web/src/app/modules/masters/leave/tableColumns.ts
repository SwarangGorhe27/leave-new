import type { MasterTableColumnConfig } from "../types";

export const STANDARD_LEAVE_COLUMNS: MasterTableColumnConfig[] = [
  { key: "code", label: "Code", sortable: true, render: "code" },
  { key: "label", label: "Name / Label", sortable: true, render: "label", altKeys: ["name"] },
  { key: "is_active", label: "Status", sortable: true, render: "status" },
  { key: "updated_at", label: "Updated At", sortable: true, render: "datetime" },
];

export const LEAVE_POLICY_COLUMNS: MasterTableColumnConfig[] = [
  { key: "name", label: "Name", sortable: true, render: "label" },
  { key: "version", label: "Version", sortable: true },
  { key: "effective_from", label: "Effective From", sortable: true },
  { key: "is_active", label: "Status", sortable: true, render: "status" },
  { key: "updated_at", label: "Updated At", sortable: true, render: "datetime" },
];

export const LEAVE_POLICY_RULE_COLUMNS: MasterTableColumnConfig[] = [
  { key: "policy", label: "Policy", sortable: true },
  { key: "leave_type", label: "Leave Type", sortable: true },
  { key: "employee_type", label: "Employee Type", sortable: true },
  { key: "updated_at", label: "Updated At", sortable: true, render: "datetime" },
];

export const LEAVE_ENCASHMENT_POLICY_COLUMNS: MasterTableColumnConfig[] = [
  { key: "leave_type", label: "Leave Type", sortable: true },
  { key: "formula_basis", label: "Formula Basis", sortable: true },
  { key: "payout_timing", label: "Payout Timing", sortable: true },
  { key: "is_active", label: "Status", sortable: true, render: "status" },
  { key: "updated_at", label: "Updated At", sortable: true, render: "datetime" },
];

export const CALENDAR_PERIOD_COLUMNS: MasterTableColumnConfig[] = [
  { key: "period_type", label: "Period Type", sortable: true },
  { key: "year_start_month", label: "Start Month", sortable: true },
  { key: "year_start_day", label: "Start Day", sortable: true },
  { key: "encashment_cycle", label: "Encashment Cycle", sortable: true },
  { key: "is_active", label: "Active Status", sortable: true, render: "status" },
  { key: "updated_at", label: "Updated At", sortable: true, render: "datetime" },
];

export const ACCRUAL_SCHEDULE_COLUMNS: MasterTableColumnConfig[] = [
  { key: "policy_rule", label: "Policy Rule", sortable: true },
  { key: "frequency", label: "Frequency", sortable: true },
  { key: "run_day_of_month", label: "Run Day", sortable: true },
  { key: "run_month", label: "Run Month", sortable: true },
  { key: "proration_on_join", label: "Proration Enabled", sortable: true, render: "boolean" },
  { key: "rounding_rule", label: "Rounding Rule", sortable: true },
  { key: "is_active", label: "Active Status", sortable: true, render: "status" },
  { key: "updated_at", label: "Updated At", sortable: true, render: "datetime" },
];
