import { useMemo } from "react";
import { FileText } from "lucide-react";
import type { LeaveApplicationAPI, LeaveBalanceAPI } from "../../../modules/leaves/types";
import { LeaveEmptyState } from "./LeaveEmptyState";
import { LeaveTypePill } from "./LeaveTypePill";
import { EmployeeLeaveStatusBadge } from "./EmployeeLeaveStatusBadge";
import { formatLeaveDate } from "./leaveDateUtils";
import { cn } from "../../ui/utils";

export function MyApplicationsView({
  applications,
  balances,
}: {
  applications: LeaveApplicationAPI[];
  balances:     LeaveBalanceAPI[];
}) {
  // Pending = still in workflow
  const pending = useMemo(
    () => applications.filter((a) =>
      ["SUBMITTED", "DRAFT", "PENDING", "ESCALATED"].includes(a.leave_status),
    ),
    [applications],
  );

  // History = everything that has reached a terminal state
  const history = useMemo(
    () =>
      applications
        .filter((a) => !["SUBMITTED", "DRAFT", "PENDING", "ESCALATED"].includes(a.leave_status))
        .sort((a, b) => {
          // Sort by applied_at descending (most recent first)
          const dateA = a.applied_at ?? a.applied_on ?? "";
          const dateB = b.applied_at ?? b.applied_on ?? "";
          return dateB.localeCompare(dateA);
        }),
    [applications],
  );

  if (applications.length === 0) {
    return (
      <LeaveEmptyState
        icon={FileText}
        title="No applications yet"
        description="Once you submit a leave request it will appear here for tracking."
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* ── Pending approvals ─────────────────────────────────────────── */}
      {pending.length > 0 && (
        <section className="flat-card overflow-hidden bg-card">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <h2 className="text-sm font-semibold text-foreground">Pending Approval</h2>
            <span className="rounded-md border border-border bg-secondary px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
              {pending.length}
            </span>
          </div>
          <div className="divide-y divide-border">
            {pending.map((app) => (
              <ApplicationRow key={app.id} app={app} />
            ))}
          </div>
        </section>
      )}

      {/* ── History ───────────────────────────────────────────────────── */}
      <section className="flat-card overflow-hidden bg-card">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-sm font-semibold text-foreground">Application History</h2>
          <span className="rounded-md border border-border bg-secondary px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
            {history.length}
          </span>
        </div>

        {history.length === 0 ? (
          <div className="px-4 py-10 text-center text-sm text-muted-foreground">
            No resolved applications yet.
          </div>
        ) : (
          <div className="divide-y divide-border">
            {history.map((app) => (
              <ApplicationRow key={app.id} app={app} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

// ── Internal row component ────────────────────────────────────────────────────

function ApplicationRow({ app }: { app: LeaveApplicationAPI }) {
  const typeName  = app.leave_type_detail?.name ?? app.leave_type_name ?? "Leave";
  const typeCode  = app.leave_type_detail?.code ?? "—";
  const appliedOn = app.applied_on ?? app.applied_at.slice(0, 10);

  return (
    <div
      className={cn(
        "flex flex-wrap items-center justify-between gap-3 px-4 py-3 transition-colors hover:bg-secondary/40",
      )}
    >
      <div className="flex min-w-0 items-center gap-3">
        <LeaveTypePill code={typeCode} />
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-foreground">{typeName}</p>
          <p className="text-xs text-muted-foreground">
            {formatLeaveDate(app.from_date)} — {formatLeaveDate(app.to_date)}
            {" · "}
            <span className="tabular-nums">{app.total_days}</span>
            {app.total_days === 1 ? " day" : " days"}
          </p>
        </div>
      </div>

      <div className="flex flex-shrink-0 flex-col items-end gap-1">
        {/* leave_status is the canonical field from LeaveApplicationSummarySerializer */}
        <EmployeeLeaveStatusBadge status={app.leave_status} />
        <p className="text-[10px] text-muted-foreground">Applied {appliedOn}</p>
      </div>
    </div>
  );
}