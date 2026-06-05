/// <reference types="vite/client" />

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@api/client';

const API_BASE_URL =
  (import.meta.env['VITE_API_BASE_URL'] as string | undefined)?.replace(/\/$/, '') ||
  'http://acme.localhost:8000';
const EMP_STORAGE_KEY = 'hrms-demo-employees';


const DEMO_EMPLOYEES: EmployeeListItem[] = [
  {
    id: 'emp-1',
    employee_code: 'EMP-0001',
    first_name: 'Aditi',
    middle_name: '',
    last_name: 'Mehra',
    full_name: 'Aditi Mehra',
    profile_photo: null,
    status: 'ACTIVE',
    status_detail: { id: 'stat-1', name: 'Active', code: 'ACTIVE', color_code: '#10B981' },
    department: 'Human Resources',
    designation: 'HR Manager',
    date_of_joining: '2024-01-15',
    work_email: 'aditi.mehra@hrms.demo',
  },
  {
    id: 'emp-2',
    employee_code: 'EMP-0002',
    first_name: 'Rohan',
    middle_name: '',
    last_name: 'Kulkarni',
    full_name: 'Rohan Kulkarni',
    profile_photo: null,
    status: 'ACTIVE',
    status_detail: { id: 'stat-1', name: 'Active', code: 'ACTIVE', color_code: '#10B981' },
    department: 'Engineering',
    designation: 'Software Engineer',
    date_of_joining: '2023-08-21',
    work_email: 'rohan.kulkarni@hrms.demo',
  },
];

function readDemoEmployees(): EmployeeListItem[] {
  const raw = localStorage.getItem(EMP_STORAGE_KEY);
  if (raw) {
    try {
      return JSON.parse(raw) as EmployeeListItem[];
    } catch {
      // fallback to seeded data
    }
  }
  localStorage.setItem(EMP_STORAGE_KEY, JSON.stringify(DEMO_EMPLOYEES));
  return DEMO_EMPLOYEES;
}

function writeDemoEmployees(items: EmployeeListItem[]) {
  localStorage.setItem(EMP_STORAGE_KEY, JSON.stringify(items));
}

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export interface EmployeeListItem {
  id: string;
  employee_code: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  full_name: string;
  profile_photo: string | null;
  status: string;
  status_detail: { id: string; name: string; code: string; color_code: string } | null;
  department: string;
  designation: string;
  date_of_joining: string | null;
  work_email: string;
}

export interface EmployeeDirectoryFilters {
  search?: string;
  departmentId?: string;
  team?: string;
  teamId?: string;
  designationId?: string;
  status?: string;
  joiningFrom?: string;
  joiningTo?: string;
  page?: number;
  pageSize?: number;
}

export interface EmployeeDirectoryResponse {
  count: number;
  page: number;
  pageSize: number;
  pageCount: number;
  results: EmployeeDirectoryItem[];
}

export interface EmployeeDirectoryItem extends EmployeeListItem {
  department_id?: string | null;
  designation_id?: string | null;
  team_id?: string | null;
  team?: string | null;
  phone?: string | null;
  location?: string | null;
  status_display?: string | null;
}

export interface MasterOption {
  id: string;
  name: string;
  code: string;
  title?: string;
  label?: string;
  is_active?: boolean;
}

export interface InviteEmployeePayload {
  first_name: string;
  last_name: string;
  middle_name?: string;
  work_email: string;
  personal_mobile: string;
  gender: string;
  department: string;
  designation: string;
  employment_type?: string;
  date_of_joining: string;
  date_of_birth?: string;
  branch?: string;
  grade?: string;
  employee_category?: string;
  source_of_hire?: string;
  payroll_status?: string;
  transport_type?: string;
  cost_center?: string;
  shift_type?: string;
  payment_mode?: string;
  notice_period_days?: string;
}

export interface InviteResponse extends EmployeeListItem {
  invite_token: string;
  invite_link: string;
}

/* ------------------------------------------------------------------ */
/*  Hooks                                                              */
/* ------------------------------------------------------------------ */

async function fetchEmployees(): Promise<EmployeeListItem[]> {
  try {
    const res = await api.get('/employees/');
    const rows = res.data?.results ?? res.data?.data?.results ?? res.data?.data ?? res.data ?? [];
    if (Array.isArray(rows) && rows.length) {
      writeDemoEmployees(rows as EmployeeListItem[]);
      return rows as EmployeeListItem[];
    }
  } catch {
    // fallback to demo data
  }
  return readDemoEmployees();
}

