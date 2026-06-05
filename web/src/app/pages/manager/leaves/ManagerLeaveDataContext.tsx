import React from "react";
import {
  LeavePortalDataProvider,
  useLeavePortalData,
  type LeavePortalDataContextValue,
} from "../../leaves/LeavePortalDataContext";

export type ManagerLeaveDataContextValue = LeavePortalDataContextValue;

export function ManagerLeaveDataProvider({ children }: { children: React.ReactNode }) {
  return <LeavePortalDataProvider role="manager">{children}</LeavePortalDataProvider>;
}

export function useManagerLeaveData() {
  return useLeavePortalData();
}
