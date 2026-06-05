import { useMemo, useRef, useState } from "react";
import { Outlet, useNavigate, Navigate, useLocation } from "react-router";
import {
  LayoutDashboard,
  Clock,
  CalendarDays,
  Wallet,
  FileText,
  Bell,
  LogOut,
  Building2,
  ChevronRight,
  Menu,
  Sun,
  Moon,
  Users,
  BarChart3,
  CheckCircle2,
  UserCheck,
  Building,
  Search,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";
import { ProfileUserMenu } from "../../../components/layout/ProfileUserMenu";

const PROFILE_PATH = "/manager/profile";

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/manager/dashboard" },
  { icon: Clock, label: "Attendance", path: "/manager/attendance" },
  { icon: CalendarDays, label: "My Leaves", path: "/manager/leaves" },
  { icon: Wallet, label: "Payslips", path: "/manager/payslips" },
  { icon: FileText, label: "Documents", path: "/manager/documents" },
  { icon: Users, label: "Team Dashboard", path: "/manager/team-dashboard" },
  { icon: UserCheck, label: "Team Attendance", path: "/manager/team-attendance" },
  { icon: CheckCircle2, label: "Approvals", path: "/manager/approvals" },
  { icon: BarChart3, label: "Reports", path: "/manager/reports" },
  { icon: Building, label: "Organization Chart", path: "/manager/org-chart" },
];

