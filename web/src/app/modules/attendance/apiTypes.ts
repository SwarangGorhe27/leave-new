export interface PaginatedResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}

export interface FilterOption {
  id: string;
  name: string;
  code?: string;
}

export interface DashboardSummaryApi {
  avg_work_hours?: number | string;
  total_present?: number | string;
  total_absent?: number | string;
  total_holidays?: number | string;
  total_late_logins?: number | string;
  total_half_days?: number | string;
}

export interface DashboardTrendPointApi {
  date: string;
  day_name?: string;
  work_hours?: number | string;
  is_holiday?: boolean;
  is_weekend?: boolean;
  status?: string;
}

export interface DashboardTrendApi {
  month?: number;
  year?: number;
  trend_data?: DashboardTrendPointApi[];
}

export interface DashboardWhosInApi {
  on_time?: number;
  late?: number;
  not_yet_in?: number;
  on_leave?: number;
  out_of_office?: number;
}

export interface DashboardFilterApi {
  departments?: FilterOption[];
  designations?: FilterOption[];
  teams?: FilterOption[];
}

export type WhoIsInStatus = 'NOT_IN' | 'LATE' | 'ON_TIME' | 'OUT_OF_OFFICE';

export interface WhoIsInSummaryApi {
  summary?: {
    not_yet_in?: number;
    late_arrivals?: number;
    on_time?: number;
    out_of_office?: number;
    total_employees?: number;
  };
}

export interface WhoIsInEmployeeApi {
  employee_id: string;
  employee_code?: string | null;
  name: string;
  designation?: string | null;
  department?: string | null;
  team?: string | null;
  login_time?: string | null;
  shift?: string | null;
  work_mode?: string | null;
  work_status_label?: string | null;
  is_late?: boolean;
  presence_state?: string;
}

export interface WhoIsInEmployeesApi {
  employees: WhoIsInEmployeeApi[];
  total?: number;
  page?: number;
}

export interface WhoIsInLiveApi {
  summary?: WhoIsInSummaryApi['summary'];
  last_refreshed?: string;
}

export interface SwipeLogApi {
  id: string;
  company_id?: string;
  employee_id?: string;
  employee_code?: string;
  employee_name?: string;
  department_name?: string;
  punch_time: string;
  punch_type: string;
  punch_source?: string;
  device_id?: string | null;
  shift_name?: string | null;
  is_within_geofence?: boolean;
}

export type SwipeLogListApi = PaginatedResponse<SwipeLogApi> | SwipeLogApi[];

export interface SwipeLiveSummaryApi {
  total_swipes_today?: number;
  total_in?: number;
  total_out?: number;
  missing_punch_count?: number;
  late_entry_count?: number;
  wfh_count?: number;
  office_count?: number;
}

export interface MatrixDayCellApi {
  date: string;
  cell_code?: string | null;
  status_code?: string | null;
  work_mode?: string | null;
  is_late?: boolean;
}

export interface MatrixRowApi {
  employee_id: string;
  employee_code: string;
  full_name: string;
  department?: string | null;
  designation?: string | null;
  days: MatrixDayCellApi[];
  summary?: { present?: number; absent?: number; leave?: number };
}

export interface MatrixGridApi {
  meta?: {
    total_records?: number;
    page?: number;
    page_size?: number;
    dates?: Array<{ date: string; day_label?: string; is_weekend?: boolean; is_holiday?: boolean }>;
  };
  rows: MatrixRowApi[];
}

export interface MatrixSummaryApi {
  present?: number;
  absent?: number;
  leave?: number;
  late?: number;
}

export interface RosterCalendarEmployeeApi {
  id: string;
  name: string;
  code: string;
  department?: string | null;
  shifts: Record<string, string>;
}

/** Roster shift picker / legend — ShiftDefinition id with display code from Shift Master. */
export interface RosterShiftOptionApi {
  id: string;
  code: string;
  name: string;
  definition_code?: string;
  start_time?: string;
  end_time?: string;
}

export interface RosterCalendarApi {
  month: number;
  year: number;
  cycle_id?: string | null;
  cycle_start?: string;
  cycle_end?: string;
  employees: RosterCalendarEmployeeApi[];
  shift_options?: RosterShiftOptionApi[];
  holidays?: string[];
  is_published?: boolean;
  is_locked?: boolean;
}

export interface RosterPublishStatusApi {
  status?: string;
  data?: { is_published?: boolean; published_at?: string; published_by?: string };
}

export interface ShiftMasterApi {
  id: string;
  code?: string;
  name?: string;
  start_time?: string;
  end_time?: string;
}

export interface AttendanceRequestEmployeeApi {
  id: string;
  name: string;
  department?: string;
  designation?: string;
}

export interface AttendanceRequestApi {
  id: string;
  employee: AttendanceRequestEmployeeApi;
  request_type: string;
  request_type_display?: string;
  date: string;
  reason: string;
  manager_status: string;
  final_status: string;
  created_at?: string;
  attendance?: {
    date?: string;
    shift_time?: string;
    punch_in?: string;
    punch_out?: string;
    working_hours?: string;
  };
  approval_workflow?: Array<{ stage?: string; status?: string; comment?: string }>;
}

export interface AttendanceRequestStatsApi {
  pending?: number;
  manager_approved?: number;
  pending_admin?: number;
  fully_approved?: number;
  rejected?: number;
}

export interface IntelligenceDashboardApi {
  total_swipes_today?: number;
  total_in_entries?: number;
  total_out_entries?: number;
  missing_punch_count?: number;
  late_entry_count?: number;
  device_offline_count?: number;
  wfh_attendance_count?: number;
  office_attendance_count?: number;
}
