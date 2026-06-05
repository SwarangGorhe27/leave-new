import { useState, useEffect } from 'react';
import {
  EmployeeAttendanceApiError,
  fetchEmployeeAttendanceList,
} from '../api/employeeAttendanceClient';
import { mapEmployeeListRecordToDaily } from '../app/modules/employee-attendance/mappers';
import { DailyAttendance, AttendanceStatus } from '../app/modules/attendance/types';

export function useAttendanceData(monthKey: string) {
  const [data, setData] = useState<DailyAttendance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetchEmployeeAttendanceList({
          month: monthKey,
          per_page: 50,
          sort: 'date_desc',
        });

        if (isMounted) {
          const mappedData: DailyAttendance[] = response.records.map((record) =>
            mapEmployeeListRecordToDaily(record, {
              employeeId: '',
              employeeName: 'Me',
            }),
          );
          setData(mappedData);
          setError(null);
        }
      } catch (err: unknown) {
        if (isMounted) {
          console.error('Error fetching attendance data:', err);
          setError(
            err instanceof EmployeeAttendanceApiError
              ? err.message
              : 'Failed to fetch attendance data',
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    if (monthKey) {
      void fetchData();
    }

    return () => {
      isMounted = false;
    };
  }, [monthKey]);

  return { data, loading, error };
}

export function mapStatus(status: string): AttendanceStatus {
  switch (status?.toUpperCase()) {
    case 'PRESENT':
      return 'Present';
    case 'ABSENT':
      return 'Absent';
    case 'HALF_DAY':
      return 'Half Day';
    case 'LEAVE':
      return 'Leave';
    case 'HOLIDAY':
      return 'Holiday';
    case 'WEEK_OFF':
      return 'Week Off';
    default:
      return 'Absent';
  }
}
