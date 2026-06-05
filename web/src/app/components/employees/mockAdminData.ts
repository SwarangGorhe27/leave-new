// ─── Attendance ────────────────────────────────────────────────────────────────

export type AttendanceStatus = "Present" | "Absent" | "Half Day" | "On Leave";

export interface AttendanceRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  department: string;
  checkIn: string;
  checkOut: string;
  status: AttendanceStatus;
  hoursWorked: string;
  date: string;
}

export const attendanceRecords: AttendanceRecord[] = [
  { id: "a1", employeeId: "EMP-001", employeeName: "Arjun Sharma",     department: "Engineering",      checkIn: "09:02", checkOut: "18:15", status: "Present",  hoursWorked: "9h 13m", date: "2026-05-05" },
  { id: "a2", employeeId: "EMP-002", employeeName: "Priya Nair",       department: "Human Resources",  checkIn: "09:30", checkOut: "18:00", status: "Present",  hoursWorked: "8h 30m", date: "2026-05-05" },
  { id: "a3", employeeId: "EMP-003", employeeName: "Vikram Mehta",     department: "Product",          checkIn: "10:05", checkOut: "19:00", status: "Present",  hoursWorked: "8h 55m", date: "2026-05-05" },
  { id: "a4", employeeId: "EMP-004", employeeName: "Sneha Krishnan",   department: "Design",           checkIn: "—",     checkOut: "—",     status: "On Leave", hoursWorked: "—",       date: "2026-05-05" },
  { id: "a5", employeeId: "EMP-005", employeeName: "Rajesh Kumar",     department: "Engineering",      checkIn: "08:50", checkOut: "17:55", status: "Present",  hoursWorked: "9h 05m", date: "2026-05-05" },
  { id: "a6", employeeId: "EMP-006", employeeName: "Ananya Iyer",      department: "Marketing",        checkIn: "09:45", checkOut: "14:00", status: "Half Day", hoursWorked: "4h 15m", date: "2026-05-05" },
  { id: "a7", employeeId: "EMP-007", employeeName: "Karthik Reddy",    department: "Analytics",        checkIn: "—",     checkOut: "—",     status: "Absent",   hoursWorked: "—",       date: "2026-05-05" },
  { id: "a8", employeeId: "EMP-008", employeeName: "Divya Pillai",     department: "Finance",          checkIn: "09:10", checkOut: "18:05", status: "Present",  hoursWorked: "8h 55m", date: "2026-05-05" },
  // Yesterday
  { id: "b1", employeeId: "EMP-001", employeeName: "Arjun Sharma",     department: "Engineering",      checkIn: "09:00", checkOut: "18:00", status: "Present",  hoursWorked: "9h 00m", date: "2026-05-04" },
  { id: "b2", employeeId: "EMP-002", employeeName: "Priya Nair",       department: "Human Resources",  checkIn: "09:20", checkOut: "18:10", status: "Present",  hoursWorked: "8h 50m", date: "2026-05-04" },
  { id: "b3", employeeId: "EMP-003", employeeName: "Vikram Mehta",     department: "Product",          checkIn: "09:45", checkOut: "18:45", status: "Present",  hoursWorked: "9h 00m", date: "2026-05-04" },
  { id: "b4", employeeId: "EMP-004", employeeName: "Sneha Krishnan",   department: "Design",           checkIn: "—",     checkOut: "—",     status: "On Leave", hoursWorked: "—",       date: "2026-05-04" },
  { id: "b5", employeeId: "EMP-005", employeeName: "Rajesh Kumar",     department: "Engineering",      checkIn: "08:55", checkOut: "18:00", status: "Present",  hoursWorked: "9h 05m", date: "2026-05-04" },
  { id: "b6", employeeId: "EMP-006", employeeName: "Ananya Iyer",      department: "Marketing",        checkIn: "09:30", checkOut: "18:30", status: "Present",  hoursWorked: "9h 00m", date: "2026-05-04" },
  { id: "b7", employeeId: "EMP-007", employeeName: "Karthik Reddy",    department: "Analytics",        checkIn: "—",     checkOut: "—",     status: "Absent",   hoursWorked: "—",       date: "2026-05-04" },
  { id: "b8", employeeId: "EMP-008", employeeName: "Divya Pillai",     department: "Finance",          checkIn: "09:05", checkOut: "18:00", status: "Present",  hoursWorked: "8h 55m", date: "2026-05-04" },
];

// ─── Leave Requests ─────────────────────────────────────────────────────────────

export type LeaveStatus = "Pending" | "Approved" | "Rejected";
export type LeaveType = "Annual Leave" | "Sick Leave" | "Casual Leave" | "Maternity Leave" | "Paternity Leave" | "Comp Off";

export interface LeaveRequest {
  id: string;
  employeeId: string;
  employeeName: string;
  department: string;
  leaveType: LeaveType;
  from: string;
  to: string;
  days: number;
  reason: string;
  status: LeaveStatus;
  appliedOn: string;
  avatarColor: string;
  initials: string;
}

