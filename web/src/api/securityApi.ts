import api from './client';

export interface SystemRole {
  id: string;
  code: string;
  label: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export async function fetchSystemRoles(): Promise<SystemRole[]> {
  const res = await api.get<SystemRole[]>('/security/rbac/roles/');
  return res.data;
}
