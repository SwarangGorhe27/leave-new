/**
 * Add Employee API — Admin Side
 *
 * All calls go to the Django backend via the shared axios client.
 * Token is injected by the interceptor in client.ts (patched separately).
 *
 * Endpoints:
 *   POST   /api/admin/employees/add/
 *   POST   /api/admin/employees/rehire/
 *   GET    /api/admin/employees/former/
 *   POST   /api/admin/employees/bulk-import/
 *   GET    /api/admin/employees/bulk-import/template/
 *   POST   /api/admin/employees/draft/
 *   GET    /api/admin/employees/draft/<draft_id>/
 */

import api from './client';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AddEmployeePayload {
  // Section 1 – Basic
  employee_code: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  joining_date: string;
  official_email: string;
  mobile_number: string;
  emergency_contact_name: string;
  emergency_contact_number: string;
  gender?: string | null;
  salutation?: string | null;
  middle_name?: string | null;
  marital_status?: string | null;
  blood_group?: string | null;
  personal_email?: string | null;
  alternate_mobile_number?: string | null;
  date_of_confirmation?: string | null;
  employee_status?: string;
  referred_by?: string | null;
  onboarding_policy?: string | null;
  allow_employee_to_fill_information?: boolean;
  probation_period?: number | null;
  employee_number_series?: string | null;
  father_name?: string | null;
  spouse_name?: string | null;
  emergency_contact_relationship?: string | null;
  profile_photo?: string | null;
  // Section 2 – Job
  employment_type?: string | null;
  department?: string | null;
  designation?: string | null;
  work_location?: string | null;
  company?: string | null;
  business_unit?: string | null;
  grade?: string | null;
  shift?: string | null;
  reporting_manager?: string | null;
  // Section 3 – Attendance
  weekly_off?: string | null;
  working_hours_start?: string | null;
  working_hours_end?: string | null;
  weekly_off_days?: string[];
  attendance_tracking_mode?: string | null;
  // Section 4 – Payroll
  salary_structure?: string | null;
  basic_salary?: number | null;
  bank_account?: {
    bank_name?: string;
    account_number?: string;
    ifsc_code?: string;
    account_type?: string;
  } | null;
  pan_number?: string | null;
  // Section 5 – Leave
  leave_policy?: string | null;
  annual_leave_balance?: number | null;
  sick_leave_balance?: number | null;
  // Section 6 – Background
  verification_status?: string | null;
  agency_name?: string | null;
  verified_by?: string | null;
  reference_number?: string | null;
  background_remarks?: string | null;
  // Section 7 – Assets
  assets?: Array<{
    asset_name: string;
    asset_id: string;
    asset_category?: string;
    asset_condition?: string;
    serial_number?: string;
    asset_assign_date: string;
    asset_return_date?: string;
    asset_status?: string;
    asset_remarks?: string;
  }>;
  // Section 8 – Account
  username?: string | null;
  temporary_password?: string | null;
  system_role?: string | null;
  // Misc
  aadhaar_number?: string | null;
  uan_number?: string | null;
  esi_number?: string | null;
  passport_number?: string | null;
  is_draft?: boolean;
  is_active?: boolean;
}

export interface AddEmployeeResponse {
  employee_id: string;
  employee_code: string;
  full_name: string;
  official_email: string;
  mobile_number: string;
  employee_status: string;
  company: { id: string; code: string | null; name: string | null } | null;
  department: { id: string; code: string | null; name: string | null } | null;
  designation: { id: string; code: string | null; name: string | null } | null;
  is_draft: boolean;
  is_active: boolean;
}

export interface FormerEmployee {
  employee_id: string;
  employee_code: string;
  full_name: string;
  department: string | null;
  designation: string | null;
  last_working_date: string | null;
  separation_reason: string | null;
  status: string;
  profile_picture_url: string | null;
}

export interface RehirePayload {
  former_employee_id: string;
  rehire_date: string;
  new_employee_code?: string;
  rehire_remarks?: string;
  restore_salary?: boolean;
  restore_assets?: boolean;
  restore_leaves?: boolean;
  employment_type?: string | null;
  department?: string | null;
  designation?: string | null;
  reporting_manager?: string | null;
  work_location?: string | null;
  shift?: string | null;
  username?: string | null;
  temporary_password?: string | null;
}

export interface BulkImportResult {
  total_rows: number;
  success_count: number;
  failed_count: number;
  results: Array<{
    row: number;
    employee_code: string | null;
    status: 'success' | 'failed';
    errors?: Record<string, string>;
  }>;
}

export interface DraftResponse {
  draft_id: string;
  draft_type: string;
  saved_at: string;
}

// ─── API Functions ─────────────────────────────────────────────────────────────

const BASE = '/admin/employees';

/** POST /api/admin/employees/add/ */
export async function createEmployee(
  payload: AddEmployeePayload,
): Promise<AddEmployeeResponse> {
  const res = await api.post<AddEmployeeResponse>(`${BASE}/add/`, payload);
  return res.data;
}

/** POST /api/admin/employees/rehire/ */
export async function rehireEmployee(
  payload: RehirePayload,
): Promise<AddEmployeeResponse> {
  const res = await api.post<AddEmployeeResponse>(`${BASE}/rehire/`, payload);
  return res.data;
}

/** GET /api/admin/employees/former/ */
export async function getFormerEmployees(params?: {
  search?: string;
  department_id?: string;
  reason?: string;
}): Promise<FormerEmployee[]> {
  const res = await api.get<FormerEmployee[]>(`${BASE}/former/`, { params });
  return res.data;
}

/** POST /api/admin/employees/bulk-import/ */
export async function bulkImportEmployees(
  file: File,
): Promise<BulkImportResult> {
  const form = new FormData();
  form.append('file', file);
  const res = await api.post<BulkImportResult>(`${BASE}/bulk-import/`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

/** GET /api/admin/employees/bulk-import/template/ — returns a Blob */
export async function downloadBulkImportTemplate(): Promise<Blob> {
  const res = await api.get(`${BASE}/bulk-import/template/`, {
    responseType: 'blob',
  });
  return res.data as Blob;
}

/** POST /api/admin/employees/draft/ */
export async function saveDraft(
  draftData: Record<string, unknown>,
  draftType: 'new' | 'rehire' = 'new',
  draftId?: string,
): Promise<DraftResponse> {
  const res = await api.post<DraftResponse>(`${BASE}/draft/`, {
    draft_data: draftData,
    draft_type: draftType,
    ...(draftId ? { draft_id: draftId } : {}),
  });
  return res.data;
}

/** GET /api/admin/employees/draft/<draft_id>/ */
export async function getDraft(draftId: string): Promise<Record<string, unknown>> {
  const res = await api.get<Record<string, unknown>>(`${BASE}/draft/${draftId}/`);
  return res.data;
}
