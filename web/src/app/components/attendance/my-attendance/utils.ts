import { DailyAttendance } from "../../../modules/attendance/types";
import { isBefore, startOfMonth } from "date-fns";

export interface AttendanceMetrics {
  avgWorkHours: number;
  avgActualWorkHours: number;
  presentDays: number;
  absentDays: number;
  leaveTaken: number;
  lateInCount: number;
  totalWorkingDays: number;
  penaltyDays: number;
  earlyOutCount: number;
  firstInAvg: string;
  lastOutAvg: string;
  bestStreak: number;
  currentStreak: number;
  deltas?: {
    avgWorkHours: string;
    avgActualWork: string;
    presentDays: string;
    absentDays: string;
    leaveTaken: string;
    lateIn: string;
  };
}

/**
 * Checks if a date is locked (e.g. payroll processed).
 * For demo: any date before April 2026 is locked.
 */
export const isDateLocked = (date: Date): boolean => {
  const lockDate = new Date(2026, 3, 1); // April 1, 2026
  return isBefore(date, lockDate);
};

export const calculateMetrics = (records: DailyAttendance[]): AttendanceMetrics => {
  const presentRecords = records.filter(r => r.status === "Present" || r.status === "Half Day" || r.status === "Work From Home");
  const presentCount = records.filter(r => r.status === "Present" || r.status === "Work From Home").length;
  const halfDayCount = records.filter(r => r.status === "Half Day").length;
  
  const totalWorkHours = presentRecords.reduce((acc, r) => acc + (r.workHours || 0), 0);
  const avgWorkHours = presentRecords.length > 0 ? totalWorkHours / presentRecords.length : 0;
  
  const avgActualWorkHours = avgWorkHours * 0.95;

  const absentDays = records.filter(r => r.status === "Absent").length;
  const leaveTaken = records.filter(r => r.status === "Leave").length;
  const lateInCount = records.filter(r => r.isLate).length;
  const earlyOutCount = records.filter(r => (r.earlyExitMins || 0) > 0).length;
  
  const totalWorkingDays = records.filter(r => r.status !== "Week Off" && r.status !== "Holiday").length;
  
  let currentStreak = 0;
  let bestStreak = 0;
  let tempStreak = 0;
  
  const sortedRecords = [...records].sort((a, b) => a.date.localeCompare(b.date));
  
  sortedRecords.forEach(r => {
    if (r.status === "Present" || r.status === "Work From Home") {
      tempStreak++;
    } else if (r.status !== "Week Off" && r.status !== "Holiday") {
      if (tempStreak > bestStreak) bestStreak = tempStreak;
      tempStreak = 0;
    }
  });
  if (tempStreak > bestStreak) bestStreak = tempStreak;
  
  for (let i = sortedRecords.length - 1; i >= 0; i--) {
    const r = sortedRecords[i];
    if (r.status === "Present" || r.status === "Work From Home") {
      currentStreak++;
    } else if (r.status !== "Week Off" && r.status !== "Holiday") {
      break;
    }
  }

  return {
    avgWorkHours,
    avgActualWorkHours,
    presentDays: presentCount + (halfDayCount * 0.5),
    absentDays,
    leaveTaken,
    lateInCount,
    totalWorkingDays,
    penaltyDays: Math.floor(lateInCount / 3),
    earlyOutCount,
    firstInAvg: "09:08 AM",
    lastOutAvg: "06:12 PM",
    bestStreak,
    currentStreak
  };
};

export const getStatusColor = (status: string) => {
  switch (status) {
    case "Present": return "attendance-status-present";
    case "Absent": return "attendance-status-absent";
    case "Leave": return "attendance-status-leave";
    case "Holiday": return "attendance-status-holiday";
    case "Week Off": return "attendance-status-weekoff";
    case "Half Day": return "attendance-status-halfday";
    case "Work From Home": return "attendance-status-present";
    default: return "attendance-status-weekoff";
  }
};

export const getStatusDots = (record: DailyAttendance) => {
  const dots: string[] = [];
  
  if (record.status === "Present") dots.push("attendance-dot-present");
  if (record.status === "Absent") dots.push("attendance-dot-absent");
  if (record.status === "Leave") dots.push("attendance-dot-holiday");
  if (record.status === "Half Day") dots.push("attendance-dot-halfday");
  if (record.status === "Holiday") dots.push("attendance-dot-holiday");
  if (record.status === "Week Off") dots.push("attendance-dot-weekoff");
  if (record.status === "Work From Home") dots.push("attendance-dot-present");
  
  if (record.isLate) dots.push("attendance-dot-late");
  if (record.earlyExitMins && record.earlyExitMins > 0) dots.push("attendance-dot-early");
  
  return Array.from(new Set(dots)); // Unique dots
};
