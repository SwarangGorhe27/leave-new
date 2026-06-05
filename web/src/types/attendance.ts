export type AttendanceCode = 'P' | 'A' | 'L' | 'H' | 'WO';

export interface AttendanceRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  designation: string;
  date: string;
  status: AttendanceCode;
  punchIn?: string;
  punchOut?: string;
  hours?: string;
}

export interface AttendanceSummaryStat {
  label: string;
  value: string;
  tone: 'success' | 'danger' | 'warning' | 'info' | 'neutral';
}
