import { useRef, useState } from "react";
import { Outlet, useNavigate, useLocation, Navigate } from "react-router";
import {
  LayoutDashboard,
  Users,
  Clock,
  CalendarDays,
  Wallet,
  FileText,
  Bell,
  Building2,
  LogOut,
  Menu,
  ChevronRight,
  Sun,
  Moon,
  ClipboardCheck,
  Settings2,
  Search,
  Mail,
  Megaphone,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";
import { EmployeeProvider } from "../../context/EmployeeContext";
import { ProfileUserMenu } from "../../../components/layout/ProfileUserMenu";

const PROFILE_PATH = "/admin/profile";

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/admin/dashboard" },
  { icon: Users, label: "Employees", path: "/admin/employees" },
  { icon: Clock, label: "Attendance", path: "/admin/attendance" },
  { icon: CalendarDays, label: "Leave", path: "/admin/leave" },
  { icon: Wallet, label: "Payroll", path: "/admin/payroll" },
  { icon: Mail, label: "Letters & Policies", path: "/admin/letters-policies" },
  { icon: Megaphone, label: "Communication Center", path: "/admin/communication-center" },
  { icon: FileText, label: "Documents", path: "/admin/documents" },
  { icon: Settings2, label: "Settings", path: "/admin/settings" },
  { icon: ClipboardCheck, label: "Profile Requests", path: "/admin/profile-requests" },
];

export function AdminLayout() {
  const { user, logout, isAuthenticated } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileTriggerRef = useRef<HTMLButtonElement>(null);

  if (!isAuthenticated || user?.role !== "admin") {
    return <Navigate to="/login" replace />;
  }

  const isActive = (path: string) => {
    if (path === "/admin/employees") return location.pathname.startsWith("/admin/employees");
    return location.pathname === path || location.pathname.startsWith(path + "/");
  };

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };
  const currentPage =
    location.pathname === PROFILE_PATH
      ? "My Profile"
      : NAV_ITEMS.find((n) => isActive(n.path))?.label ?? "Dashboard";

  const isEmployeesModule = location.pathname.startsWith("/admin/employees");

  return (
    <div className="app-shell flex h-screen overflow-hidden bg-background text-foreground">
      {/* Sidebar */}
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
                Admin Console
              </p>
            </div>
          )}
        </div>

        {!collapsed && (
          <p className="sidebar-section-title text-white/50 text-[10px] uppercase tracking-widest font-semibold px-2 pt-3 pb-2">Navigation</p>
        )}

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
                {!collapsed && active && (
                  <ChevronRight className="w-3 h-3 ml-auto opacity-60" />
                )}
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
                  <p className="text-[12px] font-semibold text-white truncate leading-tight">
                    {user?.name}
                  </p>
                  <p className="text-[10px] text-white/60 truncate">Administrator</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                title="Logout"
                className="app-icon-button p-1 rounded-md flex-shrink-0 text-white/70 hover:text-white"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main area */}
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
              className="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-secondary border border-transparent
                hover:border-border transition-all duration-150"
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

        <main
          className={`app-main flex min-h-0 flex-1 flex-col overflow-x-hidden ${
            isEmployeesModule ? "overflow-hidden" : "overflow-y-auto"
          }`}
        >
          <EmployeeProvider>
            <Outlet />
          </EmployeeProvider>
        </main>
      </div>

    </div>
  );
}