async function fetchMaster(endpoint: string): Promise<MasterOption[]> {
  try {
    const res = await api.get(`/masters/${endpoint}/`);
    const rows = res.data?.results ?? res.data?.data?.results ?? res.data?.data ?? res.data ?? [];
    if (Array.isArray(rows) && rows.length) return rows as MasterOption[];
  } catch {
    // fallback below
  }

  const fallback: Record<string, MasterOption[]> = {
    departments: [
      { id: 'dept-1', name: 'Human Resources', code: 'HR' },
      { id: 'dept-2', name: 'Finance', code: 'FIN' },
      { id: 'dept-3', name: 'Engineering', code: 'ENG' },
    ],
    designations: [
      { id: 'desig-1', name: 'HR Manager', code: 'HRM' },
      { id: 'desig-2', name: 'Payroll Specialist', code: 'PAY' },
      { id: 'desig-3', name: 'Software Engineer', code: 'SWE' },
    ],
    genders: [
      { id: 'M', name: 'Male', code: 'M' },
      { id: 'F', name: 'Female', code: 'F' },
      { id: 'O', name: 'Other', code: 'O' },
    ],
    'employment-types': [
      { id: 'etype-1', name: 'Permanent', code: 'PERM' },
      { id: 'etype-2', name: 'Contract', code: 'CONT' },
      { id: 'etype-3', name: 'Intern', code: 'INT' },
    ],
    branches: [
      { id: 'br-1', name: 'Mumbai Branch', code: 'MUM-01' },
      { id: 'br-2', name: 'Pune Branch', code: 'PUN-01' },
    ],
    grades: [
      { id: 'gr-1', name: 'L1', code: 'L1' },
      { id: 'gr-2', name: 'L2', code: 'L2' },
      { id: 'gr-3', name: 'M1', code: 'M1' },
    ],
    'employee-categories': [
      { id: 'cat-1', name: 'Staff', code: 'STAFF' },
      { id: 'cat-2', name: 'Worker', code: 'WORKER' },
      { id: 'cat-3', name: 'Trainee', code: 'TRAINEE' },
    ],
    'source-of-hire': [
      { id: 'soh-1', name: 'Referral', code: 'REF' },
      { id: 'soh-2', name: 'LinkedIn', code: 'LI' },
      { id: 'soh-3', name: 'Campus', code: 'CAMP' },
    ],
    'payroll-statuses': [
      { id: 'ps-1', name: 'Active Payroll', code: 'ACTIVE' },
      { id: 'ps-2', name: 'On Hold', code: 'HOLD' },
    ],
    'transport-types': [
      { id: 'tt-1', name: 'Company Provided', code: 'COMPANY' },
      { id: 'tt-2', name: 'Own Vehicle', code: 'OWN' },
      { id: 'tt-3', name: 'Public Transport', code: 'PUBLIC' },
    ],
    'cost-centers': [
      { id: 'cc-1', name: 'IT Delivery', code: 'CC-IT-001' },
      { id: 'cc-2', name: 'Corporate HR', code: 'CC-HR-001' },
    ],
    'shift-types': [
      { id: 'st-1', name: 'Day', code: 'DAY' },
      { id: 'st-2', name: 'Night', code: 'NIGHT' },
      { id: 'st-3', name: 'Rotational', code: 'ROT' },
    ],
  };

  return fallback[endpoint] ?? [];
}

function extractRows<T>(payload: unknown): T[] {
  const data = payload as {
    results?: T[];
    data?: T[] | { results?: T[]; data?: T[] };
  };
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  if (data?.data && Array.isArray(data.data.results)) return data.data.results;
  if (data?.data && Array.isArray(data.data.data)) return data.data.data;
  return Array.isArray(payload) ? payload as T[] : [];
}

function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const payload = token.split('.')[1];
    if (!payload) return {};
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    return JSON.parse(atob(padded)) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function syncCompanyIdFromToken(token: string) {
  const companyId = decodeJwtPayload(token).company_id;
  if (typeof companyId === 'string' && companyId.trim()) {
    localStorage.setItem('hrms_company_id', companyId);
  }
}

async function refreshDirectoryAccessToken(): Promise<string | null> {
  const refresh = localStorage.getItem('hrms_refresh_token');
  if (!refresh) return null;

  const refreshUrls = [
    `${API_BASE_URL}/api/employee/refresh/`,
    `${API_BASE_URL}/api/employees/login/refresh/`,
  ];

  for (const url of refreshUrls) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (!response.ok) continue;
      const payload = (await response.json()) as { access?: string };
      if (!payload.access) continue;
      localStorage.setItem('hrms_access_token', payload.access);
      syncCompanyIdFromToken(payload.access);
      return payload.access;
    } catch {
      // Try the next known refresh endpoint.
    }
  }

  localStorage.removeItem('hrms_access_token');
  localStorage.removeItem('hrms_refresh_token');
  return null;
}

