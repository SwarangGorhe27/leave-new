import { useMemo } from "react";
import { useAdminLeaveRequestsStore } from "../../../../modules/adminLeave/store";

export function SuperadminAuditLogs() {
  const { rows } = useAdminLeaveRequestsStore();
  const events = useMemo(
    () =>
      rows
        .flatMap((r) => (r.audit ?? []).map((a) => ({ ...a, requestId: r.id, employee: r.employee?.employee_name ?? "Unknown" })))
        .sort((a, b) => b.at.localeCompare(a.at)),
    [rows],
  );

  return (
    <div className="flat-card bg-card overflow-hidden">
      <div className="px-6 py-4 border-b border-border">
        <h2 className="text-sm font-semibold text-foreground">Audit Logs</h2>
        <p className="text-xs text-muted-foreground mt-1">System-wide immutable timeline for leave operations.</p>
      </div>
      <div className="divide-y divide-border max-h-[620px] overflow-y-auto">
        {events.map((e) => (
          <div key={e.id} className="px-6 py-4">
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-semibold text-foreground">{e.action}</p>
              <span className="text-[11px] font-semibold text-muted-foreground bg-secondary border border-border px-2 py-0.5 rounded-md">{new Date(e.at).toLocaleString()}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">Actor: {e.actor} ({e.actor_role ?? "unknown"}) · Request: {e.requestId} · Employee: {e.employee}</p>
            {(e.meta || e.previous_value || e.new_value) && (
              <p className="text-xs text-foreground mt-2">{e.meta ?? ""} {e.previous_value ? `From ${e.previous_value}` : ""} {e.new_value ? `to ${e.new_value}` : ""}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

