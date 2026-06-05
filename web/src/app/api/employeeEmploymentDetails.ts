import { Employee } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

const MY_EMPLOYMENT_DETAILS_URL = `${API_BASE_URL}/api/employee/my-employment/`;

export interface EmployeeEmploymentDetailsApi {
  employee_id: string | null;
  employee_category_id: number | string | null;
  employee_category: string | null;
  department_id: string | null;
  department: string | null;
  team: string | null;
  designation_id: string | null;
  designation: string | null;
  shift_id: string | null;
  shift: string | null;
  work_location_id: number | string | null;
  work_location: string | null;
  employee_type_id: number | string | null;
  employee_type: string | null;
  confirmation_date: string | null;
  employment_status: string | null;
  probation_period: string | null;
  notice_period: string | null;
  notice_period_days: number | string | null;
  referred_by_id: number | string | null;
  referred_by: string | null;
  reporting_to_id: string | null;
  reporting_to: string | null;
  functional_manager_id: string | null;
  functional_manager: string | null;
  hr_partner_id: string | null;
  hr_partner: string | null;
}

interface EmploymentDetailsResponse {
  employment_details?: EmployeeEmploymentDetailsApi;
}

function authHeaders() {
  const token = localStorage.getItem("hrms_access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function parseApiError(response: Response) {
  try {
    const data = await response.json();
    return data?.detail || data?.non_field_errors || JSON.stringify(data);
  } catch {
    return `Request failed with status ${response.status}`;
  }
}

function formatDisplayDate(value: string | null | undefined) {
  if (!value) return "";
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return value;
  return `${match[3]}-${match[2]}-${match[1]}`;
}

export async function getMyEmploymentDetails() {
  const response = await fetch(MY_EMPLOYMENT_DETAILS_URL, {
    method: "GET",
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  const data = (await response.json()) as EmploymentDetailsResponse;
  return data.employment_details;
}

export function employmentDetailsToEmployee(
  employee: Employee,
  details: EmployeeEmploymentDetailsApi
): Employee {
  return {
    ...employee,
    employeeId: details.employee_id ?? employee.employeeId,
    employeeCategory: details.employee_category ?? "",
    department: details.department ?? "",
    team: details.team ?? "",
    designation: details.designation ?? "",
    shift: details.shift ?? "",
    location: details.work_location ?? "",
    employeeType: details.employee_type ?? "",
    confirmationDate: formatDisplayDate(details.confirmation_date),
    employmentStatus: details.employment_status ?? "",
    probationPeriod: details.probation_period ?? "",
    noticePeriod: details.notice_period ?? "",
    noticePeriodDays: details.notice_period_days == null ? "" : String(details.notice_period_days),
    referredBy: details.referred_by ?? "",
    reportingTo: details.reporting_to ?? "",
    functionalManager: details.functional_manager ?? "",
    hrPartner: details.hr_partner ?? "",
  };
}
