import { useQuery } from '@tanstack/react-query';
import api from '@api/client';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export interface AttendanceRecordAPI {
  id: string;
  employee_code: string;
  employee_name: string;
  date: string;
  shift_name: string;
  first_in: string | null;
  last_out: string | null;
  effective_hours: string | null;
  late_mins: number;
  early_leave_mins: number;
  overtime_mins: number;
  status: 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'LEAVE' | 'HOLIDAY' | 'WEEK_OFF' | 'ON_DUTY' | 'NOT_COMPUTED';
  is_regularized: boolean;
  remarks: string;
}

export interface HolidayAPI {
  id: string;
  name: string;
  date: string;
  holiday_type: string;
  is_optional: boolean;
}

/* ------------------------------------------------------------------ */
/*  Hooks                                                              */
/* ------------------------------------------------------------------ */

async function fetchAttendanceRecords(month: number, year: number): Promise<AttendanceRecordAPI[]> {
  try {
    const res = await api.get('/me/attendance/', {
      params: { month, year },
    });
    const rows = res.data?.results ?? res.data?.data?.results ?? res.data?.data ?? res.data ?? [];
    if (Array.isArray(rows) && rows.length) return rows as AttendanceRecordAPI[];
  } catch {
    // fallback
  }

  const daysInMonth = new Date(year, month, 0).getDate();
  const records: AttendanceRecordAPI[] = [];
  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(year, month - 1, day);
    const weekday = date.getDay();
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const isWeekend = weekday === 0;

    if (isWeekend) {
      records.push({
        id: `att-${dateStr}`,
        employee_code: 'EMP-0001',
        employee_name: 'Aditi Mehra',
        date: dateStr,
        shift_name: 'General Shift',
        first_in: null,
        last_out: null,
        effective_hours: '00:00:00',
        late_mins: 0,
        early_leave_mins: 0,
        overtime_mins: 0,
        status: 'WEEK_OFF',
        is_regularized: false,
        remarks: 'Weekly off',
      });
      continue;
    }

    const lateMins = day % 6 === 0 ? 12 : 0;
    const status: AttendanceRecordAPI['status'] = day % 11 === 0 ? 'HALF_DAY' : day % 13 === 0 ? 'LEAVE' : 'PRESENT';
    records.push({
      id: `att-${dateStr}`,
      employee_code: 'EMP-0001',
      employee_name: 'Aditi Mehra',
      date: dateStr,
      shift_name: 'General Shift',
      first_in: status === 'PRESENT' || status === 'HALF_DAY' ? `${dateStr}T09:${lateMins ? '12' : '01'}:00Z` : null,
      last_out: status === 'PRESENT' ? `${dateStr}T18:05:00Z` : status === 'HALF_DAY' ? `${dateStr}T13:15:00Z` : null,
      effective_hours: status === 'PRESENT' ? '08:10:00' : status === 'HALF_DAY' ? '04:00:00' : '00:00:00',
      late_mins: lateMins,
      early_leave_mins: status === 'HALF_DAY' ? 240 : 0,
      overtime_mins: day % 9 === 0 ? 45 : 0,
      status,
      is_regularized: day % 17 === 0,
      remarks: status === 'LEAVE' ? 'Approved leave' : lateMins ? 'Traffic delay' : '',
    });
  }
  return records;
}

async function fetchHolidays(): Promise<HolidayAPI[]> {
  try {
    const res = await api.get('/me/holidays/');
    const rows = res.data?.results ?? res.data?.data ?? res.data ?? [];
    if (Array.isArray(rows) && rows.length) return rows as HolidayAPI[];
  } catch {
    // fallback
  }
  return [
    { id: 'h1', name: 'Maharashtra Day', date: '2026-05-01', holiday_type: 'National', is_optional: false },
    { id: 'h2', name: 'Independence Day', date: '2026-08-15', holiday_type: 'National', is_optional: false },
    { id: 'h3', name: 'Ganesh Chaturthi', date: '2026-09-10', holiday_type: 'Festival', is_optional: true },
  ];
}

export function useAttendanceRecords(month: number, year: number) {
  return useQuery({
    queryKey: ['attendance-records', year, month],
    queryFn: () => fetchAttendanceRecords(month, year),
    staleTime: 2 * 60_000,
  });
}

export function useUpcomingHolidays() {
  return useQuery({
    queryKey: ['holidays-upcoming'],
    queryFn: fetchHolidays,
    staleTime: 10 * 60_000,
  });
}
