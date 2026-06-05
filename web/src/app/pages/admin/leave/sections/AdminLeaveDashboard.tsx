import {
  BarChart3,
  CalendarDays,
  Clock,
  FileText,
  ShieldCheck,
  TrendingUp,
  Users,
} from "lucide-react";
import { KpiCard, SectionLabel, WidgetHeader } from "../../../../components/design-system";

export function AdminLeaveDashboard() {
  return (
    <div className="flex flex-col gap-4">
      <section>
        <SectionLabel label="Overview" />
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
          <KpiCard icon={FileText} label="Open Requests" value="18" sub="Submitted / in review" tone="purple" />
          <KpiCard icon={Clock} label="SLA Risk" value="3" sub="Due in 24 hours" tone="red" />
          <KpiCard icon={Users} label="Absenteeism" value="6.2%" sub="30-day rolling avg" tone="orange" />
          <KpiCard icon={CalendarDays} label="Holidays" value="10" sub="Configured for 2026" tone="green" />
        </div>
      </section>

      <section>
        <SectionLabel label="Analytics" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <div className="dashboard-widget lg:col-span-2">
            <WidgetHeader icon={TrendingUp} title="Leave Trends" subtitle="Monthly utilization and distribution" tone="purple" />
            <div className="grid grid-cols-6 sm:grid-cols-12 gap-2">
              {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="col-span-3 sm:col-span-2">
                  <div
                    className="h-16 rounded-md bg-secondary border border-border"
                    style={{ opacity: 0.4 + (i % 4) * 0.15 }}
                  />
                  <p className="text-[9px] font-semibold text-muted-foreground uppercase tracking-wider mt-1.5 text-center">
                    {["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][i]}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="dashboard-widget">
            <WidgetHeader icon={ShieldCheck} title="Approvals Health" subtitle="Bottlenecks and SLA snapshots" tone="green" />
            <div className="space-y-2">
              {[
                { label: "Level 1", value: "8 pending" },
                { label: "Level 2", value: "6 pending" },
                { label: "Escalations", value: "3 triggered" },
                { label: "Auto-approvals", value: "2 enabled" },
              ].map((x) => (
                <div key={x.label} className="dashboard-lifecycle-card">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-[12px] font-semibold text-foreground">{x.label}</p>
                    <span className="dashboard-badge-soon px-1.5 py-0.5 rounded text-[9px] font-semibold">{x.value}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="dashboard-lifecycle-card mt-3">
              <div className="flex items-center gap-3">
                <div className="dashboard-widget-icon w-8 h-8">
                  <BarChart3 className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0">
                  <p className="text-[12px] font-semibold text-foreground">Reports & Analytics</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">Export register, SLA, balances and trends.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
