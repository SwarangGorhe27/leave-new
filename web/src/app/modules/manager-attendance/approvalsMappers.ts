import type {
  ApprovalTimelineEntry,
  ManagerOTDetail,
  ManagerOTListItem,
  ManagerRegularizationDetail,
  ManagerRegularizationListItem,
} from '../../../api/managerAttendanceTypes';

export type ApprovalRowSource = 'local' | 'api-leave' | 'api-reg' | 'api-ot';

export type UiApprovalStatus = 'Pending' | 'Approved' | 'Rejected' | 'Sent Back' | 'Escalated';

export interface UnifiedApprovalRow {
  id: string;
  source: ApprovalRowSource;
  requestId: string;
  employeeName: string;
  employeeId: string;
  photoUrl: string;
  department: string;
  team: string;
  requestType: string;
  category: 'Attendance' | 'Leave' | 'Other';
  requestDate: string;
  effectiveDate: string;
  submittedOn: string;
  status: UiApprovalStatus;
  priority: 'Low' | 'Medium' | 'High';
  waitingDays: number;
  daysAffected: number;
  currentApprover: string;
  designation: string;
  reportingTo: string;
  reason: string;
  attachments: string[];
  commentsCount: number;
  existingData: string;
  leaveBalance: string;
  previousRequests: string;
  leaveTypeCode?: string;
  leaveTypeName?: string;
  fromDate?: string;
  toDate?: string;
  timeline: Array<{ step: string; date: string; actor: string; status: string; remarks?: string }>;
  /** Attendance API payloads for actions */
  attendanceRegId?: string;
  attendanceOtId?: string;
  claimedOtMins?: number;
}

