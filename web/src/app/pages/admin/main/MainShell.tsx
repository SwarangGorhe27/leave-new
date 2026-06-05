import { Outlet, useLocation, useNavigate } from "react-router";
import {
  LayoutDashboard,
  Users,
  Box,
  ChevronDown
} from "lucide-react";

export function MainShell() {
  const location = useLocation();
  const navigate = useNavigate();

  const activeTab = location.pathname.includes("/analytics")
    ? "analytics"
    : location.pathname.includes("/directory-module")
      ? "directory-module"
      : "directory";

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Sub-header with tabs */}
      <div className="bg-card border-b border-border px-6 flex items-center justify-between h-14 flex-shrink-0 z-10">
        <div className="flex items-center gap-1">
          <button
            onClick={() => navigate("/admin/employees/main/analytics")}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-all duration-150 font-medium ${activeTab === "analytics"
                ? "bg-secondary text-foreground font-semibold"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Analytics Hub
          </button>

          <button
            onClick={() => navigate("/admin/employees/main/directory")}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-all duration-150 font-medium ${activeTab === "directory"
                ? "bg-secondary text-foreground font-semibold"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
          >
            <Users className="w-4 h-4" />
            Employee Directory
          </button>

          <button
            onClick={() => navigate("/admin/employees/main/directory-module")}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-all duration-150 font-medium ${activeTab === "directory-module"
                ? "bg-secondary text-foreground font-semibold"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
          >
            <Box className="w-4 h-4" />
            Employee Directory Module
          </button>
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

      {/* Content */}
      <div className="flex-1 overflow-hidden bg-background">
        <Outlet />
      </div>
    </div>
  );
}
