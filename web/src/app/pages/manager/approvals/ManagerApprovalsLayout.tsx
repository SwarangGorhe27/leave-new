"use client";

import { Outlet } from "react-router";
import { ManagerLeaveDataProvider } from "../leaves/ManagerLeaveDataContext";

export function ManagerApprovalsLayout() {
  return (
    <ManagerLeaveDataProvider>
      <Outlet />
    </ManagerLeaveDataProvider>
  );
}
