import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import * as api from './api';
import {
  mapAttendanceRequestApi,
  mapDashboardSummaryToMetrics,
  mapDashboardWhosInToStats,
  mapIntelligenceToSwipeAnalytics,
  mapMatrixGridToPageData,
  mapRequestStats,
  mapRosterCalendarToUi,
  mapSwipeLiveSummaryToAnalytics,
  mapSwipeLogApi,
  mapTrendToChartData,
  mapWhoIsInEmployeeToDaily,
  mapWhoIsInSummaryToStats,
  mapDeviceDistributionToHealth,
  mapRosterShiftOptionsToDefinitions,
  mapShiftMastersToDefinitions,
  unwrapList,
  unwrapAttendanceData,
} from './mappers';
import type { RosterCalendarApi, WhoIsInStatus } from './apiTypes';
import type { ShiftDefinition } from './types';

export const attendanceKeys = {
  all: ['attendance'] as const,
  filters: () => [...attendanceKeys.all, 'filters'] as const,
  dashboardSummary: (m: number, y: number) => [...attendanceKeys.all, 'dashboard-summary', m, y] as const,
  dashboardTrend: (m: number, y: number) => [...attendanceKeys.all, 'dashboard-trend', m, y] as const,
  dashboardWhosIn: (m: number, y: number) => [...attendanceKeys.all, 'dashboard-whos-in', m, y] as const,
  whoIsInSummary: (d: string) => [...attendanceKeys.all, 'who-is-in-summary', d] as const,
  whoIsInEmployees: (d: string, s: WhoIsInStatus, search?: string, dept?: string) =>
    [...attendanceKeys.all, 'who-is-in-employees', d, s, search ?? '', dept ?? ''] as const,
  swipeLogs: (from?: string, to?: string, page?: number) =>
    [...attendanceKeys.all, 'swipe-logs', from ?? 'all', to ?? 'all', page ?? 1] as const,
  swipeLiveSummary: () => [...attendanceKeys.all, 'swipe-live-summary'] as const,
  intelligenceDashboard: () => [...attendanceKeys.all, 'intelligence-dashboard'] as const,
  matrixGrid: (y: number, m: number, p: number, dept?: string) =>
    [...attendanceKeys.all, 'matrix-grid', y, m, p, dept ?? ''] as const,
  matrixSummary: (y: number, m: number) => [...attendanceKeys.all, 'matrix-summary', y, m] as const,
  matrixDepartments: () => [...attendanceKeys.all, 'matrix-departments'] as const,
  rosterCalendar: (y: number, m: number, dept?: string) =>
    [...attendanceKeys.all, 'roster-calendar', y, m, dept ?? ''] as const,
  requests: (params: string) => [...attendanceKeys.all, 'requests', params] as const,
  requestStats: () => [...attendanceKeys.all, 'request-stats'] as const,
  employees: (search?: string) => [...attendanceKeys.all, 'employees', search ?? ''] as const,
  shiftMasters: () => [...attendanceKeys.all, 'shift-masters'] as const,
  deviceDistribution: () => [...attendanceKeys.all, 'device-distribution'] as const,
  employeeDayDetail: (empId: string, date: string) =>
    [...attendanceKeys.all, 'employee-day-detail', empId, date] as const,
};

// ─── Dashboard ───────────────────────────────────────────────────────────────

export function useDashboardSummary(month: number, year: number) {
  return useQuery({
    queryKey: attendanceKeys.dashboardSummary(month, year),
    queryFn: async () => mapDashboardSummaryToMetrics(await api.fetchDashboardSummary(month, year)),
    enabled: month >= 1 && month <= 12,
  });
}

export function useDashboardTrend(month: number, year: number) {
  return useQuery({
    queryKey: attendanceKeys.dashboardTrend(month, year),
    queryFn: async () => mapTrendToChartData(await api.fetchDashboardTrend(month, year)),
    enabled: month >= 1 && month <= 12,
  });
}

export function useDashboardWhosIn(month: number, year: number) {
  return useQuery({
    queryKey: attendanceKeys.dashboardWhosIn(month, year),
    queryFn: async () => mapDashboardWhosInToStats(await api.fetchDashboardWhosIn(month, year)),
  });
}

// ─── Who's In ────────────────────────────────────────────────────────────────

export function useWhoIsInSummary(date: Date) {
  const dateStr = format(date, 'yyyy-MM-dd');
  return useQuery({
    queryKey: attendanceKeys.whoIsInSummary(dateStr),
    queryFn: async () => mapWhoIsInSummaryToStats(await api.fetchWhoIsInSummary(dateStr)),
  });
}

