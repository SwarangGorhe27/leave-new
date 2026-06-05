export const MONTH_OPTIONS = Array.from({ length: 12 }, (_, index) => ({
  value: String(index + 1),
  label: new Date(2000, index, 1).toLocaleString("default", { month: "long" }),
}));

export const PERIOD_TYPE_OPTIONS = [
  { value: "CALENDAR", label: "Calendar" },
  { value: "FISCAL", label: "Fiscal" },
  { value: "CUSTOM", label: "Custom" },
];

export const ENCASHMENT_CYCLE_OPTIONS = [
  { value: "ANNUAL", label: "Annual" },
  { value: "ON_EXIT", label: "On Exit" },
  { value: "CUSTOM", label: "Custom" },
];

export const ACCRUAL_SCHEDULE_FREQUENCY_OPTIONS = [
  { value: "MONTHLY", label: "Monthly" },
  { value: "QUARTERLY", label: "Quarterly" },
  { value: "ANNUAL", label: "Annual" },
];

export const ACCRUAL_SCHEDULE_ROUNDING_OPTIONS = [
  { value: "FLOOR", label: "Floor" },
  { value: "CEIL", label: "Ceil" },
  { value: "ROUND_HALF", label: "Round Half" },
];

export const DAYS_IN_MONTH: Record<number, number> = {
  1: 31,
  2: 29,
  3: 31,
  4: 30,
  5: 31,
  6: 30,
  7: 31,
  8: 31,
  9: 30,
  10: 31,
  11: 30,
  12: 31,
};
