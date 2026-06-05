/**
 * HTTP client for /api/manager/attendance/* endpoints.
 * Separate from admin attendanceClient — manager team + self-service views.
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
  ApproveRejectPayload,
  ManagerAttendanceListResponse,
  ManagerAttendanceSummaryResponse,
  ManagerOTDetail,
  ManagerOTListItem,
  ManagerRegularizationDetail,
  ManagerRegularizationListItem,
  OTApprovePayload,
  TeamAttendanceMember,
  TeamAttendanceOverrideRequest,
  TeamAttendanceOverrideResponse,
  TeamMemberAttendanceResponse,
  TeamMemberProfileResponse,
  TeamMemberStatsResponse,
} from './managerAttendanceTypes';

const MANAGER_ATTENDANCE_BASE =
  `${(import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || ''}/api/manager/attendance`;

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

async function tryRefreshAccessToken(): Promise<string | null> {
  const refresh = localStorage.getItem('hrms_refresh_token');
  if (!refresh) return null;
  const access = await refreshAccessToken(refresh);
  if (!access) return null;
  setAccessToken(access);
  return access;
}

export class ManagerAttendanceApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = 'ManagerAttendanceApiError';
    this.status = status;
    this.body = body;
  }
}

async function managerAttendanceRequest<T>(
  path: string,
  init?: RequestInit & { query?: Record<string, string | number | boolean | undefined | null> },
): Promise<T> {
  const { query, ...rest } = init ?? {};
  const url = `${MANAGER_ATTENDANCE_BASE}${path}${query ? buildQuery(query) : ''}`;

  const buildHeaders = (token: string | null): Record<string, string> => {
    const headers: Record<string, string> = {
      ...(rest.headers as Record<string, string> | undefined),
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    headers['X-Tenant-Schema'] = getTenantSchema();
    const hasJsonBody =
      rest.body !== undefined &&
      !(rest.body instanceof FormData) &&
      !headers['Content-Type'];
    if (hasJsonBody) {
      headers['Content-Type'] = 'application/json';
    }
    return headers;
  };

  let token = getAccessToken();
  let res = await fetch(url, {
    credentials: 'include',
    ...rest,
    headers: buildHeaders(token),
  });

  if (res.status === 401) {
    const refreshed = await tryRefreshAccessToken();
    if (refreshed) {
      token = refreshed;
      res = await fetch(url, {
        credentials: 'include',
        ...rest,
        headers: buildHeaders(token),
      });
    }
  }

  if (!res.ok) {
    if (res.status === 401) {
      clearAuthStorage();
    }
    let msg = `Request failed (${res.status})`;
    let body: unknown;
    try {
      body = await res.json();
      const b = body as {
        detail?: string;
        message?: string;
        error?: { code?: string; message?: string };
      };
      msg = b.detail ?? b.message ?? b.error?.message ?? msg;
      if (res.status === 401) msg = 'Session expired. Please sign in again.';
      if (res.status === 403) msg = b.error?.message ?? msg ?? 'Permission denied.';
    } catch {
      if (res.status === 401) msg = 'Session expired. Please sign in again.';
    }
    throw new ManagerAttendanceApiError(msg, res.status, body);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return (await res.json()) as T;
}

function unwrapEnvelope<T>(payload: ApiEnvelope<T> | T): T {
  if (typeof payload === 'object' && payload !== null && 'success' in payload && 'data' in payload) {
    const envelope = payload as ApiEnvelope<T>;
    if (!envelope.success) {
      throw new ManagerAttendanceApiError(envelope.message || 'Request failed', 400, envelope);
    }
    return envelope.data;
  }
  return payload as T;
}

// ─── Manager self (logged-in employee) ─────────────────────────────────────

export async function fetchManagerOwnAttendanceList(params: {
  month: string;
  page?: number;
  per_page?: number;
  status?: string;
  search_date?: string;
  sort?: string;
}): Promise<ManagerAttendanceListResponse> {
  const raw = await managerAttendanceRequest<ApiEnvelope<ManagerAttendanceListResponse>>(
    '/employee/list/',
    { query: params },
  );
  return unwrapEnvelope(raw);
}

export async function fetchManagerOwnAttendanceSummary(month: string): Promise<ManagerAttendanceSummaryResponse> {
  const raw = await managerAttendanceRequest<ApiEnvelope<ManagerAttendanceSummaryResponse>>(
    '/employee/summary/',
    { query: { month } },
  );
  return unwrapEnvelope(raw);
}

// ─── Team ────────────────────────────────────────────────────────────────────

export async function fetchManagerTeam(): Promise<TeamAttendanceMember[]> {
  return managerAttendanceRequest<TeamAttendanceMember[]>('/team/');
}

export async function fetchTeamMemberAttendance(
  employeeId: string,
  params?: { month?: number; year?: number },
): Promise<TeamMemberAttendanceResponse> {
  return managerAttendanceRequest<TeamMemberAttendanceResponse>(`/team/${employeeId}/attendance/`, {
    query: params,
  });
}

export async function fetchTeamMemberStats(
  employeeId: string,
  params?: { month?: number; year?: number },
): Promise<TeamMemberStatsResponse> {
  return managerAttendanceRequest<TeamMemberStatsResponse>(`/team/${employeeId}/stats/`, {
    query: params,
  });
}

export async function fetchTeamMemberProfile(employeeId: string): Promise<TeamMemberProfileResponse> {
  return managerAttendanceRequest<TeamMemberProfileResponse>(`/team/${employeeId}/profile/`);
}

// ─── Approvals (regularization + overtime) ───────────────────────────────────

export interface ManagerApprovalListParams extends Record<string, string | number | boolean | undefined> {
  status?: string;
  reg_type?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
  department?: string;
  page?: number;
  per_page?: number;
}

function extractList<T>(payload: T[] | { results: T[] }): T[] {
  if (Array.isArray(payload)) return payload;
  if (payload && typeof payload === 'object' && 'results' in payload) {
    return (payload as { results: T[] }).results ?? [];
  }
  return [];
}

export async function fetchManagerRegularizations(
  params?: ManagerApprovalListParams,
): Promise<ManagerRegularizationListItem[]> {
  const raw = await managerAttendanceRequest<ManagerRegularizationListItem[] | { results: ManagerRegularizationListItem[] }>(
    '/regularization/',
    { query: params },
  );
  return extractList(raw);
}

export async function fetchManagerRegularizationDetail(id: string): Promise<ManagerRegularizationDetail> {
  return managerAttendanceRequest<ManagerRegularizationDetail>(`/regularization/${id}/`);
}

export async function approveManagerRegularization(
  id: string,
  body?: ApproveRejectPayload,
): Promise<ManagerRegularizationDetail> {
  return managerAttendanceRequest<ManagerRegularizationDetail>(`/regularization/${id}/approve/`, {
    method: 'POST',
    body: JSON.stringify(body ?? {}),
  });
}

export async function rejectManagerRegularization(
  id: string,
  body?: ApproveRejectPayload,
): Promise<ManagerRegularizationDetail> {
  return managerAttendanceRequest<ManagerRegularizationDetail>(`/regularization/${id}/reject/`, {
    method: 'POST',
    body: JSON.stringify(body ?? {}),
  });
}

export async function fetchManagerOvertimeRequests(
  params?: ManagerApprovalListParams,
): Promise<ManagerOTListItem[]> {
  const raw = await managerAttendanceRequest<ManagerOTListItem[] | { results: ManagerOTListItem[] }>(
    '/overtime/',
    { query: params },
  );
  return extractList(raw);
}

export async function fetchManagerOvertimeDetail(id: string): Promise<ManagerOTDetail> {
  return managerAttendanceRequest<ManagerOTDetail>(`/overtime/${id}/`);
}

export async function approveManagerOvertime(
  id: string,
  body?: OTApprovePayload,
): Promise<ManagerOTDetail> {
  return managerAttendanceRequest<ManagerOTDetail>(`/overtime/${id}/approve/`, {
    method: 'POST',
    body: JSON.stringify(body ?? {}),
  });
}

export async function rejectManagerOvertime(
  id: string,
  body?: ApproveRejectPayload,
): Promise<ManagerOTDetail> {
  return managerAttendanceRequest<ManagerOTDetail>(`/overtime/${id}/reject/`, {
    method: 'POST',
    body: JSON.stringify(body ?? {}),
  });
}

// ─── Team Attendance Override ─────────────────────────────────────────────

export async function overrideTeamAttendance(
  employeeId: string,
  body: TeamAttendanceOverrideRequest,
): Promise<TeamAttendanceOverrideResponse> {
  return managerAttendanceRequest<TeamAttendanceOverrideResponse>(
    `/team/${employeeId}/attendance/`,
    {
      method: 'POST',
      body: JSON.stringify(body),
    }
  );
}
