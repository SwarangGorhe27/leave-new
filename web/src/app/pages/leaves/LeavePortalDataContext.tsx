import React, { createContext, useCallback, useContext, useMemo } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  useAllLeaveApplications,
  useLeaveTypes,
  useMyLeaveApplications,
  useMyLeaveBalances,
  useUpcomingHolidays,
} from "../../modules/leaves/useLeaves";
import type { LeavePortalRole } from "../../modules/leaves/leavePortalConfig";
import type { HolidayAPI, LeaveApplicationAPI, LeaveBalanceAPI, LeaveTypeRef } from "../../modules/leaves/types";

const PENDING_STATUSES = new Set(["SUBMITTED", "DRAFT", "PENDING"]);

function employeeCodeFromUser(
  user: ReturnType<typeof useAuth>["user"],
  role: LeavePortalRole,
): string {
  if (!user || user.role !== role) return "EMP-0001";
  if (user.employeeId) return `EMP-${String(user.employeeId).padStart(4, "0")}`;
  return "EMP-0001";
}

export interface LeavePortalDataContextValue {
  role: LeavePortalRole;
  employeeCode: string;
  employeeName: string;
  year: number;
  leaveTypes: LeaveTypeRef[];
  balances: LeaveBalanceAPI[];
  applications: LeaveApplicationAPI[];
  teamApplications: LeaveApplicationAPI[];
  teamPendingApplications: LeaveApplicationAPI[];
  holidays: HolidayAPI[];
  refreshBalances: () => void;
  refreshApplications: () => void;
  refreshTeam: () => void;
  refreshAll: () => void;
}

const Ctx = createContext<LeavePortalDataContextValue | null>(null);

export function LeavePortalDataProvider({
  role,
  children,
}: {
  role: LeavePortalRole;
  children: React.ReactNode;
}) {
  const { user } = useAuth();
  const employeeCode = employeeCodeFromUser(user, role);
  const employeeName = user?.name ?? (role === "manager" ? "Manager" : "Employee");
  const year = new Date().getFullYear();

  const leaveTypesQ = useLeaveTypes();
  const balancesQ = useMyLeaveBalances(employeeCode);
  const appsQ = useMyLeaveApplications(employeeCode);
  const allAppsQ = useAllLeaveApplications();
  const holidaysQ = useUpcomingHolidays(year);

  const refreshAll = useCallback(() => {
    balancesQ.refresh();
    appsQ.refresh();
    allAppsQ.refresh();
  }, [balancesQ, appsQ, allAppsQ]);

  const teamApplications = useMemo(
    () => allAppsQ.data.filter((a) => a.employee_code !== employeeCode && a.status === "APPROVED"),
    [allAppsQ.data, employeeCode],
  );

  const teamPendingApplications = useMemo(() => {
    if (role !== "manager") return [];
    return allAppsQ.data.filter(
      (a) => a.employee_code !== employeeCode && PENDING_STATUSES.has(a.status),
    );
  }, [allAppsQ.data, employeeCode, role]);

  const value = useMemo<LeavePortalDataContextValue>(
    () => ({
      role,
      employeeCode,
      employeeName,
      year,
      leaveTypes: leaveTypesQ.data ?? [],
      balances: balancesQ.data ?? [],
      applications: appsQ.data ?? [],
      teamApplications,
      teamPendingApplications,
      holidays: holidaysQ.data ?? [],
      refreshBalances: balancesQ.refresh,
      refreshApplications: () => {
        appsQ.refresh();
        allAppsQ.refresh();
      },
      refreshTeam: allAppsQ.refresh,
      refreshAll,
    }),
    [
      role,
      refreshAll,
      employeeCode,
      employeeName,
      year,
      leaveTypesQ.data,
      balancesQ.data,
      appsQ.data,
      teamApplications,
      teamPendingApplications,
      holidaysQ.data,
      balancesQ.refresh,
      appsQ.refresh,
      allAppsQ.refresh,
    ],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useLeavePortalData() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useLeavePortalData must be used within LeavePortalDataProvider");
  return v;
}
