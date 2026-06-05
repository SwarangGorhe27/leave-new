import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@api/client';

function extract<T>(res: unknown): T[] {
  const d = res as Record<string, unknown>;
  return (d?.data as Record<string, unknown>)?.results as T[]
    ?? (d?.data as Record<string, unknown>)?.data as T[]
    ?? d?.data as T[]
    ?? d?.results as T[]
    ?? (Array.isArray(d) ? d : []) as T[];
}

function extractOne<T>(res: unknown): T {
  const d = res as Record<string, unknown>;
  return ((d?.data as Record<string, unknown>)?.data ?? d?.data ?? d) as T;
}

export interface BiometricDevice {
  id: string;
  name: string;
  device_type: string;
  serial_number: string;
  ip_address: string;
  port: number;
  location: string;
  status: 'ACTIVE' | 'INACTIVE' | 'ERROR' | 'OFFLINE';
  last_sync: string | null;
  last_heartbeat: string | null;
}

export interface RawPunchLog {
  id: string;
  device: string;
  employee_device_id: string;
  punch_time: string;
  is_processed: boolean;
  processed_at: string | null;
  error_message: string;
}

export interface DeviceSyncLog {
  id: string;
  device: string;
  sync_type: string;
  started_at: string;
  completed_at: string | null;
  records_pulled: number;
  records_processed: number;
  status: string;
}

export function useBiometricDevices() {
  return useQuery({
    queryKey: ['biometric', 'devices'],
    queryFn: async () => {
      const res = await api.get('/biometric/devices/');
      return extract<BiometricDevice>(res);
    },
    staleTime: 30_000,
  });
}

export function usePunchLogs(deviceId?: string) {
  return useQuery({
    queryKey: ['biometric', 'punch-logs', deviceId],
    queryFn: async () => {
      const params = deviceId ? { device: deviceId } : {};
      const res = await api.get('/biometric/punch-logs/', { params });
      return extract<RawPunchLog>(res);
    },
  });
}

export function useSyncLogs(deviceId?: string) {
  return useQuery({
    queryKey: ['biometric', 'sync-logs', deviceId],
    queryFn: async () => {
      const params = deviceId ? { device: deviceId } : {};
      const res = await api.get('/biometric/sync-logs/', { params });
      return extract<DeviceSyncLog>(res);
    },
  });
}

export function useCreateBiometricDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<BiometricDevice>) => {
      const res = await api.post('/biometric/devices/', data);
      return extractOne<BiometricDevice>(res);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['biometric', 'devices'] }),
  });
}

export function useUpdateBiometricDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...data }: Partial<BiometricDevice> & { id: string }) => {
      const res = await api.patch(`/biometric/devices/${id}/`, data);
      return extractOne<BiometricDevice>(res);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['biometric', 'devices'] }),
  });
}

export function useDeleteBiometricDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/biometric/devices/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['biometric', 'devices'] }),
  });
}

export function useSyncDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post(`/biometric/devices/${id}/sync/`);
      return extractOne<DeviceSyncLog>(res);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['biometric'] });
    },
  });
}