async function requestJson<T>(url: string): Promise<T> {
  const requestUrl = `${API_BASE_URL}${url}`;
  const buildHeaders = (token: string | null) => ({
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  });

  let token = localStorage.getItem('hrms_access_token');
  let response = await fetch(requestUrl, {
    credentials: 'include',
    headers: buildHeaders(token),
  });

  if (response.status === 401) {
    const refreshed = await refreshDirectoryAccessToken();
    if (refreshed) {
      token = refreshed;
      response = await fetch(requestUrl, {
        credentials: 'include',
        headers: buildHeaders(token),
      });
    }
  }

  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  const contentType = response.headers.get('Content-Type') ?? '';
  if (!contentType.includes('application/json')) {
    throw new Error(`Expected JSON from ${requestUrl}, received ${contentType || 'unknown content type'}`);
  }
  return response.json() as Promise<T>;
}

function normalizeMasterOption(row: MasterOption): MasterOption {
  const name = row.name ?? row.title ?? row.label ?? row.code ?? String(row.id);
  return {
    ...row,
    id: String(row.id),
    name,
    code: row.code ?? name,
  };
}

function normalizeDateParam(value?: string): string {
  const raw = value?.trim();
  if (!raw) return '';
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
  const match = raw.match(/^(\d{2})[-/](\d{2})[-/](\d{4})$/);
  if (!match) return raw;
  const [, day, month, year] = match;
  return `${year}-${month}-${day}`;
}

async function fetchOrganizationMaster(endpoint: 'departments' | 'teams' | 'designations'): Promise<MasterOption[]> {
  const params = new URLSearchParams();
  const companyId = localStorage.getItem('hrms_company_id');
  if (companyId) params.set('company_id', companyId);
  const query = params.toString();
  const payload = await requestJson<unknown>(`/api/masters/organization/${endpoint}/${query ? `?${query}` : ''}`);
  return extractRows<MasterOption>(payload)
    .filter((item) => item.is_active !== false)
    .map(normalizeMasterOption);
}

async function fetchEmployeeDirectory(filters: EmployeeDirectoryFilters): Promise<EmployeeDirectoryResponse> {
  const params = new URLSearchParams();
  const joiningFrom = normalizeDateParam(filters.joiningFrom);
  const joiningTo = normalizeDateParam(filters.joiningTo);
  const effectiveJoiningFrom = joiningFrom || joiningTo;
  const effectiveJoiningTo = joiningTo || joiningFrom;
  const page = Math.max(1, filters.page ?? 1);
  const pageSize = Math.min(100, Math.max(1, filters.pageSize ?? 12));

  if (filters.search?.trim()) params.set('search', filters.search.trim());
  if (filters.departmentId) params.set('department_id', filters.departmentId);
  if (filters.teamId) params.set('team_id', filters.teamId);
  if (filters.team) params.set('team', filters.team);
  if (filters.designationId) params.set('designation_id', filters.designationId);
  if (filters.status) params.set('status', filters.status);
  if (effectiveJoiningFrom) params.set('joining_from', effectiveJoiningFrom);
  if (effectiveJoiningTo) params.set('joining_to', effectiveJoiningTo);
  params.set('page', String(page));
  params.set('page_size', String(pageSize));
  const companyId = localStorage.getItem('hrms_company_id');
  if (companyId) params.set('company_id', companyId);

  const query = params.toString();
  const payload = await requestJson<{
    count?: number;
    page?: number;
    page_size?: number;
    page_count?: number;
    results?: EmployeeDirectoryItem[];
  }>(`/api/admin/employees/list/?${query}`);

  const results = extractRows<EmployeeDirectoryItem>(payload);
  const count = typeof payload?.count === 'number' ? payload.count : results.length;
  const resolvedPage = typeof payload?.page === 'number' ? payload.page : page;
  const resolvedPageSize = typeof payload?.page_size === 'number' ? payload.page_size : pageSize;
  const pageCount =
    typeof payload?.page_count === 'number'
      ? payload.page_count
      : Math.max(1, Math.ceil(count / resolvedPageSize) || 1);

  return {
    count,
    page: resolvedPage,
    pageSize: resolvedPageSize,
    pageCount,
    results,
  };
}

export function useEmployeeList() {
  return useQuery({
    queryKey: ['employees-list'],
    queryFn: fetchEmployees,
    staleTime: 60_000,
  });
}

export function useEmployeeDirectoryList(filters: EmployeeDirectoryFilters) {
  return useQuery({
    queryKey: [
      'admin-employee-directory',
      filters.search ?? '',
      filters.departmentId ?? '',
      filters.teamId ?? '',
      filters.team ?? '',
      filters.designationId ?? '',
      filters.status ?? 'active',
      filters.joiningFrom ?? '',
      filters.joiningTo ?? '',
      filters.page ?? 1,
      filters.pageSize ?? 12,
    ],
    queryFn: () => fetchEmployeeDirectory(filters),
    staleTime: 30_000,
    placeholderData: (prev) => prev,
    retry: 1,
  });
}

