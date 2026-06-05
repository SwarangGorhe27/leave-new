import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Employee } from '@/types/employee';

export type UserRole = 'ADMIN' | 'EMPLOYEE';

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  title: string;
  company: string;
  avatar?: string;
  permissions: string[];
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  employees: Employee[];
  login: (email: string, role: UserRole) => void;
  logout: () => void;
}

const demoAdminUser: AuthUser = {
  id: 'usr_1',
  name: 'Sakshi Deshpande',
  email: 'admin@ampcus.example',
  role: 'ADMIN',
  title: 'HR Operations Head',
  company: 'Ampcus Tech',
  permissions: [
    'employees:view',
    'employees:manage',
    'attendance:view',
    'leave:view',
    'documents:view',
    'payroll:view',
    'settings:view',
    'ai:view',
    'canteen:view',
    'biometric:view',
    'lifecycle:view',
    'forms:view'
  ]
};

const demoEmployeeUser: AuthUser = {
  id: 'usr_2',
  name: 'Aarav Mehta',
  email: 'employee@ampcus.example',
  role: 'EMPLOYEE',
  title: 'Senior Product Designer',
  company: 'Ampcus Tech',
  permissions: [
    'employees:view',
    'attendance:view',
    'leave:view',
    'documents:view',
    'payroll:view',
    'canteen:view',
    'ai:view'
  ]
};

const employees: Employee[] = [
  {
    id: 'emp_1',
    code: 'AT-2048',
    name: 'Aarav Mehta',
    email: 'employee@ampcus.example',
    designation: 'Senior Product Designer',
    department: 'Experience Design',
    location: 'Pune',
    status: 'Active',
    joinedAt: '2021-06-14',
    nextIncrement: '2026-07-01',
    leaveBalance: 14,
    presentDays: 19,
    tenure: '4y 10m',
    reportingChain: [
      { name: 'Aarav Mehta', title: 'Senior Product Designer' },
      { name: 'Neha Kapoor', title: 'Design Manager' },
      { name: 'Arjun Rao', title: 'Director, Product' }
    ],
    stats: [
      { label: 'Days Present', value: '19', delta: '+2 vs last month' },
      { label: 'Leave Balance', value: '14 days', delta: '2 casual available' },
      { label: 'Tenure', value: '4y 10m' },
      { label: 'Next Increment', value: '01 Jul 2026', delta: '75 days away' }
    ],
    recentActivity: ['Promoted to Senior Product Designer', 'Document set updated', 'Manager changed to Neha Kapoor'],
    documents: [
      { id: 'doc_1', type: 'Identity', name: 'PAN Card.pdf', uploadedAt: '2026-01-10', status: 'Valid' },
      { id: 'doc_2', type: 'Compliance', name: 'Aadhaar Front.png', uploadedAt: '2026-02-18', status: 'Valid' },
      { id: 'doc_3', type: 'Policy', name: 'NDA Signed.pdf', uploadedAt: '2025-11-01', expiresAt: '2026-05-10', status: 'Expiring Soon' }
    ],
    lifecycle: [
      { id: 'lc_1', type: 'Joined', title: 'Joined Ampcus Tech', date: '2021-06-14', details: 'Inducted into design team as Product Designer II.', actor: 'Ritika Shah' },
      { id: 'lc_2', type: 'Confirmed', title: 'Probation confirmed', date: '2021-12-14', details: 'Successfully completed 6-month probation.', actor: 'Neha Kapoor' },
      { id: 'lc_3', type: 'Promoted', title: 'Promoted to Senior Product Designer', date: '2024-04-01', details: 'Expanded ownership across design system and HR platform.', actor: 'Arjun Rao' }
    ],
    personalSections: [
      {
        id: 'personal',
        title: 'Personal Details',
        fields: [
          { label: 'Date of Birth', value: '08 Sep 1995', icon: 'Cake' },
          { label: 'Gender', value: 'Male', icon: 'UserRound' },
          { label: 'Marital Status', value: 'Single', icon: 'HeartHandshake' },
          { label: 'Blood Group', value: 'B+', icon: 'Droplets' }
        ]
      },
      {
        id: 'contact',
        title: 'Contact',
        fields: [
          { label: 'Phone', value: '+91 98765 43210', icon: 'Phone' },
          { label: 'Personal Email', value: 'aarav.personal@example.com', icon: 'Mail' },
          { label: 'Current Address', value: 'Koregaon Park, Pune', icon: 'MapPin' },
          { label: 'Emergency Contact', value: 'Karan Mehta · Brother', icon: 'ShieldPlus' }
        ]
      }
    ],
    officialSections: [
      {
        id: 'employment',
        title: 'Employment Details',
        fields: [
          { label: 'Department', value: 'Experience Design', icon: 'Building2' },
          { label: 'Designation', value: 'Senior Product Designer', icon: 'BriefcaseBusiness' },
          { label: 'Manager', value: 'Neha Kapoor', icon: 'Users' },
          { label: 'Work Location', value: 'Pune', icon: 'MapPinned' }
        ]
      },
      {
        id: 'access',
        title: 'System & Role Access',
        fields: [
          { label: 'Role', value: 'Design Admin', icon: 'ShieldCheck' },
          { label: 'Biometric Access', value: 'Enabled', icon: 'Fingerprint' },
          { label: 'Laptop Asset', value: 'MBP-1482', icon: 'Laptop' },
          { label: 'Shift', value: 'General Shift', icon: 'Clock3' }
        ]
      }
    ]
  },
  {
    id: 'emp_2',
    code: 'AT-2190',
    name: 'Mira Kulkarni',
    email: 'admin@ampcus.example',
    designation: 'HR Business Partner',
    department: 'People Operations',
    location: 'Mumbai',
    status: 'On Leave',
    joinedAt: '2023-02-02',
    nextIncrement: '2026-09-01',
    leaveBalance: 8,
    presentDays: 16,
    tenure: '3y 2m',
    reportingChain: [
      { name: 'Mira Kulkarni', title: 'HR Business Partner' },
      { name: 'Sakshi Deshpande', title: 'HR Operations Head' },
      { name: 'Arjun Rao', title: 'Director, Product' }
    ],
    stats: [
      { label: 'Days Present', value: '16' },
      { label: 'Leave Balance', value: '8 days' },
      { label: 'Tenure', value: '3y 2m' },
      { label: 'Next Increment', value: '01 Sep 2026' }
    ],
    recentActivity: ['Approved 12 leave requests', 'Uploaded appraisal letters'],
    documents: [],
    lifecycle: [
      { id: 'lc_4', type: 'Joined', title: 'Joined People Operations', date: '2023-02-02', details: 'Onboarded as HRBP for product and design orgs.', actor: 'Sakshi Deshpande' }
    ],
    personalSections: [],
    officialSections: []
  }
];

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      employees,
      login: (email, role) => {
        // Mock authentication logic based on role
        if (role === 'ADMIN') {
          set({ user: demoAdminUser, isAuthenticated: true });
        } else {
          set({ user: demoEmployeeUser, isAuthenticated: true });
        }
      },
      logout: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'hrms-auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