export function useWhoIsInEmployees(
  date: Date,
  status: WhoIsInStatus,
  search?: string,
  departmentId?: string,
) {
  const dateStr = format(date, 'yyyy-MM-dd');
  return useQuery({
    queryKey: attendanceKeys.whoIsInEmployees(dateStr, status, search, departmentId),
    queryFn: async () => {
      const res = await api.fetchWhoIsInEmployees({
        date: dateStr,
        status,
        limit: 100,
        search: search || undefined,
        department_id: departmentId,
      });
      return (res.employees ?? []).map((e) => mapWhoIsInEmployeeToDaily(e, dateStr));
    },
  });
}

// ─── Swipe Logs ──────────────────────────────────────────────────────────────

export function useSwipeLogs(
  fromDate?: Date,
  toDate?: Date,
  page = 1,
  filters?: {
    search?: string;
    department_id?: string;
    punch_type?: string;
    punch_source?: string;
  },
) {
  const from = fromDate ? format(fromDate, 'yyyy-MM-dd') : undefined;
  const to = toDate ? format(toDate, 'yyyy-MM-dd') : undefined;
  const filterKey = JSON.stringify(filters ?? {});
  return useQuery({
    queryKey: [...attendanceKeys.swipeLogs(from, to, page), filterKey],
    queryFn: async () => {
      const res = await api.fetchSwipeLogs({
        ...(from ? { from_date: from } : {}),
        ...(to ? { to_date: to } : {}),
        limit: 500,
        page,
        employee_name: filters?.search || undefined,
        department_id: filters?.department_id,
        punch_type: filters?.punch_type && filters.punch_type !== 'all' ? filters.punch_type : undefined,
        punch_source: filters?.punch_source && filters.punch_source !== 'all' ? filters.punch_source : undefined,
      });
      return unwrapList(res).map(mapSwipeLogApi);
    },
  });
}

export function useDeviceDistribution() {
  return useQuery({
    queryKey: attendanceKeys.deviceDistribution(),
    queryFn: async () => {
      const res = await api.fetchIntelligenceDeviceDistribution();
      const list = Array.isArray(res) ? res : (res as { results?: unknown[] }).results ?? [];
      return mapDeviceDistributionToHealth(
        list as Array<{ device_id?: number; device_code?: string; device_name?: string; punch_count?: number }>,
      );
    },
    staleTime: 60_000,
  });
}

export function useEmployeeDayDetail(employeeId: string | undefined, date: Date | undefined) {
  const dateStr = date ? format(date, 'yyyy-MM-dd') : '';
  return useQuery({
    queryKey: attendanceKeys.employeeDayDetail(employeeId ?? '', dateStr),
    queryFn: () => api.fetchEmployeeDayDetail(employeeId!, dateStr),
    enabled: !!employeeId && !!dateStr,
  });
}

export function useSwipeLiveSummary() {
  return useQuery({
    queryKey: attendanceKeys.swipeLiveSummary(),
    queryFn: async () => {
      try {
        return mapSwipeLiveSummaryToAnalytics(await api.fetchSwipeLogsLiveSummary());
      } catch {
        return mapIntelligenceToSwipeAnalytics(await api.fetchIntelligenceDashboard());
      }
    },
  });
}

export function useCreateSwipeLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.createSwipeLog,
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

export function useDeleteSwipeLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.deleteSwipeLog,
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

// ─── Matrix ──────────────────────────────────────────────────────────────────

export function useMatrixGrid(
  year: number,
  month: number,
  page = 1,
  departmentId?: string,
  search?: string,
) {
  return useQuery({
    queryKey: attendanceKeys.matrixGrid(year, month, page, departmentId),
    queryFn: async () =>
      mapMatrixGridToPageData(
        await api.fetchMatrixGrid({
          year,
          month,
          page,
          page_size: 50,
          department_id: departmentId,
          search,
        }),
      ),
  });
}

export function useMatrixSummary(year: number, month: number) {
  return useQuery({
    queryKey: attendanceKeys.matrixSummary(year, month),
    queryFn: () => api.fetchMatrixSummary(year, month),
  });
}

export function useMatrixDepartments() {
  return useQuery({
    queryKey: attendanceKeys.matrixDepartments(),
    queryFn: async () => (await api.fetchMatrixDepartments()).departments ?? [],
  });
}

export function useUpdateMatrixDayStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ employeeId, date, status_code }: { employeeId: string; date: string; status_code: string }) =>
      api.updateEmployeeDayStatus(employeeId, { date, status_code }),
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

export function useImportMatrix() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.importMatrix,
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

// ─── Roster ──────────────────────────────────────────────────────────────────

