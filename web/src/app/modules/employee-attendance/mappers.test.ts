import { describe, expect, it } from 'vitest';
import {
  mapApiStatusToUi,
  mapEmployeeListRecordToDaily,
  mapSummaryToMetrics,
} from './mappers';
import type { ManagerAttendanceListRecord } from '../../../api/managerAttendanceTypes';

const meta = {
  employeeId: 'emp-1',
  employeeName: 'Alice',
  department: 'Engineering',
  designation: 'Developer',
};

describe('employee attendance mappers', () => {
  it('maps API status codes to UI labels', () => {
    expect(mapApiStatusToUi('PRESENT')).toBe('Present');
    expect(mapApiStatusToUi('HALF_DAY')).toBe('Half Day');
    expect(mapApiStatusToUi('WEEK_OFF')).toBe('Week Off');
    expect(mapApiStatusToUi('LATE_IN')).toBe('Present');
  });

  it('maps list record to DailyAttendance with formatted times', () => {
    const record: ManagerAttendanceListRecord & { shift_name?: string; late_mins?: number } = {
      id: 'r1',
      date: '2026-05-07',
      day_name: 'Thu',
      timing: { in: '09:05', out: '18:15' },
      work_mode: 'OFFICE',
      work_hours: 7.7,
      status: 'PRESENT',
      shift_name: 'General Shift',
      late_mins: 5,
      actions: { can_regularize: false, can_share: true },
    };
    const daily = mapEmployeeListRecordToDaily(record, meta);
    expect(daily.status).toBe('Present');
    expect(daily.firstIn).toBe('09:05 AM');
    expect(daily.lastOut).toBe('06:15 PM');
    expect(daily.isLate).toBe(true);
    expect(daily.shiftName).toBe('General Shift');
  });

  it('maps summary API to metrics with deltas', () => {
    const records = [
      mapEmployeeListRecordToDaily(
        {
          date: '2026-05-07',
          day_name: 'Thu',
          timing: { in: '09:00', out: '18:00' },
          work_mode: 'OFFICE',
          work_hours: 8,
          status: 'PRESENT',
          actions: { can_regularize: false, can_share: true },
        },
        meta,
      ),
    ];
    const metrics = mapSummaryToMetrics(
      {
        avg_work_hours: 7.9,
        avg_actual_work: 7.5,
        present_days: 19.5,
        absent_days: 1,
        leave_taken: 0,
        late_in: 5,
        month: '2026-05',
        deltas: {
          avg_work_hours: { pct_change: 5 },
          avg_actual_work: { pct_change: -2 },
          present_days: { count_change: 0 },
          absent_days: { count_change: 1 },
          leave_taken: { count_change: 0 },
          late_in: { count_change: 2 },
        },
      },
      records,
    );
    expect(metrics.avgWorkHours).toBe(7.9);
    expect(metrics.presentDays).toBe(19.5);
    expect(metrics.deltas?.avgWorkHours).toBe('+5%');
    expect(metrics.deltas?.lateIn).toBe('+2');
  });
});
