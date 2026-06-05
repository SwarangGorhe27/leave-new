import { useQuery } from '@tanstack/react-query';
import { fetchSystemRoles, type SystemRole } from '@/api/securityApi';

export function useSystemRoles() {
  return useQuery({
    queryKey: ['security', 'rbac', 'roles'],
    queryFn: fetchSystemRoles,
    staleTime: 5 * 60 * 1000,
    select: (data: SystemRole[]) =>
      data.map((r) => ({
        v: r.code,
        l: r.label || r.code,
      })),
  });
}