export function useRosterCalendar(month: number, year: number, departmentId?: string) {
  return useQuery({
    queryKey: attendanceKeys.rosterCalendar(year, month, departmentId),
    queryFn: async () => {
      const [data, masters] = await Promise.all([
        api.fetchRosterCalendarMonthly(month, year, departmentId),
        api.fetchShiftMasters().then(unwrapList),
      ]);
      return { records: mapRosterCalendarToUi(data, masters), meta: data };
    },
  });
}

export function usePublishRoster() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.publishRoster,
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

export function useBulkShiftAssignment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.createBulkShiftAssignment,
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

export function useShiftMasters() {
  return useQuery({
    queryKey: attendanceKeys.shiftMasters(),
    queryFn: async () => unwrapList(await api.fetchShiftMasters()),
  });
}

export function useShiftDefinitions(
  month?: number,
  year?: number,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: [...attendanceKeys.shiftMasters(), 'definitions', year ?? '', month ?? ''],
    queryFn: async () => {
      const masters = unwrapList(await api.fetchShiftMasters());
      if (month != null && year != null) {
        const calendar = await api.fetchRosterCalendarMonthly(month, year);
        if (calendar.shift_options?.length) {
          return mapRosterShiftOptionsToDefinitions(calendar.shift_options);
        }
        return mapShiftMastersToDefinitions(masters);
      }
      return mapShiftMastersToDefinitions(masters);
    },
    enabled: options?.enabled !== false,
    staleTime: 5 * 60 * 1000,
  });
}

/** Prefer shift_options from loaded roster calendar to avoid a duplicate API call. */
export function resolveRosterShiftDefinitions(
  rosterMeta: RosterCalendarApi | undefined,
  fallback: ShiftDefinition[],
): ShiftDefinition[] {
  if (rosterMeta?.shift_options?.length) {
    return mapRosterShiftOptionsToDefinitions(rosterMeta.shift_options);
  }
  return fallback;
}

export function useMatrixCycleBounds(year: number, month: number) {
  return useQuery({
    queryKey: [...attendanceKeys.all, 'cycle-bounds', year, month],
    queryFn: () => api.fetchMatrixCycleBounds(year, month),
    enabled: month >= 1 && month <= 12,
  });
}

export function useCreateShiftAssignment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.createShiftAssignment,
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

export function useUnpublishRoster() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.unpublishRoster,
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

export function useExportRoster() {
  return useMutation({
    mutationFn: api.exportRosterFile,
  });
}

// ─── Requests ────────────────────────────────────────────────────────────────

export function useAttendanceRequests(params: {
  search?: string;
  request_type?: string;
  department?: string;
  status?: string;
  final_status?: string;
}) {
  const key = JSON.stringify(params);
  return useQuery({
    queryKey: attendanceKeys.requests(key),
    queryFn: async () => unwrapList(await api.fetchAttendanceRequests(params)).map(mapAttendanceRequestApi),
  });
}

export function useAttendanceRequestStats() {
  return useQuery({
    queryKey: attendanceKeys.requestStats(),
    queryFn: async () => mapRequestStats(await api.fetchAttendanceRequestStats()),
  });
}

export function useApproveAttendanceRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      api.approveAttendanceRequest(id, comment),
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

export function useRejectAttendanceRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      api.rejectAttendanceRequest(id, comment),
    onSuccess: () => qc.invalidateQueries({ queryKey: attendanceKeys.all }),
  });
}

// ─── Shared filters & employees ───────────────────────────────────────────────

export function useAttendanceFilterOptions() {
  return useQuery({
    queryKey: attendanceKeys.filters(),
    queryFn: async () => {
      const [dashboardFilters, matrixDepts, requestDeptsRaw, requestTypesRaw] = await Promise.all([
        api.fetchDashboardFilters().catch(() => ({ departments: [], designations: [], teams: [] })),
        api.fetchMatrixDepartments().catch(() => ({ departments: [] })),
        api.fetchRequestDepartments().catch(() => []),
        api.fetchRequestTypes().catch(() => []),
      ]);
      const requestDepts = unwrapList<{ id: string; name: string }>(requestDeptsRaw);
      const requestTypes = unwrapList<{ value: string; label: string }>(requestTypesRaw);
      const departments =
        dashboardFilters.departments?.length
          ? dashboardFilters.departments
          : matrixDepts.departments?.length
            ? matrixDepts.departments
            : requestDepts.map((d) => ({ id: d.id, name: d.name }));
      return {
        departments,
        designations: dashboardFilters.designations ?? [],
        teams: dashboardFilters.teams ?? [],
        requestTypes,
      };
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useAttendanceEmployees(search?: string) {
  return useQuery({
    queryKey: attendanceKeys.employees(search),
    queryFn: async () => unwrapList(await api.fetchAttendanceEmployees(search)),
  });
}
