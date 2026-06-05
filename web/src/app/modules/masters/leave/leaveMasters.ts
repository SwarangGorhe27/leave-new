import type { MasterCategoryConfig, MasterConfig } from "../types";
import {
  ACCRUAL_SCHEDULE_FIELDS,
  CALENDAR_PERIOD_FIELDS,
  LEAVE_ENCASHMENT_POLICY_FIELDS,
  LEAVE_POLICY_FIELDS,
  LEAVE_POLICY_RULE_FIELDS,
  LEAVE_REASON_FIELDS,
  LEAVE_TYPE_FIELDS,
} from "./fieldSchemas";
import {
  ACCRUAL_SCHEDULE_DEFAULTS,
  CALENDAR_PERIOD_DEFAULTS,
  CALENDAR_PERIOD_FORM_BEHAVIORS,
  LEAVE_ENCASHMENT_POLICY_DEFAULTS,
  LEAVE_POLICY_DEFAULTS,
  LEAVE_POLICY_RULE_DEFAULTS,
  LEAVE_REASON_DEFAULTS, 
  LEAVE_TYPE_DEFAULTS,
} from "./defaults";
import {
  accrualScheduleValidationSchema,
  calendarPeriodValidationSchema,                     
  leaveEncashmentPolicyValidationSchema,
  leavePolicyRuleValidationSchema,
  leavePolicyValidationSchema,
  leaveReasonValidationSchema,
  leaveTypeValidationSchema,
} from "./schemas";
import {
  ACCRUAL_SCHEDULE_COLUMNS,
  CALENDAR_PERIOD_COLUMNS,
  LEAVE_ENCASHMENT_POLICY_COLUMNS,
  LEAVE_POLICY_COLUMNS,
  LEAVE_POLICY_RULE_COLUMNS,
  STANDARD_LEAVE_COLUMNS,
} from "./tableColumns";

const LEAVE_CATEGORY_KEY = "leave";

function leaveMaster(config: Omit<MasterConfig, "category" | "categoryKey">): MasterConfig {
  return {
    ...config,
    category: LEAVE_CATEGORY_KEY,
    categoryKey: LEAVE_CATEGORY_KEY,
    categoryLabel: "Leave Masters",
  };
}

export const LEAVE_MASTER_CONFIGS: MasterConfig[] = [
  leaveMaster({
    key: "leave-type",
    apiName: "LeaveType",
    label: "Leave Types",
    formFields: LEAVE_TYPE_FIELDS,
    defaultValues: LEAVE_TYPE_DEFAULTS,
    validationSchema: leaveTypeValidationSchema,
    listColumns: STANDARD_LEAVE_COLUMNS,
    searchPlaceholder: "Search by code or name",
  }),
  leaveMaster({
    key: "leave-policy",
    apiName: "LeavePolicy",
    label: "Leave Policies",
    formFields: LEAVE_POLICY_FIELDS,
    defaultValues: LEAVE_POLICY_DEFAULTS,
    validationSchema: leavePolicyValidationSchema,
    listColumns: LEAVE_POLICY_COLUMNS,
    searchPlaceholder: "Search by policy name",
  }),
  leaveMaster({
    key: "leave-policy-rule",
    apiName: "LeavePolicyRule",
    label: "Leave Policy Rules",
    formFields: LEAVE_POLICY_RULE_FIELDS,
    defaultValues: LEAVE_POLICY_RULE_DEFAULTS,
    validationSchema: leavePolicyRuleValidationSchema,
    listColumns: LEAVE_POLICY_RULE_COLUMNS,
    searchPlaceholder: "Search policy rules",
  }),
  leaveMaster({
    key: "leave-encashment-policy",
    apiName: "LeaveEncashmentPolicy",
    label: "Leave Encashment Policies",
    formFields: LEAVE_ENCASHMENT_POLICY_FIELDS,
    defaultValues: LEAVE_ENCASHMENT_POLICY_DEFAULTS,
    validationSchema: leaveEncashmentPolicyValidationSchema,
    listColumns: LEAVE_ENCASHMENT_POLICY_COLUMNS,
    searchPlaceholder: "Search encashment policies",
  }),
  leaveMaster({
    key: "leave-reason",
    apiName: "LeaveReason",
    label: "Leave Reasons",
    formFields: LEAVE_REASON_FIELDS,
    defaultValues: LEAVE_REASON_DEFAULTS,
    validationSchema: leaveReasonValidationSchema,
    listColumns: STANDARD_LEAVE_COLUMNS,
    searchPlaceholder: "Search by code or label",
  }),
  leaveMaster({
    key: "calendar-period",
    apiName: "CalendarPeriod",
    label: "Calendar Period",
    formFields: CALENDAR_PERIOD_FIELDS,
    defaultValues: CALENDAR_PERIOD_DEFAULTS,
    validationSchema: calendarPeriodValidationSchema,
    listColumns: CALENDAR_PERIOD_COLUMNS,
    formBehaviors: [...CALENDAR_PERIOD_FORM_BEHAVIORS],
    searchPlaceholder: "Search calendar periods",
  }),
  leaveMaster({
    key: "accrual-schedule",
    apiName: "AccrualSchedule",
    label: "Accrual Schedule",
    formFields: ACCRUAL_SCHEDULE_FIELDS,
    defaultValues: ACCRUAL_SCHEDULE_DEFAULTS,
    validationSchema: accrualScheduleValidationSchema,
    listColumns: ACCRUAL_SCHEDULE_COLUMNS,
    searchPlaceholder: "Search accrual schedules",
  }),
];

export const LEAVE_MASTER_CATEGORY: MasterCategoryConfig = {
  key: LEAVE_CATEGORY_KEY,
  label: "Leave Masters",
  categoryKey: LEAVE_CATEGORY_KEY,
  categoryLabel: "Leave Masters",
  masters: LEAVE_MASTER_CONFIGS,
};
