import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../../../api/client";
import {
  adminCreateHoliday,
  type CreateAdminHolidayPayload,
} from "../../../api/leaveApi";

export interface AdminLeaveApplicationApiRow {
  id: string;
  leave_type_id: string;
  leave_type: string;
  from_date: string;
  to_date: string;
  total_days: number;
  leave_status: string;
  applied_at: string;
}

export interface AdminLeaveApplicationListResponse {
  items: AdminLeaveApplicationApiRow[];
  total: number;
}

export interface AdminLeaveBalanceApiRow {
  id: string;
  employee_id: string;
  employee_code: string;
  leave_type: string;
  leave_type_detail: {
    id: string;
    name: string;
    code: string;
    color_code: string;
    is_paid: boolean;
  };
  period_start: string;
  period_end: string;
  opening_balance: number;
  accrued: number;
  used: number;
  pending_approval: number;
  carry_forwarded: number;
  encashed: number;
  available: number;
  total_allocated: number;
}

export interface AdminLeaveHolidayApiRow {
  id: string;
  holiday_calendar_id: string;
  calendar: {
    id: string;
    code: string;
    name: string;
    calendar_year: number;
    branch_id: string | null;
  };
  holiday_date: string;
  name: string;
  holiday_type: string;
  is_active: boolean;
}

async function fetchAdminLeaveApplications(page = 1) {
  const response = await api.get<AdminLeaveApplicationListResponse>(
    "/leave/admin/applications",
    {
      params: { page },
    },
  );

  return {
    items: response.data.items ?? [],
    total: response.data.total ?? 0,
  };
}

export function useAdminLeaveApplications(page?: number) {
  return useQuery<AdminLeaveApplicationListResponse>({
    queryKey: ["admin-leave-applications", page ?? 1],
    queryFn: () => fetchAdminLeaveApplications(page ?? 1),
    staleTime: 60_000,
    gcTime: 5 * 60 * 1000,
    retry: 1,
    retryDelay: 1000,
  });
}

async function fetchAdminLeaveHolidays(year?: number) {
  const response = await api.get("/leave/admin/holidays", {
    params: year ? { year } : undefined,
  });

  return (response.data?.data ?? response.data ?? []) as AdminLeaveHolidayApiRow[];
}

export function useAdminLeaveHolidays(year: number) {
  return useQuery<AdminLeaveHolidayApiRow[]>({
    queryKey: ["admin-leave-holidays", year],
    queryFn: () => fetchAdminLeaveHolidays(year),
    staleTime: 60_000,
    gcTime: 5 * 60 * 1000,
    retry: 1,
    retryDelay: 1000,
  });
}

export function useCreateAdminHoliday(year: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateAdminHolidayPayload) => adminCreateHoliday(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-leave-holidays", year] });
      queryClient.invalidateQueries({ queryKey: ["holidays-upcoming"] });
    },
  });
}

async function fetchAdminLeaveBalances() {
  const response = await api.get("/leave/admin/balances");
  return (response.data?.data ?? response.data ?? []) as AdminLeaveBalanceApiRow[];
}

export function useAdminLeaveBalances() {
  return useQuery<AdminLeaveBalanceApiRow[]>({
    queryKey: ["admin-leave-balances"],
    queryFn: fetchAdminLeaveBalances,
    staleTime: 60_000,
    gcTime: 5 * 60 * 1000,
    retry: 1,
    retryDelay: 1000,
  });
}
