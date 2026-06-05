import type { AdminLeaveRequestRow, AdminLeaveTypeRef, LeaveTypeMasterRecord } from "./types";

const TYPES: AdminLeaveTypeRef[] = [
  { id: "lt-pl", code: "PL", name: "Privilege Leave", color_code: "#212529", is_paid: true, is_active: true },
  { id: "lt-sl", code: "SL", name: "Sick Leave", color_code: "#495057", is_paid: true, is_active: true },
  { id: "lt-cl", code: "CL", name: "Casual Leave", color_code: "#6C757D", is_paid: true, is_active: true },
  { id: "lt-lop", code: "LOP", name: "Loss of Pay", color_code: "#ADB5BD", is_paid: false, is_active: true },
  { id: "lt-co", code: "CO", name: "Comp Off", color_code: "#495057", is_paid: true, is_active: true },
  { id: "lt-shl", code: "SHL", name: "Short Leave", color_code: "#6C757D", is_paid: true, is_active: true },
  { id: "lt-od", code: "OD", name: "Out Duty", color_code: "#495057", is_paid: true, is_active: true },
  { id: "lt-wfh", code: "WFH", name: "Work From Home", color_code: "#343A40", is_paid: true, is_active: true },
  { id: "lt-gp", code: "GP", name: "Gate Pass", color_code: "#868E96", is_paid: true, is_active: true },
  { id: "lt-ot", code: "OT", name: "Overtime", color_code: "#212529", is_paid: true, is_active: true },
];

export const LEAVE_TYPE_MASTER: LeaveTypeMasterRecord[] = [
  {
    ...TYPES[0],
    description: "Planned time off for vacations and personal needs.",
    max_yearly_allocation: 14,
    carry_forward: true,
    encashment: true,
    attachment_required: false,
    gender_applicability: "ALL",
    half_day_support: true,
    hourly_leave_support: false,
    clubbing_restrictions: "Can be clubbed with CL/SL. Not with LOP.",
    future_apply_caps_days: 90,
    backdate_limits_days: 7,
    leave_year_type: "CALENDAR",
  },
  {
    ...TYPES[1],
    description: "Medical leave with optional attachments depending on policy.",
    max_yearly_allocation: 10,
    carry_forward: false,
    encashment: false,
    attachment_required: true,
    gender_applicability: "ALL",
    half_day_support: true,
    hourly_leave_support: true,
    clubbing_restrictions: "Cannot be clubbed with PL for backdated requests.",
    future_apply_caps_days: 30,
    backdate_limits_days: 3,
    leave_year_type: "CALENDAR",
  },
  {
    ...TYPES[2],
    description: "Short planned absences and urgent needs.",
    max_yearly_allocation: 12,
    carry_forward: false,
    encashment: false,
    attachment_required: false,
    gender_applicability: "ALL",
    half_day_support: true,
    hourly_leave_support: false,
    future_apply_caps_days: 60,
    backdate_limits_days: 2,
    leave_year_type: "CALENDAR",
  },
  {
    ...TYPES[3],
    description: "Unpaid leave when paid leaves are exhausted or ineligible.",
    max_yearly_allocation: 0,
    carry_forward: false,
    encashment: false,
    attachment_required: false,
    gender_applicability: "ALL",
    half_day_support: true,
    hourly_leave_support: false,
    future_apply_caps_days: 365,
    backdate_limits_days: 0,
    leave_year_type: "CALENDAR",
  },
];

function initials(name: string) {
  const parts = name.split(" ").filter(Boolean);
  return (parts[0]?.[0] ?? "U") + (parts[1]?.[0] ?? "N");
}

