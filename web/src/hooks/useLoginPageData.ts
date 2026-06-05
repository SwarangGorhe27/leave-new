import { useEffect, useState } from 'react';
import { useAuthStore } from '@store/authStore';

export interface DashboardStats {
  totalEmployees: number;
  presentToday: number;
  onLeaveToday: number;
  pendingApprovals: number;
  newHiresThisMonth: number;
  attendanceRate: number;
  departmentCount: number;
  avgTenure: string;
}

export interface EmployeeDashboardStats {
  name: string;
  title: string;
  department: string;
  location: string;
  leaveBalance: number;
  presentDays: number;
  tenure: string;
  nextIncrement: string;
  manager: string;
  recentActivity: string[];
}

/**
 * Hook for fetching admin dashboard data
 * Integrates with useAuthStore to provide real-time data
 */
export function useAdminDashboardStats(): DashboardStats | null {
  const user = useAuthStore((state) => state.user);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    if (user?.role !== 'ADMIN') return;

    // In production, this would call an API endpoint
    // For now, it simulates data based on store state
    const mockStats: DashboardStats = {
      totalEmployees: 230,
      presentToday: 215,
      onLeaveToday: 8,
      pendingApprovals: 12,
      newHiresThisMonth: 3,
      attendanceRate: 94.2,
      departmentCount: 12,
      avgTenure: '3.5 years'
    };

    setStats(mockStats);
  }, [user]);

  return stats;
}

/**
 * Hook for fetching employee dashboard data
 * Provides personalized employee statistics and information
 */
export function useEmployeeDashboardStats(): EmployeeDashboardStats | null {
  const user = useAuthStore((state) => state.user);
  const employees = useAuthStore((state) => state.employees);
  const [stats, setStats] = useState<EmployeeDashboardStats | null>(null);

  useEffect(() => {
    if (user?.role !== 'EMPLOYEE') return;

    // Get current employee data from store
    const employee = employees[1]; // Aarav Mehta (demo employee)

    if (employee) {
      const employeeStats: EmployeeDashboardStats = {
        name: employee.name,
        title: employee.designation,
        department: employee.department,
        location: employee.location,
        leaveBalance: employee.leaveBalance,
        presentDays: employee.presentDays,
        tenure: employee.tenure,
        nextIncrement: employee.nextIncrement,
        manager: employee.reportingChain?.[1]?.name || 'N/A',
        recentActivity: employee.recentActivity || []
      };

      setStats(employeeStats);
    }
  }, [user, employees]);

  return stats;
}

/**
 * Hook for real-time notifications on login page
 * Could include pending tasks, alerts, etc.
 */
export interface LoginPageAlert {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  action?: { label: string; href: string };
}

export function useLoginPageAlerts(): LoginPageAlert[] {
  const user = useAuthStore((state) => state.user);
  const [alerts, setAlerts] = useState<LoginPageAlert[]>([]);

  useEffect(() => {
    if (!user) return;

    let alertList: LoginPageAlert[] = [];

    if (user.role === 'ADMIN') {
      alertList = [
        {
          id: 'pending-leaves',
          title: 'Leave Approvals Pending',
          description: '12 leave requests awaiting your approval',
          priority: 'high',
          action: { label: 'Review', href: '/leave' }
        },
        {
          id: 'document-verification',
          title: 'Document Verifications',
          description: '18 documents need compliance review',
          priority: 'medium',
          action: { label: 'Process', href: '/documents' }
        },
        {
          id: 'new-joiners',
          title: 'New Joiners Onboarding',
          description: '3 employees requiring onboarding setup',
          priority: 'medium',
          action: { label: 'Setup', href: '/lifecycle' }
        }
      ];
    } else if (user.role === 'EMPLOYEE') {
      alertList = [
        {
          id: 'leave-balance',
          title: 'Leave Balance Alert',
          description: 'You have limited leave balance. Plan ahead.',
          priority: 'medium',
          action: { label: 'View Details', href: '/leave' }
        },
        {
          id: 'document-expiry',
          title: 'Document Expiring Soon',
          description: 'Your NDA expires on May 10, 2026',
          priority: 'low',
          action: { label: 'Update', href: '/profile' }
        }
      ];
    }

    setAlerts(alertList);
  }, [user]);

  return alerts;
}

/**
 * Hook to compute greeting based on time of day
 */
export function useTimeBasedGreeting(): string {
  const [greeting, setGreeting] = useState('Good morning');

  useEffect(() => {
    const updateGreeting = () => {
      const hour = new Date().getHours();
      if (hour < 12) {
        setGreeting('Good morning');
      } else if (hour < 18) {
        setGreeting('Good afternoon');
      } else {
        setGreeting('Good evening');
      }
    };

    updateGreeting();
    const interval = setInterval(updateGreeting, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  return greeting;
}

/**
 * Hook to get leave status color and message
 */
export function useLeaveStatusInfo(balance: number) {
  return {
    status: balance > 10 ? 'healthy' : balance > 5 ? 'warning' : 'critical',
    color: balance > 10 ? 'success' : balance > 5 ? 'warning' : 'danger',
    message: balance > 10 ? 'Sufficient balance' : balance > 5 ? 'Plan ahead' : 'Low balance'
  };
}

/**
 * Hook to compute tenure string from dates
 */
export function useTenureInfo(joinedAt: string): { tenure: string; years: number; months: number } {
  const joined = new Date(joinedAt);
  const now = new Date();

  const diffTime = Math.abs(now.getTime() - joined.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  const years = Math.floor(diffDays / 365);
  const months = Math.floor((diffDays % 365) / 30);

  return {
    tenure: `${years}y ${months}m`,
    years,
    months
  };
}
