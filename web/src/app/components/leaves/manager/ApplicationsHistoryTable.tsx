import { useMemo, useState } from "react";
import {
  Download,
  FileText,
  MoreHorizontal,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import type { LeaveApplicationAPI, LeaveApplicationStatus } from "../../../modules/leaves/types";
import { Button } from "../../ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../../ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../ui/dialog";
import { cn } from "../../ui/utils";
import { EmployeeLeaveStatusBadge, employeeLeaveStatusLabel } from "./EmployeeLeaveStatusBadge";
import { LeaveEmptyState } from "./LeaveEmptyState";
import { LeaveTypePill } from "./LeaveTypePill";
import { formatLeaveDate, formatLeaveShortDate } from "./leaveDateUtils";

const MONTHS = [
  { v: "", l: "Month" },
  ...Array.from({ length: 12 }, (_, i) => ({
    v: String(i + 1),
    l: new Date(2000, i, 1).toLocaleDateString("en-IN", { month: "short" }),
  })),
];

function escapeCsv(s: string) {
  if (s.includes(",") || s.includes('"') || s.includes("\n")) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

function exportCsv(rows: LeaveApplicationAPI[]) {
  const headers = ["Type", "Code", "From", "To", "Days", "Status", "Applied", "Reason"];
  const lines = [
    headers.join(","),
    ...rows.map((r) =>
      [
        escapeCsv(r.leave_type_detail?.name ?? ""),
        escapeCsv(r.leave_type_detail?.code ?? ""),
        r.from_date,
        r.to_date,
        String(r.total_days),
        escapeCsv(employeeLeaveStatusLabel(r.status)),
        r.applied_on,
        escapeCsv(r.reason ?? ""),
      ].join(","),
    ),
  ];
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `leave-applications-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export function ApplicationsHistoryTable({
  applications,
  leaveTypeOptions,
}: {
  applications: LeaveApplicationAPI[];
  leaveTypeOptions: { id: string; name: string; code: string }[];
}) {
  const [search, setSearch] = useState("");
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [leaveTypeId, setLeaveTypeId] = useState("");
  const [status, setStatus] = useState<"" | LeaveApplicationStatus>("");
  const [pendingBucket, setPendingBucket] = useState<"" | "in" | "out">("");
  const [category, setCategory] = useState<"" | "paid" | "unpaid">("");
  const [rangeStart, setRangeStart] = useState("");
  const [rangeEnd, setRangeEnd] = useState("");
  const [detail, setDetail] = useState<LeaveApplicationAPI | null>(null);

  const years = useMemo(() => {
    const y = new Set<number>();
    y.add(new Date().getFullYear());
    for (const a of applications) {
      y.add(new Date(a.from_date).getFullYear());
      y.add(new Date(a.applied_on).getFullYear());
    }
    return Array.from(y).sort((a, b) => b - a);
  }, [applications]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return applications.filter((a) => {
      if (q) {
        const blob = `${a.leave_type_detail?.name ?? ""} ${a.leave_type_detail?.code ?? ""} ${a.reason} ${a.status}`.toLowerCase();
        if (!blob.includes(q)) return false;
      }
      if (leaveTypeId && a.leave_type !== leaveTypeId) return false;
      if (status && a.status !== status) return false;
      if (category === "paid" && !a.leave_type_detail?.is_paid) return false;
      if (category === "unpaid" && a.leave_type_detail?.is_paid) return false;

      if (pendingBucket === "in") {
        if (a.status !== "SUBMITTED" && a.status !== "DRAFT" && a.status !== "PENDING") return false;
      }
      if (pendingBucket === "out") {
        if (a.status === "SUBMITTED" || a.status === "DRAFT" || a.status === "PENDING") return false;
      }

      const from = new Date(a.from_date);
      if (month && String(from.getMonth() + 1) !== month) return false;
      if (year && String(from.getFullYear()) !== year) return false;

      if (rangeStart && a.to_date < rangeStart) return false;
      if (rangeEnd && a.from_date > rangeEnd) return false;

      return true;
    });
  }, [applications, search, month, year, leaveTypeId, status, pendingBucket, category, rangeStart, rangeEnd]);

  const reset = () => {
    setSearch("");
    setMonth("");
    setYear("");
    setLeaveTypeId("");
    setStatus("");
    setPendingBucket("");
    setCategory("");
    setRangeStart("");
    setRangeEnd("");
  };

  const filterSelect =
    "flat-input h-9 min-w-[7.5rem] flex-1 rounded-lg px-2.5 text-xs font-medium sm:min-w-0 sm:flex-none sm:max-w-[11rem]";

  if (applications.length === 0) {
    return (
      <LeaveEmptyState
        icon={FileText}
        title="No applications yet"
        description="Submit a leave request to build your history. Filters and export will appear once you have records."
      />
    );
  }

  return (
    <div className="space-y-3">
      <div className="flat-card bg-card p-3 sm:p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative min-w-0 flex-1 max-w-md">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search type, code, reason, status…"
              className="flat-input dark:bg-slate-900 dark:text-white dark:border-slate-700 dark:placeholder:text-slate-400 h-10 w-full rounded-xl pl-12 pr-3 text-sm"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-9 gap-1.5 rounded-lg border-border text-xs font-semibold"
              onClick={() => exportCsv(filtered)}
            >
              <Download className="h-3.5 w-3.5" />
              Export
            </Button>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-border pt-3">
          <span className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            <SlidersHorizontal className="h-3.5 w-3.5" />
            Filters
          </span>
          <select className={filterSelect} value={month} onChange={(e) => setMonth(e.target.value)}>
            {MONTHS.map((m) => (
              <option key={m.v || "all"} value={m.v}>
                {m.l}
              </option>
            ))}
          </select>
          <select className={filterSelect} value={year} onChange={(e) => setYear(e.target.value)}>
            <option value="">Year</option>
            {years.map((y) => (
              <option key={y} value={String(y)}>
                {y}
              </option>
            ))}
          </select>
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
            <option value="DRAFT">Draft</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="CANCELLED">Cancelled</option>
            <option value="REVOKED">Revoked</option>
          </select>
          <select
            className={filterSelect}
            value={pendingBucket}
            onChange={(e) => setPendingBucket(e.target.value as "" | "in" | "out")}
          >
            <option value="">Pending filter</option>
            <option value="in">In workflow</option>
            <option value="out">Resolved</option>
          </select>
          <select className={filterSelect} value={category} onChange={(e) => setCategory(e.target.value as typeof category)}>
            <option value="">Category</option>
            <option value="paid">Paid</option>
            <option value="unpaid">Unpaid</option>
          </select>
          <input
            type="date"
            value={rangeStart}
            onChange={(e) => setRangeStart(e.target.value)}
            className={cn(filterSelect, "min-w-[9rem]")}
            aria-label="Range start"
          />
          <input
            type="date"
            value={rangeEnd}
            onChange={(e) => setRangeEnd(e.target.value)}
            className={cn(filterSelect, "min-w-[9rem]")}
            aria-label="Range end"
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-9 rounded-lg text-xs font-semibold text-muted-foreground hover:text-foreground"
            onClick={reset}
          >
            Reset
          </Button>
        </div>
      </div>

      <div className="flat-card overflow-hidden bg-card">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left">
            <thead className="sticky top-0 z-10 bg-secondary/95 backdrop-blur-sm">
              <tr className="border-b border-border">
                {["Leave", "From", "To", "Days", "Reason", "Applied", "Status", ""].map((h) => (
                  <th
                    key={h || "actions"}
                    className="whitespace-nowrap px-3 py-2.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground sm:px-4"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((app) => (
                <tr
                  key={app.id}
                  className="transition-colors duration-150 hover:bg-secondary/60"
                >
                  <td className="px-3 py-2.5 sm:px-4">
                    <div className="flex items-center gap-2">
                      <LeaveTypePill code={app.leave_type_detail?.code ?? "—"} />
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-foreground">{app.leave_type_detail?.name}</p>
                        <p className="text-[11px] text-muted-foreground">
                          {app.leave_type_detail?.is_paid ? "Paid" : "Unpaid"}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-3 py-2.5 text-xs text-muted-foreground sm:px-4">
                    {formatLeaveShortDate(app.from_date)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2.5 text-xs text-muted-foreground sm:px-4">
                    {formatLeaveShortDate(app.to_date)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2.5 text-sm font-semibold tabular-nums text-foreground sm:px-4">
                    {app.total_days}
                  </td>
                  <td className="max-w-[200px] px-3 py-2.5 sm:max-w-[240px] sm:px-4">
                    <p className="truncate text-xs text-muted-foreground" title={app.reason}>
                      {app.reason}
                    </p>
                  </td>
                  <td className="whitespace-nowrap px-3 py-2.5 text-xs text-muted-foreground sm:px-4">
                    {formatLeaveDate(app.applied_on)}
                  </td>
                  <td className="px-3 py-2.5 sm:px-4">
                    <EmployeeLeaveStatusBadge status={app.status} />
                  </td>
                  <td className="px-2 py-2.5 text-right sm:px-3">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground"
                          aria-label="Row actions"
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-44 rounded-lg border-border">
                        <DropdownMenuItem className="text-sm" onClick={() => setDetail(app)}>
                          View details
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-sm"
                          onClick={() => navigator.clipboard?.writeText(app.id)}
                        >
                          Copy request ID
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
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
            <DialogTitle className="text-base">Application details</DialogTitle>
          </DialogHeader>
          {detail && (
            <div className="space-y-2 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <LeaveTypePill code={detail.leave_type_detail?.code ?? "—"} />
                <EmployeeLeaveStatusBadge status={detail.status} />
              </div>
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{detail.leave_type_detail?.name}</span> ·{" "}
                {detail.total_days} day{detail.total_days !== 1 ? "s" : ""}
              </p>
              <p className="text-xs text-muted-foreground">
                {formatLeaveDate(detail.from_date)} — {formatLeaveDate(detail.to_date)}
              </p>
              <div className="rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs">
                <p className="font-semibold text-foreground">Reason</p>
                <p className="mt-1 text-muted-foreground">{detail.reason}</p>
              </div>
              <p className="text-xs text-muted-foreground">Applied on {formatLeaveDate(detail.applied_on)}</p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
