import { z } from "zod";

const optionalNumber = z.coerce.number().optional();
const requiredPositiveNumber = z.coerce.number().min(1, "Must be greater than 0");

export const leaveTypeValidationSchema = z
  .object({
    code: z.string().trim().min(1, "Code is required"),
    name: z.string().trim().min(1, "Name is required"),
    employee_type: z.string().optional(),
    description: z.string().optional(),
    max_days_per_year: requiredPositiveNumber,
    max_consecutive_days: optionalNumber,
    carry_forward_enabled: z.boolean().optional(),
    max_carry_forward_days: optionalNumber,
    encashable: z.boolean().optional(),
    requires_attachment: z.boolean().optional(),
    attachment_threshold_days: optionalNumber,
    min_notice_days: optionalNumber,
    applicable_gender: z.string().optional(),
    has_expiry: z.boolean().optional(),
    expiry_days: optionalNumber,
    is_paid: z.boolean().optional(),
    allow_half_day: z.boolean().optional(),
    allow_hourly: z.boolean().optional(),
    is_clubbing_allowed: z.boolean().optional(),
    clubbing_restricted_with: z.array(z.string()).optional(),
    backdate_allowed_days: optionalNumber,
    future_apply_cap_days: optionalNumber,
    leave_year_type: z.string().optional(),
    is_active: z.boolean().optional(),
  })
  .superRefine((data, ctx) => {
    if (data.carry_forward_enabled && (data.max_carry_forward_days === undefined || Number.isNaN(data.max_carry_forward_days))) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Max carry forward days is required", path: ["max_carry_forward_days"] });
    }
    if (data.requires_attachment && (data.attachment_threshold_days === undefined || Number.isNaN(data.attachment_threshold_days))) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Attachment threshold days is required", path: ["attachment_threshold_days"] });
    }
    if (data.has_expiry && (!data.expiry_days || data.expiry_days < 1)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Expiry days is required when expiry is enabled", path: ["expiry_days"] });
    }
    if (
      data.max_consecutive_days !== undefined &&
      !Number.isNaN(data.max_consecutive_days) &&
      data.max_consecutive_days > data.max_days_per_year
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Max consecutive days cannot exceed max days per year",
        path: ["max_consecutive_days"],
      });
    }
  });

export const leavePolicyValidationSchema = z.object({
  name: z.string().trim().min(1, "Name is required"),
  description: z.string().optional(),
  effective_from: z.string().trim().min(1, "Effective from is required"),
  effective_to: z.string().optional(),
  version: z.string().optional(),
  is_active: z.boolean().optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  created_by: z.string().optional(),
  updated_by: z.string().optional(),
});

export const leavePolicyRuleValidationSchema = z.object({
  policy: z.string().trim().min(1, "Policy is required"),
  leave_type: z.string().trim().min(1, "Leave type is required"),
  probation_restricted: z.boolean().optional(),
  notice_period_restricted: z.boolean().optional(),
  grade: z.string().optional(),
  employee_type: z.string().optional(),
  accrual_frequency: z.string().optional(),
  accrual_proration_basis: z.string().optional(),
  rounding_rule: z.string().optional(),
});

export const leaveEncashmentPolicyValidationSchema = z.object({
  leave_type: z.string().trim().min(1, "Leave type is required"),
  formula_basis: z.string().trim().min(1, "Formula basis is required"),
  working_days_divisor: z.coerce.number().min(1).default(26),
  max_encashable_days_per_year: z.coerce.number().min(0).optional(),
  min_balance_to_retain: z.coerce.number().min(0).optional(),
  payout_timing: z.string().optional(),
  tax_treatment: z.string().optional(),
  is_active: z.boolean().optional(),
});

export const leaveReasonValidationSchema = z.object({
  module: z.string().trim().min(1, "Module is required"),
  code: z.string().trim().min(1, "Code is required"),
  label: z.string().trim().min(1, "Label is required"),
  is_active: z.boolean().optional(),
});

export const calendarPeriodValidationSchema = z
  .object({
    period_type: z.string().trim().min(1, "Period type is required"),
    year_start_month: z.string().trim().min(1, "Year start month is required"),
    year_start_day: z.coerce.number().min(1).max(31),
    cf_reset_date: z.string().optional(),
    accrual_start_month: z.string().optional(),
    encashment_cycle: z.string().optional(),
    is_active: z.boolean().optional(),
    version: z.string().optional(),
    created_at: z.string().optional(),
    updated_at: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    const month = Number(data.year_start_month);
    const day = Number(data.year_start_day);
    const maxDays = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1];
    if (!month || month < 1 || month > 12) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Invalid month", path: ["year_start_month"] });
      return;
    }
    if (!maxDays || day > maxDays) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `Day must be between 1 and ${maxDays} for selected month`,
        path: ["year_start_day"],
      });
    }
  });

export const accrualScheduleValidationSchema = z
  .object({
    policy_rule: z.string().trim().min(1, "Policy rule is required"),
    frequency: z.string().trim().min(1, "Frequency is required"),
    run_day_of_month: z.coerce.number().min(1, "Run day must be at least 1").max(31, "Run day cannot exceed 31"),
    run_month: z.string().optional(),
    proration_on_join: z.boolean().optional(),
    rounding_rule: z.string().trim().min(1, "Rounding rule is required"),
    is_active: z.boolean().optional(),
    version: z.string().optional(),
    created_at: z.string().optional(),
    updated_at: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    if ((data.frequency === "QUARTERLY" || data.frequency === "ANNUAL") && !data.run_month?.trim()) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Run month is required for this frequency", path: ["run_month"] });
    }
  });
