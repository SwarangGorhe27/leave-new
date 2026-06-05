import { format, parseISO } from 'date-fns';
import type {
  AttendanceRequestApi,
  AttendanceRequestStatsApi,
  DashboardSummaryApi,
  DashboardTrendApi,
  DashboardWhosInApi,
  IntelligenceDashboardApi,
  MatrixGridApi,
  MatrixRowApi,
  PaginatedResponse,
  RosterCalendarApi,
  RosterShiftOptionApi,
  SwipeLiveSummaryApi,
  SwipeLogApi,
  WhoIsInEmployeeApi,
  WhoIsInSummaryApi,
} from './apiTypes';
import type { DailyAttendance, DeviceHealth, RosterRecord, ShiftDefinition, SwipeLog } from './types';
import type { AttendanceStatus } from './types';
import type { ShiftMasterApi } from './apiTypes';

function toNumber(value: unknown, fallback = 0): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (value == null || value === '') return fallback;
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

export function mapDashboardSummaryToMetrics(summary: DashboardSummaryApi) {
  const totalPresent = toNumber(summary.total_present);
  const totalAbsent = toNumber(summary.total_absent);
  return {
    avgWorkHours: toNumber(summary.avg_work_hours),
    totalAbsent,
    holidays: toNumber(summary.total_holidays),
    lateLogins: toNumber(summary.total_late_logins),
    avgAttendance: totalPresent
      ? (totalPresent / Math.max(totalPresent + totalAbsent, 1)) * 100
      : 0,
    totalEmployees: 0,
  };
}

export function mapTrendToChartData(trend: DashboardTrendApi) {
  return (trend.trend_data ?? []).map((p) => ({
    day: p.date ? format(parseISO(p.date), 'dd MMM') : '',
    hours: toNumber(p.work_hours),
    employees: p.status === 'Present' ? 1 : 0,
  }));
}

export function mapWhoIsInSummaryToStats(summary: WhoIsInSummaryApi) {
  const s = summary.summary ?? {};
  return {
    onTime: toNumber(s.on_time),
    lateIn: toNumber(s.late_arrivals),
    notYetIn: toNumber(s.not_yet_in),
    onLeave: 0,
    outOfOffice: toNumber(s.out_of_office),
  };
}

function mapPresenceToStatus(emp: WhoIsInEmployeeApi): AttendanceStatus {
  if (emp.work_status_label?.toLowerCase().includes('leave')) return 'Leave';
  if (emp.presence_state === 'OUT' && !emp.login_time) return 'Absent';
  if (emp.is_late) return 'Present';
  if (emp.login_time) return 'Present';
  return 'Absent';
}

function formatLoginTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  try {
    return format(parseISO(iso), 'hh:mm a');
  } catch {
    return iso;
  }
}

export function mapWhoIsInEmployeeToDaily(
  emp: WhoIsInEmployeeApi,
  dateStr: string,
): DailyAttendance {
  const workMode =
    emp.work_mode === 'REMOTE' || emp.work_mode === 'WFH'
      ? 'WFH'
      : emp.work_mode === 'CLIENT_SITE'
        ? 'Field'
        : 'WFO';

  return {
    id: `${emp.employee_id}-${dateStr}`,
    employeeId: emp.employee_code ?? emp.employee_id,
    employeeName: emp.name,
    department: emp.department ?? '—',
    designation: emp.designation ?? '—',
    team: emp.team ?? '—',
    date: dateStr,
    status: mapPresenceToStatus(emp),
    workMode,
    shiftName: emp.shift ?? 'General',
    firstIn: formatLoginTime(emp.login_time),
    lastOut: '—',
    workHours: 0,
    lateMins: emp.is_late ? 1 : 0,
    earlyExitMins: 0,
    lop: 0,
    otMins: 0,
    exception: false,
    approvalPending: false,
    geoViolation: false,
    locked: false,
    isLate: !!emp.is_late,
    isAbsent: !emp.login_time && emp.presence_state !== 'IN',
    isHalfDay: false,
    expectedInTime: '09:00 AM',
    email: undefined,
  };
}

