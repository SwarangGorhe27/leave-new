export type EmploymentStatus = 'Active' | 'On Leave' | 'Probation';
export type LifecycleEventType = 'Joined' | 'Confirmed' | 'Promoted' | 'Incremented';

export interface EmployeeStat {
  label: string;
  value: string;
  delta?: string;
}

export interface ReportingPerson {
  name: string;
  title: string;
}

export interface EmployeeDocument {
  id: string;
  type: string;
  name: string;
  uploadedAt: string;
  expiresAt?: string;
  status: 'Valid' | 'Expiring Soon' | 'Expired';
}

export interface LifecycleEvent {
  id: string;
  type: LifecycleEventType;
  title: string;
  date: string;
  details: string;
  actor: string;
}

export interface EmployeeProfileSectionField {
  label: string;
  value: string;
  icon: string;
}

export interface EmployeeProfileSection {
  id: string;
  title: string;
  fields: EmployeeProfileSectionField[];
}

export interface Employee {
  id: string;
  code: string;
  name: string;
  email: string;
  avatar?: string;
  designation: string;
  department: string;
  location: string;
  status: EmploymentStatus;
  joinedAt: string;
  nextIncrement: string;
  leaveBalance: number;
  presentDays: number;
  tenure: string;
  reportingChain: ReportingPerson[];
  stats: EmployeeStat[];
  recentActivity: string[];
  documents: EmployeeDocument[];
  lifecycle: LifecycleEvent[];
  personalSections: EmployeeProfileSection[];
  officialSections: EmployeeProfileSection[];
}
