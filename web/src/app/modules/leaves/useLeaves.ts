import { useCallback, useEffect, useState } from "react";
import type { UseQueryResult } from "@tanstack/react-query";
import {
  useApplyLeave as useApplyLeaveApi,
  useCancelLeave as useCancelLeaveApi,
  useMyLeaveApplications as useMyLeaveApplicationsApi,
  useMyLeaveBalances as useMyLeaveBalancesApi,
  useLeaveApplicationDetail as useLeaveApplicationDetailApi,
  useLeaveTypes as useLeaveTypesApi,
  useResubmitLeave as useResubmitLeaveApi,
  useUpdateLeave as useUpdateLeaveApi,
  useUpcomingHolidays as useUpcomingHolidaysApi,
  DEMO_APPLICATIONS,
  readStore,
  writeStore,
} from "../../../hooks/useLeave";
import type {
  ApplyLeavePayload,
  HolidayAPI,
  LeaveApplicationAPI,
  LeaveApplicationStatus,
  LeaveBalanceAPI,
  LeaveTypeRef,
  UpdateLeavePayload,
} from "./types";

const LEAVE_APP_KEY = "hrms-demo-leave-applications";

// ── Re-export types needed by components ─────────────────────────────────────
export type {
  ApplyLeavePayload,
  HolidayAPI,
  LeaveApplicationAPI,
  LeaveApplicationStatus,
  LeaveBalanceAPI,
  LeaveTypeRef,
  UpdateLeavePayload,
};

// ─────────────────────────────────────────────────────────────────────────────
// ESS hooks (employee self-service)
// ─────────────────────────────────────────────────────────────────────────────

export function useLeaveTypes() {
  const q = useLeaveTypesApi();
  return { data: q.data ?? [], refresh: q.refetch, isLoading: q.isLoading, error: q.error };
}

/** employeeCode is accepted for API compatibility; the real filter happens on the backend. */
export function useMyLeaveBalances(_employeeCode?: string) {
  const q = useMyLeaveBalancesApi();
  return { data: q.data ?? [], refresh: q.refetch, isLoading: q.isLoading, error: q.error };
}

/** year is accepted for API compatibility; the real filter happens on the backend. */
export function useMyLeaveApplications(_employeeCode?: string) {
  const q = useMyLeaveApplicationsApi();
  return { data: q.data ?? [], refresh: q.refetch, isLoading: q.isLoading, error: q.error };
}

export function useLeaveApplicationDetail(id: string | null): {
  data: LeaveApplicationAPI | null;
  refresh: UseQueryResult<LeaveApplicationAPI, Error>["refetch"];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
} {
  const q = useLeaveApplicationDetailApi(id);
  return {
    data: q.data as LeaveApplicationAPI | null,
    refresh: q.refetch,
    isLoading: q.isLoading,
    isError: q.isError,
    error: q.error ?? null,
  };
}

export function useUpcomingHolidays(_year?: number) {
  const q = useUpcomingHolidaysApi();
  return { data: q.data ?? [], refresh: q.refetch, isLoading: q.isLoading, error: q.error };
}

/**
 * useApplyLeave
 *
 * Payload shape (LeaveApplicationCreateSerializer):
 *   { leave_type_id, from_date, to_date, reason?, is_half_day }
 *
 * Note: `employee` param is kept for call-site compatibility but not sent to
 * the API (the backend derives employee from the auth token).
 */
export function useApplyLeave(_employee?: { employee_code: string; employee_name: string }) {
  const mutation = useApplyLeaveApi();
  return { ...mutation, isPending: mutation.isPending };
}

/**
 * useCancelLeave
 *
 * mutateAsync({ id, reason? })
 * Payload: { reason: string }  (LeaveApplicationCancelSerializer)
 */
export function useCancelLeave() {
  const mutation = useCancelLeaveApi();
  return { ...mutation, isPending: mutation.isPending };
}

/**
 * useUpdateLeave
 *
 * mutateAsync({ id, payload })
 * Payload: LeaveApplicationUpdateSerializer
 *   { leave_type_id?, from_date?, to_date?, is_half_day?, reason? }
 */
export function useUpdateLeave() {
  const mutation = useUpdateLeaveApi();
  return { ...mutation, isPending: mutation.isPending };
}

export function useResubmitLeave() {
  const mutation = useResubmitLeaveApi();
  return { ...mutation, isPending: mutation.isPending };
}

// ─────────────────────────────────────────────────────────────────────────────
// Local / admin hooks (offline-first, localStorage backed)
// ─────────────────────────────────────────────────────────────────────────────

/** Returns all cached applications (used by admin views). */
export function useAllLeaveApplications() {
  const [data, setData] = useState<LeaveApplicationAPI[]>(() =>
    readStore(LEAVE_APP_KEY, DEMO_APPLICATIONS),
  );

  const refresh = useCallback(() => {
    setData(readStore(LEAVE_APP_KEY, DEMO_APPLICATIONS));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  return { data, refresh, isLoading: false, error: null as unknown };
}

/** Admin: approve a leave application in the local cache. */
export function useApproveLeave() {
  const [isPending, setIsPending] = useState(false);

  const mutate = useCallback(async (id: string) => {
    setIsPending(true);
    try {
      const apps = readStore<LeaveApplicationAPI>(LEAVE_APP_KEY, DEMO_APPLICATIONS).map((app) =>
        app.id === id
          ? {
              ...app,
              leave_status: "APPROVED" as LeaveApplicationStatus,
              status:       "APPROVED" as LeaveApplicationStatus,
              approved_at:  new Date().toISOString(),
            }
          : app,
      );
      writeStore(LEAVE_APP_KEY, apps);
      return apps.find((a) => a.id === id);
    } finally {
      setIsPending(false);
    }
  }, []);

  return { mutate, isPending };
}

/** Admin: reject a leave application in the local cache. */
export function useRejectLeave() {
  const [isPending, setIsPending] = useState(false);

  const mutate = useCallback(async ({ id, remarks }: { id: string; remarks?: string }) => {
    setIsPending(true);
    try {
      const apps = readStore<LeaveApplicationAPI>(LEAVE_APP_KEY, DEMO_APPLICATIONS).map((app) =>
        app.id === id
          ? {
              ...app,
              leave_status: "REJECTED" as LeaveApplicationStatus,
              status:       "REJECTED" as LeaveApplicationStatus,
              reason: remarks?.trim()
                ? `${app.reason ?? ""} (Rejected: ${remarks.trim()})`
                : app.reason,
            }
          : app,
      );
      writeStore(LEAVE_APP_KEY, apps);
      return apps.find((a) => a.id === id);
    } finally {
      setIsPending(false);
    }
  }, []);

  return { mutate, isPending };
}