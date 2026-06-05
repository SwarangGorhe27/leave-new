import { useMemo, useState, useEffect } from "react";
import { Check, ChevronDown, ChevronRight, Download, Eye, FileText, Paperclip, X, Calendar, Building2 } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import { useAuth } from "../../context/AuthContext";
import { updateAdminEmployee } from "../../../store/slices/adminSlice";
import { AppDispatch, RootState } from "../../../store";
import {
  getChangeRequests,
  getEmployeeDisplayName,
  mergeChangeRequests,
  reviewChangeRequest,
} from "../../modules/ess/storage";
import {
  approveApiChangeRequest,
  fetchAdminChangeRequests,
  isApiRequestId,
  rejectApiChangeRequest,
} from "../../modules/ess/changeRequestApi";
import { ProfileChangeRequest, RequestStatus } from "../../modules/ess/types";
import type { Employee } from "../../components/employees/mockData";

/* ─── Helpers ──────────────────────────────────────────────────────────────── */

function flattenObject(obj: any, prefix = ""): Record<string, string> {
  if (typeof obj !== "object" || obj === null) return prefix ? { [prefix]: String(obj ?? "") } : {};
  const result: Record<string, string> = {};
  for (const key of Object.keys(obj)) {
    if (key.startsWith("_")) continue; // skip internal fields
    const fullKey = prefix ? `${prefix}.${key}` : key;
    const val = obj[key];
    if (Array.isArray(val)) {
      val.forEach((item, i) => Object.assign(result, flattenObject(item, `${fullKey}[${i}]`)));
    } else if (typeof val === "object" && val !== null) {
      Object.assign(result, flattenObject(val, fullKey));
    } else {
      result[fullKey] = String(val ?? "");
    }
  }
  return result;
}

function buildDiffRows(oldValue: unknown, newValue: unknown) {
  const oldFlat = flattenObject(oldValue as any);
  const newFlat = flattenObject(newValue as any);
  const allKeys = new Set([...Object.keys(oldFlat), ...Object.keys(newFlat)]);
  return Array.from(allKeys)
    .filter((k) => oldFlat[k] !== newFlat[k])
    .map((k) => ({ field: k, oldValue: oldFlat[k] ?? "", newValue: newFlat[k] ?? "" }));
}

const SENSITIVE_PATTERNS = [
  "account", "pan", "aadhaar", "uan", "pf", "esi", "passport", "visa",
];

function maskSensitive(field: string, value: string): string {
  const low = field.toLowerCase();
  const isSensitive = SENSITIVE_PATTERNS.some((p) => low.includes(p));
  if (!isSensitive) return value;
  if (value.startsWith("data:")) return "[file]";
  if (value.length > 6) {
    return value.slice(0, 2) + "••••" + value.slice(-2);
  }
  return value;
}

function isDataUrl(value: string) {
  return typeof value === "string" && value.startsWith("data:");
}

const requestStatusColors: Record<string, string> = {
  draft: "bg-slate-100 border-slate-200 text-slate-600",
  pending: "bg-amber-50 border-amber-200 text-amber-700",
  approved: "bg-emerald-50 border-emerald-200 text-emerald-700",
  rejected: "bg-rose-50 border-rose-200 text-rose-700",
};

function isWithinDateRange(isoDate: string, from: string, to: string): boolean {
  if (!from && !to) return true;
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) return false;
  if (from) {
    const start = new Date(from);
    start.setHours(0, 0, 0, 0);
    if (date < start) return false;
  }
  if (to) {
    const end = new Date(to);
    end.setHours(23, 59, 59, 999);
    if (date > end) return false;
  }
  return true;
}

function getEmployeeDepartmentForRequest(
  request: ProfileChangeRequest,
  employees: Employee[],
): string {
  const primary = getEmployeeDepartment(request.employee_id, employees);
  if (primary) return primary;
  if (request._employeeCode) {
    return getEmployeeDepartment(request._employeeCode, employees);
  }
  return "";
}

function getEmployeeDepartment(employeeId: string, employees: Employee[]): string {
  const emp = employees.find(
    (e) => e.id === employeeId || e.employeeId === employeeId,
  );
  if (emp?.department?.trim()) return emp.department.trim();

  try {
    const raw = localStorage.getItem("admin_employees_db");
    if (raw) {
      const stored = JSON.parse(raw) as Employee[];
      const match = stored.find(
        (e) => e.id === employeeId || e.employeeId === employeeId,
      );
      if (match?.department?.trim()) return match.department.trim();
    }
  } catch {
    /* ignore */
  }

  return "";
}

