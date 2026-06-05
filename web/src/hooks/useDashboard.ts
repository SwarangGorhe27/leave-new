import { useQuery } from '@tanstack/react-query';
import api from '@api/client';

export interface DashboardData {
  employees: {
    total: number;
    active: number;
    on_leave: number;
    new_hires_this_month: number;
  };
  departments: Array<{ name: string; count: number }>;
  attendance: {
    present_today: number;
    absent_today: number;
    late_today: number;
    attendance_rate: number;
    daily_trend: Array<{ date: string; present: number; absent?: number; late?: number }>;
  };
  leave: {
    pending_approvals: number;
  };
  upcoming_birthdays: Array<{ name: string; code: string; date: string }>;
  recent_employees: Array<{
    id: string;
    code: string;
    name: string;
    status: string;
    department: string;
    designation: string;
    location: string;
  }>;
}

const DEMO_DASHBOARD: DashboardData = {
  employees: {
    total: 132,
    active: 128,
    on_leave: 4,
    new_hires_this_month: 6,
  },
  departments: [
    { name: 'Engineering', count: 54 },
    { name: 'Human Resources', count: 12 },
    { name: 'Finance', count: 16 },
    { name: 'Operations', count: 28 },
    { name: 'Sales & Marketing', count: 18 },
    { name: 'Administration', count: 4 },
  ],
  attendance: {
    present_today: 109,
    absent_today: 19,
    late_today: 8,
    attendance_rate: 82.6,
    daily_trend: (() => {
      const trend = [];
      for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        trend.push({
          date: d.toISOString().slice(0, 10),
          present: 105 + Math.floor(Math.random() * 15),
          late: 4 + Math.floor(Math.random() * 7),
          absent: 10 + Math.floor(Math.random() * 8),
        });
      }
      return trend;
    })(),
  },
  leave: {
    pending_approvals: 5,
  },
  upcoming_birthdays: [
    { name: 'Rahul Sharma', code: 'EMP-0023', date: new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate() + 2).toISOString().slice(0, 10) },
    { name: 'Priya Nair', code: 'EMP-0047', date: new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate() + 5).toISOString().slice(0, 10) },
    { name: 'Arjun Patel', code: 'EMP-0089', date: new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate() + 9).toISOString().slice(0, 10) },
  ],
  recent_employees: [
    { id: 'emp-101', code: 'EMP-0127', name: 'Sneha Kulkarni', status: 'ACTIVE', department: 'Engineering', designation: 'Software Engineer', location: 'Pune Office' },
    { id: 'emp-102', code: 'EMP-0128', name: 'Vikram Joshi', status: 'ACTIVE', department: 'Finance', designation: 'Financial Analyst', location: 'Mumbai Office' },
    { id: 'emp-103', code: 'EMP-0129', name: 'Ananya Singh', status: 'ACTIVE', department: 'Human Resources', designation: 'HR Executive', location: 'Pune Office' },
    { id: 'emp-104', code: 'EMP-0130', name: 'Rohan Desai', status: 'ACTIVE', department: 'Operations', designation: 'Operations Lead', location: 'Bangalore Office' },
    { id: 'emp-105', code: 'EMP-0131', name: 'Kavya Reddy', status: 'PROBATION', department: 'Sales & Marketing', designation: 'Sales Executive', location: 'Hyderabad Office' },
  ],
};

async function fetchDashboard(): Promise<DashboardData> {
  try {
    const response = await api.get('/dashboard/');
    const data: DashboardData = response.data?.data ?? response.data;
    if (data?.employees?.total) return data;
  } catch { /* fallback */ }
  return DEMO_DASHBOARD;
}

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboard,
    refetchInterval: 60_000, // refresh every 60s
    staleTime: 30_000,
  });
}
