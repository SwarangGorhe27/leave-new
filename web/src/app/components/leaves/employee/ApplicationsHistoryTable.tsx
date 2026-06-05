import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import {
  Download,
  FileText,
  MoreHorizontal,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import type { ApplyLeavePayload } from "../../../../hooks/useLeave";
import type {
  LeaveApplicationAPI,
  LeaveApplicationStatus,
} from "../../../modules/leaves/types";
import {
  useCancelLeave,
  useLeaveApplicationDetail,
  useResubmitLeave,
  useUpdateLeave,
} from "../../../modules/leaves/useLeaves";
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
import { Input } from "../../ui/input";
import { Textarea } from "../../ui/textarea";
import { cn } from "../../ui/utils";
import {
  EmployeeLeaveStatusBadge,
  employeeLeaveStatusLabel,
} from "./EmployeeLeaveStatusBadge";
import { LeaveEmptyState } from "./LeaveEmptyState";
import { LeaveTypePill } from "./LeaveTypePill";
import {
  formatLeaveDate,
  formatLeaveShortDate,
} from "./leaveDateUtils";

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const MONTHS = [
  { v: "", l: "Month" },
  ...Array.from({ length: 12 }, (_, i) => ({
    v: String(i + 1),
    l: new Date(2000, i, 1).toLocaleDateString("en-IN", { month: "short" }),
  })),
];

const SESSION_OPTIONS = [
  { value: "1", label: "Session 1 (First Half)" },
  { value: "2", label: "Session 2 (Second Half)" },
] as const;

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

type Session = "1" | "2";

function apiSessionToFormSession(
  session?: "first_half" | "second_half"
): Session {
  return session === "second_half" ? "2" : "1";
}

function sessionLabel(
  session?: "first_half" | "second_half"
): string {
  if (session === "first_half") return "First Half";
  if (session === "second_half") return "Second Half";
  return "-";
}

function escapeCsv(s: string) {
  if (s.includes(",") || s.includes('"') || s.includes("\n")) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

function exportCsv(rows: LeaveApplicationAPI[]) {
  const headers = [
    "Type",
    "Code",
    "From",
    "To",
    "From Session",
    "To Session",
    "Days",
    "Status",
    "Applied",
    "Reason",
  ];
  const lines = [
    headers.join(","),
    ...rows.map((r) =>
      [
        escapeCsv(r.leave_type_detail?.name ?? ""),
        escapeCsv(r.leave_type_detail?.code ?? ""),
        r.from_date,
        r.to_date,
        escapeCsv(sessionLabel(r.from_session)),
        escapeCsv(sessionLabel(r.to_session)),
        String(r.total_days),
        escapeCsv(employeeLeaveStatusLabel(r.leave_status)),
        r.applied_on,
        escapeCsv(r.reason ?? ""),
      ].join(",")
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

/**
 * FIX: Parse ISO date strings (YYYY-MM-DD) without timezone shifts.
 * new Date("2026-06-05") is parsed as UTC midnight, which rolls back
 * one day in UTC+5:30 when calling .getMonth()/.getFullYear() locally.
 * Splitting manually avoids that entirely.
 */
function parseLocalDate(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

/**
 * FIX: Normalise any status value to lowercase for consistent comparison.
 * The backend LeaveStatusChoices uses lowercase ("pending", "approved", etc.)
 * but some display paths may pass uppercase. Always compare lowercase → lowercase.
 */
function normaliseStatus(s?: string): string {
  return (s ?? "").toLowerCase();
}

/* ------------------------------------------------------------------ */
/*  Edit-form state type                                               */
/* ------------------------------------------------------------------ */

interface EditFormState {
  leaveType: string;
  from_date: string;
  to_date: string;
  fromSession: Session;
  toSession: Session;
  reason: string;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

export function ApplicationsHistoryTable({
  applications,
  leaveTypeOptions,
}: {
  applications: LeaveApplicationAPI[];
  leaveTypeOptions: { id: string; name: string; code: string }[];
}) {
  /* ── filter state ───────────────────────────────────────────────── */
  const [search, setSearch] = useState("");
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [leaveTypeId, setLeaveTypeId] = useState("");
  const [status, setStatus] = useState<"" | LeaveApplicationStatus>("");
  const [pendingBucket, setPendingBucket] = useState<"" | "in" | "out">("");
  const [category, setCategory] = useState<"" | "paid" | "unpaid">("");
  const [rangeStart, setRangeStart] = useState("");
  const [rangeEnd, setRangeEnd] = useState("");

  /* ── dialog state ───────────────────────────────────────────────── */
  const [selectedDetailId, setSelectedDetailId] = useState<string | null>(null);
  const [selectedDetailRow, setSelectedDetailRow] = useState<LeaveApplicationAPI | null>(null);
  const [editForm, setEditForm] = useState<EditFormState>({
    leaveType: "",
    from_date: "",
    to_date: "",
    fromSession: "1",
    toSession: "2",
    reason: "",
  });
  const [isEditing, setIsEditing] = useState(false);
  const [removedDocumentIds, setRemovedDocumentIds] = useState<string[]>([]);
  const [newDocuments, setNewDocuments] = useState<File[]>([]);

  /* ── mutations ──────────────────────────────────────────────────── */
  const updateMutation = useUpdateLeave();
  const cancelMutation = useCancelLeave();
  const resubmitMutation = useResubmitLeave();

  /* ── handlers ───────────────────────────────────────────────────── */
  const openEditLeave = (app: LeaveApplicationAPI) => {
    setSelectedDetailRow(app);
    setSelectedDetailId(app.id);
    setIsEditing(true);
  };

  const handleSaveEdit = (e?: FormEvent) => {
    if (e) e.preventDefault();
    if (!selectedDetail) return;

    const formData = new FormData();
    formData.append("from_date", editForm.from_date);
    formData.append("to_date", editForm.to_date);
    formData.append(
      "from_session",
      editForm.fromSession === "2" ? "second_half" : "first_half"
    );
    formData.append(
      "to_session",
      editForm.toSession === "2" ? "second_half" : "first_half"
    );
    formData.append("reason", editForm.reason.trim());

    removedDocumentIds.forEach((id) => {
      formData.append("remove_document_ids", id);
    });

    newDocuments.forEach((file) => {
      formData.append("attachments", file);
    });

    updateMutation.mutate(
      {
        id: selectedDetail.id,
        payload: formData as unknown as Partial<ApplyLeavePayload>,
      },
      {
        onSuccess: () => {
          setSelectedDetailId(null);
          setSelectedDetailRow(null);
          setIsEditing(false);
          setRemovedDocumentIds([]);
          setNewDocuments([]);
        },
      }
    );
  };

  const handleCancelLeave = (app: LeaveApplicationAPI) => {
    cancelMutation.mutate(app.id);
  };

  const handleResubmitLeave = (app: LeaveApplicationAPI) => {
    resubmitMutation.mutate(app.id);
  };

  const detailQuery = useLeaveApplicationDetail(selectedDetailId);

  const selectedDetail = (detailQuery.data as LeaveApplicationAPI | null) ?? selectedDetailRow;

  useEffect(() => {
    if (!selectedDetail || !isEditing) return;

    setEditForm({
      leaveType: selectedDetail.leave_type_id,
      from_date: selectedDetail.from_date,
      to_date: selectedDetail.to_date,
      fromSession: apiSessionToFormSession(selectedDetail.from_session),
      toSession: apiSessionToFormSession(selectedDetail.to_session),
      reason: selectedDetail.reason ?? "",
    });
    setRemovedDocumentIds([]);
    setNewDocuments([]);
  }, [selectedDetail, isEditing]);

  const openDetail = (app: LeaveApplicationAPI) => {
    setSelectedDetailRow(app);
    setSelectedDetailId(app.id);
    setIsEditing(false);
  };

  /* ── derived ────────────────────────────────────────────────────── */
  const years = useMemo(() => {
    const y = new Set<number>();
    y.add(new Date().getFullYear());
    for (const a of applications) {
      // FIX: use parseLocalDate to avoid UTC→local timezone rollback
      y.add(parseLocalDate(a.from_date).getFullYear());
      y.add(parseLocalDate(a.to_date).getFullYear());
    }
    return Array.from(y).sort((a, b) => b - a);
  }, [applications]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();

    return applications.filter((a) => {
      // ── Search ─────────────────────────────────────────────────────
      if (q) {
        const blob = [
          a.leave_type_detail?.name ?? "",
          a.leave_type_detail?.code ?? "",
          a.reason ?? "",
          // FIX: was searching a.status (raw lowercase) but leave_status is
          // the display field shown in the UI — search both for safety.
          employeeLeaveStatusLabel(a.leave_status),
          a.leave_status ?? "",
          a.status ?? "",
        ]
          .join(" ")
          .toLowerCase();
        if (!blob.includes(q)) return false;
      }

      // ── Leave type ────────────────────────────────────────────────
      // FIX: was comparing a.leave_type (name string like "Casual Leave")
      // against leaveTypeId (a UUID). Must compare a.leave_type_id instead.
      if (leaveTypeId && a.leave_type_id !== leaveTypeId) return false;

      // ── Status ────────────────────────────────────────────────────
      // FIX: status dropdown options were uppercase ("APPROVED") but the
      // backend returns lowercase ("approved"). Normalise both sides.
      if (status && normaliseStatus(a.leave_status) !== normaliseStatus(status))
        return false;

      // ── Category (paid / unpaid) ───────────────────────────────────
      if (category === "paid" && !a.leave_type_detail?.is_paid) return false;
      if (category === "unpaid" && a.leave_type_detail?.is_paid) return false;

      // ── Pending bucket ─────────────────────────────────────────────
      // FIX: was hardcoding uppercase "SUBMITTED"/"DRAFT"/"PENDING" but the
      // model only has lowercase values. Normalise all comparisons.
      const normStatus = normaliseStatus(a.leave_status ?? a.status);
      const inWorkflow =
        normStatus === "pending" ||
        normStatus === "submitted" ||
        normStatus === "draft";

      if (pendingBucket === "in" && !inWorkflow) return false;
      if (pendingBucket === "out" && inWorkflow) return false;

      // ── Month / Year ───────────────────────────────────────────────
      // FIX: was using new Date(a.from_date) which shifts UTC midnight into
      // local time — in IST (UTC+5:30) "2026-06-05" becomes May 31 locally.
      // parseLocalDate() uses Date(y, m-1, d) to stay in local timezone.
      const from = parseLocalDate(a.from_date);
      if (month && String(from.getMonth() + 1) !== month) return false;
      if (year && String(from.getFullYear()) !== year) return false;

      // ── Date range ─────────────────────────────────────────────────
      // String comparison works correctly for ISO dates (YYYY-MM-DD).
      if (rangeStart && a.to_date < rangeStart) return false;
      if (rangeEnd && a.from_date > rangeEnd) return false;

      return true;
    });
  }, [
    applications,
    search,
    month,
    year,
    leaveTypeId,
    status,
    pendingBucket,
    category,
    rangeStart,
    rangeEnd,
  ]);

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
    "flat-input h-10 min-w-[8rem] flex-1 rounded-lg px-3 text-xs font-medium sm:min-w-0 sm:flex-none sm:max-w-[12rem]";

  /* ── empty state ────────────────────────────────────────────────── */
  if (applications.length === 0) {
    return (
      <LeaveEmptyState
        icon={FileText}
        title="No applications yet"
        description="Submit a leave request to build your history. Filters and export will appear once you have records."
      />
    );
  }

  /* ── render ─────────────────────────────────────────────────────── */
  return (
    <div className="space-y-5">
      {/* ── Filters bar ─────────────────────────────────────────────── */}
      <div className="flat-card bg-card p-5 sm:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative min-w-0 flex-1 max-w-md">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search type, code, reason, status…"
              className="flat-input dark:bg-slate-900 dark:text-white dark:border-slate-700 dark:placeholder:text-slate-400 h-10 w-full rounded-xl pl-12 pr-4 text-sm"
            />
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-10 gap-2 rounded-lg border-border px-4 text-sm font-semibold"
              onClick={() => exportCsv(filtered)}
            >
              <Download className="h-4 w-4" />
              Export
            </Button>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3 border-t border-border pt-5">
          <span className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            <SlidersHorizontal className="h-3.5 w-3.5" />
            Filters
          </span>
          <select
            className={filterSelect}
            value={month}
            onChange={(e) => setMonth(e.target.value)}
          >
            {MONTHS.map((m) => (
              <option key={m.v || "all"} value={m.v}>
                {m.l}
              </option>
            ))}
          </select>
          <select
            className={filterSelect}
            value={year}
            onChange={(e) => setYear(e.target.value)}
          >
            <option value="">Year</option>
            {years.map((y) => (
              <option key={y} value={String(y)}>
                {y}
              </option>
            ))}
          </select>
          <select
            className={filterSelect}
            value={leaveTypeId}
            onChange={(e) => setLeaveTypeId(e.target.value)}
          >
            <option value="">Leave type</option>
            {leaveTypeOptions.map((lt) => (
              <option key={lt.id} value={lt.id}>
                {lt.name} ({lt.code})
              </option>
            ))}
          </select>

          {/*
            FIX: Status option values changed from uppercase ("APPROVED") to
            lowercase ("approved") to match what the backend actually returns
            in LeaveStatusChoices. The normaliseStatus() helper also covers
            any edge case where the API returns uppercase.
          */}
          <select
            className={filterSelect}
            value={status}
            onChange={(e) =>
              setStatus(e.target.value as "" | LeaveApplicationStatus)
            }
          >
            <option value="">Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="cancelled">Cancelled</option>
          </select>

          <select
            className={filterSelect}
            value={pendingBucket}
            onChange={(e) =>
              setPendingBucket(e.target.value as "" | "in" | "out")
            }
          >
            <option value="">Pending filter</option>
            <option value="in">In workflow</option>
            <option value="out">Resolved</option>
          </select>
          <select
            className={filterSelect}
            value={category}
            onChange={(e) =>
              setCategory(e.target.value as typeof category)
            }
          >
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
            className="h-10 rounded-lg px-3 text-sm font-semibold text-muted-foreground hover:text-foreground"
            onClick={reset}
          >
            Reset
          </Button>
        </div>
      </div>

      {/* ── Table ───────────────────────────────────────────────────── */}
      <div className="flat-card overflow-hidden bg-card">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left">
            <thead className="sticky top-0 z-10 bg-secondary/95 backdrop-blur-sm">
              <tr className="border-b border-border">
                {[
                  "Leave",
                  "From",
                  "To",
                  "From Session",
                  "To Session",
                  "Days",
                  "Reason",
                  "Applied",
                  "Status",
                  "",
                ].map((h) => (
                  <th
                    key={h || "actions"}
                    className="whitespace-nowrap px-4 py-3.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground sm:px-5"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((app) => {
                const normRowStatus = normaliseStatus(app.leave_status ?? app.status);
                return (
                  <tr
                    key={app.id}
                    className="transition-colors duration-150 hover:bg-secondary/60"
                  >
                    {/* Leave type */}
                    <td className="px-4 py-3 sm:px-5">
                      <div className="flex items-center gap-2">
                        <LeaveTypePill
                          code={app.leave_type_code ?? "—"}
                        />
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-foreground">
                            {app.leave_type_detail?.name ?? app.leave_type}
                          </p>
                        </div>
                      </div>
                    </td>

                    {/* From date */}
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-muted-foreground sm:px-5">
                      {formatLeaveShortDate(app.from_date)}
                    </td>

                    {/* To date */}
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-muted-foreground sm:px-5">
                      {formatLeaveShortDate(app.to_date)}
                    </td>

                    {/* From Session */}
                    <td className="whitespace-nowrap px-4 py-3 sm:px-5">
                      <span className="inline-flex items-center rounded-md bg-secondary px-2 py-0.5 text-[11px] font-medium text-foreground">
                        {sessionLabel(app.from_session)}
                      </span>
                    </td>

                    {/* To Session */}
                    <td className="whitespace-nowrap px-4 py-3 sm:px-5">
                      <span className="inline-flex items-center rounded-md bg-secondary px-2 py-0.5 text-[11px] font-medium text-foreground">
                        {sessionLabel(app.to_session)}
                      </span>
                    </td>

                    {/* Days */}
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-semibold tabular-nums text-foreground sm:px-5">
                      {app.total_days}
                    </td>

                    {/* Reason */}
                    <td className="max-w-[200px] px-4 py-3 sm:max-w-[240px] sm:px-5">
                      <p
                        className="truncate text-sm text-muted-foreground"
                        title={app.reason}
                      >
                        {app.reason}
                      </p>
                    </td>

                    {/* Applied on */}
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-muted-foreground sm:px-5">
                      {formatLeaveDate(app.applied_at)}
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3 sm:px-5">
                      <EmployeeLeaveStatusBadge status={app.leave_status} />
                    </td>

                    {/* Actions */}
                    <td className="px-2 py-3 text-right sm:px-4">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button
                            type="button"
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                            aria-label="Row actions"
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </button>
                        </DropdownMenuTrigger>

                        <DropdownMenuContent
                          align="end"
                          sideOffset={6}
                          className="z-50 w-52 rounded-xl border border-border bg-popover p-1 shadow-lg"
                        >
                          {/* FIX: was comparing uppercase "PENDING"/"SUBMITTED"/"DRAFT"
                              against normalised lowercase status — now uses normRowStatus */}
                          {(normRowStatus === "pending" ||
                            normRowStatus === "submitted" ||
                            normRowStatus === "draft") && (
                            <>
                              <DropdownMenuItem
                                className="cursor-pointer rounded-md text-sm"
                                onClick={() => openEditLeave(app)}
                              >
                                Edit pending leave
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="cursor-pointer rounded-md text-sm text-red-500 focus:text-red-500"
                                onClick={() => handleCancelLeave(app)}
                                disabled={cancelMutation.isPending}
                              >
                                Cancel leave
                              </DropdownMenuItem>
                            </>
                          )}

                          {/* {(normRowStatus === "rejected" ||
                            normRowStatus === "cancelled") && (
                            <DropdownMenuItem
                              className="cursor-pointer rounded-md text-sm"
                              onClick={() => handleResubmitLeave(app)}
                              disabled={resubmitMutation.isPending}
                            >
                              Resubmit leave
                            </DropdownMenuItem>
                          )} */}

                          <DropdownMenuItem
                            className="cursor-pointer rounded-md text-sm"
                            onClick={() => openDetail(app)}
                          >
                            View details
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filtered.length === 0 && (
          <div className="border-t border-border px-4 py-10 text-center text-sm text-muted-foreground">
            No rows match your filters.
          </div>
        )}
      </div>

      {/* ── View details dialog ──────────────────────────────────────── */}
      <Dialog
        open={!!selectedDetailId}
        onOpenChange={(o) => {
          if (!o) {
            setSelectedDetailId(null);
            setSelectedDetailRow(null);
            setIsEditing(false);
            setRemovedDocumentIds([]);
            setNewDocuments([]);
          }
        }}
      >
        <DialogContent className="max-w-md rounded-xl border-border">
          <DialogHeader>
            <DialogTitle className="text-base">
              {isEditing ? "Edit application" : "Application details"}
            </DialogTitle>
          </DialogHeader>
          {detailQuery.isLoading && (
            <div className="space-y-2 text-sm">
              <p className="text-sm font-medium text-foreground">Loading details…</p>
              <p className="text-sm text-muted-foreground">Fetching the latest application payload from the server.</p>
            </div>
          )}
          {detailQuery.error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              Failed to load details. Please try again.
            </div>
          )}
          {!detailQuery.isLoading && selectedDetail && (
            isEditing ? (
              <form className="space-y-4 text-sm" onSubmit={handleSaveEdit}>
                <div className="space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <LeaveTypePill
                      code={
                        leaveTypeOptions.find((lt) => lt.id === selectedDetail.leave_type_id)
                          ?.code ?? selectedDetail.leave_type_code ?? "—"
                      }
                    />
                    <EmployeeLeaveStatusBadge
                      status={
                        selectedDetail.leave_status ??
                        (selectedDetail.status as LeaveApplicationStatus)
                      }
                    />
                  </div>
                  <p className="text-muted-foreground">
                    <span className="font-medium text-foreground">
                      {
                        leaveTypeOptions.find((lt) => lt.id === selectedDetail.leave_type_id)
                          ?.name ?? selectedDetail.leave_type_detail?.name ?? selectedDetail.leave_type_code ?? selectedDetail.leave_type
                      }
                    </span>{" "}
                    · {selectedDetail.total_days} day{selectedDetail.total_days !== 1 ? "s" : ""}
                  </p>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    From Date <span className="text-red-500">*</span>
                  </label>
                  <Input
                    type="date"
                    value={editForm.from_date}
                    required
                    onChange={(e) =>
                      setEditForm((c) => ({ ...c, from_date: e.target.value }))
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    To Date <span className="text-red-500">*</span>
                  </label>
                  <Input
                    type="date"
                    value={editForm.to_date}
                    required
                    min={editForm.from_date || undefined}
                    onChange={(e) =>
                      setEditForm((c) => ({ ...c, to_date: e.target.value }))
                    }
                  />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <label className="space-y-1.5 text-sm">
                    <span className="block text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      From Session <span className="text-red-500">*</span>
                    </span>
                    <select
                      value={editForm.fromSession}
                      required
                      onChange={(e) =>
                        setEditForm((c) => ({
                          ...c,
                          fromSession: e.target.value as Session,
                        }))
                      }
                      className="flat-input h-10 w-full rounded-xl px-3 text-sm"
                    >
                      {SESSION_OPTIONS.map((s) => (
                        <option key={s.value} value={s.value}>
                          {s.label}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="space-y-1.5 text-sm">
                    <span className="block text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      To Session <span className="text-red-500">*</span>
                    </span>
                    <select
                      value={editForm.toSession}
                      required
                      onChange={(e) =>
                        setEditForm((c) => ({
                          ...c,
                          toSession: e.target.value as Session,
                        }))
                      }
                      className="flat-input h-10 w-full rounded-xl px-3 text-sm"
                    >
                      {SESSION_OPTIONS.map((s) => (
                        <option key={s.value} value={s.value}>
                          {s.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <label className="block space-y-1.5 text-sm">
                  <span className="block text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Reason <span className="text-red-500">*</span>
                  </span>
                  <Textarea
                    value={editForm.reason}
                    required
                    onChange={(e) =>
                      setEditForm((c) => ({ ...c, reason: e.target.value }))
                    }
                    className="min-h-[100px]"
                    placeholder="Describe the reason for your leave…"
                  />
                </label>

                <div className="rounded-xl border border-border bg-secondary/50 px-4 py-3 text-xs text-muted-foreground">
                  <p className="font-semibold text-foreground">Original details</p>
                  <p className="mt-1.5">
                    Applied on: <span className="text-foreground">
                      {formatLeaveDate(selectedDetail.applied_at ?? selectedDetail.applied_on)}
                    </span>
                  </p>
                  <p>
                    Status: <span className="text-foreground">
                      {selectedDetail.leave_status ?? (selectedDetail.status as LeaveApplicationStatus)}
                    </span>
                  </p>
                </div>

                <div className="space-y-3 rounded-lg border border-border bg-secondary/40 p-4 text-sm">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-foreground">Documents</p>
                    <span className="text-xs text-muted-foreground">Add or remove files</span>
                  </div>
                  <div className="space-y-2">
                    {selectedDetail.documents?.filter((doc) => !removedDocumentIds.includes(doc.id)).map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center justify-between gap-3 rounded-xl border border-border bg-background/80 px-3 py-2 text-sm"
                      >
                        <a
                          href={doc.file_url}
                          target="_blank"
                          rel="noreferrer"
                          className="truncate text-primary underline"
                        >
                          {doc.file_name}
                        </a>
                        <button
                          type="button"
                          onClick={() => setRemovedDocumentIds((current) => [...current, doc.id])}
                          className="text-xs font-semibold text-red-500"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                    {newDocuments.map((file, index) => (
                      <div
                        key={`${file.name}-${file.size}-${index}`}
                        className="flex items-center justify-between gap-3 rounded-xl border border-border bg-background/80 px-3 py-2 text-sm"
                      >
                        <span className="truncate">{file.name}</span>
                        <button
                          type="button"
                          onClick={() =>
                            setNewDocuments((current) => current.filter((_, idx) => idx !== index))
                          }
                          className="text-xs font-semibold text-red-500"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                    <label className="grid gap-2 text-sm">
                      <span className="text-xs text-muted-foreground">Upload new documents</span>
                      <input
                        type="file"
                        multiple
                        onChange={(event) => {
                          const files = event.target.files;
                          if (!files) return;
                          setNewDocuments((current) => [...current, ...Array.from(files)]);
                          event.target.value = "";
                        }}
                        className="text-sm"
                      />
                    </label>
                  </div>
                </div>

                {updateMutation.isError && (
                  <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {(updateMutation.error as Error)?.message ||
                      "Failed to update leave. Please try again."}
                  </div>
                )}

                <div className="flex flex-wrap items-center justify-end gap-3 border-t border-border bg-card px-5 py-4">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setIsEditing(false);
                      setRemovedDocumentIds([]);
                      setNewDocuments([]);
                    }}
                    disabled={updateMutation.isPending}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" size="sm" disabled={updateMutation.isPending}>
                    {updateMutation.isPending ? "Saving…" : "Save changes"}
                  </Button>
                </div>
              </form>
            ) : (
              <div className="space-y-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <LeaveTypePill
                    code={
                      leaveTypeOptions.find((lt) => lt.id === selectedDetail.leave_type_id)
                        ?.code ?? selectedDetail.leave_type_code ?? "—"
                    }
                  />
                  <EmployeeLeaveStatusBadge
                    status={
                      selectedDetail.leave_status ??
                      (selectedDetail.status as LeaveApplicationStatus)
                    }
                  />
                </div>
                <p className="text-muted-foreground">
                  <span className="font-medium text-foreground">
                    {
                      leaveTypeOptions.find((lt) => lt.id === selectedDetail.leave_type_id)
                        ?.name ?? selectedDetail.leave_type_detail?.name ?? selectedDetail.leave_type_code ?? selectedDetail.leave_type
                    }
                  </span>{" "}
                  · {selectedDetail.total_days} day{selectedDetail.total_days !== 1 ? "s" : ""}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatLeaveDate(selectedDetail.from_date)} — {formatLeaveDate(selectedDetail.to_date)}
                </p>
                <div className="grid grid-cols-2 gap-2 rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs">
                  <div>
                    <p className="font-semibold text-foreground">From Session</p>
                    <p className="mt-0.5 text-muted-foreground">
                      {sessionLabel(selectedDetail.from_session)}
                    </p>
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">To Session</p>
                    <p className="mt-0.5 text-muted-foreground">
                      {sessionLabel(selectedDetail.to_session)}
                    </p>
                  </div>
                </div>
                <div className="rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs space-y-2">
                  <p className="font-semibold text-foreground">Reason</p>
                  <p className="text-muted-foreground">{selectedDetail.reason ?? "—"}</p>
                </div>
                {selectedDetail.contact_number && (
                  <div className="rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs">
                    <p className="font-semibold text-foreground">Contact number</p>
                    <p className="text-muted-foreground">{selectedDetail.contact_number}</p>
                  </div>
                )}
                {selectedDetail.documents?.length ? (
                  <div className="rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs">
                    <p className="font-semibold text-foreground">Documents</p>
                    <div className="mt-2 space-y-2">
                      {selectedDetail.documents.map((doc) => (
                        <a
                          key={doc.id}
                          href={doc.file_url}
                          target="_blank"
                          rel="noreferrer"
                          className="block text-sm text-primary underline"
                        >
                          {doc.file_name}
                        </a>
                      ))}
                    </div>
                  </div>
                ) : null}
                {selectedDetail.leave_days?.length ? (
                  <div className="rounded-lg border border-border bg-secondary/40 px-3 py-2 text-xs">
                    <p className="font-semibold text-foreground">Leave days</p>
                    <div className="mt-2 grid gap-2 text-[11px] text-muted-foreground">
                      {selectedDetail.leave_days.map((day) => (
                        <div
                          key={day.id}
                          className="grid grid-cols-[1fr_auto] gap-2 rounded-lg bg-background/80 px-2 py-2"
                        >
                          <p>
                            {formatLeaveDate(day.leave_date)} · {sessionLabel(day.session)}
                          </p>
                          <p className="text-right font-semibold text-foreground">
                            {day.day_value}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
                <p className="text-xs text-muted-foreground">
                  Applied on {formatLeaveDate(selectedDetail.applied_at ?? selectedDetail.applied_on)}
                </p>
                {/* FIX: normalised status comparison for the "Edit" button visibility */}
                {(normaliseStatus(selectedDetail.leave_status) === "pending" ||
                  normaliseStatus(selectedDetail.leave_status) === "submitted" ||
                  normaliseStatus(selectedDetail.leave_status) === "draft") && (
                  <div className="flex justify-end">
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => setIsEditing(true)}
                    >
                      Edit pending leave
                    </Button>
                  </div>
                )}
              </div>
            )
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
