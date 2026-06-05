import type { MasterFieldConfig } from "../types";
import {
  ACCRUAL_SCHEDULE_FREQUENCY_OPTIONS,
  ACCRUAL_SCHEDULE_ROUNDING_OPTIONS,
  ENCASHMENT_CYCLE_OPTIONS,
  MONTH_OPTIONS,
  PERIOD_TYPE_OPTIONS,
} from "./constants";

const GENDER_OPTIONS = [
  { value: "MALE", label: "Male" },
  { value: "FEMALE", label: "Female" },
  { value: "ALL", label: "All" },
];

const LEAVE_YEAR_OPTIONS = [
  { value: "CALENDAR", label: "Calendar" },
  { value: "FISCAL", label: "Fiscal" },
  { value: "CUSTOM", label: "Custom" },
];

const ACCRUAL_FREQUENCY_OPTIONS = [
  { value: "MONTHLY", label: "Monthly" },
  { value: "QUARTERLY", label: "Quarterly" },
  { value: "ANNUAL", label: "Annual" },
];

const ACCRUAL_PRORATION_OPTIONS = [
  { value: "CALENDAR_DAYS", label: "Calendar Days" },
  { value: "WORKING_DAYS", label: "Working Days" },
];

const ROUNDING_RULE_OPTIONS = [
  { value: "FLOOR", label: "Floor" },
  { value: "CEIL", label: "Ceil" },
  { value: "ROUND", label: "Round" },
];

const FORMULA_BASIS_OPTIONS = [
  { value: "BASIC_SALARY", label: "Basic Salary" },
  { value: "GROSS_SALARY", label: "Gross Salary" },
  { value: "CTC", label: "CTC" },
];

const PAYOUT_TIMING_OPTIONS = [
  { value: "ANNUAL", label: "Annual" },
  { value: "ON_EXIT", label: "On Exit" },
  { value: "CUSTOM", label: "Custom" },
];

const TAX_TREATMENT_OPTIONS = [
  { value: "TAXABLE", label: "Taxable" },
  { value: "EXEMPT", label: "Exempt" },
  { value: "PARTIAL_EXEMPT", label: "Partial Exempt" },
];

const MODULE_OPTIONS = [
  { value: "LEAVE", label: "Leave" },
  { value: "GATE_PASS", label: "Gate Pass" },
  { value: "OUT_DUTY", label: "Out Duty" },
  { value: "REGULARIZATION", label: "Regularization" },
  { value: "COMP_OFF", label: "Comp Off" },
];

