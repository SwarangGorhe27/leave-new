import { Suspense } from "react";
import { NavLink, useLocation, useOutlet } from "react-router";
import { cn } from "../../../components/ui/utils";
import {
  Users,
  Info,
  UserPlus,
  Briefcase,
  Settings,
  GitGraph,
  LogOut,
} from "lucide-react";
import { useEmployee } from "../../../context/EmployeeContext";

export function EmployeesShell() {
  const location = useLocation();
  const outlet = useOutlet();
  const { selectedEmployeeId, clearSelection } = useEmployee();

  const isInformation = location.pathname.includes("/information");
  const isAddEmployee = location.pathname.includes("/add");
  const isManagement = location.pathname.includes("/management");
  const isSetup = location.pathname.includes("/setup");
  const isOrgChart = location.pathname.includes("/org-chart");
  const isOffboarding = location.pathname.includes("/offboarding");

  const activeTab = isInformation
    ? "information"
    : isAddEmployee
      ? "add"
      : isManagement
        ? "management"
        : isSetup
          ? "setup"
          : isOrgChart
            ? "org-chart"
            : isOffboarding
              ? "offboarding"
              : "directory";

  const tabClass = (isActive: boolean) =>
    cn(
      "relative z-[1] flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-150",
      isActive
        ? "bg-secondary font-semibold text-foreground"
        : "text-muted-foreground hover:bg-secondary hover:text-foreground",
    );

  return (
    <div className="employees-module-shell grid min-h-0 flex-1 grid-rows-[auto_minmax(0,1fr)] overflow-hidden">
      {/* Tabs must stay above React Flow (pane captures pointer events) */}
      <div className="employees-module-tabs sticky top-0 z-[200] flex h-14 shrink-0 items-center justify-between border-b border-border bg-card px-6 shadow-sm">
        <div className="relative z-[1] flex items-center gap-1">

          <NavLink
            to="/admin/employees"
            end
            onClick={() => clearSelection()}
            className={({ isActive }) => tabClass(isActive)}
          >
            <Users className="w-4 h-4" />
            Employee List
          </NavLink>

          <NavLink
            to="/admin/employees/add"
            className={({ isActive }) => tabClass(isActive)}
          >
            <UserPlus className="w-4 h-4" />
            Add Employee
          </NavLink>

          <NavLink
            to="/admin/employees/management/verification"
            className={({ isActive }) => tabClass(isActive || activeTab === "management")}
          >
            <Briefcase className="w-4 h-4" />
            Management
          </NavLink>

          <NavLink
            to="/admin/employees/setup"
            className={({ isActive }) => tabClass(isActive || activeTab === "setup")}
          >
            <Settings className="w-4 h-4" />
            Setup
          </NavLink>

          <NavLink
            to="/admin/employees/org-chart"
            onMouseEnter={() => {
              void import("./OrganizationChartPage");
            }}
            className={({ isActive }) => tabClass(isActive)}
          >
            <GitGraph className="w-4 h-4" />
            Org Chart
          </NavLink>

          <NavLink
            to="/admin/employees/offboarding"
            className={({ isActive }) => tabClass(isActive)}
          >
            <LogOut className="w-4 h-4" />
            Employee Offboarding
          </NavLink>

          {selectedEmployeeId && (
            <NavLink
              to={`/admin/employees/information/${selectedEmployeeId}`}
              className={({ isActive }) => tabClass(isActive)}
            >
              <Info className="w-4 h-4" />
              Information
            </NavLink>
          )}
        </div>

        <span className="text-xs font-medium text-muted-foreground bg-secondary border border-border px-3 py-1.5 rounded-lg">
          {new Date().toLocaleDateString("en-IN", {
            weekday: "long",
            day: "2-digit",
            month: "short",
            year: "numeric",
          })}
        </span>
      </div>

      <div className="employees-module-content relative z-0 flex min-h-0 flex-1 flex-col overflow-hidden bg-background">
        <Suspense
          fallback={
            <div className="flex h-full min-h-0 items-center justify-center text-sm font-medium text-muted-foreground">
              Loading…
            </div>
          }
        >
          <div key={location.key} className="employees-module-outlet flex min-h-0 flex-1 flex-col overflow-y-auto">
            {outlet}
          </div>
        </Suspense>
      </div>
    </div>
  );
}