export type AttendanceStatus = "Present" | "Absent" | "Half Day" | "Leave" | "Holiday" | "Week Off";
export type WorkMode = "WFO" | "WFH" | "Field";
export type RequestStatus = "Pending" | "Approved" | "Rejected";
export type RequestType = "Regularization" | "Leave" | "Overtime" | "Comp-Off";
export type SwipeStatus = "Approved" | "Pending" | "Rejected" | "Missing Punch" | "Duplicate Swipe" | "Late Entry" | "Early Exit";
export type DeviceType = "Biometric Device" | "Mobile App" | "Web Login" | "QR Attendance" | "RFID Card";

export interface EmployeeLite {
  id: string;
  name: string;
  department: string;
  location: string;
}

export interface DailyAttendance {
  id: string;
  employeeId: string;
  employeeName: string;
  department: string;
  designation: string;
  team: string;
  date: string;
  status: AttendanceStatus;
  workMode: WorkMode;
  shiftName: string;
  firstIn: string;
  lastOut: string;
  workHours: number;
  lateMins: number;
  earlyExitMins: number;
  lop: number;
  otMins: number;
  exception: boolean;
  exceptionType?: string;
  approvalPending: boolean;
  geoViolation: boolean;
  locked: boolean;
  isLate: boolean;
  isAbsent: boolean;
  isHalfDay: boolean;
  expectedInTime?: string;
  manager?: string;
  leaveBalance?: number;
  lastAttendanceDate?: string;
  avgLoginTime?: string;
  delayMins?: number;
  graceUsed?: boolean;
  lateLoginCycle?: string;
  deviceSource?: string;
  location?: string;
  leaveType?: string;
  leaveDuration?: string;
  returnDate?: string;
  contactNo?: string;
  email?: string;
}

export interface PunchLog {
  time: string;
  type: "IN" | "OUT";
  source: string;
}

export interface AttendanceException {
  id: string;
  employeeId: string;
  date: string;
  type: "Missing Punch" | "Late Cycle Trigger" | "Short Hours";
  status: "Resolved" | "Pending";
  severity: "Info" | "Warning" | "Critical";
  assignedTo?: string;
}

export interface AttendanceRequest {
  id: string;
  employeeId: string;
  employeeName?: string;
  type: RequestType;
  date: string;
  reason: string;
  status: "Pending" | "Approved" | "Rejected" | "Cancelled" | "Under Review";
  oldValue?: string;
  newValue?: string;
  comments?: string;
  workflowStep?: string;
  attendanceDate?: string;
  requestedStatus?: string;
  submittedDate?: string;
  lastUpdated?: string;
  approvedBy?: string;
  approvedDate?: string;
  rejectedBy?: string;
  rejectionReason?: string;
  rejectionDate?: string;
}

export interface AttendanceSession {
  id: string;
  employeeId: string;
  date: string;
  start: string;
  end: string;
  minutes: number;
}

export interface ShiftDefinition {
  id: string;
  /** Internal definition code (e.g. SD_US1_1600_0100) — used for API assignments. */
  code: string;
  /** User-facing label shown in roster cells and legend (e.g. "US 1 Shift"). */
  name: string;
  startTime: string;
  endTime: string;
  color: string;
  type: "General" | "Night" | "Rotational" | "Flexible";
}

export interface RosterRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  employeeCode: string;
  department: string;
  designation: string;
  team: string;
  avatar?: string;
  workingDays: number;
  weekOffs: number;
  shifts: { [date: string]: string }; // date (YYYY-MM-DD) -> shift display name or OFF
}

export interface RosterAnalytics {
  totalEmployees: number;
  totalWorkingDays: number;
  totalWeekOffs: number;
  nightShiftEmployees: number;
  rotationalShiftEmployees: number;
  flexibleShiftEmployees: number;
}

export interface SwipeLog {
  id: string;
  employeeId: string;
  employeeName: string;
  employeeCode: string;
  department: string;
  designation: string;
  avatar?: string;
  swipeTime: string;
  swipeDate: string;
  type: "IN" | "OUT";
  shiftName: string;
  shiftTiming: string;
  deviceName: string;
  deviceId: string;
  deviceType: DeviceType;
  accessCardId: string;
  branch: string;
  doorName: string;
  ipAddress: string;
  gpsCoordinates: string;
  receivedOn: string;
  syncTime: string;
  status: SwipeStatus;
  verificationMethod: "Face" | "Fingerprint" | "Mobile GPS" | "QR Scan" | "Card Tap";
  spoofDetection: "Safe" | "Suspicious" | "N/A";
  faceMatchScore?: number;
  workMode?: WorkMode;
}

export interface SwipeAnalytics {
  totalSwipesToday: number;
  totalInEntries: number;
  totalOutEntries: number;
  missingPunchCount: number;
  lateEntryCount: number;
  deviceOfflineCount: number;
  wfhAttendanceCount: number;
  officeAttendanceCount: number;
}

export interface DeviceHealth {
  id: string;
  name: string;
  status: "Online" | "Offline" | "Error";
  lastSyncTime: string;
  batteryStatus: number;
  location: string;
}
