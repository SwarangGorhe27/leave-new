import { useMemo, useState } from "react";
import { CheckCircle2, Search, SlidersHorizontal, XCircle } from "lucide-react";
import type { LeaveApplicationAPI, LeaveApplicationStatus } from "../../../modules/leaves/types";
import { useApproveLeave, useRejectLeave } from "../../../modules/leaves/useLeaves";
import { Button } from "../../ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../ui/dialog";
import { Textarea } from "../../ui/textarea";
import { cn } from "../../ui/utils";
import { EmployeeLeaveStatusBadge } from "../employee/EmployeeLeaveStatusBadge";
import { LeaveEmptyState } from "../employee/LeaveEmptyState";
import { LeaveTypePill } from "../employee/LeaveTypePill";
import { formatLeaveDate, formatLeaveShortDate } from "../employee/leaveDateUtils";

export function TeamLeaveApplicationsTable({
  applications,
  leaveTypeOptions,
  onActionComplete,
}: {
  applications: LeaveApplicationAPI[];
  leaveTypeOptions: { id: string; name: string; code: string }[];
  onActionComplete?: () => void;
}) {
  const approveLeave = useApproveLeave();
  const rejectLeave = useRejectLeave();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<"" | LeaveApplicationStatus>("");
  const [leaveTypeId, setLeaveTypeId] = useState("");
  const [detail, setDetail] = useState<LeaveApplicationAPI | null>(null);
  const [rejectTarget, setRejectTarget] = useState<LeaveApplicationAPI | null>(null);
  const [rejectRemarks, setRejectRemarks] = useState("");
  const [busyId, setBusyId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return applications.filter((a) => {
      if (q) {
        const blob = `${a.employee_name} ${a.leave_type_detail?.name ?? ""} ${a.reason} ${a.status}`.toLowerCase();
        if (!blob.includes(q)) return false;
      }
      if (leaveTypeId && a.leave_type !== leaveTypeId) return false;
      if (status && a.status !== status) return false;
      return true;
    });
  }, [applications, search, leaveTypeId, status]);

  const filterSelect =
    "flat-input h-10 min-w-[8rem] flex-1 rounded-lg px-3 text-xs font-medium sm:min-w-0 sm:flex-none sm:max-w-[12rem]";

  const handleApprove = async (app: LeaveApplicationAPI) => {
    setBusyId(app.id);
    try {
      await approveLeave.mutate(app.id);
      onActionComplete?.();
    } finally {
      setBusyId(null);
    }
  };

  const handleReject = async () => {
    if (!rejectTarget) return;
    setBusyId(rejectTarget.id);
    try {
      await rejectLeave.mutate({ id: rejectTarget.id, remarks: rejectRemarks });
      setRejectTarget(null);
      setRejectRemarks("");
      onActionComplete?.();
    } finally {
      setBusyId(null);
    }
  };

  if (applications.length === 0) {
    return (
      <LeaveEmptyState
        icon={CheckCircle2}
        title="No team requests pending"
        description="When your team submits leave for approval, requests will appear here."
      />
    );
  }

  return (
    <div className="space-y-5">
      <div className="flat-card bg-card p-5 sm:p-6">
        <div className="relative min-w-0 max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search employee, type, reason…"
            className="flat-input dark:bg-slate-900 dark:text-white dark:border-slate-700 dark:placeholder:text-slate-400 h-10 w-full rounded-xl pl-12 pr-4 text-sm"
          />
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3 border-t border-border pt-5">
          <span className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            <SlidersHorizontal className="h-3.5 w-3.5" />
            Filters
          </span>
          <select className={filterSelect} value={leaveTypeId} onChange={(e) => setLeaveTypeId(e.target.value)}>
            <option value="">Leave type</option>
            {leaveTypeOptions.map((lt) => (
              <option key={lt.id} value={lt.id}>
                {lt.name} ({lt.code})
              </option>
            ))}
          </select>
          <select
            className={filterSelect}
            value={status}
            onChange={(e) => setStatus(e.target.value as "" | LeaveApplicationStatus)}
          >
            <option value="">Status</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="PENDING">Pending</option>
            <option value="DRAFT">Draft</option>
          </select>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-10 rounded-lg px-3 text-sm font-semibold text-muted-foreground hover:text-foreground"
            onClick={() => {
              setSearch("");
              setLeaveTypeId("");
              setStatus("");
            }}
          >
            Reset
          </Button>
        </div>
      </div>

      <div className="flat-card overflow-hidden bg-card">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[800px] text-left">
            <thead className="sticky top-0 z-10 bg-secondary/95 backdrop-blur-sm">
              <tr className="border-b border-border">
                {["Employee", "Leave", "From", "To", "Days", "Applied", "Status", "Actions"].map((h) => (
                  <th
                    key={h}
                    className="whitespace-nowrap px-4 py-3.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground sm:px-5"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((app) => (
                <tr key={app.id} className="transition-colors duration-150 hover:bg-secondary/60">
                  <td className="px-4 py-3 text-sm font-medium text-foreground sm:px-5">{app.employee_name}</td>
                  <td className="px-4 py-3 sm:px-5">
                    <div className="flex items-center gap-2">
                      <LeaveTypePill code={app.leave_type_detail?.code ?? "—"} />
                      <span className="text-sm text-foreground">{app.leave_type_detail?.name}</span>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-muted-foreground sm:px-5">
                    {formatLeaveShortDate(app.from_date)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-muted-foreground sm:px-5">
                    {formatLeaveShortDate(app.to_date)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm font-semibold tabular-nums sm:px-5">{app.total_days}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-muted-foreground sm:px-5">
                    {formatLeaveDate(app.applied_on)}
                  </td>
                  <td className="px-4 py-3 sm:px-5">
                    <EmployeeLeaveStatusBadge status={app.status} />
                  </td>
                  <td className="px-4 py-3 sm:px-5">
                    <div className="flex flex-wrap items-center gap-2">
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        className="h-8 gap-1 rounded-lg text-xs font-semibold"
                        disabled={busyId === app.id}
                        onClick={() => setDetail(app)}
                      >
                        View
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        className="h-8 gap-1 rounded-lg text-xs font-semibold"
                        disabled={busyId === app.id}
                        onClick={() => handleApprove(app)}
                      >
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Approve
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        className="h-8 gap-1 rounded-lg border-red-200 text-xs font-semibold text-red-600 hover:bg-red-50 dark:border-red-900 dark:text-red-400 dark:hover:bg-red-950"
                        disabled={busyId === app.id}
                        onClick={() => {
                          setRejectTarget(app);
                          setRejectRemarks("");
                        }}
                      >
                        <XCircle className="h-3.5 w-3.5" />
                        Reject
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <div className="border-t border-border px-4 py-10 text-center text-sm text-muted-foreground">
            No rows match your filters.
          </div>
        )}
      </div>

      <Dialog open={!!detail} onOpenChange={(o) => !o && setDetail(null)}>
        <DialogContent className="max-w-md rounded-xl border-border">
          <DialogHeader>
            <DialogTitle className="text-base">Team leave request</DialogTitle>
          </DialogHeader>
          {detail && (
            <div className="space-y-2 text-sm">
              <p className="font-medium text-foreground">{detail.employee_name}</p>
              <div className="flex flex-wrap items-center gap-2">
                <LeaveTypePill code={detail.leave_type_detail?.code ?? "—"} />
                <EmployeeLeaveStatusBadge status={detail.status} />
              </div>
              <p className="text-muted-foreground">
                {formatLeaveDate(detail.from_date)} — {formatLeaveDate(detail.to_date)} · {detail.total_days} day
                {detail.total_days !== 1 ? "s" : ""}
              </p>
              <div className="rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs">
                <p className="font-semibold text-foreground">Reason</p>
                <p className="mt-1 text-muted-foreground">{detail.reason}</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={!!rejectTarget} onOpenChange={(o) => !o && setRejectTarget(null)}>
        <DialogContent className="max-w-md rounded-xl border-border">
          <DialogHeader>
            <DialogTitle className="text-base">Reject leave request</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Rejecting request for {rejectTarget?.employee_name}. Optional remarks are stored with the record.
            </p>
            <Textarea
              value={rejectRemarks}
              onChange={(e) => setRejectRemarks(e.target.value)}
              placeholder="Reason for rejection (optional)"
              className="min-h-[100px]"
            />
            <div className="flex justify-end gap-2">
              <Button type="button" variant="ghost" size="sm" onClick={() => setRejectTarget(null)}>
                Cancel
              </Button>
              <Button
                type="button"
                size="sm"
                variant="destructive"
                disabled={busyId === rejectTarget?.id}
                onClick={handleReject}
              >
                Reject
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