export const LEAVE_TYPE_FIELDS: MasterFieldConfig[] = [
  { key: "code", label: "Code", type: "text", required: true, section: "Basic Information", placeholder: "Enter code" },
  { key: "name", label: "Name", type: "text", required: true, section: "Basic Information", placeholder: "Enter name" },
  { key: "color_code", label: "Color", type: "color", section: "Basic Information", placeholder: "Select color" },
  { key: "employee_type", label: "Employee Type", type: "select", relationMaster: "EmployeeType", section: "Basic Information" },
  { key: "description", label: "Description", type: "textarea", section: "Basic Information", placeholder: "Enter description" },
  { key: "max_days_per_year", label: "Max Days Per Year", type: "number", required: true, min: 1, section: "Leave Limits" },
  { key: "max_consecutive_days", label: "Max Consecutive Days", type: "number", min: 1, section: "Leave Limits" },
  { key: "carry_forward_enabled", label: "Carry Forward Enabled", type: "boolean", defaultValue: false, section: "Carry Forward" },
  {
    key: "max_carry_forward_days",
    label: "Max Carry Forward Days",
    type: "number",
    min: 0,
    section: "Carry Forward",
    disabledWhen: { field: "carry_forward_enabled", equals: false },
  },
  { key: "encashable", label: "Encashable", type: "boolean", defaultValue: false, section: "Encashment" },
  { key: "requires_attachment", label: "Requires Attachment", type: "boolean", defaultValue: false, section: "Attachment Rules" },
  {
    key: "attachment_threshold_days",
    label: "Attachment Threshold Days",
    type: "number",
    min: 0,
    section: "Attachment Rules",
    disabledWhen: { field: "requires_attachment", equals: false },
  },
  { key: "min_notice_days", label: "Min Notice Days", type: "number", min: 0, section: "Application Rules" },
  { key: "applicable_gender", label: "Applicable Gender", type: "select", options: GENDER_OPTIONS, section: "Application Rules", defaultValue: "ALL" },
  { key: "has_expiry", label: "Has Expiry", type: "boolean", defaultValue: false, section: "Application Rules" },
  {
    key: "expiry_days",
    label: "Expiry Days",
    type: "number",
    min: 1,
    section: "Application Rules",
    disabledWhen: { field: "has_expiry", equals: false },
  },
  { key: "is_paid", label: "Is Paid", type: "boolean", defaultValue: true, section: "Application Rules" },
  { key: "allow_half_day", label: "Allow Half Day", type: "boolean", defaultValue: false, section: "Application Rules" },
  { key: "allow_hourly", label: "Allow Hourly", type: "boolean", defaultValue: false, section: "Application Rules" },
  { key: "is_clubbing_allowed", label: "Is Clubbing Allowed", type: "boolean", defaultValue: false, section: "Clubbing Rules" },
  {
    key: "clubbing_restricted_with",
    label: "Clubbing Restricted With",
    type: "multiselect",
    relationMaster: "LeaveType",
    section: "Clubbing Rules",
    disabledWhen: { field: "is_clubbing_allowed", equals: false },
  },
  { key: "backdate_allowed_days", label: "Backdate Allowed Days", type: "number", min: 0, section: "Backdate / Future Apply" },
  { key: "future_apply_cap_days", label: "Future Apply Cap Days", type: "number", min: 0, section: "Backdate / Future Apply" },
  { key: "leave_year_type", label: "Leave Year Type", type: "select", options: LEAVE_YEAR_OPTIONS, section: "Leave Year", defaultValue: "CALENDAR" },
  { key: "is_active", label: "Active", type: "boolean", defaultValue: true, section: "System" },
];

export const LEAVE_POLICY_FIELDS: MasterFieldConfig[] = [
  { key: "name", label: "Name", type: "text", required: true, placeholder: "Enter policy name" },
  { key: "description", label: "Description", type: "textarea", placeholder: "Enter description" },
  { key: "effective_from", label: "Effective From", type: "date", required: true },
  { key: "effective_to", label: "Effective To", type: "date" },
  { key: "version", label: "Version", type: "text", placeholder: "e.g. 1.0" },
  { key: "is_active", label: "Active", type: "boolean", defaultValue: true },
  { key: "created_at", label: "Created At", type: "text", readOnly: true, section: "Metadata" },
  { key: "updated_at", label: "Updated At", type: "text", readOnly: true, section: "Metadata" },
  { key: "created_by", label: "Created By", type: "text", readOnly: true, section: "Metadata" },
  { key: "updated_by", label: "Updated By", type: "text", readOnly: true, section: "Metadata" },
];

export const LEAVE_POLICY_RULE_FIELDS: MasterFieldConfig[] = [
  { key: "policy", label: "Policy", type: "select", relationMaster: "LeavePolicy", required: true },
  { key: "leave_type", label: "Leave Type", type: "select", relationMaster: "LeaveType", required: true },
  { key: "probation_restricted", label: "Probation Restricted", type: "boolean", defaultValue: false },
  { key: "notice_period_restricted", label: "Notice Period Restricted", type: "boolean", defaultValue: false },
  { key: "grade", label: "Grade", type: "select", relationMaster: "Grade" },
  { key: "employee_type", label: "Employee Type", type: "select", relationMaster: "EmployeeType" },
  { key: "accrual_frequency", label: "Accrual Frequency", type: "select", options: ACCRUAL_FREQUENCY_OPTIONS, section: "Additional Rule Config" },
  { key: "accrual_proration_basis", label: "Accrual Proration Basis", type: "select", options: ACCRUAL_PRORATION_OPTIONS, section: "Additional Rule Config" },
  { key: "rounding_rule", label: "Rounding Rule", type: "select", options: ROUNDING_RULE_OPTIONS, section: "Additional Rule Config" },
];

