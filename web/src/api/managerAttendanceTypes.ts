/** Manager attendance API response types (mirror backend serializers). */

export type TeamAttendanceStatus =
  | 'present'
  | 'absent'
  | 'on_leave'
  | 'late'
  | 'holiday';

export interface TeamAttendanceMember {
  id: string;
  name: string;
  employee_code: string | null;
  role: string;
  department: string | null;
  status: TeamAttendanceStatus;
  check_in: string | null;
  check_out: string | null;
  work_hours: number;
  avatar_url: string | null;
}

export interface TeamAttendanceRecord {
  date: string;
  check_in: string | null;
  check_out: string | null;
  status: TeamAttendanceStatus;
  work_hours: number | null;
}

export interface TeamMemberAttendanceResponse {
  employee_id: string;
  total_hours: number;
  average_hours: number;
  present_days: number;
  absent_days: number;
  late_days: number;
  records: TeamAttendanceRecord[];
}

export interface TeamMemberStatsResponse {
  avg_work_hours: number;
  total_hours: number;
  attendance_score: number;
  absences: number;
  late_count: number;
  leave_days: number;
}

export interface TeamMemberProfileResponse {
  id: string;
  name: string;
  role: string;
  department: string | null;
  avatar_url: string | null;
  email: string;
  join_date: string | null;
}

export interface AttendanceTiming {
  in: string | null;
  out: string | null;
}

export interface ManagerAttendanceListRecord {
  id?: string;
  employee_id?: string;
  employee_name?: string | null;
  date: string;
  attendance_date?: string | null;
  day_name: string;
  timing: AttendanceTiming;
  punch_in_time?: string | null;
  punch_out_time?: string | null;
  work_mode: string | null;
  work_hours: number;
  working_hours?: number;
  status: string;
  status_label?: string | null;
  shift_id?: string | null;
  shift_code?: string | null;
  shift_name?: string | null;
  shift_details?: {
    id?: string | null;
    code?: string | null;
    name?: string | null;
    start_time?: string | null;
    end_time?: string | null;
  };
  late_mins?: number;
  early_exit_mins?: number;
  ot_mins?: number;
  is_locked?: boolean;
  actions: {
    can_regularize: boolean;
    can_share: boolean;
  };
}

export interface ManagerAttendanceListResponse {
  total: number;
  page: number;
  per_page: number;
  records: ManagerAttendanceListRecord[];
}

export interface ManagerAttendanceSummaryResponse {
  avg_work_hours: number;
  avg_actual_work: number;
  present_days: number;
  absent_days: number;
  leave_taken: number;
  late_in: number;
  deltas: Record<string, Record<string, number>>;
  month: string;
}

export interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
  errors?: unknown;
}

export interface ApprovalWorkflowStepInfo {
  step_order: number;
  approver_type: string;
}

export interface ManagerRegularizationListItem {
  id: string;
  employee_name: string;
  employee_code: string;
  department: string | null;
  regularization_date: string;
  reg_type: string;
  requested_in: string | null;
  requested_out: string | null;
  requested_status: string | null;
  status: string;
  current_step: ApprovalWorkflowStepInfo | null;
  created_at: string;
  days_waiting: number;
}

export interface ManagerRegularizationDetail extends ManagerRegularizationListItem {
  mode: string | null;
  permission_mins: number | null;
  justification: string | null;
  reason_option_label: string | null;
  timeline: ApprovalTimelineEntry[];
  updated_at: string;
  context_info: {
    existing_punch_in: string | null;
    existing_punch_out: string | null;
    previous_requests_count: number;
  };
}

export interface ManagerOTListItem {
  id: string;
  employee_name: string;
  employee_code: string;
  ot_date: string;
  claimed_ot_mins: number;
  status: string;
  current_step: ApprovalWorkflowStepInfo | null;
  created_at: string;
}

export interface ManagerOTDetail extends ManagerOTListItem {
  approved_ot_mins: number | null;
  reason: string | null;
  timeline: ApprovalTimelineEntry[];
  updated_at: string;
}

export interface ApprovalTimelineEntry {
  step_order: number | null;
  approver_type: string | null;
  approver_name: string | null;
  status: string;
  acted_at: string | null;
  remarks: string | null;
}

export interface ApproveRejectPayload {
  remarks?: string;
}

export interface OTApprovePayload extends ApproveRejectPayload {
  approved_ot_mins?: number | null;
}

export interface TeamAttendanceOverrideRequest {
  date: string;
  status: string;
  punch_in?: string | null;
  punch_out?: string | null;
}

export interface TeamAttendanceOverrideResponse {
  id: string;
  employee_id: string;
  date: string;
  status: string;
  punch_in: string | null;
  punch_out: string | null;
  created_at: string;
  updated_at: string;
}
