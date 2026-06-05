import { DailyAttendance, AttendanceException, AttendanceRequest, ShiftDefinition, RosterRecord, SwipeLog, DeviceHealth } from "./types";

const DEPARTMENTS = ["Engineering", "Product", "Design", "HR", "Marketing", "Sales"];
const DESIGNATIONS = ["Software Engineer", "Senior Engineer", "Product Manager", "UI Designer", "HR Manager", "Marketing Lead"];
const TEAMS = ["Core Platform", "Mobile App", "User Experience", "Talent Acquisition", "Brand Growth"];
const SHIFTS = ["General Shift (09:00 - 18:00)", "Morning Shift (06:00 - 15:00)", "Evening Shift (14:00 - 23:00)"];

const EMPLOYEES = [
  { id: "EMP001", name: "Amit Sharma", dept: "Engineering", desig: "Senior Engineer", team: "Core Platform", email: "amit.s@company.com", contact: "+91 98765 43210", manager: "Rajesh Kumar" },
  { id: "EMP002", name: "Priya Patel", dept: "Product", desig: "Product Manager", team: "Mobile App", email: "priya.p@company.com", contact: "+91 98765 43211", manager: "Rajesh Kumar" },
  { id: "EMP003", name: "Rahul Verma", dept: "Design", desig: "UI Designer", team: "User Experience", email: "rahul.v@company.com", contact: "+91 98765 43212", manager: "Sonia Mehra" },
  { id: "EMP004", name: "Ananya Iyer", dept: "Engineering", desig: "Software Engineer", team: "Core Platform", email: "ananya.i@company.com", contact: "+91 98765 43213", manager: "Amit Sharma" },
  { id: "EMP005", name: "Siddharth Malhotra", dept: "HR", desig: "HR Manager", team: "Talent Acquisition", email: "sid.m@company.com", contact: "+91 98765 43214", manager: "Sonia Mehra" },
  { id: "EMP006", name: "Sneha Reddy", dept: "Marketing", desig: "Marketing Lead", team: "Brand Growth", email: "sneha.r@company.com", contact: "+91 98765 43215", manager: "Vikram Singh" },
  { id: "EMP007", name: "Vikram Singh", dept: "Engineering", desig: "Software Engineer", team: "Mobile App", email: "vikram.s@company.com", contact: "+91 98765 43216", manager: "Amit Sharma" },
  { id: "EMP008", name: "Kavita Joshi", dept: "Sales", desig: "Sales Lead", team: "Brand Growth", email: "kavita.j@company.com", contact: "+91 98765 43217", manager: "Vikram Singh" },
  { id: "EMP009", name: "Rohan Gupta", dept: "Engineering", desig: "Senior Engineer", team: "Core Platform", email: "rohan.g@company.com", contact: "+91 98765 43218", manager: "Amit Sharma" },
  { id: "EMP010", name: "Megha Rao", dept: "Product", desig: "Product Analyst", team: "Mobile App", email: "megha.r@company.com", contact: "+91 98765 43219", manager: "Priya Patel" },
];

export const SHIFT_DEFINITIONS: ShiftDefinition[] = [
  { id: "S1", code: "GEN", name: "General Shift", startTime: "09:00", endTime: "18:00", color: "bg-blue-500", type: "General" },
  { id: "S2", code: "NS", name: "Night Shift", startTime: "22:00", endTime: "07:00", color: "bg-indigo-600", type: "Night" },
  { id: "S3", code: "FS", name: "First Shift", startTime: "06:00", endTime: "15:00", color: "bg-emerald-500", type: "Rotational" },
  { id: "S4", code: "SS", name: "Second Shift", startTime: "14:00", endTime: "23:00", color: "bg-amber-500", type: "Rotational" },
  { id: "S5", code: "OFF", name: "Week Off", startTime: "00:00", endTime: "00:00", color: "bg-slate-200", type: "General" },
  { id: "S6", code: "WFH", name: "Work From Home", startTime: "09:00", endTime: "18:00", color: "bg-purple-500", type: "Flexible" },
  { id: "S7", code: "OD", name: "On Duty", startTime: "09:00", endTime: "18:00", color: "bg-cyan-500", type: "Flexible" },
  { id: "S8", code: "HL", name: "Holiday", startTime: "00:00", endTime: "00:00", color: "bg-red-200", type: "General" },
];