function humanizeCode(value: string): string {
  return value
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function mapApiStatus(status: string | undefined): UiApprovalStatus {
  const normalized = (status ?? '').toUpperCase();
  if (normalized === 'APPROVED') return 'Approved';
  if (normalized === 'REJECTED') return 'Rejected';
  if (normalized === 'ESCALATED') return 'Escalated';
  if (normalized === 'SENT_BACK' || normalized === 'RETURNED') return 'Sent Back';
  return 'Pending';
}

function avatarFor(name: string, seed: string): string {
  return `https://api.dicebear.com/9.x/notionists/svg?seed=${encodeURIComponent(seed || name)}`;
}

function formatIsoDate(value: string | null | undefined): string {
  if (!value) return '';
  return value.slice(0, 10);
}

function formatTimeline(entries: ApprovalTimelineEntry[] | undefined): UnifiedApprovalRow['timeline'] {
  if (!entries?.length) return [];
  return entries.map((entry) => ({
    step: entry.approver_type
      ? `Step ${entry.step_order ?? '—'} · ${humanizeCode(entry.approver_type)}`
      : `Step ${entry.step_order ?? '—'}`,
    date: formatIsoDate(entry.acted_at) || '—',
    actor: entry.approver_name ?? '—',
    status: humanizeCode(entry.status),
    remarks: entry.remarks ?? undefined,
  }));
}

function currentApproverLabel(
  status: UiApprovalStatus,
  step: { step_order: number; approver_type: string } | null | undefined,
): string {
  if (status !== 'Pending') return 'Completed';
  if (!step) return 'You';
  return `Step ${step.step_order} · ${humanizeCode(step.approver_type)}`;
}

export function regularizationListToRow(item: ManagerRegularizationListItem): UnifiedApprovalRow {
  const status = mapApiStatus(item.status);
  const effectiveDate = formatIsoDate(item.regularization_date);
  const submittedOn = formatIsoDate(item.created_at);

  return {
    id: `reg-${item.id}`,
    source: 'api-reg',
    attendanceRegId: item.id,
    requestId: `REG-${item.id.slice(0, 8).toUpperCase()}`,
    employeeName: item.employee_name,
    employeeId: item.employee_code,
    photoUrl: avatarFor(item.employee_name, item.id),
    department: item.department ?? '—',
    team: '—',
    requestType: humanizeCode(item.reg_type),
    category: 'Attendance',
    requestDate: effectiveDate,
    effectiveDate,
    submittedOn,
    status,
    priority: item.days_waiting >= 3 ? 'High' : item.days_waiting >= 1 ? 'Medium' : 'Low',
    waitingDays: item.days_waiting ?? 0,
    daysAffected: 1,
    currentApprover: currentApproverLabel(status, item.current_step),
    designation: '—',
    reportingTo: '—',
    reason: `${humanizeCode(item.reg_type)} · ${effectiveDate}`,
    attachments: [],
    commentsCount: 0,
    existingData: buildRegExistingData(item),
    leaveBalance: 'N/A',
    previousRequests: '—',
    timeline: [
      {
        step: 'Submitted',
        date: submittedOn,
        actor: item.employee_name,
        status: 'Pending',
      },
    ],
  };
}

function buildRegExistingData(item: ManagerRegularizationListItem): string {
  const parts: string[] = [];
  if (item.requested_in) parts.push(`Requested in: ${item.requested_in}`);
  if (item.requested_out) parts.push(`Requested out: ${item.requested_out}`);
  if (item.requested_status) parts.push(`Requested status: ${humanizeCode(item.requested_status)}`);
  return parts.length ? parts.join(' · ') : 'No punch correction details.';
}

export function overtimeListToRow(item: ManagerOTListItem): UnifiedApprovalRow {
  const status = mapApiStatus(item.status);
  const effectiveDate = formatIsoDate(item.ot_date);
  const submittedOn = formatIsoDate(item.created_at);
  const otHours = Math.round((item.claimed_ot_mins / 60) * 10) / 10;

  return {
    id: `ot-${item.id}`,
    source: 'api-ot',
    attendanceOtId: item.id,
    claimedOtMins: item.claimed_ot_mins,
    requestId: `OT-${item.id.slice(0, 8).toUpperCase()}`,
    employeeName: item.employee_name,
    employeeId: item.employee_code,
    photoUrl: avatarFor(item.employee_name, item.id),
    department: '—',
    team: '—',
    requestType: 'Overtime',
    category: 'Attendance',
    requestDate: effectiveDate,
    effectiveDate,
    submittedOn,
    status,
    priority: 'Medium',
    waitingDays: Math.max(
      0,
      Math.floor((Date.now() - new Date(submittedOn).getTime()) / 86_400_000),
    ),
    daysAffected: otHours,
    currentApprover: currentApproverLabel(status, item.current_step),
    designation: '—',
    reportingTo: '—',
    reason: `Claimed ${item.claimed_ot_mins} minutes OT`,
    attachments: [],
    commentsCount: 0,
    existingData: `Claimed overtime: ${item.claimed_ot_mins} minutes (${otHours}h)`,
    leaveBalance: 'N/A',
    previousRequests: '—',
    timeline: [
      {
        step: 'Submitted',
        date: submittedOn,
        actor: item.employee_name,
        status: 'Pending',
      },
    ],
  };
}

export function mergeRegularizationDetail(row: UnifiedApprovalRow, detail: ManagerRegularizationDetail): UnifiedApprovalRow {
  const punchIn = detail.context_info?.existing_punch_in;
  const punchOut = detail.context_info?.existing_punch_out;
  const existingParts: string[] = [];
  if (punchIn) existingParts.push(`Existing in: ${String(punchIn).slice(11, 16) || punchIn}`);
  if (punchOut) existingParts.push(`Existing out: ${String(punchOut).slice(11, 16) || punchOut}`);
  if (detail.context_info?.previous_requests_count != null) {
    existingParts.push(`${detail.context_info.previous_requests_count} prior approved request(s)`);
  }

  return {
    ...row,
    reason: detail.justification || detail.reason_option_label || row.reason,
    existingData: existingParts.length ? existingParts.join(' · ') : row.existingData,
    previousRequests: `${detail.context_info?.previous_requests_count ?? 0} approved regularization(s)`,
    timeline: formatTimeline(detail.timeline).length
      ? formatTimeline(detail.timeline)
      : row.timeline,
    status: mapApiStatus(detail.status),
    waitingDays: detail.days_waiting ?? row.waitingDays,
    currentApprover: currentApproverLabel(mapApiStatus(detail.status), detail.current_step),
  };
}

export function mergeOvertimeDetail(row: UnifiedApprovalRow, detail: ManagerOTDetail): UnifiedApprovalRow {
  return {
    ...row,
    reason: detail.reason ?? row.reason,
    claimedOtMins: detail.claimed_ot_mins,
    existingData: `Claimed: ${detail.claimed_ot_mins} min${
      detail.approved_ot_mins != null ? ` · Approved: ${detail.approved_ot_mins} min` : ''
    }`,
    timeline: formatTimeline(detail.timeline).length ? formatTimeline(detail.timeline) : row.timeline,
    status: mapApiStatus(detail.status),
    currentApprover: currentApproverLabel(mapApiStatus(detail.status), detail.current_step),
  };
}
