import { AlertTriangle, BarChart3, Briefcase, CalendarDays, CheckCircle2, Clock, UserCheck, Users } from "lucide-react";
import { useMemo } from "react";
import {
  PortalPage,
  SectionLabel,
  KpiCard,
  WidgetHeader,
  KPI_ICON_TONES,
  type KpiTone,
} from "../../../../../components/design-system";
import { useUpcomingHolidays } from "../../../../modules/leaves/useLeaves";
import { useAdminLeaveRequestsStore } from "../../../../modules/adminLeave/store";

export function SuperadminLeaveDashboard() {
  const { activeRows } = useAdminLeaveRequestsStore();
  const holidaysQ = useUpcomingHolidays(new Date().getFullYear());

  const metrics = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    const pending = activeRows.filter((r) => r.status === "SUBMITTED");
    const approvedToday = activeRows.filter((r) => r.status === "APPROVED" && r.audit.some((a) => a.action.includes("APPROVE") && a.at.startsWith(today)));
    const rejected = activeRows.filter((r) => r.status === "REJECTED");
    const onLeave = activeRows.filter((r) => r.status === "APPROVED").length;
    const escalated = activeRows.filter((r) => r.priority === "CRITICAL" && r.status === "SUBMITTED").length;
    const compOffPending = activeRows.filter((r) => r.category === "COMP_OFF" && r.status === "SUBMITTED").length;
    const activeWfh = activeRows.filter((r) => r.category === "WFH" && r.status === "APPROVED").length;
    return { pending, approvedToday, rejected, onLeave, escalated, compOffPending, activeWfh };
  }, [activeRows]);

  return (
    <PortalPage>
      {/* TOP — KPI row with exact dashboard styling */}
      <section>
        <SectionLabel label="Overview" />
        <div className="grid grid-cols-2 xl:grid-cols-5 gap-3">
          <KpiCard
            icon={Users}
            label="Employees on Leave"
            value={metrics.onLeave}
            sub="Currently approved"
            tone="purple"
          />

          <KpiCard
            icon={Clock}
            label="Pending Approvals"
            value={metrics.pending.length}
            sub="Awaiting action"
            tone="orange"
          />

          <KpiCard
            icon={CheckCircle2}
            label="Approved Today"
            value={metrics.approvedToday.length}
            sub="Across workflows"
            tone="green"
          />

          <KpiCard
            icon={AlertTriangle}
            label="Rejected Requests"
            value={metrics.rejected.length}
            sub="Current period"
            tone="red"
          />

          <KpiCard
            icon={CalendarDays}
            label="Upcoming Holidays"
            value={holidaysQ.data.length}
            sub="Configured calendar"
            tone="gray"
          />
        </div>
      </section>

      {/* MIDDLE — Analytics */}
      <section>
        <SectionLabel label="Distribution & Alerts" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          {/* Leave Distribution by Department */}
          <div className="dashboard-widget lg:col-span-2">
            <WidgetHeader
              icon={BarChart3}
              title="Leave Distribution by Department"
              subtitle="Headcount across teams"
              tone="purple"
            />
            <div className="space-y-2 mt-4">
              {Object.entries(
                activeRows.reduce<Record<string, number>>((acc, row) => {
                  acc[row.employee.department] = (acc[row.employee.department] ?? 0) + 1;
                  return acc;
                }, {}),
              ).map(([dept, count]) => (
                <div key={dept} className="p-3 rounded-lg border border-border bg-background/50 flex items-center justify-between hover:bg-secondary transition-colors">
                  <p className="text-sm font-semibold text-foreground">{dept}</p>
                  <span className="text-[11px] font-bold text-primary bg-primary/10 px-3 py-1 rounded-full border border-primary/20">
                    {count} Leaves
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Command Center Alerts */}
          <div className="dashboard-widget">
            <WidgetHeader
              icon={AlertTriangle}
              title="Command Center Alerts"
              subtitle="Escalations & special requests"
              tone="orange"
            />
            <div className="space-y-2 mt-4">
              {[
                { icon: Briefcase, label: "Comp Off Pending", value: metrics.compOffPending, tone: "purple" as KpiTone },
                { icon: UserCheck, label: "Active WFH Requests", value: metrics.activeWfh, tone: "green" as KpiTone },
                { icon: AlertTriangle, label: "Escalated Requests", value: metrics.escalated, tone: "red" as KpiTone },
              ].map(({ icon: Icon, label, value, tone }) => {
                const iconTone = KPI_ICON_TONES[tone];
                return (
                  <div key={label} className="dashboard-lifecycle-card">
                    <div className="flex items-center gap-3 justify-between">
                      <div className="flex items-center gap-3 min-w-0">
                        <div
                          className="dashboard-widget-icon w-8 h-8"
                          style={{
                            background: iconTone.background,
                            boxShadow: iconTone.boxShadow,
                          }}
                        >
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <p className="text-[12px] font-semibold text-foreground truncate">{label}</p>
                      </div>
                      <span className="min-w-[24px] h-[24px] px-1.5 rounded bg-primary text-primary-foreground text-[9px] font-bold flex items-center justify-center flex-shrink-0">
                        {value}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 p-3 rounded-lg border border-border bg-background/50">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                <p className="text-[11px] text-muted-foreground font-semibold">Use Reports & Analytics for exportable deep insights.</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </PortalPage>
  );
}

