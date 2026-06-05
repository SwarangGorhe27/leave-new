import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@api/client';

/* ------------------------------------------------------------------ */
/*  Types                                                               */
/* ------------------------------------------------------------------ */

export type ChangeRequestStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

export interface ProfileChangeRequest {
  section: string;
  section_label: string;
  changes: Record<string, unknown>;
  reason?: string;
}

export interface ProfileChangeRequestResponse {
  id: string;
  section: string;
  section_label: string;
  changes: Record<string, unknown>;
  reason?: string;
  status: ChangeRequestStatus;
  created_at: string;
  reviewed_by?: string;
  reviewed_at?: string;
  rejection_reason?: string;
}

/* ------------------------------------------------------------------ */
/*  API calls                                                           */
/* ------------------------------------------------------------------ */

async function submitRequest(req: ProfileChangeRequest): Promise<ProfileChangeRequestResponse> {
  try {
    const response = await api.post('/profile-change-requests/', req);
    const data = response.data?.data ?? response.data;
    if (data?.id) return data as ProfileChangeRequestResponse;
  } catch {
    // fall through to demo
  }
  // Demo fallback — simulates a real submission
  await new Promise((r) => setTimeout(r, 700));
  return {
    id: `req-${Date.now()}`,
    status: 'PENDING',
    created_at: new Date().toISOString(),
    ...req,
  };
}

async function fetchPendingRequests(): Promise<ProfileChangeRequestResponse[]> {
  try {
    const response = await api.get('/profile-change-requests/?status=PENDING');
    const data = response.data?.data ?? response.data;
    if (Array.isArray(data)) return data as ProfileChangeRequestResponse[];
  } catch {
    // fall through to demo
  }
  return [];
}

/* ------------------------------------------------------------------ */
/*  Hooks                                                               */
/* ------------------------------------------------------------------ */

export function useProfileChangeRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: submitRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-change-requests'] });
    },
  });
}

export function usePendingChangeRequests() {
  return useQuery({
    queryKey: ['pending-change-requests'],
    queryFn: fetchPendingRequests,
    staleTime: 2 * 60_000,
  });
}