export const leaveRequests: LeaveRequest[] = [
  { id: "l1", employeeId: "EMP-004", employeeName: "Sneha Krishnan",  department: "Design",          leaveType: "Sick Leave",    from: "2026-05-01", to: "2026-05-07", days: 5, reason: "Medical treatment and recovery",      status: "Approved", appliedOn: "2026-04-28", avatarColor: "#DC2626", initials: "SK" },
  { id: "l2", employeeId: "EMP-006", employeeName: "Ananya Iyer",     department: "Marketing",       leaveType: "Casual Leave",  from: "2026-05-05", to: "2026-05-05", days: 1, reason: "Personal work",                        status: "Approved", appliedOn: "2026-05-03", avatarColor: "#D97706", initials: "AI" },
  { id: "l3", employeeId: "EMP-002", employeeName: "Priya Nair",      department: "Human Resources", leaveType: "Annual Leave",  from: "2026-05-18", to: "2026-05-22", days: 5, reason: "Family vacation to Goa",               status: "Pending",  appliedOn: "2026-05-04", avatarColor: "#0891B2", initials: "PN" },
  { id: "l4", employeeId: "EMP-001", employeeName: "Arjun Sharma",    department: "Engineering",     leaveType: "Comp Off",      from: "2026-05-09", to: "2026-05-09", days: 1, reason: "Worked on weekend sprint",             status: "Pending",  appliedOn: "2026-05-05", avatarColor: "#4F46E5", initials: "AS" },
  { id: "l5", employeeId: "EMP-005", employeeName: "Rajesh Kumar",    department: "Engineering",     leaveType: "Casual Leave",  from: "2026-04-25", to: "2026-04-25", days: 1, reason: "Personal emergency",                   status: "Approved", appliedOn: "2026-04-24", avatarColor: "#7C3AED", initials: "RK" },
  { id: "l6", employeeId: "EMP-003", employeeName: "Vikram Mehta",    department: "Product",         leaveType: "Annual Leave",  from: "2026-06-02", to: "2026-06-06", days: 5, reason: "Summer holidays with family",          status: "Pending",  appliedOn: "2026-05-05", avatarColor: "#059669", initials: "VM" },
  { id: "l7", employeeId: "EMP-008", employeeName: "Divya Pillai",    department: "Finance",         leaveType: "Sick Leave",    from: "2026-04-10", to: "2026-04-11", days: 2, reason: "Fever and rest",                       status: "Approved", appliedOn: "2026-04-09", avatarColor: "#BE185D", initials: "DP" },
  { id: "l8", employeeId: "EMP-007", employeeName: "Karthik Reddy",   department: "Analytics",       leaveType: "Annual Leave",  from: "2026-04-28", to: "2026-05-02", days: 3, reason: "Travel plans",                         status: "Rejected", appliedOn: "2026-04-20", avatarColor: "#0F766E", initials: "KR" },
];

// ─── Payroll ─────────────────────────────────────────────────────────────────────

export type PayrollStatus = "Processed" | "Pending" | "On Hold";

export interface PayrollRecord {
  employeeId: string;
  employeeName: string;
  department: string;
  designation: string;
  basicSalary: number;
  hra: number;
  conveyance: number;
  medicalAllowance: number;
  specialAllowance: number;
  grossSalary: number;
  pf: number;
  tds: number;
  netSalary: number;
  status: PayrollStatus;
  avatarColor: string;
  initials: string;
}

