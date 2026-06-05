import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../app/context/AuthContext';
import type { Employee } from '../app/components/employees/mockData';
import {
  fetchFullEmployeeProfile,
  type EmployeePortal,
} from '../api/employeeModuleApi';

function portalFromRole(role?: string): EmployeePortal {
  if (role === 'admin') return 'admin';
  if (role === 'manager') return 'manager';
  return 'employee';
}

export function employeeProfileQueryKey(portal: EmployeePortal, employeeId: string) {
  return ['employee-module-profile', portal, employeeId] as const;
}

/** Self-service profile (employee / manager My Profile). */
export function useMyEmployeeModuleProfile() {
  const { user } = useAuth();
  const portal = portalFromRole(user?.role);
  const employeeId = user?.employeeId ?? user?.employeeCode ?? user?.email ?? 'self';

  return useQuery({
    queryKey: employeeProfileQueryKey(portal, employeeId),
    queryFn: async () => fetchFullEmployeeProfile(portal, employeeId),
    enabled: Boolean(user),
    staleTime: 30_000,
  });
}

/** Admin employee information page by UUID. */
export function useAdminEmployeeModuleProfile(employeeId: string | undefined) {
  return useQuery({
    queryKey: employeeProfileQueryKey('admin', employeeId ?? ''),
    queryFn: async () => fetchFullEmployeeProfile('admin', employeeId!),
    enabled: Boolean(employeeId),
    staleTime: 30_000,
  });
}

export function useInvalidateEmployeeProfile() {
  const qc = useQueryClient();
  return (portal: EmployeePortal, employeeId: string, merged?: Employee) => {
    const key = employeeProfileQueryKey(portal, employeeId);
    if (merged) {
      qc.setQueryData(key, merged);
      return;
    }
    qc.invalidateQueries({ queryKey: key });
  };
}

export type { Employee };