/* ─── File Preview Modal ───────────────────────────────────────────────────── */
function FilePreviewModal({ dataUrl, fileName, onClose }: { dataUrl: string; fileName: string; onClose: () => void }) {
  const isImage = dataUrl.startsWith("data:image");
  const isPdf = dataUrl.startsWith("data:application/pdf");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div
        className="relative bg-card rounded-2xl border border-border shadow-2xl max-w-3xl w-full mx-4 max-h-[90vh] flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border shrink-0">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-semibold text-foreground truncate max-w-xs">{fileName}</span>
          </div>
          <div className="flex items-center gap-2">
            <a
              href={dataUrl}
              download={fileName}
              className="inline-flex items-center gap-1.5 h-8 rounded-lg border border-border bg-secondary px-3 text-xs font-bold text-foreground hover:bg-secondary/80 transition-colors"
            >
              <Download className="h-3.5 w-3.5" /> Download
            </a>
            <button
              onClick={onClose}
              className="h-8 w-8 flex items-center justify-center rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {isImage ? (
            <img src={dataUrl} alt={fileName} className="max-w-full mx-auto rounded-lg" />
          ) : isPdf ? (
            <iframe src={dataUrl} title={fileName} className="w-full h-[600px] rounded-lg border border-border" />
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-3">
              <FileText className="h-12 w-12" />
              <p className="text-sm">Preview not available for this file type.</p>
              <a
                href={dataUrl}
                download={fileName}
                className="inline-flex items-center gap-1.5 h-9 rounded-lg bg-foreground text-primary-foreground px-4 text-xs font-bold hover:opacity-90 transition-opacity"
              >
                <Download className="h-3.5 w-3.5" /> Download
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── Diff Table ───────────────────────────────────────────────────────────── */
function DiffTable({ rows }: { rows: { field: string; oldValue: string; newValue: string }[] }) {
  const [preview, setPreview] = useState<{ dataUrl: string; fileName: string } | null>(null);
  if (rows.length === 0) {
    return <p className="text-xs text-muted-foreground italic py-2">No field-level differences detected.</p>;
  }
  return (
    <>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-xs">
          <thead className="bg-secondary/60">
            <tr>
              <th className="text-left p-2.5 font-bold text-muted-foreground uppercase tracking-wider text-[10px] w-1/3">Field</th>
              <th className="text-left p-2.5 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Current Value</th>
              <th className="text-left p-2.5 font-bold text-foreground uppercase tracking-wider text-[10px]">Requested Value</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {rows.map((row) => (
              <tr key={row.field} className="hover:bg-secondary/20 transition-colors">
                <td className="p-2.5 font-mono text-[10px] font-medium text-foreground align-top">{row.field}</td>
                <td className="p-2.5 text-muted-foreground align-top">
                  {isDataUrl(row.oldValue) ? (
                    <button
                      onClick={() => setPreview({ dataUrl: row.oldValue, fileName: row.field + "_current" })}
                      className="inline-flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <Eye className="h-3 w-3" /> View file
                    </button>
                  ) : (
                    <span>{maskSensitive(row.field, row.oldValue) || "—"}</span>
                  )}
                </td>
                <td className="p-2.5 text-foreground font-semibold align-top">
                  {isDataUrl(row.newValue) ? (
                    <button
                      onClick={() => setPreview({ dataUrl: row.newValue, fileName: row.field + "_new" })}
                      className="inline-flex items-center gap-1.5 text-[10px] text-primary font-bold hover:opacity-80 transition-opacity"
                    >
                      <Eye className="h-3 w-3" /> Preview new file
                    </button>
                  ) : (
                    <span className={row.newValue !== row.oldValue ? "text-foreground" : "text-muted-foreground"}>
                      {maskSensitive(row.field, row.newValue) || "—"}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {preview && (
        <FilePreviewModal
          dataUrl={preview.dataUrl}
          fileName={preview.fileName}
          onClose={() => setPreview(null)}
        />
      )}
    </>
  );
}

/* ─── Request Card ─────────────────────────────────────────────────────────── */
function RequestCard({
  request,
  employeeName,
  isExpanded,
  onToggle,
  onApprove,
  onReject,
  rejectingId,
  setRejectingId,
  rejectionComment,
  setRejectionComment,
  onConfirmReject,
}: {
  request: ProfileChangeRequest;
  employeeName: string;
  isExpanded: boolean;
  onToggle: () => void;
  onApprove: () => void;
  onReject: () => void;
  rejectingId: string | null;
  setRejectingId: (id: string | null) => void;
  rejectionComment: string;
  setRejectionComment: (v: string) => void;
  onConfirmReject: () => void;
}) {
  const diffRows = useMemo(() => buildDiffRows(request.changes.oldValue, request.changes.newValue), [request.changes]);
  const isPending = request.status === "pending";

  return (
    <section className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
      {/* Card Header */}
      <button
        className="flex w-full items-center justify-between gap-3 px-5 py-4 hover:bg-secondary/20 transition-colors text-left"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="shrink-0">
            {isExpanded ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-bold text-foreground truncate">{request.section_label}</h3>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Employee: <span className="font-semibold">{employeeName}</span>
              {" "}({request._employeeCode || request.employee_id}) • {new Date(request.created_at).toLocaleString("en-IN")}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[10px] text-muted-foreground font-medium">{diffRows.length} change{diffRows.length !== 1 ? "s" : ""}</span>
          <span className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-wider ${requestStatusColors[request.status] ?? ""}`}>
            {request.status}
          </span>
        </div>
      </button>

      {/* Expanded body */}
      {isExpanded && (
        <div className="border-t border-border px-5 py-4 space-y-4 bg-secondary/5">
          <DiffTable rows={diffRows} />

          {/* Supporting Document */}
          {request.supportingDoc && (
            <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3">
              <Paperclip className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-foreground">Supporting Document</p>
                <p className="text-[11px] text-muted-foreground truncate">{request.supportingDoc.fileName}</p>
              </div>
              <a
                href={request.supportingDoc.dataUrl}
                download={request.supportingDoc.fileName}
                className="inline-flex items-center gap-1.5 h-8 rounded-lg bg-foreground text-primary-foreground px-3 text-[10px] font-bold hover:opacity-90 transition-opacity"
              >
                <Download className="h-3 w-3" /> Download
              </a>
            </div>
          )}

          {/* Rejection comment (read-only if already rejected) */}
          {request.rejection_comment && (
            <div className="rounded-lg bg-rose-50/60 border border-rose-100 p-3 text-xs">
              <p className="font-bold text-rose-700">Rejection Reason:</p>
              <p className="text-rose-600 mt-1">{request.rejection_comment}</p>
            </div>
          )}

          {/* Approval notice */}
          {request.status === "approved" && (
            <div className="flex items-center gap-2 text-emerald-700 text-xs font-medium bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2">
              <Check className="h-4 w-4" />
              Approved by <span className="font-bold ml-1">{request.reviewed_by ?? "Admin"}</span>
              {request.reviewed_at && (
                <span className="ml-1">on {new Date(request.reviewed_at).toLocaleDateString("en-IN")}</span>
              )}
            </div>
          )}

          {/* Action buttons (only for pending) */}
          {isPending && (
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <button
                onClick={onApprove}
                className="inline-flex items-center gap-2 h-9 rounded-lg bg-foreground text-primary-foreground px-5 text-xs font-bold hover:opacity-90 transition-opacity"
              >
                <Check className="h-3.5 w-3.5" /> Approve
              </button>
              <button
                onClick={() => setRejectingId(request.id)}
                className="h-9 rounded-lg border border-border bg-card px-4 text-xs font-bold text-foreground hover:bg-secondary transition-colors"
              >
                Reject
              </button>
              {rejectingId === request.id && (
                <div className="flex items-center gap-2 flex-wrap">
                  <input
                    value={rejectionComment}
                    onChange={(e) => setRejectionComment(e.target.value)}
                    placeholder="Rejection reason (optional)"
                    className="h-9 rounded-lg border border-border bg-background px-3 text-sm min-w-64 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                  <button
                    onClick={onConfirmReject}
                    className="h-9 rounded-lg bg-rose-600 text-white px-4 text-xs font-bold hover:bg-rose-700 transition-colors"
                  >
                    Confirm Reject
                  </button>
                  <button
                    onClick={() => { setRejectingId(null); setRejectionComment(""); }}
                    className="h-9 w-9 flex items-center justify-center rounded-lg border border-border text-muted-foreground hover:bg-secondary transition-colors"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

/* ─── Main Page ────────────────────────────────────────────────────────────── */

export function ProfileChangeRequestsPage() {
  const { user } = useAuth();
  const dispatch = useDispatch<AppDispatch>();
  const adminEmployees = useSelector((state: RootState) => state.admin.employees);
  const [refreshTick, setRefreshTick] = useState(0);
  const [statusFilter, setStatusFilter] = useState<RequestStatus | "all">("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("all");
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [rejectionComment, setRejectionComment] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [apiRequests, setApiRequests] = useState<ProfileChangeRequest[]>([]);
  const [loadingRequests, setLoadingRequests] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoadingRequests(true);
    fetchAdminChangeRequests()
      .then((rows) => {
        if (!cancelled) setApiRequests(rows);
      })
      .finally(() => {
        if (!cancelled) setLoadingRequests(false);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshTick]);

  const allRequests = useMemo(
    () => mergeChangeRequests(getChangeRequests(), apiRequests),
    [refreshTick, apiRequests],
  );

  const departmentOptions = useMemo(() => {
    const depts = new Set<string>();
    adminEmployees.forEach((emp) => {
      if (emp.department?.trim()) depts.add(emp.department.trim());
    });
    allRequests.forEach((req) => {
      const dept = getEmployeeDepartmentForRequest(req, adminEmployees);
      if (dept) depts.add(dept);
    });
    return Array.from(depts).sort((a, b) => a.localeCompare(b));
  }, [adminEmployees, allRequests]);

  const filteredRequests = useMemo(() => {
    return allRequests
      .filter((r) => r.status !== "draft")
      .filter((r) => isWithinDateRange(r.created_at, dateFrom, dateTo))
      .filter((r) => {
        if (departmentFilter === "all") return true;
        return getEmployeeDepartmentForRequest(r, adminEmployees) === departmentFilter;
      });
  }, [allRequests, dateFrom, dateTo, departmentFilter, adminEmployees]);

  const requests = useMemo(() => {
    if (statusFilter === "all") return filteredRequests;
    return filteredRequests.filter((r) => r.status === statusFilter);
  }, [filteredRequests, statusFilter]);

  const counts = useMemo(() => ({
    all: filteredRequests.length,
    pending: filteredRequests.filter((r) => r.status === "pending").length,
    approved: filteredRequests.filter((r) => r.status === "approved").length,
    rejected: filteredRequests.filter((r) => r.status === "rejected").length,
  }), [filteredRequests]);

  const hasDateFilter = Boolean(dateFrom || dateTo);
  const hasDepartmentFilter = departmentFilter !== "all";
  const hasActiveFilters = hasDateFilter || hasDepartmentFilter;

  const approve = async (id: string) => {
    const pending = allRequests.find((r) => r.id === id);
    if (!pending) return;

    if (isApiRequestId(id)) {
      const ok = await approveApiChangeRequest(id);
      if (!ok) return;
      setRefreshTick((v) => v + 1);
      return;
    }

    reviewChangeRequest({ requestId: id, reviewer: user?.name ?? "Admin", status: "approved" });
    const empId = pending.employee_id;
    const fromStorage = (() => {
      try {
        const raw = localStorage.getItem("admin_employees_db");
        if (!raw) return null;
        const emps = JSON.parse(raw) as typeof adminEmployees;
        return emps.find((e) => e.id === empId || e.employeeId === empId) ?? null;
      } catch {
        return null;
      }
    })();
    const fromRedux = adminEmployees.find((e) => e.id === empId || e.employeeId === empId);
    const updated = fromStorage ?? fromRedux;
    if (updated) dispatch(updateAdminEmployee(updated));
    setRefreshTick((v) => v + 1);
  };

  const reject = async (id: string) => {
    if (isApiRequestId(id)) {
      const ok = await rejectApiChangeRequest(id, rejectionComment.trim() || "Rejected by admin");
      if (!ok) return;
    } else {
      reviewChangeRequest({ requestId: id, reviewer: user?.name ?? "Admin", status: "rejected", rejectionComment });
    }
    setRejectingId(null);
    setRejectionComment("");
    setRefreshTick((v) => v + 1);
  };

  return (
    <div className="portal-page admin-dashboard">
      {/* Header */}
      <div className="rounded-xl border border-border bg-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-foreground">Profile Change Requests</h2>
            <p className="text-sm text-muted-foreground mt-0.5">Review and approve employee-submitted profile update requests.</p>
          </div>
          {/* Stats pills */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-amber-50 border border-amber-200 text-amber-700 text-xs font-bold px-3 py-1">
              {counts.pending} Pending
            </span>
            <span className="rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold px-3 py-1">
              {counts.approved} Approved
            </span>
            <span className="rounded-full bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold px-3 py-1">
              {counts.rejected} Rejected
            </span>
          </div>
        </div>

        {/* Filter tabs + date range */}
        <div className="flex flex-wrap items-center justify-between gap-3 mt-4 border-t border-border pt-4">
          <div className="flex flex-wrap items-center gap-2">
            {(["all", "pending", "approved", "rejected"] as const).map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`h-9 px-4 rounded-lg text-sm font-semibold border transition-colors capitalize ${statusFilter === status
                  ? "bg-foreground border-foreground text-primary-foreground"
                  : "border-border text-muted-foreground hover:text-foreground hover:bg-secondary"
                  }`}
              >
                {status} ({counts[status as keyof typeof counts] ?? counts.all})
              </button>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
              <Building2 className="h-3.5 w-3.5" />
              <label htmlFor="department-filter">Department</label>
            </div>
            <select
              id="department-filter"
              value={departmentFilter}
              onChange={(e) => setDepartmentFilter(e.target.value)}
              className="h-9 min-w-[160px] rounded-lg border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            >
              <option value="all">All Departments</option>
              {departmentOptions.map((dept) => (
                <option key={dept} value={dept}>
                  {dept}
                </option>
              ))}
            </select>

            <div className="hidden sm:block w-px h-6 bg-border mx-1" />

            <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              <span>From</span>
            </div>
            <input
              type="date"
              value={dateFrom}
              max={dateTo || undefined}
              onChange={(e) => setDateFrom(e.target.value)}
              className="h-9 rounded-lg border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
            <span className="text-xs font-semibold text-muted-foreground">To</span>
            <input
              type="date"
              value={dateTo}
              min={dateFrom || undefined}
              onChange={(e) => setDateTo(e.target.value)}
              className="h-9 rounded-lg border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
            {hasActiveFilters && (
              <button
                type="button"
                onClick={() => {
                  setDateFrom("");
                  setDateTo("");
                  setDepartmentFilter("all");
                }}
                className="h-9 px-3 rounded-lg border border-border text-xs font-bold text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
              >
                Reset filters
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Empty state */}
      {!loadingRequests && requests.length === 0 && (
        <div className="rounded-xl border border-dashed border-border bg-card p-12 text-center">
          <FileText className="h-10 w-10 mx-auto text-muted-foreground/40 mb-3" />
          <p className="text-sm font-semibold text-foreground">No requests found</p>
          <p className="text-xs text-muted-foreground mt-1">
            {hasActiveFilters
              ? "No profile change requests match the selected status, department, or date range."
              : "No profile change requests match the selected filter."}
          </p>
        </div>
      )}

      {loadingRequests && requests.length === 0 && (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <p className="text-sm text-muted-foreground">Loading profile change requests…</p>
        </div>
      )}

      {/* Request cards */}
      <div className="space-y-3">
        {requests.map((request) => (
          <RequestCard
            key={request.id}
            request={request}
            employeeName={getEmployeeDisplayName(request.employee_id, adminEmployees, request)}
            isExpanded={expandedId === request.id}
            onToggle={() => setExpandedId(expandedId === request.id ? null : request.id)}
            onApprove={() => approve(request.id)}
            onReject={() => setRejectingId(request.id)}
            rejectingId={rejectingId}
            setRejectingId={setRejectingId}
            rejectionComment={rejectionComment}
            setRejectionComment={setRejectionComment}
            onConfirmReject={() => reject(request.id)}
          />
        ))}
      </div>
    </div>
  );
}
