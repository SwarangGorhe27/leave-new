import { useState } from "react";
import { attendanceDataset, requestBadgeClass } from "../../modules/attendance/store";
import { RequestType } from "../../modules/attendance/types";
import { format, parseISO } from "date-fns";
import { Clock, CheckCircle, XCircle } from "lucide-react";

const tabs: RequestType[] = ["Regularization", "Leave", "Overtime", "Comp-Off"];

export function RequestsManager() {
  const [tab, setTab] = useState<RequestType>("Regularization");
  const [view, setView] = useState<"pending" | "history">("pending");
  const rows = attendanceDataset.requests.filter((r) => r.type === tab);

  const pendingRequests = rows.filter(r => r.status === "Pending" || r.status === "Under Review");
  const historyRequests = rows.filter(r => r.status === "Approved" || r.status === "Rejected" || r.status === "Cancelled");

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "Approved":
        return <CheckCircle className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />;
      case "Rejected":
        return <XCircle className="w-3 h-3 text-rose-600 dark:text-rose-400" />;
      case "Pending":
      case "Under Review":
        return <Clock className="w-3 h-3 text-amber-600 dark:text-amber-400" />;
      default:
        return null;
    }
  };

  const displayRequests = view === "pending" ? pendingRequests : historyRequests;

  return (
    <div className="flat-card bg-card p-3">
      <div className="flex gap-1.5 mb-2 flex-wrap">
        {tabs.map((entry) => (
          <button key={entry} onClick={() => setTab(entry)} className={`h-7 px-2 rounded text-[11px] font-medium border ${tab === entry ? "bg-secondary border-border" : "border-border text-muted-foreground"}`}>{entry}</button>
        ))}
      </div>

      {tab === "Regularization" && (
        <div className="flex gap-1.5 mb-2">
          <button
            onClick={() => setView("pending")}
            className={`h-6 px-2 rounded text-[10px] font-semibold border transition-all ${
              view === "pending"
                ? "bg-amber-100 text-amber-700 border-amber-300 dark:bg-amber-500/15 dark:text-amber-300 dark:border-amber-500/30"
                : "border-border text-muted-foreground dark:border-slate-600 dark:text-slate-400"
            }`}
          >
            Pending ({pendingRequests.length})
          </button>
          <button
            onClick={() => setView("history")}
            className={`h-6 px-2 rounded text-[10px] font-semibold border transition-all ${
              view === "history"
                ? "bg-secondary border-border"
                : "border-border text-muted-foreground dark:border-slate-600 dark:text-slate-400"
            }`}
          >
            History ({historyRequests.length})
          </button>
        </div>
      )}

      <div className="space-y-1.5 max-h-96 overflow-y-auto">
        {displayRequests.length > 0 ? (
          displayRequests.map((row) => (
            <div key={row.id} className="rounded-lg border border-border dark:border-slate-700 p-2 bg-secondary/30 dark:bg-slate-700/30 hover:bg-secondary/50 dark:hover:bg-slate-700/50 transition-colors">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="mt-0.5">{getStatusIcon(row.status)}</div>
                    <p className="text-xs font-medium text-foreground dark:text-white truncate">{row.employeeName || "Employee"}</p>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-background dark:bg-slate-600 text-muted-foreground dark:text-slate-300 whitespace-nowrap">{row.date}</span>
                  </div>
                  <p className="text-[10px] text-muted-foreground dark:text-slate-400 line-clamp-1">{row.reason}</p>
                  {view === "history" && row.lastUpdated && (
                    <p className="text-[9px] text-muted-foreground dark:text-slate-400 mt-1">
                      Updated: {format(parseISO(row.lastUpdated.split(" ")[0]), "MMM d, h:mm a")}
                    </p>
                  )}
                </div>
                <span className={`text-[10px] px-1.5 py-0.5 border rounded font-semibold whitespace-nowrap ${requestBadgeClass[row.status as keyof typeof requestBadgeClass] || "bg-slate-100 text-slate-700 border-slate-300 dark:bg-slate-500/15 dark:text-slate-300 dark:border-slate-500/30"}`}>{row.status}</span>
              </div>
              {view === "pending" && (row.status === "Pending" || row.status === "Under Review") && (
                <div className="flex gap-1.5 mt-2">
                  <button className="text-[10px] font-medium px-2 py-1 border border-border rounded hover:bg-secondary dark:hover:bg-slate-600 transition-colors">Approve</button>
                  <button className="text-[10px] font-medium px-2 py-1 border border-border rounded hover:bg-secondary dark:hover:bg-slate-600 transition-colors">Reject</button>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-6">
            <p className="text-[10px] text-muted-foreground dark:text-slate-400">
              {view === "pending" ? "No pending requests" : "No history found"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

