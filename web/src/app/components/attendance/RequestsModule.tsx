import { useState } from "react";
import { attendanceDataset, requestBadgeClass } from "../../modules/attendance/store";
import { RequestType } from "../../modules/attendance/types";

const TABS: RequestType[] = ["Regularization", "Leave", "Overtime", "Comp-Off"];

export function RequestsModule({ employeeId, adminMode }: { employeeId?: string; adminMode?: boolean }) {
  const [tab, setTab] = useState<RequestType>("Regularization");
  const rows = attendanceDataset.requests.filter((request) => request.type === tab && (!employeeId || request.employeeId === employeeId));

  return (
    <div className="flat-card bg-card p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex gap-2 flex-wrap">
          {TABS.map((entry) => (
            <button key={entry} onClick={() => setTab(entry)} className={`h-8 px-3 rounded-lg text-xs border ${tab === entry ? "bg-secondary border-border text-foreground" : "border-border text-muted-foreground"}`}>
              {entry}
            </button>
          ))}
        </div>
        <button className="h-8 px-3 rounded-lg text-xs bg-foreground text-primary-foreground">Apply Request</button>
      </div>
      <div className="space-y-2">
        {rows.map((row) => (
          <div key={row.id} className="border border-border rounded-lg p-3 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-foreground">{row.date}</p>
              <p className="text-xs text-muted-foreground">{row.reason}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded border ${requestBadgeClass[row.status]}`}>{row.status}</span>
              {adminMode && (
                <>
                  <button className="text-xs px-2 py-1 border border-border rounded">Approve</button>
                  <button className="text-xs px-2 py-1 border border-border rounded">Reject</button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
