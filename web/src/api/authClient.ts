function resolveApiBase(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (raw === undefined || raw.trim() === "") {
    return "";
  }
  return raw.replace(/\/$/, "");
}

const BASE_URL = resolveApiBase();

const LOGIN_PATH = BASE_URL ? `${BASE_URL}/api/employee/login/` : "/api/employee/login/";
const REFRESH_PATH = BASE_URL ? `${BASE_URL}/api/employee/refresh/` : "/api/employee/refresh/";

export function getTenantSchema(): string {
  return (
    localStorage.getItem('hrms_tenant_schema') ||
    (import.meta.env.VITE_TENANT_SCHEMA as string | undefined) ||
    'acme'
  );
}

export function setTenantSchema(schema: string) {
  localStorage.setItem('hrms_tenant_schema', schema);
}

/** Clear all auth-related browser storage (login session). */
export function clearAuthStorage() {
  localStorage.removeItem('hrms_user');
  localStorage.removeItem('hrms_access_token');
  localStorage.removeItem('hrms_refresh_token');
  localStorage.removeItem('hrms_company_id');
}

export function getAccessToken(): string | null {
  return localStorage.getItem('hrms_access_token');
}

export function getCompanyId(): string | null {
  return (
    localStorage.getItem('hrms_company_id') ||
    (import.meta.env.VITE_COMPANY_ID as string | undefined) ||
    null
  );
}

export function setAccessToken(token: string) {
  localStorage.setItem('hrms_access_token', token);
}

export interface LoginResponseUser {
  user_id?: string;
  email?: string;
  username?: string;
  employee_id?: string;
  employee_code?: string;
  full_name?: string;
  company_id?: string;
  company_name?: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user_type?: string;
  user?: LoginResponseUser;
  roles?: Array<{ role_code?: string; company_id?: string }>;
}

export interface LoginResult {
  success: boolean;
  message?: string;
  data?: LoginResponse;
}

export async function loginWithBackend(
  email: string,
  password: string,
): Promise<LoginResult> {
  const normalizedEmail = email.trim().toLowerCase();

  let response: Response;
  try {
    response = await fetch(LOGIN_PATH, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-Schema': getTenantSchema(),
      },
      credentials: 'include',
      body: JSON.stringify({
        email: normalizedEmail,
        username: normalizedEmail,
        password,
      }),
    });
  } catch {
    return {
      success: false,
      message: 'Cannot reach the server. Check that the backend is running and VITE_API_BASE_URL / proxy settings are correct.',
    };
  }

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const msg =
      payload.detail ||
      payload.message ||
      (Array.isArray(payload.non_field_errors) ? payload.non_field_errors[0] : undefined) ||
      (typeof payload === 'object' && payload !== null
        ? Object.values(payload)
            .flat()
            .find((v) => typeof v === 'string')
        : undefined) ||
      'Invalid email or password.';
    return { success: false, message: String(msg) };
  }

  if (!payload.access) {
    return { success: false, message: 'Login succeeded but no access token was returned.' };
  }

  return { success: true, data: payload as LoginResponse };
}

export async function refreshAccessToken(refresh: string): Promise<string | null> {
  const response = await fetch(REFRESH_PATH, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Tenant-Schema': getTenantSchema(),
    },
    credentials: 'include',
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) return null;
  const payload = await response.json();
  const access = payload.access ?? null;
  if (access) {
    localStorage.setItem('hrms_access_token', access);
    if (payload.refresh) {
      localStorage.setItem('hrms_refresh_token', payload.refresh);
    }
  }
  return access;
}
