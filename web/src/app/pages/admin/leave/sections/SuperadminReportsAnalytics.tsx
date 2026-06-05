import { useMemo, useState } from "react";
import { useAdminLeaveRequestsStore } from "../../../../modules/adminLeave/store";

export function SuperadminReportsAnalytics() {
  const { activeRows } = useAdminLeaveRequestsStore();
  const [range, setRange] = useState<"30" | "90" | "365">("90");

  const summary = useMemo(() => {
    const byType = activeRows.reduce<Record<string, number>>((acc, row) => {
      acc[row.leave_type.name] = (acc[row.leave_type.name] ?? 0) + 1;
      return acc;
    }, {});
    const byStatus = activeRows.reduce<Record<string, number>>((acc, row) => {
      acc[row.status] = (acc[row.status] ?? 0) + 1;
      return acc;
    }, {});
    return { byType, byStatus };
  }, [activeRows]);

  return (
    <div className="space-y-5">
      <div className="flat-card bg-card p-5 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-foreground">Reports & Analytics</h2>
          {/* <p className="text-xs text-muted-foreground mt-1">Leave trends, utilization and approval performance.</p> */}
        </div>
        <select value={range} onChange={(e) => setRange(e.target.value as "30" | "90" | "365")} className="flat-input px-3 py-2 text-sm">
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last 365 days</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="flat-card bg-card p-5">
          <h3 className="text-sm font-semibold text-foreground">Leave Type Utilization</h3>
          <div className="mt-3 space-y-2">
            {Object.entries(summary.byType).map(([type, count]) => (
              <div key={type} className="p-3 rounded-lg border border-border bg-secondary/40 flex items-center justify-between">
                <p className="text-sm text-foreground">{type}</p>
                <span className="text-[11px] font-semibold text-muted-foreground bg-card border border-border px-2 py-0.5 rounded-md">{count}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="flat-card bg-card p-5">
          <h3 className="text-sm font-semibold text-foreground">Approval Performance</h3>
          <div className="mt-3 space-y-2">
            {Object.entries(summary.byStatus).map(([status, count]) => (
              <div key={status} className="p-3 rounded-lg border border-border bg-secondary/40 flex items-center justify-between">
                <p className="text-sm text-foreground">{status}</p>
                <span className="text-[11px] font-semibold text-muted-foreground bg-card border border-border px-2 py-0.5 rounded-md">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