export function useOrganizationDepartments() {
  return useQuery({
    queryKey: ['organization-masters', 'departments'],
    queryFn: () => fetchOrganizationMaster('departments'),
    staleTime: 10 * 60_000,
  });
}

export function useOrganizationTeams() {
  return useQuery({
    queryKey: ['organization-masters', 'teams'],
    queryFn: () => fetchOrganizationMaster('teams'),
    staleTime: 10 * 60_000,
  });
}

export function useOrganizationDesignations() {
  return useQuery({
    queryKey: ['organization-masters', 'designations'],
    queryFn: () => fetchOrganizationMaster('designations'),
    staleTime: 10 * 60_000,
  });
}

export function useDepartments() {
  return useQuery({
    queryKey: ['masters-departments'],
    queryFn: () => fetchMaster('departments'),
    staleTime: 10 * 60_000,
  });
}

export function useDesignations() {
  return useQuery({
    queryKey: ['masters-designations'],
    queryFn: () => fetchMaster('designations'),
    staleTime: 10 * 60_000,
  });
}

export function useGenders() {
  return useQuery({
    queryKey: ['masters-genders'],
    queryFn: () => fetchMaster('genders'),
    staleTime: 10 * 60_000,
  });
}

export function useEmploymentTypes() {
  return useQuery({
    queryKey: ['masters-employment-types'],
    queryFn: () => fetchMaster('employment-types'),
    staleTime: 10 * 60_000,
  });
}

export function useBranches() {
  return useQuery({
    queryKey: ['masters-branches'],
    queryFn: () => fetchMaster('branches'),
    staleTime: 10 * 60_000,
  });
}

export function useGrades() {
  return useQuery({
    queryKey: ['masters-grades'],
    queryFn: () => fetchMaster('grades'),
    staleTime: 10 * 60_000,
  });
}

export function useEmployeeCategories() {
  return useQuery({
    queryKey: ['masters-employee-categories'],
    queryFn: () => fetchMaster('employee-categories'),
    staleTime: 10 * 60_000,
  });
}

export function useSourceOfHire() {
  return useQuery({
    queryKey: ['masters-source-of-hire'],
    queryFn: () => fetchMaster('source-of-hire'),
    staleTime: 10 * 60_000,
  });
}

export function usePayrollStatuses() {
  return useQuery({
    queryKey: ['masters-payroll-statuses'],
    queryFn: () => fetchMaster('payroll-statuses'),
    staleTime: 10 * 60_000,
  });
}

export function useTransportTypes() {
  return useQuery({
    queryKey: ['masters-transport-types'],
    queryFn: () => fetchMaster('transport-types'),
    staleTime: 10 * 60_000,
  });
}

export function useCostCenters() {
  return useQuery({
    queryKey: ['masters-cost-centers'],
    queryFn: () => fetchMaster('cost-centers'),
    staleTime: 10 * 60_000,
  });
}

export function useShiftTypes() {
  return useQuery({
    queryKey: ['masters-shift-types'],
    queryFn: () => fetchMaster('shift-types'),
    staleTime: 10 * 60_000,
  });
}

export function useAccountTypes() {
  return useQuery({
    queryKey: ['masters-account-types'],
    queryFn: () => fetchMaster('account-types'),
    staleTime: 10 * 60_000,
  });
}

export function useInviteEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: InviteEmployeePayload): Promise<InviteResponse> => {
      try {
        const res = await api.post('/employees/invite/', payload);
        return res.data;
      } catch {
        const current = readDemoEmployees();
        const nextCode = `EMP-${String(current.length + 1).padStart(4, '0')}`;
        const employee: EmployeeListItem = {
          id: crypto.randomUUID(),
          employee_code: nextCode,
          first_name: payload.first_name,
          middle_name: payload.middle_name ?? '',
          last_name: payload.last_name,
          full_name: [payload.first_name, payload.middle_name, payload.last_name].filter(Boolean).join(' '),
          profile_photo: null,
          status: 'ACTIVE',
          status_detail: { id: 'stat-1', name: 'Active', code: 'ACTIVE', color_code: '#10B981' },
          department: payload.department || 'Human Resources',
          designation: payload.designation || 'Employee',
          date_of_joining: payload.date_of_joining,
          work_email: payload.work_email,
        };
        writeDemoEmployees([employee, ...current]);
        return {
          ...employee,
          invite_token: crypto.randomUUID(),
          invite_link: `/setup-password?token=${encodeURIComponent(crypto.randomUUID())}`,
        };
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['employees-list'] });
    },
  });
}
