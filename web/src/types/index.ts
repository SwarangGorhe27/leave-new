// ──── Common ────
export interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  meta?: Record<string, unknown>;
  errors?: Array<{ code: string; message: string; field?: string }>;
}

export interface PaginatedResponse<T> {
  results: T[];
  next: string | null;
  previous: string | null;
}

// ──── Auth ────
export interface LoginResponse {
  access: string;
  refresh: string;
}

// ──── Employee ────
export interface Employee {
  id: string;
  employee_code: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  gender_detail?: { name: string };
  avatar: string | null;
  is_active: boolean;
  employment?: EmployeeEmployment;
}

export interface EmployeeEmployment {
  date_of_joining: string;
  designation_detail?: { name: string };
  department_detail?: { name: string };
  employment_type_detail?: { name: string };
  reporting_manager_detail?: { full_name: string };
}

// ──── Attendance ────
export interface AttendanceRecord {
  id: string;
  employee: string;
  date: string;
  status: string;
  first_in: string | null;
  last_out: string | null;
  effective_hours: string;
  overtime_hours: string;
}

// ──── Leave ────
export interface LeaveType {
  id: string;
  name: string;
  code: string;
  color_code: string;
  is_paid: boolean;
}

export interface LeaveBalance {
  id: string;
  leave_type: string;
  leave_type_detail: LeaveType;
  opening_balance: number;
  accrued: number;
  used: number;
  carry_forwarded: number;
  available: number;
  total_allocated: number;
}

export interface LeaveApplication {
  id: string;
  employee: string;
  employee_name: string;
  leave_type_detail: LeaveType;
  from_date: string;
  to_date: string;
  total_days: number;
  reason: string;
  status: string;
  applied_on: string;
}

// ──── Payroll ────
export interface PayrollRun {
  id: string;
  name: string;
  year: number;
  month: number;
  status: string;
  total_gross: number;
  total_net: number;
  employee_count: number;
}

export interface Payslip {
  id: string;
  employee: string;
  employee_name: string;
  gross_earnings: number;
  total_deductions: number;
  net_pay: number;
  paid_days: number;
  lop_days: number;
}
