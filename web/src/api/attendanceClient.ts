import { clearAuthStorage, getTenantSchema, refreshAccessToken } from './authClient';
export { getTenantSchema } from './authClient';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');
export const ATTENDANCE_BASE = `${BASE_URL}/api/admin/attendance`;

export function getAccessToken(): string | null {
  return localStorage.getItem('hrms_access_token');
}

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const part = token.split('.')[1];
    if (!part) return null;
    const padded = part + '='.repeat((4 - (part.length % 4)) % 4);
    return JSON.parse(atob(padded.replace(/-/g, '+').replace(/_/g, '/')));
  } catch {
    return null;
  }
}

export function parseAccessTokenClaims(): Record<string, unknown> | null {
  const token = getAccessToken();
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(
      decodeURIComponent(
        decoded
          .split('')
          .map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`)
          .join(''),
      ),
    );
  } catch {
    return null;
  }
}

export function getCompanyIdFromToken(): string | null {
  const claims = parseAccessTokenClaims();
  if (claims?.company_id) return String(claims.company_id);
  return null;
}

export function getCompanyId(): string | null {
  const fromToken = getCompanyIdFromToken();
  if (fromToken) {
    const stored = localStorage.getItem('hrms_company_id');
    if (stored !== fromToken) {
      localStorage.setItem('hrms_company_id', fromToken);
    }
    return fromToken;
  }
  return (
    localStorage.getItem('hrms_company_id') ||
    (import.meta.env.VITE_COMPANY_ID as string | undefined) ||
    null
  );
}

export function setCompanyId(companyId: string) {
  localStorage.setItem('hrms_company_id', companyId);
}

export function syncCompanyIdFromToken(): string | null {
  const fromToken = getCompanyIdFromToken();
  if (fromToken) {
    setCompanyId(fromToken);
  }
  return fromToken;
}

export function setAccessToken(token: string) {
  localStorage.setItem('hrms_access_token', token);
}

export function setRefreshToken(token: string) {
  localStorage.setItem('hrms_refresh_token', token);
}

async function parseJsonSafe(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text };
  }
}

function errorMessage(status: number, body: unknown): string {
  if (typeof body === 'object' && body !== null) {
    const b = body as Record<string, unknown>;
    if (typeof b.detail === 'string') return b.detail;
    if (typeof b.message === 'string') return b.message;
    const err = b.error as Record<string, unknown> | undefined;
    if (err && typeof err.message === 'string') return err.message;
    if (err && typeof err.message === 'object') {
      return JSON.stringify(err.message);
    }
  }
  if (status === 401) return 'Session expired. Please sign in again.';
  if (status === 403) return 'You do not have permission to access this attendance data.';
  if (status >= 500) return 'Server error while loading attendance data.';
  return `Request failed (${status})`;
}

async function tryRefreshAccessToken(): Promise<string | null> {
  const refresh = localStorage.getItem('hrms_refresh_token');
  if (!refresh) return null;
  const access = await refreshAccessToken(refresh);
  if (!access) return null;
  setAccessToken(access);
  return access;
}

export class AttendanceApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = 'AttendanceApiError';
    this.status = status;
    this.body = body;
  }
}

export async function attendanceFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = path.startsWith('http')
    ? path
    : `${ATTENDANCE_BASE}${path.startsWith('/') ? path : `/${path}`}`;

  const buildHeaders = (access: string | null): Record<string, string> => {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'X-Tenant-Schema': getTenantSchema(),
      ...(init.headers as Record<string, string> | undefined),
    };

    if (access) {
      headers.Authorization = `Bearer ${access}`;
    }

    if (init.body && !(init.body instanceof FormData) && !('Content-Type' in headers)) {
      headers['Content-Type'] = 'application/json';
    }

    return headers;
  };

  let access = getAccessToken();
  let response = await fetch(url, {
    ...init,
    credentials: 'include',
    headers: buildHeaders(access),
  });

  if (response.status === 401 && access) {
    const refreshed = await tryRefreshAccessToken();
    if (refreshed) {
      access = refreshed;
      response = await fetch(url, {
        ...init,
        credentials: 'include',
        headers: buildHeaders(access),
      });
    }
  }

  const body = await parseJsonSafe(response);

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthStorage();
    }
    throw new AttendanceApiError(errorMessage(response.status, body), response.status, body);
  }

  return body as T;
}

export function attendanceQuery(
  params: Record<string, string | number | boolean | undefined | null>,
): string {
  const q = new URLSearchParams();
  const companyId = getCompanyId();
  if (companyId && !('company_id' in params)) {
    q.set('company_id', companyId);
  }
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      q.set(key, String(value));
    }
  });
  const s = q.toString();
  return s ? `?${s}` : '';
}

export function withCompany<T extends Record<string, unknown>>(params: T): T & { company_id?: string } {
  const companyId = getCompanyId();
  if (!companyId) return params;
  return { ...params, company_id: companyId };
}

export async function pollJobStatus<T extends { status: string }>(
  fetchStatus: () => Promise<T>,
  options?: { intervalMs?: number; maxAttempts?: number; terminalStatuses?: string[] },
): Promise<T> {
  const intervalMs = options?.intervalMs ?? 4000;
  const maxAttempts = options?.maxAttempts ?? 60;
  const terminal = new Set(options?.terminalStatuses ?? ['completed', 'failed', 'COMPLETED', 'FAILED', 'SUCCESS', 'ERROR']);

  for (let i = 0; i < maxAttempts; i++) {
    const result = await fetchStatus();
    if (terminal.has(result.status)) {
      return result;
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  throw new AttendanceApiError('Job polling timed out', 408);
}
