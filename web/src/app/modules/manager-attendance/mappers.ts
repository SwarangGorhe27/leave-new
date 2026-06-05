import type {
  ManagerAttendanceListRecord,
  TeamAttendanceMember,
  TeamAttendanceRecord,
  TeamAttendanceStatus,
} from '../../../api/managerAttendanceTypes';
import type { AttendanceStatus, DailyAttendance } from '../attendance/types';

const TEAM_STATUS_LABEL: Record<TeamAttendanceStatus, string> = {
  present: 'Present',
  absent: 'Absent',
  on_leave: 'Leave',
  late: 'Late',
  holiday: 'Holiday',
};

export function teamStatusLabel(status: TeamAttendanceStatus | string | undefined): string {
  if (!status) return 'No Record';
  return TEAM_STATUS_LABEL[status as TeamAttendanceStatus] ?? status;
}

function mapApiStatusToUi(status: string): AttendanceStatus {
  const normalized = status.toUpperCase().replace(/\s+/g, '_');
  const map: Record<string, AttendanceStatus> = {
    PRESENT: 'Present',
    ABSENT: 'Absent',
    HALF_DAY: 'Half Day',
    HALFDAY: 'Half Day',
    LEAVE: 'Leave',
    ON_LEAVE: 'Leave',
    HOLIDAY: 'Holiday',
    WEEK_OFF: 'Week Off',
    WEEKOFF: 'Week Off',
    LATE: 'Half Day',
  };
  return map[normalized] ?? 'Present';
}

function mapTeamStatusToUi(status: TeamAttendanceStatus | string): AttendanceStatus {
  const map: Record<string, AttendanceStatus> = {
    present: 'Present',
    absent: 'Absent',
    on_leave: 'Leave',
    late: 'Half Day',
    holiday: 'Holiday',
  };
  return map[status] ?? 'Present';
}

function emptyDailyAttendance(
  employeeId: string,
  employeeName: string,
  department: string,
  designation: string,
  date: string,
  partial?: Partial<DailyAttendance>,
): DailyAttendance {
  return {
    id: `${employeeId}-${date}`,
    employeeId,
    employeeName,
    department,
    designation,
    team: '',
    date,
    status: 'Absent',
    workMode: 'WFO',
    shiftName: '',
    firstIn: '',
    lastOut: '',
    workHours: 0,
    lateMins: 0,
    earlyExitMins: 0,
    lop: 0,
    otMins: 0,
    exception: false,
    approvalPending: false,
    geoViolation: false,
    locked: false,
    isLate: false,
    isAbsent: true,
    isHalfDay: false,
    ...partial,
  };
}

export function mapManagerListRecordToDaily(
  record: ManagerAttendanceListRecord,
  meta: { employeeId: string; employeeName: string; department: string; designation: string },
): DailyAttendance {
  const status = mapApiStatusToUi(record.status);
  const isLate = record.status.toUpperCase().includes('LATE');
  return emptyDailyAttendance(meta.employeeId, meta.employeeName, meta.department, meta.designation, record.date, {
    status,
    workMode: (record.work_mode as DailyAttendance['workMode']) || 'WFO',
    firstIn: record.timing?.in ?? '',
    lastOut: record.timing?.out ?? '',
    workHours: record.work_hours ?? 0,
    isLate,
    isAbsent: status === 'Absent',
    isHalfDay: status === 'Half Day',
    approvalPending: false,
  });
}

export function mapTeamRecordToDaily(
  record: TeamAttendanceRecord,
  meta: { employeeId: string; employeeName: string; department: string; designation: string },
): DailyAttendance {
  const status = mapTeamStatusToUi(record.status);
  const isLate = record.status === 'late';
  return emptyDailyAttendance(meta.employeeId, meta.employeeName, meta.department, meta.designation, record.date, {
    status,
    firstIn: record.check_in ?? '',
    lastOut: record.check_out ?? '',
    workHours: record.work_hours ?? 0,
    isLate,
    isAbsent: status === 'Absent',
    isHalfDay: status === 'Half Day',
  });
}

export function mapTeamMemberToTodayRecord(
  member: TeamAttendanceMember,
): DailyAttendance | undefined {
  const today = new Date().toISOString().slice(0, 10);
  const status = mapTeamStatusToUi(member.status);
  return emptyDailyAttendance(member.id, member.name, member.department ?? '', member.role, today, {
    status,
    firstIn: member.check_in ?? '',
    lastOut: member.check_out ?? '',
    workHours: member.work_hours ?? 0,
    isLate: member.status === 'late',
    isAbsent: member.status === 'absent',
    isHalfDay: status === 'Half Day',
  });
}

export function teamMemberDisplayId(member: TeamAttendanceMember): string {
  return member.employee_code ?? member.id;
}

export function teamMemberAvatar(member: TeamAttendanceMember): string {
  if (member.avatar_url) return member.avatar_url;
  const label = member.name?.trim()?.[0] ?? '?';
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(member.name)}&background=6366f1&color=fff&size=128&bold=true&format=svg&length=1&font-size=0.45&chars=${encodeURIComponent(label)}`;
}
