import {
  attendanceFetch,
  attendanceQuery,
  ATTENDANCE_BASE,
  getAccessToken,
  getCompanyId,
  getTenantSchema,
} from '../../../api/attendanceClient';
import type {
  AttendanceRequestApi,
  AttendanceRequestStatsApi,
  DashboardFilterApi,
  DashboardSummaryApi,
  DashboardTrendApi,
  DashboardWhosInApi,
  FilterOption,
  IntelligenceDashboardApi,
  MatrixGridApi,
  MatrixSummaryApi,
  PaginatedResponse,
  RosterCalendarApi,
  RosterPublishStatusApi,
  ShiftMasterApi,
  SwipeLiveSummaryApi,
  SwipeLogApi,
  SwipeLogListApi,
  WhoIsInEmployeesApi,
  WhoIsInLiveApi,
  WhoIsInStatus,
  WhoIsInSummaryApi,
} from './apiTypes';

function route(path: string, params?: Record<string, string | number | boolean | undefined | null>) {
  const q = attendanceQuery(params ?? {});
  return `${path}${q}`;
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export const fetchDashboardSummary = (month: number, year: number) =>
  attendanceFetch<DashboardSummaryApi>(route('/dashboard/summary', { month, year }));

export const fetchDashboardTrend = (month: number, year: number) =>
  attendanceFetch<DashboardTrendApi>(route('/dashboard/trend', { month, year }));

export const fetchDashboardWhosIn = (month?: number, year?: number) =>
  attendanceFetch<DashboardWhosInApi>(route('/dashboard/whos-in', { month, year }));

export const fetchDashboardEmployeePresence = (date: string) =>
  attendanceFetch<unknown>(route('/dashboard/employee-presence', { date }));

export const fetchDashboardLive = () =>
  attendanceFetch<unknown>(route('/dashboard/live'));

export const fetchDashboardFilters = () =>
  attendanceFetch<DashboardFilterApi>(route('/dashboard/filters'));

// ─── Who's In ────────────────────────────────────────────────────────────────

export const fetchWhoIsInSummary = (date: string) =>
  attendanceFetch<WhoIsInSummaryApi>(route('/who-is-in/summary/', { date }));

export const fetchWhoIsInEmployees = (params: {
  date: string;
  status: WhoIsInStatus;
  page?: number;
  limit?: number;
  search?: string;
  department_id?: string;
  designation_id?: string;
  team_id?: string;
  shift_id?: string;
}) => attendanceFetch<WhoIsInEmployeesApi>(route('/who-is-in/employees/', params));

export const fetchWhoIsInLive = (date: string) =>
  attendanceFetch<WhoIsInLiveApi>(route('/who-is-in/live/', { date }));

export const fetchEmployeeDailySummary = (employeeId: string, date: string) =>
  attendanceFetch<unknown>(route(`/employees/${employeeId}/daily-summary/`, { date }));

export const createManualPunch = (body: Record<string, unknown>) =>
  attendanceFetch<unknown>('/punch/', { method: 'POST', body: JSON.stringify(body) });

// ─── Swipe Logs ──────────────────────────────────────────────────────────────

export const fetchSwipeLogs = (params: {
  from_date?: string;
  to_date?: string;
  page?: number;
  limit?: number;
  employee_id?: string;
  employee_code?: string;
  employee_name?: string;
  department_id?: string;
  punch_type?: string;
  punch_source?: string;
  device_id?: string;
}) => attendanceFetch<SwipeLogListApi | SwipeLogApi[]>(route('/swipe-logs/', params));

export const fetchSwipeLog = (id: string) =>
  attendanceFetch<SwipeLogApi>(`/swipe-logs/${id}/`);

export const createSwipeLog = (body: Record<string, unknown>) =>
  attendanceFetch<SwipeLogApi>('/swipe-logs/', { method: 'POST', body: JSON.stringify(body) });

export const updateSwipeLog = (id: string, body: Record<string, unknown>) =>
  attendanceFetch<SwipeLogApi>(`/swipe-logs/${id}/`, { method: 'PATCH', body: JSON.stringify(body) });

export const deleteSwipeLog = (id: string) =>
  attendanceFetch<void>(`/swipe-logs/${id}/`, { method: 'DELETE' });

export const fetchSwipeLogsLive = (params?: { since?: string; limit?: number }) =>
  attendanceFetch<{ data?: SwipeLogApi[] }>(route('/swipe-logs/live/', params));

export const fetchSwipeLogsLiveSummary = () =>
  attendanceFetch<SwipeLiveSummaryApi>(route('/swipe-logs/live/summary/'));

export const bulkDeleteSwipeLogs = (ids: string[]) =>
  attendanceFetch<unknown>('/swipe-logs/bulk-delete/', {
    method: 'POST',
    body: JSON.stringify({ swipe_log_ids: ids }),
  });

export const triggerSwipeSync = () =>
  attendanceFetch<unknown>('/swipe-logs/sync/trigger/', { method: 'POST', body: '{}' });

export const exportSwipeLogs = (body: Record<string, unknown>) =>
  attendanceFetch<unknown>('/swipe-logs/export', { method: 'POST', body: JSON.stringify(body) });

// ─── Matrix ──────────────────────────────────────────────────────────────────

export const fetchMatrixGrid = (params: {
  year: number;
  month: number;
  page?: number;
  page_size?: number;
  department_id?: string;
  branch_id?: string;
  search?: string;
}) => attendanceFetch<MatrixGridApi>(route('/attendance-matrix/grid/', params));

export const fetchMatrixSummary = (year: number, month: number) =>
  attendanceFetch<MatrixSummaryApi>(route('/attendance-matrix/summary/', { year, month }));

export const fetchMatrixDepartments = () =>
  attendanceFetch<{ departments: FilterOption[] }>(route('/attendance-matrix/departments/'));

export const fetchMatrixLive = (branch_id?: string) =>
  attendanceFetch<unknown>(route('/attendance-matrix/live/', { branch_id }));

export const fetchMatrixCycleBounds = (year: number, month: number) =>
  attendanceFetch<unknown>(route('/attendance-matrix/cycle-bounds/', { year, month }));

export const importMatrix = (formData: FormData) =>
  attendanceFetch<unknown>('/attendance-matrix/import/', { method: 'POST', body: formData });

export const fetchEmployeeDayDetail = (employeeId: string, date: string) =>
  attendanceFetch<unknown>(route(`/attendance-matrix/employees/${employeeId}/day-detail/`, { date }));

export const updateEmployeeDayStatus = (
  employeeId: string,
  body: { date: string; status_code: string },
) =>
  attendanceFetch<unknown>(
    `/attendance-matrix/employees/${employeeId}/day-detail/update-status/`,
    { method: 'POST', body: JSON.stringify(body) },
  );

export const fetchEmployeeMonthlySummary = (employeeId: string, year: number, month: number) =>
  attendanceFetch<unknown>(
    route(`/attendance-matrix/employees/${employeeId}/monthly-summary/`, { year, month }),
  );

// ─── Roster ──────────────────────────────────────────────────────────────────

export const fetchRosterCalendarMonthly = (
  month: number,
  year: number,
  department_id?: string,
) =>
  attendanceFetch<RosterCalendarApi>(
    route('/roster-calendar/monthly/', { month, year, department_id }),
  );

export const fetchRosterCalendarDay = (date: string, department_id?: string) =>
  attendanceFetch<unknown>(route('/roster-calendar/day/', { date, department_id }));

export const fetchRosterConflicts = (month: number, year: number) =>
  attendanceFetch<unknown>(route('/roster-calendar/conflicts/', { month, year }));

export const publishRoster = (body: Record<string, unknown>) =>
  attendanceFetch<unknown>('/roster-publish/', { method: 'POST', body: JSON.stringify(body) });

export const unpublishRoster = (body: Record<string, unknown>) =>
  attendanceFetch<unknown>('/roster-unpublish/', { method: 'POST', body: JSON.stringify(body) });

export const fetchRosterPublishStatus = (job_id?: string) =>
  attendanceFetch<RosterPublishStatusApi>(
    route('/roster-publish-status/', job_id ? { job_id } : {}),
  );

export const fetchRosterPublishHistory = (year?: number) =>
  attendanceFetch<unknown>(route('/roster-publish-history/', { year }));

export const lockRoster = (body: Record<string, unknown>) =>
  attendanceFetch<unknown>('/roster-lock/', { method: 'POST', body: JSON.stringify(body) });

export const unlockRoster = (body: Record<string, unknown>) =>
  attendanceFetch<unknown>('/roster-unlock/', { method: 'POST', body: JSON.stringify(body) });

export const fetchRosterLockStatus = (month: number, year: number) =>
  attendanceFetch<unknown>(route('/roster-lock-status/', { month, year }));

export const createBulkShiftAssignment = (body: Record<string, unknown>) =>
  attendanceFetch<unknown>('/shift-assignments/bulk/', {
    method: 'POST',
    body: JSON.stringify(body),
  });

export const fetchShiftMasters = () =>
  attendanceFetch<PaginatedResponse<ShiftMasterApi> | ShiftMasterApi[]>(route('/shift-masters/'));

export const fetchShiftRosters = (params?: Record<string, string | number>) =>
  attendanceFetch<PaginatedResponse<unknown>>(route('/shift-rosters/', params));

// ─── Requests ────────────────────────────────────────────────────────────────

export const fetchAttendanceRequests = (params?: {
  search?: string;
  request_type?: string;
  department?: string;
  status?: string;
  manager_status?: string;
  final_status?: string;
  date_from?: string;
  date_to?: string;
}) => attendanceFetch<PaginatedResponse<AttendanceRequestApi> | AttendanceRequestApi[]>(
  route('/requests/', params),
);

export const fetchAttendanceRequestStats = () =>
  attendanceFetch<AttendanceRequestStatsApi>(route('/requests/stats/'));

export const fetchAttendanceRequest = (id: string) =>
  attendanceFetch<AttendanceRequestApi>(`/requests/${id}/`);

export const approveAttendanceRequest = (id: string, comment = '', stage = 'admin') =>
  attendanceFetch<AttendanceRequestApi>(`/requests/${id}/approve/`, {
    method: 'POST',
    body: JSON.stringify({ comment, stage }),
  });

export const rejectAttendanceRequest = (id: string, comment = '', stage = 'admin') =>
  attendanceFetch<AttendanceRequestApi>(`/requests/${id}/reject/`, {
    method: 'POST',
    body: JSON.stringify({ comment, stage }),
  });

export const fetchRequestDepartments = () =>
  attendanceFetch<FilterOption[]>(route('/departments/'));

export const fetchRequestTypes = () =>
  attendanceFetch<Array<{ value: string; label: string }>>(route('/request-types/'));

export const fetchAttendanceEmployees = (search?: string) =>
  attendanceFetch<PaginatedResponse<unknown> | unknown[]>(
    route('/employees/', search ? { search } : {}),
  );

// ─── Intelligence / Analytics ────────────────────────────────────────────────

export const fetchIntelligenceDashboard = (params?: Record<string, string>) =>
  attendanceFetch<IntelligenceDashboardApi>(route('/intelligence/dashboard/', params));

export const fetchIntelligenceTrends = (params?: Record<string, string>) =>
  attendanceFetch<unknown>(route('/intelligence/trends/', params));

export const fetchIntelligencePeakHours = (params?: Record<string, string>) =>
  attendanceFetch<unknown>(route('/intelligence/peak-hours/', params));

export const fetchIntelligenceDeviceDistribution = () =>
  attendanceFetch<unknown>(route('/intelligence/device-distribution/'));

export const fetchIntelligenceVerificationStats = () =>
  attendanceFetch<unknown>(route('/intelligence/verification-stats/'));

export const fetchIntelligenceMissingPunches = (params?: Record<string, string>) =>
  attendanceFetch<unknown>(route('/intelligence/missing-punches/', params));

export const fetchIntelligenceAnomalies = () =>
  attendanceFetch<unknown>(route('/intelligence/anomalies/'));

// ─── Shift assignments (single cell) ─────────────────────────────────────────

export const createShiftAssignment = (body: Record<string, unknown>) =>
  attendanceFetch<unknown>('/shift-assignments/', {
    method: 'POST',
    body: JSON.stringify(body),
  });

export const exportRosterFile = async (params: {
  month: number;
  year: number;
  format?: 'csv' | 'xlsx';
  department_id?: string;
}): Promise<Blob> => {
  const q = attendanceQuery({
    month: params.month,
    year: params.year,
    format: params.format ?? 'csv',
    department_id: params.department_id,
  });
  const access = getAccessToken();
  const headers: Record<string, string> = { Accept: '*/*', 'X-Tenant-Schema': getTenantSchema() };
  if (access) headers.Authorization = `Bearer ${access}`;
  const response = await fetch(`${ATTENDANCE_BASE}/shift-roster-export${q}`, { headers });
  if (!response.ok) {
    throw new Error(`Roster export failed (${response.status})`);
  }
  return response.blob();
};

export const fetchEntityAuditHistory = (params: {
  entity_type: string;
  entity_id: string;
  date_from?: string;
  date_to?: string;
}) => attendanceFetch<unknown>(route('/audit-logs/entity-history/', params));