export function mapSwipeLogApi(row: SwipeLogApi): SwipeLog {
  const punchTime = row.punch_time ?? '';
  let swipeDate = '';
  let swipeTime = punchTime;
  try {
    const d = parseISO(punchTime);
    swipeDate = format(d, 'yyyy-MM-dd');
    swipeTime = format(d, 'hh:mm a');
  } catch {
    swipeDate = punchTime.slice(0, 10);
  }

  const deviceType =
    row.punch_source === 'BIOMETRIC'
      ? 'Biometric Device'
      : row.punch_source === 'MOBILE'
      ? 'Mobile App'
      : row.punch_source === 'WEB'
      ? 'Web Login'
      : 'RFID Card';

  return {
    id: String(row.id),
    employeeId: row.employee_id ?? '',
    employeeName: row.employee_name ?? '—',
    employeeCode: row.employee_code ?? '—',
    department: row.department_name ?? '—',
    designation: '—',
    swipeTime,
    swipeDate,
    type: row.punch_type === 'OUT' ? 'OUT' : 'IN',
    shiftName: row.shift_name ?? '—',
    shiftTiming: '—',
    deviceName: row.device_id ? String(row.device_id) : '—',
    deviceId: row.device_id ? String(row.device_id) : '—',
    deviceType,
    accessCardId: '—',
    branch: '—',
    doorName: '—',
    ipAddress: '—',
    gpsCoordinates: '—',
    receivedOn: punchTime,
    syncTime: punchTime,
    status: 'Approved',
    verificationMethod: 'Fingerprint',
    spoofDetection: 'N/A',
  };
}

const CELL_STATUS: Record<string, AttendanceStatus> = {
  P: 'Present',
  A: 'Absent',
  L: 'Leave',
  H: 'Holiday',
  W: 'Week Off',
  HD: 'Half Day',
};

export function mapMatrixRowToUi(row: MatrixRowApi, year: number, month: number): {
  employeeId: string;
  employeeName: string;
  employeeCode: string;
  department: string;
  days: Record<string, AttendanceStatus | string>;
} {
  const days: Record<string, AttendanceStatus | string> = {};
  row.days.forEach((cell) => {
    const code = cell.cell_code ?? cell.status_code ?? '';
    days[cell.date] = CELL_STATUS[code] ?? code;
  });
  return {
    employeeId: row.employee_id,
    employeeName: row.full_name,
    employeeCode: row.employee_code,
    department: row.department ?? '—',
    days,
  };
}

function isInternalShiftCode(code: string): boolean {
  const c = code.toUpperCase();
  return c.startsWith('SD_') || (c.length > 10 && c.includes('_'));
}

/** Map internal definition codes to legend display names (e.g. SD_US1_* → "US 1 Shift"). */
export function buildShiftNameDisplayMap(
  options?: RosterShiftOptionApi[],
  masters?: ShiftMasterApi[],
): Map<string, string> {
  const map = new Map<string, string>();

  for (const opt of options ?? []) {
    const name = (opt.name ?? '').trim();
    if (!name) continue;
    const def = (opt.definition_code ?? opt.code ?? '').toUpperCase();
    const code = (opt.code ?? '').toUpperCase();
    if (def) map.set(def, name);
    if (code) map.set(code, name);
    map.set(name.toUpperCase(), name);
    if (opt.start_time && opt.end_time) {
      map.set(`time:${opt.start_time}-${opt.end_time}`, name);
    }
  }

  for (const m of masters ?? []) {
    const name = (m.name ?? '').trim();
    if (!name) continue;
    const code = (m.code ?? '').toUpperCase();
    if (code) map.set(code, name);
    const start = m.start_time?.slice(0, 5);
    const end = m.end_time?.slice(0, 5);
    if (start && end) {
      map.set(`time:${start}-${end}`, name);
    }
  }

  return map;
}

export function findShiftDefinition(
  definitions: ShiftDefinition[],
  cellValue: string | undefined,
): ShiftDefinition | undefined {
  const v = (cellValue ?? '').trim();
  if (!v) return undefined;
  const upper = v.toUpperCase();
  return definitions.find(
    (s) =>
      s.name === v
      || s.code.toUpperCase() === upper
      || s.name.toUpperCase() === upper,
  );
}

export function getRosterShiftDisplayLabel(
  cellValue: string | undefined,
  definitions: ShiftDefinition[],
): string {
  const v = (cellValue ?? '').trim();
  if (!v) return '—';
  if (v.toUpperCase() === 'OFF' || v.toUpperCase() === 'WO' || v.toUpperCase() === 'HL') {
    return v.toUpperCase() === 'WO' ? 'Week Off' : v.toUpperCase() === 'HL' ? 'Holiday' : 'OFF';
  }
  const shift = findShiftDefinition(definitions, v);
  return shift?.name ?? v;
}

function resolveRosterShiftLabel(raw: string, nameMap: Map<string, string>): string {
  const trimmed = (raw ?? '').trim();
  if (!trimmed) return trimmed;
  const upper = trimmed.toUpperCase();
  if (upper === 'OFF' || upper === 'WO' || upper === 'HL') {
    return upper === 'WO' ? 'Week Off' : upper === 'HL' ? 'Holiday' : 'OFF';
  }
  const mapped = nameMap.get(upper);
  if (mapped) return mapped;
  if (!isInternalShiftCode(upper)) return trimmed;
  return trimmed;
}

