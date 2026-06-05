import { useState } from "react";
import {
  BarChart3,
  CalendarDays,
  FileText,
  ListChecks,
  Network,
  SlidersHorizontal,
  BookOpen,
} from "lucide-react";
import { AdminLeaveRequests } from "./sections/AdminLeaveRequests";
import { AdminHolidayCalendarManagement } from "./sections/AdminHolidayCalendarManagement";
import { SuperadminLeaveDashboard } from "./sections/SuperadminLeaveDashboard";
import { SuperadminLeaveRequests } from "./sections/SuperadminLeaveRequests";
import { SuperadminAuditLogs } from "./sections/SuperadminAuditLogs";
import { SuperadminReportsAnalytics } from "./sections/SuperadminReportsAnalytics";
import { SuperadminWorkflowSettings } from "./sections/SuperadminWorkflowSettings";
import { AdminLeaveAllocations } from "./sections/AdminLeaveAllocations";

type SectionId =
  | "dashboard"
  | "applications"
  // | "policies"
  | "holidays"
  | "audit"
  | "reports"
  | "workflow"
  | "legacy-requests"
  // | "leave-types"
  | "leave-allocations";

const SECTIONS: { id: SectionId; label: string; icon: React.ElementType }[] = [
  {
    id: "dashboard",
    label: "Leave Dashboard",
    icon: BarChart3,
  },
  {
    id: "applications",
    label: "Leave Applications",
    icon: ListChecks,
  },
  // {
  //   id: "policies",
  //   label: "Leave Policies",
  //   icon: ShieldCheck,
  // },
  // {
  //   id: "leave-types",
  //   label: "Leave Types",
  //   icon: Tag,
  // },
  {
    id: "leave-allocations",
    label: "Leave Allocations",
    icon: BookOpen,
  },
  {
    id: "holidays",
    label: "Holiday Management",
    icon: CalendarDays,
  },
  {
    id: "audit",
    label: "Audit Logs",
    icon: FileText,
  },
  {
    id: "reports",
    label: "Reports & Analytics",
    icon: BarChart3,
  },
  {
    id: "workflow",
    label: "Workflow Settings",
    icon: Network,
  },
  {
    id: "legacy-requests",
    label: "Legacy Requests View",
    icon: SlidersHorizontal,
  },
];

export function AdminLeaveModule() {
  const [active, setActive] = useState<SectionId>("dashboard");

  const handleTabClick = (id: SectionId) => {
    setActive(id);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Sub-header with tabs */}
      <div className="bg-card border-b border-border/60 px-6 flex items-center justify-between h-16 flex-shrink-0 z-10">
        <div className="flex items-center gap-0.5 overflow-x-auto flex-1">
          {SECTIONS.map((section) => {
            const Icon = section.icon;
            const isActive = active === section.id;
            return (
              <button
                key={section.id}
                onClick={() => handleTabClick(section.id)}
                className={`flex items-center gap-2 px-4 py-2.5 text-sm rounded-xl transition-all duration-150 font-medium whitespace-nowrap ${
                  isActive
                    ? "bg-primary text-primary-foreground font-semibold shadow-lg shadow-primary/20"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                }`}
              >
                <Icon className="w-4 h-4" />
                {section.label}
              </button>
            );
          })}
        </div>

        <span className="text-xs font-semibold text-muted-foreground bg-secondary border border-border/50 px-3 py-2 rounded-lg flex-shrink-0 ml-4 uppercase tracking-wide">
          {new Date().toLocaleDateString("en-IN", {
            weekday: "short",
            day: "2-digit",
            month: "short",
            year: "numeric",
          })}
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden bg-background">
        <div className="p-8 h-full overflow-y-auto">
          {active === "dashboard" && <SuperadminLeaveDashboard />}
          {active === "applications" && <SuperadminLeaveRequests title="Leave Applications" />}
          {active === "leave-allocations" && <AdminLeaveAllocations />}
          {active === "holidays" && <AdminHolidayCalendarManagement />}
          {active === "audit" && <SuperadminAuditLogs />}
          {active === "reports" && <SuperadminReportsAnalytics />}
          {active === "workflow" && <SuperadminWorkflowSettings />}
          {active === "legacy-requests" && <AdminLeaveRequests />}
        </div>
      </div>
    </div>
  );
}