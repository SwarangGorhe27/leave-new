import { Outlet, useNavigate, useLocation } from "react-router";
import { 
  FileText, 
  Megaphone, 
  Send, 
  ShieldCheck, 
  Handshake, 
} from "lucide-react";
import { cn } from "../../../components/ui/utils";

const TABS = [
  { label: "Identity Verification", path: "/admin/employees/management/verification", icon: ShieldCheck },
  { label: "Contract Details", path: "/admin/employees/management/contracts", icon: Handshake },
];

export function EmployeeManagementLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="flex flex-col h-full bg-background/50">
      {/* Secondary Top Navbar (Sub-navbar) */}
      <div className="bg-card/50 backdrop-blur-md border-b border-border px-6 py-2 flex items-center gap-1 overflow-x-auto no-scrollbar sticky top-0 z-20 shadow-sm">
        {TABS.map((tab) => {
          const isActive = location.pathname === tab.path;
          const Icon = tab.icon;
          return (
            <button
              key={tab.label}
              onClick={() => navigate(tab.path)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 whitespace-nowrap group",
                isActive
                  ? "bg-secondary text-foreground shadow-sm font-semibold"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              <Icon className={cn("w-4 h-4 transition-transform group-hover:scale-110", isActive ? "text-foreground" : "text-muted-foreground")} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
}