export const LEAVE_ENCASHMENT_POLICY_FIELDS: MasterFieldConfig[] = [
  { key: "leave_type", label: "Leave Type", type: "select", relationMaster: "LeaveType", required: true, section: "Policy Mapping" },
  { key: "formula_basis", label: "Formula Basis", type: "select", options: FORMULA_BASIS_OPTIONS, required: true, section: "Formula" },
  { key: "working_days_divisor", label: "Working Days Divisor", type: "number", min: 1, defaultValue: 26, section: "Formula" },
  { key: "max_encashable_days_per_year", label: "Max Encashable Days Per Year", type: "number", min: 0, section: "Limits" },
  { key: "min_balance_to_retain", label: "Min Balance To Retain", type: "number", min: 0, section: "Limits" },
  { key: "payout_timing", label: "Payout Timing", type: "select", options: PAYOUT_TIMING_OPTIONS, section: "Processing" },
  { key: "tax_treatment", label: "Tax Treatment", type: "select", options: TAX_TREATMENT_OPTIONS, section: "Processing" },
  { key: "is_active", label: "Active", type: "boolean", defaultValue: true, section: "Flags" },
];

export const LEAVE_REASON_FIELDS: MasterFieldConfig[] = [
  { key: "module", label: "Module", type: "select", options: MODULE_OPTIONS, required: true },
  { key: "code", label: "Code", type: "text", required: true, placeholder: "Enter code" },
  { key: "label", label: "Label", type: "text", required: true, placeholder: "Enter label" },
  { key: "is_active", label: "Active", type: "boolean", defaultValue: true },
];

export const CALENDAR_PERIOD_FIELDS: MasterFieldConfig[] = [
  { key: "period_type", label: "Period Type", type: "select", options: PERIOD_TYPE_OPTIONS, required: true, section: "Basic Configuration" },
  {
    key: "year_start_month",
    label: "Year Start Month",
    type: "select",
    options: MONTH_OPTIONS,
    required: true,
    section: "Basic Configuration",
    disabledWhen: { field: "period_type", equals: "CALENDAR" },
  },
  {
    key: "year_start_day",
    label: "Year Start Day",
    type: "number",
    required: true,
    min: 1,
    max: 31,
    section: "Basic Configuration",
    disabledWhen: { field: "period_type", equals: "CALENDAR" },
  },
  { key: "cf_reset_date", label: "CF Reset Date", type: "date", section: "Carry Forward" },
  { key: "accrual_start_month", label: "Accrual Start Month", type: "select", options: MONTH_OPTIONS, section: "Accrual" },
  { key: "encashment_cycle", label: "Encashment Cycle", type: "select", options: ENCASHMENT_CYCLE_OPTIONS, section: "Encashment" },
  { key: "is_active", label: "Active", type: "boolean", defaultValue: true, section: "System" },
  { key: "version", label: "Version", type: "text", section: "Metadata" },
  { key: "created_at", label: "Created At", type: "text", readOnly: true, section: "Metadata" },
  { key: "updated_at", label: "Updated At", type: "text", readOnly: true, section: "Metadata" },
];

export const ACCRUAL_SCHEDULE_FIELDS: MasterFieldConfig[] = [
  { key: "policy_rule", label: "Policy Rule", type: "select", relationMaster: "LeavePolicyRule", required: true, section: "Policy Mapping" },
  { key: "frequency", label: "Frequency", type: "select", options: ACCRUAL_SCHEDULE_FREQUENCY_OPTIONS, required: true, section: "Schedule Configuration" },
  { key: "run_day_of_month", label: "Run Day Of Month", type: "number", required: true, min: 1, max: 31, section: "Schedule Configuration" },
  {
    key: "run_month",
    label: "Run Month",
    type: "select",
    options: MONTH_OPTIONS,
    section: "Schedule Configuration",
    disabledWhen: { field: "frequency", equals: "MONTHLY" },
  },
  { key: "proration_on_join", label: "Proration On Join", type: "boolean", defaultValue: false, section: "Proration" },
  { key: "rounding_rule", label: "Rounding Rule", type: "select", options: ACCRUAL_SCHEDULE_ROUNDING_OPTIONS, required: true, section: "Rounding" },
  { key: "is_active", label: "Active", type: "boolean", defaultValue: true, section: "System" },
  { key: "version", label: "Version", type: "text", section: "Metadata" },
  { key: "created_at", label: "Created At", type: "text", readOnly: true, section: "Metadata" },
  { key: "updated_at", label: "Updated At", type: "text", readOnly: true, section: "Metadata" },
];
