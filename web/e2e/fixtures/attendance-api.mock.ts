/** Mock API payloads for Playwright E2E (employee attendance). */

export const MOCK_SUMMARY = {
  success: true,
  message: '',
  data: {
    avg_work_hours: 7.9,
    avg_actual_work: 7.5,
    present_days: 19.5,
    absent_days: 1,
    leave_taken: 0,
    late_in: 5,
    month: '2026-05',
    deltas: {
      avg_work_hours: { pct_change: 5, count_change: null },
      avg_actual_work: { pct_change: -2, count_change: null },
      present_days: { pct_change: null, count_change: 0 },
      absent_days: { pct_change: null, count_change: 1 },
      leave_taken: { pct_change: null, count_change: 0 },
      late_in: { pct_change: null, count_change: 2 },
    },
  },
  errors: null,
};

export const MOCK_LIST = {
  success: true,
  message: '',
  data: {
    total: 2,
    page: 1,
    per_page: 50,
    records: [
      {
        id: 'rec-1',
        date: '2026-05-07',
        day_name: 'Thu',
        timing: { in: '09:05', out: '18:15' },
        work_mode: 'OFFICE',
        work_hours: 7.7,
        status: 'PRESENT',
        shift_name: 'General Shift',
        late_mins: 5,
        early_exit_mins: 0,
        ot_mins: 0,
        actions: { can_regularize: false, can_share: true },
      },
      {
        id: 'rec-2',
        date: '2026-05-08',
        day_name: 'Fri',
        timing: { in: null, out: null },
        work_mode: 'OFFICE',
        work_hours: 0,
        status: 'ABSENT',
        shift_name: 'General Shift',
        late_mins: 0,
        early_exit_mins: 0,
        ot_mins: 0,
        actions: { can_regularize: true, can_share: true },
      },
    ],
  },
  errors: null,
};

export const MOCK_PUNCH_DETAILS = {
  success: true,
  message: '',
  data: {
    date: '2026-05-07',
    status: 'PRESENT',
    punch_in: { time: '09:05', location: 'Main Entrance', status: 'Present' },
    punch_out: { time: '18:15', location: 'Main Gate Exit', status: 'Present' },
    shift: 'General Shift',
    work_hours: 7.7,
  },
  errors: null,
};

export const MOCK_REG_OPTIONS = {
  success: true,
  message: '',
  data: {
    request_types: ['Missing Punch', 'Late Arrival', 'Early Exit'],
    requested_statuses: ['Present', 'Half Day', 'Absent'],
  },
  errors: null,
};

export function employeeAuthStorage() {
  return {
    hrms_user: JSON.stringify({
      email: 'alice@e2e.test',
      role: 'employee',
      name: 'Alice Attendance',
      employeeId: 'e2e-emp-1',
      employeeCode: 'E2E001',
    }),
    hrms_access_token: 'e2e-test-access-token',
    hrms_refresh_token: 'e2e-test-refresh-token',
    hrms_company_id: 'e2e-company-1',
    hrms_tenant_schema: 'empatt',
  };
}