export function mapRosterCalendarToUi(
  data: RosterCalendarApi,
  masters?: ShiftMasterApi[],
): RosterRecord[] {
  const nameMap = buildShiftNameDisplayMap(data.shift_options, masters);

  return (data.employees ?? []).map((emp) => {
    const shifts: Record<string, string> = {};
    for (const [date, raw] of Object.entries(emp.shifts ?? {})) {
      shifts[date] = resolveRosterShiftLabel(String(raw), nameMap);
    }
    return {
      id: emp.id,
      employeeId: emp.id,
      employeeName: emp.name,
      employeeCode: emp.code,
      department: emp.department ?? '—',
      designation: '—',
      team: '—',
      workingDays: Object.keys(shifts).filter((d) => shifts[d] !== 'OFF').length,
      weekOffs: Object.keys(shifts).filter((d) => shifts[d] === 'OFF').length,
      shifts,
    };
  });
}

export interface MatrixPageEmployee {
  id: string;
  employeeUuid: string;
  name: string;
  department: string;
  designation?: string;
  attendance: Record<string, { status: string; history: unknown[] }>;
}

/** Unwrap `{ data: T }` envelopes used by some attendance endpoints. */
export function unwrapAttendanceData<T>(payload: unknown): T {
  if (payload != null && typeof payload === 'object' && 'data' in payload) {
    return (payload as { data: T }).data;
  }
  return payload as T;
}

export function unwrapList<T>(data: unknown): T[] {
  const inner = unwrapAttendanceData<PaginatedResponse<T> | T[] | null | undefined>(data);
  if (!inner) return [];
  if (Array.isArray(inner)) return inner;
  if (typeof inner === 'object') {
    const obj = inner as Record<string, unknown>;
    if (Array.isArray(obj.results)) return obj.results as T[];
    if (Array.isArray(obj.requests)) return obj.requests as T[];
    if (Array.isArray(obj.items)) return obj.items as T[];
  }
  return [];
}

function capitalizeStatus(s: string): 'Pending' | 'Approved' | 'Rejected' {
  const lower = (s ?? '').toLowerCase();
  if (lower === 'approved') return 'Approved';
  if (lower === 'rejected') return 'Rejected';
  return 'Pending';
}

function mapAdminStatus(finalStatus: string): 'Pending' | 'Approved' | 'Rejected' {
  const lower = (finalStatus ?? '').toLowerCase();
  if (lower === 'fully_approved' || lower === 'approved') return 'Approved';
  if (lower === 'rejected') return 'Rejected';
  if (lower === 'pending_admin_approval') return 'Pending';
  return 'Pending';
}

export interface UiAttendanceRequest {
  id: string;
  employeeId: string;
  employeeName: string;
  department: string;
  designation: string;
  requestType: string;
  attendanceDate: string;
  submittedOn: string;
  managerStatus: 'Pending' | 'Approved' | 'Rejected';
  adminStatus: 'Pending' | 'Approved' | 'Rejected';
  reason: string;
  shiftTiming?: string;
  punchIn?: string;
  punchOut?: string;
  workingHours?: string;
  managerRemarks?: string;
  adminRemarks?: string;
  rawId: string;
}

export function mapAttendanceRequestApi(r: AttendanceRequestApi): UiAttendanceRequest {
  const wf = r.approval_workflow ?? [];
  const managerRemark = wf.find((w) => w.stage === 'manager')?.comment;
  const adminRemark = wf.find((w) => w.stage === 'admin')?.comment;
  const rawId = r.id.startsWith('REG-')
    ? r.id
    : r.id.replace(/^REQ-0*/, '');
  return {
    id: r.id,
    rawId,
    employeeId: r.employee?.id ?? '',
    employeeName: r.employee?.name ?? '—',
    department: r.employee?.department ?? '—',
    designation: r.employee?.designation ?? '—',
    requestType: r.request_type_display ?? r.request_type,
    attendanceDate: r.date,
    submittedOn: r.created_at?.slice(0, 10) ?? r.date,
    managerStatus: capitalizeStatus(r.manager_status),
    adminStatus: mapAdminStatus(r.final_status),
    reason: r.reason ?? '',
    shiftTiming: r.attendance?.shift_time,
    punchIn: r.attendance?.punch_in,
    punchOut: r.attendance?.punch_out,
    workingHours: r.attendance?.working_hours,
    managerRemarks: managerRemark,
    adminRemarks: adminRemark,
  };
}

