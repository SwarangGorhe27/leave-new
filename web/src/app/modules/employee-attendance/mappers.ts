import type { ManagerAttendanceListRecord } from '../../../api/managerAttendanceTypes';
import type { ManagerAttendanceSummaryResponse } from '../../../api/managerAttendanceTypes';
import type { RegularizationHistoryRecord } from '../../../api/employeeAttendanceClient';
import type { AttendanceStatus, DailyAttendance, WorkMode } from '../attendance/types';
import type { AttendanceRequest } from '../attendance/types';
import type { AttendanceMetrics } from '../../components/attendance/my-attendance/utils';

function formatTime12h(value: string | null | undefined): string {
  if (!value) return '';
  const match = /^(\d{1,2}):(\d{2})$/.exec(value.trim());
  if (!match) return value;
  let hours = Number(match[1]);
  const mins = match[2];
  const suffix = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12;
  return `${String(hours).padStart(2, '0')}:${mins} ${suffix}`;
}

export function mapApiStatusToUi(status: string): AttendanceStatus {
  const normalized = status.toUpperCase().replace(/\s+/g, '_');
  const map: Record<string, AttendanceStatus> = {
     P: 'Present',
    A: 'Absent',
    HD: 'Half Day',
    L: 'Leave',
    H: 'Holiday',
    WO: 'Week Off',
    PRESENT: 'Present',
    ABSENT: 'Absent',
    HALF_DAY: 'Half Day',
    HALFDAY: 'Half Day',
    LEAVE: 'Leave',
    ON_LEAVE: 'Leave',
    HOLIDAY: 'Holiday',
    WEEK_OFF: 'Week Off',
    WEEKOFF: 'Week Off',
    WORK_FROM_HOME: 'Present',
    WFH: 'Present',
    LATE_IN: 'Present',
  };
  return map[normalized] ?? 'Absent';
}

function mapWorkMode(value: string | null | undefined): WorkMode {
  const normalized = (value || '').toUpperCase();
  if (normalized.includes('REMOTE') || normalized.includes('WFH') || normalized.includes('HOME')) {
    return 'WFH';
  }
  if (normalized.includes('FIELD')) return 'Field';
  return 'WFO';
}

export function mapEmployeeListRecordToDaily(
  record: ManagerAttendanceListRecord,
  meta: { employeeId: string; employeeName: string; department?: string; designation?: string },
): DailyAttendance {
  const status = mapApiStatusToUi(record.status);
  const isLate =
    record.status.toUpperCase().includes('LATE') || ((record as { late_mins?: number }).late_mins ?? 0) > 0;
  const lateMins = (record as { late_mins?: number }).late_mins ?? 0;
  const earlyExitMins = (record as { early_exit_mins?: number }).early_exit_mins ?? 0;
  const otMins = (record as { ot_mins?: number }).ot_mins ?? 0;

  return {
    id: (record as { id?: string }).id ?? `${meta.employeeId}-${record.date}`,
    employeeId: meta.employeeId,
    employeeName: meta.employeeName,
    department: meta.department ?? '',
    designation: meta.designation ?? '',
    team: '',
    date: record.date,
    status,
    workMode: mapWorkMode(record.work_mode),
    shiftName: (record as { shift_name?: string }).shift_name || 'General Shift',
    firstIn: formatTime12h(record.timing?.in),
    lastOut: formatTime12h(record.timing?.out),
    workHours: record.work_hours ?? 0,
    lateMins,
    earlyExitMins,
    lop: 0,
    otMins,
    exception: isLate || earlyExitMins > 0,
    approvalPending: false,
    geoViolation: false,
    locked: false,
    isLate,
    isAbsent: status === 'Absent',
    isHalfDay: status === 'Half Day',
  };
}

function formatDelta(delta?: { pct_change?: number | null; count_change?: number | null }): string {
  if (!delta) return '—';
  if (delta.pct_change != null && Number.isFinite(delta.pct_change)) {
    const sign = delta.pct_change > 0 ? '+' : '';
    return `${sign}${Math.round(delta.pct_change)}%`;
  }
  if (delta.count_change != null) {
    const sign = delta.count_change > 0 ? '+' : '';
    return `${sign}${delta.count_change}`;
  }
  return 'Stable';
}

export function mapSummaryToMetrics(
  summary: ManagerAttendanceSummaryResponse,
  records: DailyAttendance[],
): AttendanceMetrics {
  const computed = records.reduce(
    (acc, record) => {
      if (record.isLate) acc.lateInCount += 1;
      if ((record.earlyExitMins || 0) > 0) acc.earlyOutCount += 1;
      return acc;
    },
    { lateInCount: 0, earlyOutCount: 0 },
  );

  return {
    avgWorkHours: summary.avg_work_hours,
    avgActualWorkHours: summary.avg_actual_work,
    presentDays: summary.present_days,
    absentDays: summary.absent_days,
    leaveTaken: summary.leave_taken,
    lateInCount: summary.late_in ?? computed.lateInCount,
    totalWorkingDays: records.filter((r) => r.status !== 'Week Off' && r.status !== 'Holiday').length,
    penaltyDays: 0,
    earlyOutCount: computed.earlyOutCount,
    firstInAvg: '—',
    lastOutAvg: '—',
    bestStreak: 0,
    currentStreak: 0,
    deltas: {
      avgWorkHours: formatDelta(summary.deltas?.avg_work_hours),
      avgActualWork: formatDelta(summary.deltas?.avg_actual_work),
      presentDays: formatDelta(summary.deltas?.present_days),
      absentDays: formatDelta(summary.deltas?.absent_days),
      leaveTaken: formatDelta(summary.deltas?.leave_taken),
      lateIn: formatDelta(summary.deltas?.late_in),
    },
  };
}

function mapRequestStatus(status: string): AttendanceRequest['status'] {
  const normalized = status.toUpperCase();
  if (normalized === 'APPROVED' || normalized === 'FULLY_APPROVED') return 'Approved';
  if (normalized === 'REJECTED') return 'Rejected';
  if (normalized === 'CANCELLED') return 'Cancelled';
  if (normalized === 'IN_REVIEW' || normalized === 'UNDER_REVIEW') return 'Under Review';
  return 'Pending';
}

export function mapRegularizationHistoryToRequest(
  record: RegularizationHistoryRecord,
  employeeId: string,
  employeeName: string,
): AttendanceRequest {
  return {
    id: record.regularization_id,
    employeeId,
    employeeName,
    type: 'Regularization',
    date: record.date,
    reason: record.reason || '',
    status: mapRequestStatus(record.status),
    attendanceDate: record.date,
    requestedStatus: record.requested_status,
    submittedDate: record.submitted_at || undefined,
    lastUpdated: record.reviewed_at || record.submitted_at || undefined,
    comments: record.reviewer_comment || undefined,
  };
}
