import { Outlet, useNavigate, useLocation } from "react-router";
import { cn } from "../../../components/ui/utils";

const TABS = [
  { label: "Dashboard", path: "/admin/attendance/dashboard" },
  { label: "Who's In?", path: "/admin/attendance/whos-in" },
  { label: "Shift Roster", path: "/admin/attendance/roster" },
  { label: "Swipe Logs", path: "/admin/attendance/swipe-logs" },
  { label: "Attendance Matrix", path: "/admin/attendance/matrix" },
  { label: "Requests", path: "/admin/attendance/requests" },
];

export function AttendanceLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="flex flex-col h-full">
      {/* Secondary Top Navbar */}
      <div className="bg-card border-b border-border px-6 py-2 flex items-center gap-1 overflow-x-auto no-scrollbar">
        {TABS.map((tab) => {
          const isActive = location.pathname === tab.path;
          return (
            <button
              key={tab.label}
              onClick={() => !tab.disabled && navigate(tab.path)}
              disabled={tab.disabled}
              className={cn(
                "px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 whitespace-nowrap",
                isActive
                  ? "bg-secondary text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50",
                tab.disabled && "opacity-50 cursor-not-allowed grayscale"
              )}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto bg-background/50">
        <Outlet />
      </div>
    </div>
  );
}
