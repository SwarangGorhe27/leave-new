export const LEAVE_TYPE_DEFAULTS = {
  carry_forward_enabled: false,
  encashable: false,
  requires_attachment: false,
  has_expiry: false,
  is_paid: true,
  color_code: "#3B82F6",
  allow_half_day: false,
  allow_hourly: false,
  is_clubbing_allowed: false,
  clubbing_restricted_with: [] as string[],
  applicable_gender: "ALL",
  leave_year_type: "CALENDAR",
  is_active: true,
};

export const LEAVE_POLICY_DEFAULTS = {
  is_active: true,
};

export const LEAVE_POLICY_RULE_DEFAULTS = {
  probation_restricted: false,
  notice_period_restricted: false,
};

export const LEAVE_ENCASHMENT_POLICY_DEFAULTS = {
  working_days_divisor: 26,
  is_active: true,
};

export const LEAVE_REASON_DEFAULTS = {
  is_active: true,
};

export const CALENDAR_PERIOD_DEFAULTS = {
  period_type: "CALENDAR",
  year_start_month: "1",
  year_start_day: 1,
  is_active: true,
};

export const ACCRUAL_SCHEDULE_DEFAULTS = {
  frequency: "MONTHLY",
  run_day_of_month: 1,
  proration_on_join: false,
  rounding_rule: "ROUND_HALF",
  is_active: true,
};

export const CALENDAR_PERIOD_FORM_BEHAVIORS = [
  {
    when: { field: "period_type", equals: "CALENDAR" },
    set: { year_start_month: "1", year_start_day: 1 },
  },
] as const;
