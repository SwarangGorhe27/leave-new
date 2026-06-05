import React from "react";
import {
  LeavePortalDataProvider,
  useLeavePortalData,
  type LeavePortalDataContextValue,
} from "../../leaves/LeavePortalDataContext";

export type EmployeeLeaveDataContextValue = LeavePortalDataContextValue;

export function EmployeeLeaveDataProvider({ children }: { children: React.ReactNode }) {
  return <LeavePortalDataProvider role="employee">{children}</LeavePortalDataProvider>;
}

export function useEmployeeLeaveData() {
  return useLeavePortalData();
}
