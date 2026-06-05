import { attendanceDataset } from "../../modules/attendance/store";

export function ExceptionsPanel({ employeeId }: { employeeId?: string }) {
  const rows = attendanceDataset.exceptions.filter((entry) => !employeeId || entry.employeeId === employeeId);
  const severityClass: Record<string, string> = {
    Info: "bg-sky-100 text-sky-700 border-sky-300",
    Warning: "bg-amber-100 text-amber-700 border-amber-300",
    Critical: "bg-rose-100 text-rose-700 border-rose-300",
  };
  return (
    <div className="flat-card bg-card p-3">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-semibold text-foreground">Exceptions Panel</p>
        <button className="text-[10px] px-2 py-1 border border-border rounded-lg font-medium">Export CSV</button>
      </div>
      <div className="space-y-1.5">
        {rows.map((row) => (
          <div key={row.id} className="rounded-lg border border-border p-2 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-foreground">{row.type}</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">{row.date} · Assigned: {row.assignedTo || "Unassigned"}</p>
            </div>
            <div className="flex items-center gap-1.5">
              <span className={`text-[10px] px-1.5 py-0.5 rounded border ${severityClass[row.severity]}`}>{row.severity}</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded border ${row.status === "Resolved" ? "bg-secondary/20 text-muted-foreground border-border" : "bg-amber-100 text-amber-700 border-amber-300"}`}>{row.status}</span>
              <button className="text-[10px] px-2 py-0.5 border border-border rounded font-medium">Resolve</button>
              <button className="text-[10px] px-2 py-0.5 border border-border rounded font-medium">Assign</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
