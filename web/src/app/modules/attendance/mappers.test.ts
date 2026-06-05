import { describe, expect, it } from 'vitest';
import {
  buildShiftNameDisplayMap,
  unwrapList,
  mapRequestStats,
  mapDashboardSummaryToMetrics,
  mapRosterCalendarToUi,
  mapRosterShiftOptionsToDefinitions,
  mapWhoIsInSummaryToStats,
} from './mappers';
import type { DashboardSummaryApi, RosterCalendarApi, WhoIsInSummaryApi } from './apiTypes';

describe('attendance mappers', () => {
  it('maps dashboard summary metrics', () => {
    const summary: DashboardSummaryApi = {
      avg_work_hours: 8.5,
      total_present: 20,
      total_absent: 2,
      total_holidays: 1,
      total_late_logins: 3,
    };
    const metrics = mapDashboardSummaryToMetrics(summary);
    expect(metrics.avgWorkHours).toBe(8.5);
    expect(metrics.totalAbsent).toBe(2);
    expect(metrics.lateLogins).toBe(3);
  });

  it('maps who-is-in summary stats', () => {
    const api: WhoIsInSummaryApi = {
      summary: { on_time: 5, late_arrivals: 2, not_yet_in: 1, out_of_office: 3 },
    };
    expect(mapWhoIsInSummaryToStats(api)).toEqual({
      onTime: 5,
      lateIn: 2,
      notYetIn: 1,
      onLeave: 0,
      outOfOffice: 3,
    });
  });

  it('maps roster calendar using employee UUID for assignments', () => {
    const api: RosterCalendarApi = {
      month: 5,
      year: 2026,
      cycle_id: 'cycle-1',
      employees: [
        {
          id: 'emp-uuid-1',
          name: 'Jane Doe',
          code: 'E001',
          department: 'Engineering',
          shifts: { '2026-05-01': 'GEN' },
        },
      ],
    };
    const rows = mapRosterCalendarToUi(api);
    expect(rows[0].employeeId).toBe('emp-uuid-1');
    expect(rows[0].employeeCode).toBe('E001');
    expect(rows[0].shifts['2026-05-01']).toBe('GEN');
  });

  it('maps roster cells from internal definition codes to legend names', () => {
    const api: RosterCalendarApi = {
      month: 6,
      year: 2026,
      employees: [
        {
          id: 'emp-1',
          name: 'Rajesh Kumar',
          code: 'EMP001',
          shifts: { '2026-06-01': 'SD_US1_1600_0100', '2026-06-07': 'OFF' },
        },
      ],
      shift_options: [
        {
          id: 'def-1',
          code: 'SD_US1_1600_0100',
          name: 'US 1 Shift',
          definition_code: 'SD_US1_1600_0100',
          start_time: '16:00',
          end_time: '01:00',
        },
      ],
    };
    const rows = mapRosterCalendarToUi(api);
    expect(rows[0].shifts['2026-06-01']).toBe('US 1 Shift');
    expect(rows[0].shifts['2026-06-07']).toBe('OFF');
  });

  it('buildShiftNameDisplayMap links definition_code to shift name', () => {
    const map = buildShiftNameDisplayMap(
      [{ id: '1', code: 'SD_DAY_0930_1830', name: 'Day Shift', definition_code: 'SD_DAY_0930_1830', start_time: '09:30', end_time: '18:30' }],
      [],
    );
    expect(map.get('SD_DAY_0930_1830')).toBe('Day Shift');
  });

  it('unwrapList handles data envelope and results pagination', () => {
    expect(unwrapList({ data: [{ id: '1' }] })).toEqual([{ id: '1' }]);
    expect(unwrapList({ results: [{ id: '2' }] })).toEqual([{ id: '2' }]);
  });

  it('mapRequestStats reads backend field names', () => {
    expect(
      mapRequestStats({
        pending_requests: 2,
        approved_by_manager: 3,
        pending_admin: 1,
        fully_approved: 4,
        rejected: 1,
      }),
    ).toEqual({
      pending: 2,
      managerApproved: 3,
      pendingAdmin: 1,
      approved: 4,
      rejected: 1,
    });
  });

  it('maps roster shift_options to definitions with ShiftDefinition ids', () => {
    const defs = mapRosterShiftOptionsToDefinitions([
      {
        id: 'def-uuid-1',
        code: 'MG',
        name: 'Morning Shift',
        definition_code: 'SD_MORNING_0900_1800',
        start_time: '09:00',
        end_time: '18:00',
      },
    ]);
    expect(defs[0].id).toBe('def-uuid-1');
    expect(defs[0].code).toBe('SD_MORNING_0900_1800');
    expect(defs[0].name).toBe('Morning Shift');
    expect(defs[0].name).toBe('Morning Shift');
  });
});