export function mapRequestStats(stats: unknown) {
  const s = unwrapAttendanceData<AttendanceRequestStatsApi>(stats) ?? {};
  const row = s as AttendanceRequestStatsApi & Record<string, unknown>;
  return {
    pending: toNumber(row.pending_requests ?? row.pending),
    managerApproved: toNumber(row.approved_by_manager ?? row.manager_approved),
    pendingAdmin: toNumber(row.pending_admin),
    approved: toNumber(row.fully_approved),
    rejected: toNumber(row.rejected),
  };
}

export function mapSwipeLiveSummaryToAnalytics(s: SwipeLiveSummaryApi) {
  return {
    totalSwipesToday: toNumber(s.total_swipes_today),
    totalInEntries: toNumber(s.total_in),
    totalOutEntries: toNumber(s.total_out),
    missingPunchCount: toNumber(s.missing_punch_count),
    lateEntryCount: toNumber(s.late_entry_count),
    wfhAttendanceCount: toNumber(s.wfh_count),
    officeAttendanceCount: toNumber(s.office_count),
  };
}

export function mapIntelligenceToSwipeAnalytics(s: IntelligenceDashboardApi) {
  return {
    totalSwipesToday: toNumber(s.total_swipes_today),
    totalInEntries: toNumber(s.total_in_entries),
    totalOutEntries: toNumber(s.total_out_entries),
    missingPunchCount: toNumber(s.missing_punch_count),
    lateEntryCount: toNumber(s.late_entry_count),
    wfhAttendanceCount: toNumber(s.wfh_attendance_count),
    officeAttendanceCount: toNumber(s.office_attendance_count),
  };
}

export function mapDashboardWhosInToStats(d: DashboardWhosInApi) {
  return {
    onTime: toNumber(d.on_time),
    lateIn: toNumber(d.late),
    notYetIn: toNumber(d.not_yet_in),
    onLeave: toNumber(d.on_leave),
    outOfOffice: toNumber(d.out_of_office),
  };
}

const SHIFT_COLORS = [
  'bg-blue-500',
  'bg-indigo-600',
  'bg-emerald-500',
  'bg-amber-500',
  'bg-purple-500',
  'bg-cyan-500',
];

export function mapRosterShiftOptionsToDefinitions(
  options: RosterShiftOptionApi[],
): ShiftDefinition[] {
  const offCodes = new Set(['OFF', 'WO', 'HL']);
  return options.map((opt, i) => {
    const code = (opt.definition_code ?? opt.code ?? '').trim();
    const name = (opt.name ?? code).trim();
    return {
      id: opt.id,
      code,
      name,
      startTime: opt.start_time?.slice(0, 5) ?? '09:00',
      endTime: opt.end_time?.slice(0, 5) ?? '18:00',
      color: SHIFT_COLORS[i % SHIFT_COLORS.length],
      type: offCodes.has(code) ? 'General' : 'General',
    };
  });
}

export function mapShiftMastersToDefinitions(masters: ShiftMasterApi[]): ShiftDefinition[] {
  const offCodes = new Set(['OFF', 'WO', 'HL']);
  return masters.map((m, i) => {
    const code = (m.code ?? m.name ?? 'SHIFT').toUpperCase();
    return {
      id: m.id,
      code,
      name: m.name ?? code,
      startTime: m.start_time?.slice(0, 5) ?? '09:00',
      endTime: m.end_time?.slice(0, 5) ?? '18:00',
      color: SHIFT_COLORS[i % SHIFT_COLORS.length],
      type: offCodes.has(code) ? 'General' : 'General',
    };
  });
}

export function mapDeviceDistributionToHealth(
  items: Array<{ device_id?: number; device_code?: string; device_name?: string; punch_count?: number }>,
): DeviceHealth[] {
  return items.map((d) => ({
    id: String(d.device_id ?? d.device_code ?? ''),
    name: d.device_name ?? d.device_code ?? 'Device',
    status: (d.punch_count ?? 0) > 0 ? 'Online' : 'Offline',
    lastSyncTime: '—',
    batteryStatus: (d.punch_count ?? 0) > 0 ? 100 : 0,
    location: d.device_code ?? '—',
  }));
}

export function mapMatrixGridToPageData(grid: MatrixGridApi): MatrixPageEmployee[] {
  return (grid.rows ?? []).map((row) => {
    const attendance: MatrixPageEmployee['attendance'] = {};
    row.days.forEach((cell) => {
      attendance[cell.date] = {
        status: cell.cell_code ?? cell.status_code ?? 'MR',
        history: [],
      };
    });
    return {
      id: row.employee_code,
      employeeUuid: row.employee_id,
      name: row.full_name,
      department: row.department ?? '—',
      designation: row.designation ?? undefined,
      attendance,
    };
  });
}