export function ManagerLayout() {
  const { user, logout, isAuthenticated } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileTriggerRef = useRef<HTMLButtonElement>(null);

  if (!isAuthenticated || user?.role !== "manager") {
    return <Navigate to="/login" replace />;
  }

  const isActive = (path: string) =>
    path === "/manager/leaves"
      ? location.pathname.startsWith("/manager/leaves")
      : location.pathname === path || location.pathname.startsWith(path + "/");

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const currentPage = useMemo(() => {
    if (location.pathname.startsWith("/manager/leaves")) {
      const seg = location.pathname.split("/").filter(Boolean).pop() ?? "dashboard";
      const titles: Record<string, string> = {
        leaves: "Leave center",
        dashboard: "Leave · Dashboard",
        apply: "Leave",
        applications: "Leave",
        balance: "Leave",
        holidays: "Leave",
        team: "Leave · Team",
        policy: "Leave",
        notifications: "Leave",
      };
      return titles[seg] ?? "Leave center";
    }
    if (location.pathname === PROFILE_PATH) return "My Profile";
    return NAV_ITEMS.find((n) => isActive(n.path))?.label ?? "Dashboard";
  }, [location.pathname]);

  return (
    <div className="app-shell flex h-screen overflow-hidden bg-background text-foreground">
      <aside
        className={`app-sidebar flex flex-col flex-shrink-0 border-r border-white/10 bg-[#2B1555]
          transition-all duration-200 ease-in-out overflow-hidden
          ${collapsed ? "w-[68px]" : "w-[220px]"}`}
      >
        <div
          className={`app-sidebar-logo flex items-center flex-shrink-0 border-b border-white/10
          ${collapsed ? "justify-center px-0" : "px-4 gap-2.5"}`}
        >
          <div className="w-7 h-7 rounded-md bg-white/20 flex items-center justify-center flex-shrink-0">
            <Building2 className="w-3.5 h-3.5 text-white" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-[13px] font-bold text-white leading-tight">
                HR<span className="text-white/70 font-semibold">MS</span>
              </p>
              <p className="text-[9px] text-white/60 tracking-wider uppercase font-medium">
                Manager Portal
              </p>
            </div>
          )}
        </div>

        {!collapsed && <p className="sidebar-section-title text-white/50 text-[10px] uppercase tracking-widest font-semibold px-2 pt-3 pb-2">Navigation</p>}

        <nav className={`flex-1 overflow-y-auto ${collapsed ? "px-2 pt-3 space-y-0.5" : "px-2 space-y-0.5"}`}>
          {NAV_ITEMS.map(({ icon: Icon, label, path }) => {
            const active = isActive(path);
            return (
              <button
                key={path}
                onClick={() => navigate(path)}
                title={collapsed ? label : undefined}
                className={`app-nav-item w-full flex items-center gap-2.5 rounded-md text-[12px] font-medium
                  transition-all duration-150
                  ${active ? "bg-white/15 text-white" : "text-white/70 hover:bg-white/10 hover:text-white"}
                  ${collapsed ? "justify-center px-2 py-2" : "px-2.5 py-2"}`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {!collapsed && <span className="truncate">{label}</span>}
                {!collapsed && active && <ChevronRight className="w-3 h-3 ml-auto opacity-60" />}
              </button>
            );
          })}
        </nav>

        <div className="px-2 pb-2 border-t border-white/10 pt-2">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className={`app-nav-item w-full flex items-center gap-2.5 rounded-md text-[12px] font-medium text-white/70 hover:text-white hover:bg-white/10
              ${collapsed ? "justify-center px-2 py-2" : "px-2.5 py-2"}`}
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <Menu className="w-4 h-4 flex-shrink-0" />
            {!collapsed && <span>Collapse</span>}
          </button>
        </div>

        <div className="border-t border-white/10 p-2">
          {collapsed ? (
            <button
              onClick={handleLogout}
              title="Logout"
              className="app-nav-item w-full flex items-center justify-center py-2 rounded-md text-white/70 hover:text-white hover:bg-white/10"
            >
              <LogOut className="w-4 h-4" />
            </button>
          ) : (
            <div className="flex items-center justify-between px-2 py-1.5 rounded-md hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-2 min-w-0">
                <div className="premium-avatar w-7 h-7 rounded-md bg-white/20 text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                  {user?.initials}
                </div>
                <div className="min-w-0">
                  <p className="text-[12px] font-semibold text-white truncate leading-tight">{user?.name}</p>
                  <p className="text-[10px] text-white/60 truncate">Manager</p>
                </div>
              </div>
              <button onClick={handleLogout} title="Logout" className="app-icon-button p-1 rounded-md flex-shrink-0 text-white/70 hover:text-white">
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        <header className="app-topbar flex items-center justify-between px-4 flex-shrink-0 sticky top-0 z-30">
          <div className="min-w-0">
            <h1 className="text-[13px] font-semibold text-foreground leading-tight">{currentPage}</h1>
            <p className="text-[10px] text-muted-foreground leading-tight mt-0.5">
              {new Date().toLocaleDateString("en-IN", {
                weekday: "short",
                day: "2-digit",
                month: "short",
                year: "numeric",
              })}
            </p>
          </div>

          <div className="flex items-center gap-1.5">
            <div className="app-search hidden md:flex items-center gap-2 px-2.5">
              <Search className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
              <input
                className="h-full flex-1 border-0 bg-transparent p-0 text-[12px] shadow-none outline-none placeholder:text-muted-foreground text-foreground"
                placeholder="Search anything"
                aria-label="Global search"
              />
            </div>

            <button
              onClick={toggleTheme}
              className="app-icon-button flex items-center justify-center"
              title={isDark ? "Light mode" : "Dark mode"}
            >
              {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
            </button>

            <button
              type="button"
              onClick={() => navigate("/manager/leaves/notifications")}
              className="app-icon-button flex items-center justify-center relative"
              title="Notifications"
            >
              <Bell className="w-3.5 h-3.5" />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-primary" />
            </button>

            <div className="w-px h-5 bg-border mx-0.5 hidden sm:block" />

            <button
              ref={profileTriggerRef}
              type="button"
              onClick={() => setProfileOpen((open) => !open)}
              className="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-secondary border border-transparent hover:border-border transition-all duration-150"
              aria-expanded={profileOpen}
              aria-haspopup="menu"
            >
              <div className="premium-avatar w-6 h-6 rounded-md bg-primary text-primary-foreground flex items-center justify-center text-[9px] font-bold">
                {user?.initials}
              </div>
              <span className="text-[12px] font-medium text-foreground hidden sm:block max-w-[120px] truncate">
                {user?.name}
              </span>
            </button>
            <ProfileUserMenu
              open={profileOpen}
              onClose={() => setProfileOpen(false)}
              anchorRef={profileTriggerRef}
              profilePath={PROFILE_PATH}
              userName={user?.name}
              userEmail={user?.email}
              onLogout={handleLogout}
            />
          </div>
        </header>

        <main className="app-main flex-1 overflow-x-hidden overflow-y-auto">
          <Outlet />
        </main>
      </div>

    </div>
  );
}
