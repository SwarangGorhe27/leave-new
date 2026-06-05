import { useMemo } from 'react';
import { useAuthStore } from '@store/authStore';

export function usePermissions() {
  const permissions = useAuthStore((state) => state.user.permissions);

  return useMemo(
    () => ({
      can: (action: string, resource: string) => permissions.includes(`${resource}:${action}`) || permissions.includes(`${resource}:view`),
      permissions
    }),
    [permissions]
  );
}