const generateAttendance = (month: number, year: number): DailyAttendance[] => {
  const data: DailyAttendance[] = [];
  const daysInMonth = new Date(year, month, 0).getDate();

  EMPLOYEES.forEach(emp => {
    for (let day = 1; day <= daysInMonth; day++) {
      const date = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const dayOfWeek = new Date(date).getDay();

      const baseRecord: Partial<DailyAttendance> = {
        id: `ATT-${emp.id}-${date}`,
        employeeId: emp.id,
        employeeName: emp.name,
        department: emp.dept,
        designation: emp.desig,
        team: emp.team,
        email: emp.email,
        contactNo: emp.contact,
        manager: emp.manager,
        date,
        shiftName: SHIFTS[0],
        expectedInTime: "09:00 AM",
        avgLoginTime: "09:05 AM",
        leaveBalance: 15,
        location: "Mumbai HQ",
        deviceSource: "Web Portal",
        lastAttendanceDate: `${year}-${String(month).padStart(2, '0')}-${String(day - 1).padStart(2, '0')}`,
      };

      if (dayOfWeek === 0 || dayOfWeek === 6) {
        data.push({
          ...(baseRecord as DailyAttendance),
          status: "Week Off",
          workMode: "WFO",
          workHours: 0,
          lateMins: 0,
          earlyExitMins: 0,
          lop: 0,
          otMins: 0,
          exception: false,
          approvalPending: false,
          geoViolation: false,
          locked: true,
          isLate: false,
          isAbsent: false,
          isHalfDay: false
        });
        continue;
      }

      const rand = Math.random();
      let status: any = "Present";
      let isAbsent = false;
      let isHalfDay = false;
      let isLate = Math.random() > 0.8;
      let workHours = 8 + (Math.random() * 2 - 1);
      let workMode: any = Math.random() > 0.8 ? "WFH" : "WFO";

      if (rand > 0.95) {
        status = "Absent";
        isAbsent = true;
        workHours = 0;
        isLate = false;
      } else if (rand > 0.9) {
        status = "Half Day";
        isHalfDay = true;
        workHours = 4;
      } else if (rand > 0.85) {
        status = "Leave";
        isAbsent = true;
        workHours = 0;
        isLate = false;
        baseRecord.leaveType = "Privilege Leave";
        baseRecord.leaveDuration = "1 Day";
        baseRecord.returnDate = `${year}-${String(month).padStart(2, '0')}-${String(day + 1).padStart(2, '0')}`;
      }

      data.push({
        ...(baseRecord as DailyAttendance),
        status,
        workMode,
        firstIn: status === "Present" ? (isLate ? "09:45 AM" : "09:05 AM") : "",
        lastOut: status === "Present" ? "06:15 PM" : "",
        workHours: status === "Present" ? workHours : (status === "Half Day" ? 4 : 0),
        lateMins: isLate ? 45 : 0,
        delayMins: isLate ? 45 : 0,
        earlyExitMins: 0,
        lop: isAbsent ? 1 : (isHalfDay ? 0.5 : 0),
        otMins: workHours > 8.5 ? (workHours - 8.5) * 60 : 0,
        exception: isLate || isAbsent,
        approvalPending: false,
        geoViolation: false,
        locked: false,
        isLate,
        isAbsent,
        isHalfDay,
        graceUsed: isLate && Math.random() > 0.5,
        lateLoginCycle: "Cycle 1 (1-15 May)",
      });
    }
  });

  return data;
};

const generateRoster = (month: number, year: number): RosterRecord[] => {
  const data: RosterRecord[] = [];
  const daysInMonth = new Date(year, month, 0).getDate();

  EMPLOYEES.forEach(emp => {
    const shifts: { [date: string]: string } = {};
    let workingDays = 0;
    let weekOffs = 0;

    for (let day = 1; day <= daysInMonth; day++) {
      const date = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const dayOfWeek = new Date(date).getDay();

      if (dayOfWeek === 0 || dayOfWeek === 6) {
        shifts[date] = "OFF";
        weekOffs++;
      } else {
        const rand = Math.random();
        if (rand > 0.95) shifts[date] = "HL";
        else if (rand > 0.9) shifts[date] = "NS";
        else if (rand > 0.85) shifts[date] = "WFH";
        else {
          shifts[date] = "GEN";
          workingDays++;
        }
      }
    }

    data.push({
      id: `ROSTER-${emp.id}`,
      employeeId: emp.id,
      employeeName: emp.name,
      employeeCode: emp.id,
      department: emp.dept,
      designation: emp.desig,
      team: emp.team,
      avatar: `${emp.id}`,
      workingDays,
      weekOffs,
      shifts,
    });
  });

  return data;
};

