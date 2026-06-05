import { NavLink } from "react-router";
import {
  LayoutDashboard,
  PenLine,
  FileStack,
  Scale,
  Palmtree,
  Users,
  ScrollText,
  Bell,
  PanelLeftClose,
  PanelLeft,
  type LucideIcon,
} from "lucide-react";
import { cn } from "../../ui/utils";
import { Button } from "../../ui/button";

const LINKS: { to: string; label: string; icon: LucideIcon; end?: boolean }[] = [
  { to: "/manager/leaves/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/manager/leaves/apply", label: "Apply Leave", icon: PenLine },
  { to: "/manager/leaves/applications", label: "My Applications", icon: FileStack },
  { to: "/manager/leaves/balance", label: "Leave Balance", icon: Scale },
  { to: "/manager/leaves/holidays", label: "Holiday Calendar", icon: Palmtree },
  { to: "/manager/leaves/team", label: "Team Calendar", icon: Users },
  { to: "/manager/leaves/policy", label: "Leave Policy", icon: ScrollText },
  { to: "/manager/leaves/notifications", label: "Notifications", icon: Bell },
];

export function ManagerLeaveSidebar({
  collapsed,
  onToggleCollapsed,
}: {
  collapsed: boolean;
  onToggleCollapsed?: () => void;
}) {
  return (
    <aside
      className={cn(
        "flex flex-shrink-0 flex-col border-b border-border bg-card lg:border-b-0 lg:border-r",
        "lg:sticky lg:top-0 lg:h-[calc(100vh-4rem)] lg:max-h-[calc(100vh-4rem)]",
        collapsed ? "lg:w-[72px]" : "lg:w-56"
      )}
    >
      <nav
        className={cn(
          "flex gap-1 overflow-x-auto px-2 py-2 lg:flex-1 lg:flex-col lg:overflow-y-auto lg:px-2 lg:py-3",
          "scrollbar-thin"
        )}
        aria-label="Leave module"
      >
        {LINKS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            title={collapsed ? label : undefined}
            className={({ isActive }) =>
              cn(
                "group relative flex items-center gap-2.5 rounded-xl px-2.5 py-2 text-left text-sm font-medium transition-all duration-150",
                "whitespace-nowrap lg:whitespace-normal",
                isActive
                  ? "bg-primary text-primary-foreground font-semibold shadow-lg shadow-primary/20"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50",
                collapsed && "lg:justify-center lg:px-2"
              )
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span
                    className="absolute left-0 top-1/2 hidden h-6 w-0.5 -translate-y-1/2 rounded-r-full bg-[#2B1555] lg:block"
                    aria-hidden
                  />
                )}

                <Icon
                  className={cn(
                    "h-[18px] w-[18px] flex-shrink-0 transition-transform duration-150",
                    "group-hover:scale-[1.02]"
                  )}
                  aria-hidden
                />

                {!collapsed && <span className="truncate">{label}</span>}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {onToggleCollapsed && (
        <div className="hidden border-t border-border p-2 lg:block">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className={cn(
              "h-9 w-full justify-center gap-2 rounded-xl text-xs font-semibold text-muted-foreground hover:text-[#2B1555]",
              collapsed && "px-2"
            )}
            onClick={onToggleCollapsed}
          >
            {collapsed ? (
              <PanelLeft className="h-4 w-4" />
            ) : (
              <PanelLeftClose className="h-4 w-4" />
            )}

            {!collapsed && <span>Collapse</span>}
          </Button>
        </div>
      )}
    </aside>
  );
}