export const payrollRecords: PayrollRecord[] = [
  { employeeId: "EMP-001", employeeName: "Arjun Sharma",   department: "Engineering",     designation: "Senior Developer",    basicSalary: 75000, hra: 30000, conveyance: 3000, medicalAllowance: 1250, specialAllowance: 10750, grossSalary: 120000, pf: 9000,  tds: 8500,  netSalary: 102500, status: "Processed", avatarColor: "#4F46E5", initials: "AS" },
  { employeeId: "EMP-002", employeeName: "Priya Nair",     department: "Human Resources", designation: "HR Manager",          basicSalary: 65000, hra: 26000, conveyance: 3000, medicalAllowance: 1250, specialAllowance: 9750,  grossSalary: 105000, pf: 7800,  tds: 7200,  netSalary: 90000,  status: "Processed", avatarColor: "#0891B2", initials: "PN" },
  { employeeId: "EMP-003", employeeName: "Vikram Mehta",   department: "Product",         designation: "Product Manager",     basicSalary: 90000, hra: 36000, conveyance: 3000, medicalAllowance: 1250, specialAllowance: 19750, grossSalary: 150000, pf: 10800, tds: 15000, netSalary: 124200, status: "Processed", avatarColor: "#059669", initials: "VM" },
  { employeeId: "EMP-004", employeeName: "Sneha Krishnan", department: "Design",          designation: "UI/UX Designer",      basicSalary: 55000, hra: 22000, conveyance: 3000, medicalAllowance: 1250, specialAllowance: 8750,  grossSalary: 90000,  pf: 6600,  tds: 5000,  netSalary: 78400,  status: "On Hold",   avatarColor: "#DC2626", initials: "SK" },
  { employeeId: "EMP-005", employeeName: "Rajesh Kumar",   department: "Engineering",     designation: "DevOps Engineer",     basicSalary: 70000, hra: 28000, conveyance: 3000, medicalAllowance: 1250, specialAllowance: 12750, grossSalary: 115000, pf: 8400,  tds: 9000,  netSalary: 97600,  status: "Processed", avatarColor: "#7C3AED", initials: "RK" },
  { employeeId: "EMP-006", employeeName: "Ananya Iyer",    department: "Marketing",       designation: "Marketing Specialist",basicSalary: 45000, hra: 18000, conveyance: 3000, medicalAllowance: 1250, specialAllowance: 7750,  grossSalary: 75000,  pf: 5400,  tds: 3000,  netSalary: 66600,  status: "Pending",   avatarColor: "#D97706", initials: "AI" },
  { employeeId: "EMP-007", employeeName: "Karthik Reddy",  department: "Analytics",       designation: "Data Analyst",        basicSalary: 58000, hra: 23200, conveyance: 3000, medicalAllowance: 1250, specialAllowance: 9550,  grossSalary: 95000,  pf: 6960,  tds: 6000,  netSalary: 82040,  status: "On Hold",   avatarColor: "#0F766E", initials: "KR" },
  { employeeId: "EMP-008", employeeName: "Divya Pillai",   department: "Finance",         designation: "Finance Executive",   basicSalary: 48000, hra: 19200, conveyance: 3000, medicalAllowance: 1250, specialAllowance: 8550,  grossSalary: 80000,  pf: 5760,  tds: 4200,  netSalary: 70040,  status: "Processed", avatarColor: "#BE185D", initials: "DP" },
];

// ─── Documents ────────────────────────────────────────────────────────────────────

export type DocCategory = "Policy" | "Contract" | "Certificate" | "ID Proof" | "Payslip" | "Other";

export interface Document {
  id: string;
  name: string;
  category: DocCategory;
  uploadedBy: string;
  uploadDate: string;
  size: string;
  type: "PDF" | "DOC" | "XLSX" | "IMG";
  employeeName?: string;
}

export const documents: Document[] = [
  { id: "d1",  name: "Employee Handbook 2026",             category: "Policy",      uploadedBy: "Admin",          uploadDate: "2026-01-10", size: "2.4 MB", type: "PDF" },
  { id: "d2",  name: "Code of Conduct",                    category: "Policy",      uploadedBy: "Admin",          uploadDate: "2026-01-10", size: "1.1 MB", type: "PDF" },
  { id: "d3",  name: "Offer Letter – Arjun Sharma",        category: "Contract",    uploadedBy: "Priya Nair",     uploadDate: "2021-03-10", size: "320 KB", type: "PDF", employeeName: "Arjun Sharma" },
  { id: "d4",  name: "Appointment Letter – Priya Nair",    category: "Contract",    uploadedBy: "Admin",          uploadDate: "2020-05-28", size: "285 KB", type: "PDF", employeeName: "Priya Nair" },
  { id: "d5",  name: "Experience Certificate – Vikram Mehta", category: "Certificate", uploadedBy: "Priya Nair",  uploadDate: "2026-03-15", size: "210 KB", type: "PDF", employeeName: "Vikram Mehta" },
  { id: "d6",  name: "Payslip Apr 2026 – Arjun Sharma",    category: "Payslip",     uploadedBy: "System",         uploadDate: "2026-05-01", size: "180 KB", type: "PDF", employeeName: "Arjun Sharma" },
  { id: "d7",  name: "Payslip Apr 2026 – Priya Nair",      category: "Payslip",     uploadedBy: "System",         uploadDate: "2026-05-01", size: "180 KB", type: "PDF", employeeName: "Priya Nair" },
  { id: "d8",  name: "Leave Policy 2026",                  category: "Policy",      uploadedBy: "Admin",          uploadDate: "2026-01-05", size: "950 KB", type: "PDF" },
  { id: "d9",  name: "NDA – Sneha Krishnan",               category: "Contract",    uploadedBy: "Admin",          uploadDate: "2022-01-03", size: "150 KB", type: "PDF", employeeName: "Sneha Krishnan" },
  { id: "d10", name: "Aadhar Card – Rajesh Kumar",         category: "ID Proof",    uploadedBy: "Rajesh Kumar",   uploadDate: "2021-11-20", size: "420 KB", type: "IMG", employeeName: "Rajesh Kumar" },
  { id: "d11", name: "PAN Card – Divya Pillai",            category: "ID Proof",    uploadedBy: "Divya Pillai",   uploadDate: "2020-11-30", size: "390 KB", type: "IMG", employeeName: "Divya Pillai" },
  { id: "d12", name: "Training Completion – Ananya Iyer",  category: "Certificate", uploadedBy: "Priya Nair",     uploadDate: "2026-04-20", size: "200 KB", type: "PDF", employeeName: "Ananya Iyer" },
];
