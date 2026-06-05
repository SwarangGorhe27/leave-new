export { LEAVE_MASTER_CATEGORY, LEAVE_MASTER_CONFIGS } from "./leaveMasters";
export {
  ACCRUAL_SCHEDULE_FIELDS,
  CALENDAR_PERIOD_FIELDS,
  LEAVE_ENCASHMENT_POLICY_FIELDS,
  LEAVE_POLICY_FIELDS,
  LEAVE_POLICY_RULE_FIELDS,
  LEAVE_REASON_FIELDS,
  LEAVE_TYPE_FIELDS,
} from "./fieldSchemas";
export {
  accrualScheduleValidationSchema,
  calendarPeriodValidationSchema,
  leaveEncashmentPolicyValidationSchema,
  leavePolicyRuleValidationSchema,
  leavePolicyValidationSchema,
  leaveReasonValidationSchema,
  leaveTypeValidationSchema,
} from "./schemas";
export {
  ACCRUAL_SCHEDULE_DEFAULTS,
  CALENDAR_PERIOD_DEFAULTS,
  CALENDAR_PERIOD_FORM_BEHAVIORS,
  LEAVE_ENCASHMENT_POLICY_DEFAULTS,
  LEAVE_POLICY_DEFAULTS,
  LEAVE_POLICY_RULE_DEFAULTS,
  LEAVE_REASON_DEFAULTS,
  LEAVE_TYPE_DEFAULTS,
} from "./defaults";
export {
  ACCRUAL_SCHEDULE_COLUMNS,
  CALENDAR_PERIOD_COLUMNS,
  LEAVE_ENCASHMENT_POLICY_COLUMNS,
  LEAVE_POLICY_COLUMNS,
  LEAVE_POLICY_RULE_COLUMNS,
  STANDARD_LEAVE_COLUMNS,
} from "./tableColumns";
export {
  ACCRUAL_SCHEDULE_FREQUENCY_OPTIONS,
  ACCRUAL_SCHEDULE_ROUNDING_OPTIONS,
  DAYS_IN_MONTH,
  ENCASHMENT_CYCLE_OPTIONS,
  MONTH_OPTIONS,
  PERIOD_TYPE_OPTIONS,
} from "./constants";

/** Retired leave master URL keys mapped to current leave masters. */
export const LEGACY_LEAVE_MASTER_KEY_ALIASES: Record<string, string> = {
  "leave-accrual-rule": "accrual-schedule",
  "leave-encashment-rule": "leave-encashment-policy",
  "leave-carry-forward-rule": "leave-policy-rule",
  "leave-approval-matrix": "leave-policy-rule",
  "leave-escalation-matrix": "leave-policy-rule",
  "leave-reason-master": "leave-reason",
  "holiday-calendar": "calendar-period",
  holiday: "calendar-period",
  "restricted-holiday": "leave-type",
  "leave-balance-setting": "leave-policy-rule",
  "sandwich-leave-rule": "leave-policy-rule",
  "probation-leave-rule": "leave-policy-rule",
  "maternity-paternity-rule": "leave-policy-rule",
  "compensatory-leave-rule": "leave-policy-rule",
  "leave-document-rule": "leave-policy-rule",
  "leave-cancellation-rule": "leave-policy-rule",
  "leave-blackout-date": "leave-policy-rule",
};