const generateSwipeLogs = (count: number): SwipeLog[] => {
  const data: SwipeLog[] = [];
  const deviceTypes: any[] = ["Biometric Device", "Mobile App", "Web Login", "QR Attendance", "RFID Card"];
  const verificationMethods: any[] = ["Face", "Fingerprint", "Mobile GPS", "QR Scan", "Card Tap"];
  const statuses: any[] = ["Approved", "Pending", "Rejected", "Missing Punch", "Duplicate Swipe", "Late Entry", "Early Exit"];
  const branches = ["Mumbai HQ", "Pune Office", "Bangalore Tech Park", "Delhi Regional"];
  const doors = ["Main Entrance", "Server Room", "Cafeteria", "South Wing Exit"];

  for (let i = 0; i < count; i++) {
    const emp = EMPLOYEES[Math.floor(Math.random() * EMPLOYEES.length)];
    const today = new Date();
    const isToday = Math.random() > 0.3;
    let dateStr = "";
    if (isToday) {
      dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    } else {
      const pastDate = new Date();
      pastDate.setDate(today.getDate() - (Math.floor(Math.random() * 10) + 1));
      dateStr = `${pastDate.getFullYear()}-${String(pastDate.getMonth() + 1).padStart(2, '0')}-${String(pastDate.getDate()).padStart(2, '0')}`;
    }
    const date = dateStr;
    const hour = Math.floor(Math.random() * 14) + 6; // 6 AM to 8 PM
    const min = Math.floor(Math.random() * 60);
    const sec = Math.floor(Math.random() * 60);
    const time = `${String(hour).padStart(2, '0')}:${String(min).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
    const type = Math.random() > 0.5 ? "IN" : "OUT";
    const deviceType = deviceTypes[Math.floor(Math.random() * deviceTypes.length)];
    const workMode = deviceType === "Mobile App" ? "WFH" : (deviceType === "Web Login" ? (Math.random() > 0.5 ? "WFH" : "WFO") : "WFO");

    data.push({
      id: `SWIPE-${i}`,
      employeeId: emp.id,
      employeeName: emp.name,
      employeeCode: emp.id,
      department: emp.dept,
      designation: emp.desig,
      avatar: `${emp.id}`,
      swipeDate: date,
      swipeTime: time,
      type: type as "IN" | "OUT",
      shiftName: "General Shift",
      shiftTiming: "09:00 - 18:00",
      deviceName: "BioMax-X990",
      deviceId: `DEV-${Math.floor(Math.random() * 1000)}`,
      deviceType: deviceType,
      accessCardId: `CRD-${Math.floor(Math.random() * 10000)}`,
      branch: branches[Math.floor(Math.random() * branches.length)],
      doorName: doors[Math.floor(Math.random() * doors.length)],
      ipAddress: `192.168.1.${Math.floor(Math.random() * 255)}`,
      gpsCoordinates: "19.0760° N, 72.8777° E",
      receivedOn: `${date} ${time}`,
      syncTime: `${date} ${time}`,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      verificationMethod: verificationMethods[Math.floor(Math.random() * verificationMethods.length)],
      spoofDetection: Math.random() > 0.9 ? "Suspicious" : "Safe",
      faceMatchScore: Math.random() > 0.8 ? 98.5 : undefined,
      workMode: workMode as "WFO" | "WFH" | "Field",
    });
  }

  return data.sort((a, b) => b.swipeTime.localeCompare(a.swipeTime));
};

export const MOCK_DEVICES: DeviceHealth[] = [
  { id: "D1", name: "BioMax Main Entry", status: "Online", lastSyncTime: "2026-05-11 10:15 AM", batteryStatus: 85, location: "Main Gate" },
  { id: "D2", name: "BioMax Cafeteria", status: "Online", lastSyncTime: "2026-05-11 10:10 AM", batteryStatus: 92, location: "Cafeteria" },
  { id: "D3", name: "QR Scanner North", status: "Offline", lastSyncTime: "2026-05-10 06:00 PM", batteryStatus: 0, location: "North Wing" },
  { id: "D4", name: "Mobile App Hub", status: "Online", lastSyncTime: "2026-05-11 10:18 AM", batteryStatus: 100, location: "Cloud" },
];

export const MOCK_ATTENDANCE: DailyAttendance[] = generateAttendance(5, 2026);
export const MOCK_ROSTER: RosterRecord[] = generateRoster(5, 2026);
export const MOCK_SWIPE_LOGS: SwipeLog[] = generateSwipeLogs(200);

export const MOCK_EXCEPTIONS: AttendanceException[] = [
  { id: "EXC1", employeeId: "EMP001", date: "2026-05-10", type: "Late Cycle Trigger", status: "Pending", severity: "Warning" },
  { id: "EXC2", employeeId: "EMP004", date: "2026-05-09", type: "Missing Punch", status: "Pending", severity: "Critical" },
];

export const MOCK_REQUESTS: AttendanceRequest[] = [
  // EMP001 - Amit Sharma
  { id: "REQ1", employeeId: "EMP001", employeeName: "Amit Sharma", type: "Regularization", date: "2026-05-07", attendanceDate: "2026-05-05", requestedStatus: "Present", reason: "Forgot to punch out during system maintenance", status: "Approved", submittedDate: "2026-05-07 09:15 AM", lastUpdated: "2026-05-08 02:30 PM", approvedBy: "Rajesh Kumar", approvedDate: "2026-05-08 02:30 PM" },
  { id: "REQ2", employeeId: "EMP001", employeeName: "Amit Sharma", type: "Regularization", date: "2026-05-03", attendanceDate: "2026-05-01", requestedStatus: "Present", reason: "Office access card issue, worked from home", status: "Approved", submittedDate: "2026-05-03 10:45 AM", lastUpdated: "2026-05-04 11:00 AM", approvedBy: "Rajesh Kumar", approvedDate: "2026-05-04 11:00 AM" },
  { id: "REQ3", employeeId: "EMP001", employeeName: "Amit Sharma", type: "Regularization", date: "2026-04-28", attendanceDate: "2026-04-26", requestedStatus: "Present", reason: "Attended client meeting, forgot morning punch", status: "Rejected", submittedDate: "2026-04-28 03:45 PM", lastUpdated: "2026-04-29 01:15 PM", rejectedBy: "Rajesh Kumar", rejectionReason: "Supporting documents not provided for client visit", rejectionDate: "2026-04-29 01:15 PM" },

  // EMP002 - Priya Patel
  { id: "REQ4", employeeId: "EMP002", employeeName: "Priya Patel", type: "Regularization", date: "2026-05-10", attendanceDate: "2026-05-08", requestedStatus: "Present", reason: "Forgot to punch out", status: "Pending", submittedDate: "2026-05-10 04:20 PM", lastUpdated: "2026-05-10 04:20 PM" },
  { id: "REQ5", employeeId: "EMP002", employeeName: "Priya Patel", type: "Regularization", date: "2026-05-06", attendanceDate: "2026-05-04", requestedStatus: "Present", reason: "Early exit - attended training session", status: "Approved", submittedDate: "2026-05-06 05:00 PM", lastUpdated: "2026-05-07 09:30 AM", approvedBy: "Rajesh Kumar", approvedDate: "2026-05-07 09:30 AM" },
  { id: "REQ6", employeeId: "EMP002", employeeName: "Priya Patel", type: "Regularization", date: "2026-04-30", attendanceDate: "2026-04-29", requestedStatus: "Half Day", reason: "Doctor appointment - left early", status: "Approved", submittedDate: "2026-04-30 01:00 PM", lastUpdated: "2026-05-01 10:15 AM", approvedBy: "Rajesh Kumar", approvedDate: "2026-05-01 10:15 AM" },

  // EMP003 - Rahul Verma
  { id: "REQ7", employeeId: "EMP003", employeeName: "Rahul Verma", type: "Regularization", date: "2026-05-09", attendanceDate: "2026-05-07", requestedStatus: "Present", reason: "Network issue prevented punch recording", status: "Under Review", submittedDate: "2026-05-09 02:15 PM", lastUpdated: "2026-05-09 02:15 PM" },
  { id: "REQ8", employeeId: "EMP003", employeeName: "Rahul Verma", type: "Regularization", date: "2026-05-02", attendanceDate: "2026-04-30", requestedStatus: "Present", reason: "Attended emergency client presentation", status: "Approved", submittedDate: "2026-05-02 06:00 PM", lastUpdated: "2026-05-03 11:45 AM", approvedBy: "Sonia Mehra", approvedDate: "2026-05-03 11:45 AM" },
  { id: "REQ9", employeeId: "EMP003", employeeName: "Rahul Verma", type: "Regularization", date: "2026-04-25", attendanceDate: "2026-04-23", requestedStatus: "Present", reason: "Forgot to punch in", status: "Rejected", submittedDate: "2026-04-25 10:30 AM", lastUpdated: "2026-04-26 03:00 PM", rejectedBy: "Sonia Mehra", rejectionReason: "Repeated violation - previous warning on file", rejectionDate: "2026-04-26 03:00 PM" },

  // EMP004 - Ananya Iyer  
  { id: "REQ10", employeeId: "EMP004", employeeName: "Ananya Iyer", type: "Regularization", date: "2026-05-11", attendanceDate: "2026-05-09", requestedStatus: "Present", reason: "Mobile app crash, worked on desktop instead", status: "Pending", submittedDate: "2026-05-11 03:30 PM", lastUpdated: "2026-05-11 03:30 PM" },
  { id: "REQ11", employeeId: "EMP004", employeeName: "Ananya Iyer", type: "Regularization", date: "2026-05-05", attendanceDate: "2026-05-03", requestedStatus: "Half Day", reason: "Medical emergency", status: "Approved", submittedDate: "2026-05-05 02:00 PM", lastUpdated: "2026-05-06 08:30 AM", approvedBy: "Amit Sharma", approvedDate: "2026-05-06 08:30 AM" },

  // EMP005 - Siddharth Malhotra
  { id: "REQ12", employeeId: "EMP005", employeeName: "Siddharth Malhotra", type: "Regularization", date: "2026-05-08", attendanceDate: "2026-05-06", requestedStatus: "Present", reason: "Attended HR conference, field work", status: "Approved", submittedDate: "2026-05-08 04:45 PM", lastUpdated: "2026-05-09 09:00 AM", approvedBy: "Sonia Mehra", approvedDate: "2026-05-09 09:00 AM" },
  { id: "REQ13", employeeId: "EMP005", employeeName: "Siddharth Malhotra", type: "Regularization", date: "2026-04-29", attendanceDate: "2026-04-27", requestedStatus: "Present", reason: "Biometric reader malfunction", status: "Cancelled", submittedDate: "2026-04-29 11:00 AM", lastUpdated: "2026-04-29 02:15 PM" },

  // EMP006 - Sneha Reddy
  { id: "REQ14", employeeId: "EMP006", employeeName: "Sneha Reddy", type: "Regularization", date: "2026-05-04", attendanceDate: "2026-05-02", requestedStatus: "Present", reason: "Client visit - spent entire day offsite", status: "Approved", submittedDate: "2026-05-04 06:15 PM", lastUpdated: "2026-05-05 10:30 AM", approvedBy: "Vikram Singh", approvedDate: "2026-05-05 10:30 AM" },
];

export const MOCK_ATTENDANCE_DATA: DailyAttendance[] = generateAttendance(5, 2026);

const generateMatrixData = (month: number, year: number): any[] => {
  const data: any[] = [];
  const daysInMonth = new Date(year, month, 0).getDate();
  
  EMPLOYEES.forEach(emp => {
    const record: any = {
      id: emp.id,
      name: emp.name,
      department: emp.dept,
      designation: emp.desig,
      attendance: {}
    };

    let pCount = 0, aCount = 0, lCount = 0, hCount = 0, woCount = 0;

    for (let day = 1; day <= daysInMonth; day++) {
      const dateKey = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const dayOfWeek = new Date(dateKey).getDay();
      
      let status = "P";
      if (dayOfWeek === 0 || dayOfWeek === 6) {
        status = "WO";
        woCount++;
      } else {
        const rand = Math.random();
        if (rand > 0.95) { status = "A"; aCount++; }
        else if (rand > 0.9) { status = "L"; lCount++; }
        else if (rand > 0.85) { status = "WFH"; pCount++; }
        else { status = "P"; pCount++; }
      }
      
      record.attendance[dateKey] = {
        status,
        swipeIn: status === "P" || status === "WFH" ? "09:05 AM" : null,
        swipeOut: status === "P" || status === "WFH" ? "06:15 PM" : null,
        totalHours: status === "P" || status === "WFH" ? 9.1 : (status === "HD" ? 4.5 : 0),
        shift: "General Shift",
        remarks: status === "L" ? "Sick Leave Applied" : (status === "A" ? "No Information" : ""),
        history: [
          { time: "2026-05-11 10:00 AM", user: "System", action: "Status Generated", from: "-", to: status }
        ]
      };
    }

    record.summary = { P: pCount, A: aCount, L: lCount, H: hCount, WO: woCount, OT: 2, totalWorking: pCount + aCount };
    data.push(record);
  });
  return data;
};

export const MOCK_MATRIX_DATA = generateMatrixData(5, 2026);

export const MOCK_DEPARTMENTS = DEPARTMENTS;
export const MOCK_DESIGNATIONS = DESIGNATIONS;
export const MOCK_TEAMS = TEAMS;
export const MOCK_EMPLOYEES = EMPLOYEES;
export const MOCK_SHIFTS = SHIFTS;

// Aliases for backward compatibility
export const attendanceEmployees = MOCK_EMPLOYEES;
export const attendanceExceptions = MOCK_EXCEPTIONS;
export const attendanceRequests = MOCK_REQUESTS;
export const dailyAttendance = MOCK_ATTENDANCE;
