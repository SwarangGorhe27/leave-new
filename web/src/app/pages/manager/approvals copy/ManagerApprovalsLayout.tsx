"use client";

import { NavLink, Outlet } from "react-router";
import { cn } from "../../../components/ui/utils";
import { ManagerLeaveDataProvider } from "../leaves/ManagerLeaveDataContext";

const TABS = [{ label: "Requests", to: "/manager/approvals/requests" }];

export function ManagerApprovalsLayout() {
  return (
    <ManagerLeaveDataProvider>
      <div className="space-y-6">
        <div className="flat-card bg-card p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-foreground">Approvals</p>
              {/* <p className="text-xs text-muted-foreground mt-1">
                Review and act on requests submitted by direct and indirect team members.
              </p> */}
            </div>

            <div className="flex flex-wrap gap-2 rounded-2xl bg-secondary/20 p-1.5">
              {TABS.map((tab) => (
                <NavLink
                  key={tab.to}
                  to={tab.to}
                  className={({ isActive }) =>
                    cn(
                      "inline-flex items-center rounded-full px-4 py-2 text-sm font-semibold transition",
                      isActive
                        ? "bg-foreground text-background"
                        : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                    )
                  }
                >
                  {tab.label}
                </NavLink>
              ))}
            </div>
          </div>
        </div>

        <Outlet />
      </div>
    </ManagerLeaveDataProvider>
  );
}
