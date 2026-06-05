/**
 * EmployeeModule — legacy wrapper component (not used by current routes).
 * Retained for backwards compatibility only. The active implementation
 * lives in EmployeesShell → EmployeeDirectory → InformationLayout.
 */
import { Outlet, useLocation, useNavigate } from "react-router";
import { Users, Info, Building2, Bell } from "lucide-react";

type ActiveTab = "directory" | "information";

export function EmployeeModule() {
  const location = useLocation();
  const navigate = useNavigate();

  const isInformation = location.pathname.includes("/information");
  const activeTab: ActiveTab = isInformation ? "information" : "directory";

  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      {/* Topbar */}
      <header className="bg-card border-b border-border px-6 flex items-center justify-between h-14 flex-shrink-0">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-foreground rounded-lg flex items-center justify-center">
              <Building2 className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="text-sm font-bold text-foreground">
              HR<span className="text-muted-foreground">MS</span>
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button className="w-8 h-8 flex items-center justify-center text-muted-foreground hover:text-foreground rounded-lg hover:bg-secondary transition-colors relative">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-foreground rounded-full" />
          </button>
          <div className="w-8 h-8 rounded-lg bg-foreground flex items-center justify-center text-primary-foreground text-xs font-bold">
            AD
          </div>
        </div>
      </header>

      {/* Sub-header */}
      <div className="bg-card border-b border-border px-6 flex items-center justify-between h-12 flex-shrink-0">
        <div className="flex items-center gap-1">
          <div className="flex items-center gap-2 mr-3">
            <Users className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-semibold text-foreground">Employees</span>
          </div>
          <button
            onClick={() => navigate("/admin/employees")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg transition-all font-medium ${
              activeTab === "directory"
                ? "bg-secondary text-foreground font-semibold"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground"
            }`}
          >
            <Users className="w-3.5 h-3.5" /> Directory
          </button>
          <button
            className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg transition-all font-medium ${
              activeTab === "information"
                ? "bg-secondary text-foreground font-semibold"
                : "text-muted-foreground/50 cursor-default"
            }`}
            title={activeTab !== "information" ? "Select an employee to view information" : undefined}
          >
            <Info className="w-3.5 h-3.5" /> Information
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  );
}