const EMPLOYEES = [
  { employee_code: "EMP-0001", employee_name: "Arjun Sharma", department: "Engineering", designation: "Software Engineer", avatarColor: "#212529" },
  { employee_code: "EMP-0002", employee_name: "Rohan Kulkarni", department: "Sales", designation: "Sales Executive", avatarColor: "#343A40" },
  { employee_code: "EMP-0003", employee_name: "Divya Pillai", department: "Finance", designation: "Finance Analyst", avatarColor: "#495057" },
  { employee_code: "EMP-0004", employee_name: "Sneha Krishnan", department: "HR", designation: "HRBP", avatarColor: "#6C757D" },
  { employee_code: "EMP-0005", employee_name: "Vikram Mehta", department: "Product", designation: "Product Manager", avatarColor: "#212529" },
];

const STATUSES = ["SUBMITTED", "APPROVED", "REJECTED", "CANCELLED"] as const;

export const ADMIN_LEAVE_REQUESTS: AdminLeaveRequestRow[] = Array.from({ length: 42 }, (_, i) => {
  const employee = EMPLOYEES[i % EMPLOYEES.length];
  const leave_type = TYPES[i % TYPES.length];
  const start = new Date(2026, 4, 1 + (i % 25));
  const days = (i % 4) + 1;
  const end = new Date(start);
  end.setDate(start.getDate() + Math.max(0, days - 1));
  const toISO = (d: Date) => d.toISOString().slice(0, 10);
  const status = STATUSES[i % STATUSES.length];
  const categories: AdminLeaveRequestRow["category"][] = ["LEAVE", "COMP_OFF", "SHORT_LEAVE", "OUT_DUTY", "WFH", "GATE_PASS", "OVERTIME"];
  const category = categories[i % categories.length];
  const priorityMap: AdminLeaveRequestRow["priority"][] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

  const id = `lr-${i + 1}`;
  const workflow_level = status === "SUBMITTED" ? 1 : 2;

  return {
    id,
    employee: { ...employee, initials: initials(employee.employee_name) },
    leave_type,
    from_date: toISO(start),
    to_date: toISO(end),
    total_days: days,
    duration: days === 1 && i % 6 === 0 ? "HALF" : "FULL",
    applied_on: toISO(new Date(2026, 3, 20 + (i % 15))),
    reason: i % 3 === 0 ? "Personal commitment" : i % 3 === 1 ? "Medical appointment" : "Family function",
    backup_employee: i % 5 === 0 ? "Priya Nair" : undefined,
    status,
    priority: priorityMap[i % priorityMap.length],
    workflow_stage: status === "SUBMITTED" ? "Manager Review" : status === "APPROVED" ? "Completed" : "Closed",
    category,
    current_approver: status === "SUBMITTED" ? "Manager" : "—",
    payroll_lock: i % 9 === 0 ? "Locked" : "Unlocked",
    workflow_level,
    deleted_at: null,
    approval_history: [
      { level: 1, approver: "Manager", status: status === "SUBMITTED" ? "PENDING" : "APPROVED", acted_at: status === "SUBMITTED" ? undefined : new Date().toISOString() },
      { level: 2, approver: "HRBP", status: status === "APPROVED" ? "APPROVED" : status === "REJECTED" ? "REJECTED" : "PENDING", acted_at: status === "APPROVED" || status === "REJECTED" ? new Date().toISOString() : undefined },
    ],
    comments: [
      { id: `${id}-c1`, author: "System", created_at: new Date().toISOString(), message: "Request created." },
    ],
    attachments: i % 7 === 0 ? [{ id: `${id}-a1`, name: "Medical Certificate", url: "#", type: "pdf" }] : [],
    audit: [
      {
        id: `${id}-e1`,
        at: new Date().toISOString(),
        actor: "System",
        actor_role: "admin",
        action: "SUBMITTED",
        meta: "Submitted via ESS",
        ip_address: "10.10.1.25",
        device_info: "Chrome / Windows",
      },
    ],
    ledger_impact: [
      { id: `${id}-l1`, leave_type_code: leave_type.code, effect: "DEBIT", days, note: "Pending approval reservation" },
    ],
  };
});

