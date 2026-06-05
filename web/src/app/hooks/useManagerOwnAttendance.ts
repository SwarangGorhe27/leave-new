import { useCallback, useEffect, useState } from 'react';
import { format } from 'date-fns';
import {
  fetchManagerOwnAttendanceList,
  ManagerAttendanceApiError,
} from '../../api/managerAttendanceClient';
import { mapManagerListRecordToDaily } from '../modules/manager-attendance/mappers';
import type { DailyAttendance } from '../modules/attendance/types';

export interface UseManagerOwnAttendanceOptions {
  monthDate: Date;
  employeeId?: string;
  employeeName?: string;
  department?: string;
  designation?: string;
}

export function useManagerOwnAttendance({
  monthDate,
  employeeId = '',
  employeeName = 'Me',
  department = '',
  designation = '',
}: UseManagerOwnAttendanceOptions) {
  const [records, setRecords] = useState<DailyAttendance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const monthKey = format(monthDate, 'yyyy-MM');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchManagerOwnAttendanceList({
        month: monthKey,
        per_page: 50,
        sort: 'date_desc',
      });
      const mapped = data.records.map((record) =>
        mapManagerListRecordToDaily(record, {
          employeeId,
          employeeName,
          department,
          designation,
        }),
      );
      setRecords(mapped);
    } catch (err) {
      const message =
        err instanceof ManagerAttendanceApiError
          ? err.message
          : 'Failed to load attendance. Please try again.';
      setError(message);
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, [monthKey, employeeId, employeeName, department, designation]);

  useEffect(() => {
    void load();
  }, [load]);

  return { records, loading, error, reload: load, monthKey };
}
