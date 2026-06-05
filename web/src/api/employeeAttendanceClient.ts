/**
 * HTTP client for /api/employee/attendance/* endpoints (employee self-service).
 */

import {
  clearAuthStorage,
  getAccessToken,
  getCompanyId,
  getTenantSchema,
  refreshAccessToken,
  setAccessToken,
} from './authClient';
import type {
  ApiEnvelope,
  ManagerAttendanceListResponse,
  ManagerAttendanceSummaryResponse,
} from './managerAttendanceTypes';

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') ||
  'http://acme.localhost:8000';

const EMPLOYEE_ATTENDANCE_BASE = `${API_BASE}/api/employee/attendance`;

function buildQuery(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : '';
}

function unwrapEnvelope<T>(payload: ApiEnvelope<T>): T {
  return payload.data;
}

async function tryRefreshAccessToken(): Promise<string | null> {
  const refresh = localStorage.getItem('hrms_refresh_token');
  if (!refresh) return null;
  const access = await refreshAccessToken(refresh);
  if (!access) return null;
  setAccessToken(access);
  return access;
}

export class EmployeeAttendanceApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = 'EmployeeAttendanceApiError';
    this.status = status;
    this.body = body;
  }
}

async function employeeAttendanceRequest<T>(
  path: string,
  init?: RequestInit & { query?: Record<string, string | number | boolean | undefined | null> },
): Promise<T> {
  const { query, ...rest } = init ?? {};
  const url = `${EMPLOYEE_ATTENDANCE_BASE}${path}${query ? buildQuery(query) : ''}`;

  const buildHeaders = (token: string | null): Record<string, string> => {
    const headers: Record<string, string> = {
      ...(rest.headers as Record<string, string> | undefined),
    };
    if (token) headers.Authorization = `Bearer ${token}`;
    headers['X-Tenant-Schema'] = getTenantSchema();
    const hasJsonBody =
      rest.body !== undefined && !(rest.body instanceof FormData) && !headers['Content-Type'];
    if (hasJsonBody) headers['Content-Type'] = 'application/json';
    return headers;
  };

  let token = getAccessToken();
  let res = await fetch(url, { credentials: 'include', ...rest, headers: buildHeaders(token) });

  if (res.status === 401) {
    const refreshed = await tryRefreshAccessToken();
    if (refreshed) {
      token = refreshed;
      res = await fetch(url, { credentials: 'include', ...rest, headers: buildHeaders(token) });
    }
  }

  if (!res.ok) {
    if (res.status === 401) clearAuthStorage();
    let msg = `Request failed (${res.status})`;
    let body: unknown;
    try {
      body = await res.json();
      const b = body as { detail?: string; message?: string; errors?: Record<string, unknown> };
      msg = b.message ?? b.detail ?? msg;
      if (res.status === 401) msg = 'Session expired. Please sign in again.';
    } catch {
      if (res.status === 401) msg = 'Session expired. Please sign in again.';
    }
    throw new EmployeeAttendanceApiError(msg, res.status, body);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export interface PunchDetailsResponse {
  date: string;
  status?: string;
  punch_in: { time: string | null; location: string | null; status: string };
  punch_out: { time: string | null; location: string | null; status: string };
  shift: string | null;
  shift_start?: string | null;
  shift_end?: string | null;
  work_hours: number;
}

export interface RegularizationOptionsResponse {
  request_types: string[];
  requested_statuses: string[];
}

export interface RegularizationBulkPayload {
  dates: Array<{ date: string; reason: string }>;
  request_type: string;
  requested_status: string;
  corrected_in_time?: string | null;
  corrected_out_time?: string | null;
}

export interface RegularizationHistoryRecord {
  regularization_id: string;
  date: string;
  request_type: string;
  requested_status: string;
  corrected_in_time: string | null;
  corrected_out_time: string | null;
  reason: string | null;
  status: string;
  submitted_at: string | null;
  reviewed_at: string | null;
  reviewer_comment: string | null;
}

export interface RegularizationHistoryResponse {
  records: RegularizationHistoryRecord[];
  total: number;
}

export interface ClockStatusResponse {
  status: string;
  first_in: string | null;
  last_out: string | null;
  is_currently_in: boolean;
  work_hours: number;
}

export async function fetchEmployeeAttendanceList(params: {
  month: string;
  page?: number;
  per_page?: number;
  status?: string;
  employee_id?: string;
  search_date?: string;
  from_date?: string;
  to_date?: string;
  sort?: string;
}): Promise<ManagerAttendanceListResponse> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<ManagerAttendanceListResponse>>('/list/', {
    query: params,
  });
  return unwrapEnvelope(raw);
}

export async function fetchEmployeeAttendanceSummary(
  month: string,
): Promise<ManagerAttendanceSummaryResponse> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<ManagerAttendanceSummaryResponse>>(
    '/summary/',
    { query: { month } },
  );
  return unwrapEnvelope(raw);
}

export async function fetchEmployeePunchDetails(date: string): Promise<PunchDetailsResponse> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<PunchDetailsResponse>>('/punch-details/', {
    query: { date },
  });
  return unwrapEnvelope(raw);
}

export async function fetchRegularizationOptions(): Promise<RegularizationOptionsResponse> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<RegularizationOptionsResponse>>(
    '/regularization/options/',
  );
  return unwrapEnvelope(raw);
}

export async function submitEmployeeRegularization(
  payload: RegularizationBulkPayload,
): Promise<unknown> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<unknown>>('/regularization/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return unwrapEnvelope(raw);
}

export async function fetchEmployeeRegularizationHistory(params: {
  month?: string;
  status?: string;
} = {}): Promise<RegularizationHistoryResponse> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<RegularizationHistoryResponse>>(
    '/regularization/',
    { query: params },
  );
  return unwrapEnvelope(raw);
}

export async function clockInEmployee(): Promise<ClockStatusResponse> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<ClockStatusResponse>>('/clock-in/', {
    method: 'POST',
    body: JSON.stringify({}),
  });
  return unwrapEnvelope(raw);
}

export async function clockOutEmployee(): Promise<ClockStatusResponse> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<ClockStatusResponse>>('/clock-out/', {
    method: 'POST',
    body: JSON.stringify({}),
  });
  return unwrapEnvelope(raw);
}

export async function fetchEmployeeTodayStatus(): Promise<ClockStatusResponse> {
  const raw = await employeeAttendanceRequest<ApiEnvelope<ClockStatusResponse>>('/today/');
  return unwrapEnvelope(raw);
}
