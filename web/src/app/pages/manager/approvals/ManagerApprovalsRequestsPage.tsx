import { useEffect, useMemo, useRef, useState } from "react";
import {
  Download,
  FileText,
  X,
  Clock,
  CheckCircle2,
  AlertCircle,
  Search,
  MessageSquare,
  Paperclip,
  XCircle,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  CornerUpLeft,
  CalendarDays,
  User,
  Building,
  Info,
  Calendar,
} from "lucide-react";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "../../../components/ui/drawer";
import { Input } from "../../../components/ui/input";
import { Button } from "../../../components/ui/button";
import { cn } from "../../../components/ui/utils";
import { useManagerLeaveData } from "../leaves/ManagerLeaveDataContext";
import type { LeaveApplicationAPI } from "../../../modules/leaves/types";
import { useApproveLeave, useRejectLeave } from "../../../modules/leaves/useLeaves";
import { useManagerApprovals } from "../../../hooks/useManagerApprovals";
import {
  mergeOvertimeDetail,
  mergeRegularizationDetail,
  type ApprovalRowSource,
  type UnifiedApprovalRow,
} from "../../../modules/manager-attendance/approvalsMappers";
import {
  approveManagerOvertime,
  approveManagerRegularization,
  fetchManagerOvertimeDetail,
  fetchManagerRegularizationDetail,
  ManagerAttendanceApiError,
  rejectManagerOvertime,
  rejectManagerRegularization,
} from "../../../../api/managerAttendanceClient";
import { EmployeeLeaveStatusBadge } from "../../../components/leaves/employee/EmployeeLeaveStatusBadge";
import { LeaveTypePill } from "../../../components/leaves/employee/LeaveTypePill";
import { formatLeaveDate, formatLeaveShortDate } from "../../../components/leaves/employee/leaveDateUtils";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../../../components/ui/dialog";
import { Textarea } from "../../../components/ui/textarea";

// --- Types ---
type RequestCategory = "Attendance" | "Leave" | "Other";
type RequestStatus = "Pending" | "Approved" | "Rejected" | "Sent Back" | "Escalated";
type Priority = "Low" | "Medium" | "High";

/** Unified row for inbox (leave + attendance APIs + optional local demo rows) */
type RequestRow = UnifiedApprovalRow & {
  _apiLeave?: LeaveApplicationAPI;
};

type RowSource = ApprovalRowSource;

// --- Constants ---
const STATUS_STYLES: Record<RequestStatus, string> = {
  Pending: "bg-[#F59E0B] text-white border border-[#F59E0B]",
  Approved: "bg-[#10B981] text-white border border-[#10B981]",
  Rejected: "bg-[#EF4444] text-white border border-[#EF4444]",
  "Sent Back": "bg-[#3B82F6] text-white border border-[#3B82F6]",
  Escalated: "bg-[#DC2626] text-white border border-[#DC2626]",
};

const TYPE_COLORS: Record<string, string> = {
  Regularization: "bg-[#2563EB] text-white border border-[#2563EB]",
  "Late Login": "bg-[#4F46E5] text-white border border-[#4F46E5]",
  "Earned Leave": "bg-[#059669] text-white border border-[#059669]",
  "Sick Leave": "bg-[#E11D48] text-white border border-[#E11D48]",
  "Comp Off": "bg-[#7C3AED] text-white border border-[#7C3AED]",
  Permission: "bg-[#C026D3] text-white border border-[#C026D3]",
  "Work From Home": "bg-[#0891B2] text-white border border-[#0891B2]",
  "Half Day": "bg-[#0F766E] text-white border border-[#0F766E]",
  default: "bg-[#4B5563] text-white border border-[#4B5563]",
};

// --- Mock Data (non-API "Other" category demo only) ---
const MOCK_REQUESTS: Omit<RequestRow, "source">[] = [
  {
    id: "r2",
    requestId: "REQ-1031",
    employeeName: "Karan Verma",
    employeeId: "EMP-1934",
    photoUrl: "https://api.dicebear.com/9.x/notionists/svg?seed=Karan",
    department: "Operations",
    team: "Field Services",
    requestType: "Comp Off",
    category: "Leave",
    requestDate: "2026-05-15",
    effectiveDate: "2026-05-16",
    submittedOn: "2026-05-15",
    status: "Pending",
    priority: "Low",
    waitingDays: 0,
    daysAffected: 1,
    currentApprover: "Radha Singh",
    designation: "Field Supervisor",
    reportingTo: "Rohit Sharma",
    reason: "Worked full shift on a holiday (May 1st), requesting comp off for family event.",
    attachments: ["attendance-report.pdf"],
    commentsCount: 0,
    existingData: "Attendance shows 9 hours on holiday 1 May.",
    leaveBalance: "Comp Off: 2 days",
    previousRequests: "Previous comp off approved in Apr 2026.",
    timeline: [{ step: "Submitted", date: "2026-05-15", actor: "Karan Verma", status: "Pending" }],
  },
  {
    id: "r3",
    requestId: "REQ-1034",
    employeeName: "Nisha Rao",
    employeeId: "EMP-1546",
    photoUrl: "https://api.dicebear.com/9.x/notionists/svg?seed=Nisha",
    department: "HR",
    team: "Recruitment",
    requestType: "Permission",
    category: "Other",
    requestDate: "2026-05-14",
    effectiveDate: "2026-05-14",
    submittedOn: "2026-05-14",
    status: "Approved",
    priority: "Low",
    waitingDays: 0,
    daysAffected: 0,
    currentApprover: "Completed",
    designation: "Recruitment Lead",
    reportingTo: "Rohit Sharma",
    reason: "Doctor appointment for three hours in the afternoon.",
    attachments: ["medical-note.pdf"],
    commentsCount: 1,
    existingData: "Requested permission from 14:30 to 18:00.",
    leaveBalance: "N/A",
    previousRequests: "Permission request approved in Mar 2026.",
    timeline: [
      { step: "Submitted", date: "2026-05-14", actor: "Nisha Rao", status: "Approved" },
      { step: "Approved", date: "2026-05-14", actor: "Rohit Sharma", status: "Approved", remarks: "Approved, please update calendar." },
    ],
  },
  {
    id: "r5",
    requestId: "REQ-1045",
    employeeName: "Sanya Mehta",
    employeeId: "EMP-1677",
    photoUrl: "https://api.dicebear.com/9.x/notionists/svg?seed=Sanya",
    department: "Finance",
    team: "Payroll",
    requestType: "Earned Leave",
    category: "Leave",
    requestDate: "2026-05-18",
    effectiveDate: "2026-05-20",
    submittedOn: "2026-05-12",
    status: "Pending",
    priority: "Medium",
    waitingDays: 2,
    daysAffected: 3,
    currentApprover: "Rohit Sharma",
    designation: "Payroll Analyst",
    reportingTo: "Rohit Sharma",
    reason: "Planned personal travel for three days. Backup resource is Varun.",
    attachments: [],
    commentsCount: 0,
    existingData: "Leave balance: 6 days remaining.",
    leaveBalance: "Earned Leave: 6 days",
    previousRequests: "One approved earned leave in Mar 2026.",
    timeline: [
      { step: "Submitted", date: "2026-05-12", actor: "Sanya Mehta", status: "Pending" },
      { step: "Pending with Manager", date: "2026-05-12", actor: "Rohit Sharma", status: "In Review" },
    ],
  },
  {
    id: "r7",
    requestId: "REQ-1051",
    employeeName: "Priya Singh",
    employeeId: "EMP-1205",
    photoUrl: "https://api.dicebear.com/9.x/notionists/svg?seed=Priya",
    department: "Marketing",
    team: "Digital",
    requestType: "Sick Leave",
    category: "Leave",
    requestDate: "2026-05-13",
    effectiveDate: "2026-05-14",
    submittedOn: "2026-05-10",
    status: "Pending",
    priority: "High",
    waitingDays: 4,
    daysAffected: 2,
    currentApprover: "Rohit Sharma",
    designation: "Marketing Specialist",
    reportingTo: "Rohit Sharma",
    reason: "Down with viral fever. Requested leaves for proper rest.",
    attachments: ["medical-prescription.pdf"],
    commentsCount: 1,
    existingData: "Leave balance: 4 days remaining.",
    leaveBalance: "Sick Leave: 4 days",
    previousRequests: "None recently.",
    timeline: [{ step: "Submitted", date: "2026-05-10", actor: "Priya Singh", status: "Pending" }],
  },
];

// --- Helpers ---
function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
}


function saveFile(content: string, fileName: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

/** Map an API leave application → unified RequestRow */
function leaveApiToRow(app: LeaveApplicationAPI): RequestRow {
  const apiStatus = app.status?.toUpperCase();
  let status: RequestStatus = "Pending";
  if (apiStatus === "APPROVED") status = "Approved";
  else if (apiStatus === "REJECTED") status = "Rejected";
  else if (apiStatus === "DRAFT") status = "Pending";

  const submittedDate = app.applied_on?.slice(0, 10) ?? app.from_date?.slice(0, 10) ?? "";
  const fromDate = app.from_date?.slice(0, 10) ?? "";
  const toDate = app.to_date?.slice(0, 10) ?? "";

  const waitDays =
    status === "Pending"
      ? Math.max(0, Math.floor((Date.now() - new Date(submittedDate).getTime()) / 86_400_000))
      : 0;

  return {
    id: `api-${app.id}`,
    source: "api-leave",
    _apiLeave: app,
    requestId: `LVE-${app.id.slice(0, 6).toUpperCase()}`,
    employeeName: app.employee_name ?? "—",
    employeeId: app.employee_code ?? "—",
    photoUrl: `https://api.dicebear.com/9.x/notionists/svg?seed=${encodeURIComponent(app.employee_name ?? app.id)}`,
    department: "—",
    team: "—",
    requestType: app.leave_type_detail?.name ?? "Leave",
    category: "Leave",
    requestDate: fromDate,
    effectiveDate: fromDate,
    submittedOn: submittedDate,
    status,
    priority: "Medium",
    waitingDays: waitDays,
    daysAffected: app.total_days ?? 0,
    currentApprover: status === "Pending" ? "You" : "Completed",
    designation: "—",
    reportingTo: "—",
    reason: app.reason ?? "—",
    attachments: [],
    commentsCount: 0,
    existingData: `${app.total_days ?? 0} day(s) requested.`,
    leaveBalance: "—",
    previousRequests: "—",
    leaveTypeCode: app.leave_type_detail?.code,
    leaveTypeName: app.leave_type_detail?.name,
    fromDate,
    toDate,
    timeline: [
      {
        step: "Submitted",
        date: submittedDate,
        actor: app.employee_name ?? "Employee",
        status: "Pending",
      },
    ],
  };
}

// --- Reject dialog for attendance API rows ---
function ApiAttendanceRejectDialog({
  row,
  onClose,
  onDone,
}: {
  row: RequestRow;
  onClose: () => void;
  onDone: () => void;
}) {
  const [remarks, setRemarks] = useState("");
  const [busy, setBusy] = useState(false);

  const handleReject = async () => {
    setBusy(true);
    try {
      if (row.source === "api-reg" && row.attendanceRegId) {
        await rejectManagerRegularization(row.attendanceRegId, { remarks });
      } else if (row.source === "api-ot" && row.attendanceOtId) {
        await rejectManagerOvertime(row.attendanceOtId, { remarks });
      }
      onDone();
    } catch (err) {
      const message =
        err instanceof ManagerAttendanceApiError ? err.message : "Failed to reject request.";
      alert(message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-md rounded-xl border-border">
        <DialogHeader>
          <DialogTitle className="text-base">Reject attendance request</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Rejecting {row.requestType} for {row.employeeName}.
          </p>
          <Textarea
            value={remarks}
            onChange={(e) => setRemarks(e.target.value)}
            placeholder="Reason for rejection (optional)"
            className="min-h-[100px]"
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button type="button" size="sm" variant="destructive" disabled={busy} onClick={handleReject}>
              Reject
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// --- Reject dialog for API leave rows ---
function ApiLeaveRejectDialog({
  row,
  onClose,
  onDone,
}: {
  row: RequestRow;
  onClose: () => void;
  onDone: () => void;
}) {
  const rejectLeave = useRejectLeave();
  const [remarks, setRemarks] = useState("");
  const [busy, setBusy] = useState(false);

  const handleReject = async () => {
    if (!row._apiLeave) return;
    setBusy(true);
    try {
      await rejectLeave.mutate({ id: row._apiLeave.id, remarks });
      onDone();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-md rounded-xl border-border">
        <DialogHeader>
          <DialogTitle className="text-base">Reject leave request</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Rejecting request for {row.employeeName}. Optional remarks are stored with the record.
          </p>
          <Textarea
            value={remarks}
            onChange={(e) => setRemarks(e.target.value)}
            placeholder="Reason for rejection (optional)"
            className="min-h-[100px]"
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button type="button" size="sm" variant="destructive" disabled={busy} onClick={handleReject}>
              Reject
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// --- Main Page ---
export default function ManagerApprovalsRequestsPage() {
  const { teamPendingApplications, refreshTeam } = useManagerLeaveData();
  const approveLeave = useApproveLeave();

  const [localRows, setLocalRows] = useState<RequestRow[]>(
    MOCK_REQUESTS.map((r) => ({ ...r, source: "local" as RowSource }))
  );

  const [apiRejectTarget, setApiRejectTarget] = useState<RequestRow | null>(null);
  const [attendanceRejectTarget, setAttendanceRejectTarget] = useState<RequestRow | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Filters
  const [query, setQuery] = useState("");
  const [requestType, setRequestType] = useState<string>("ALL");
  const [category, setCategory] = useState<RequestCategory | "ALL">("ALL");
  const [status, setStatus] = useState<RequestStatus | "ALL">("Pending");
  const [department, setDepartment] = useState<string>("ALL");
  const [showOnlyPending, setShowOnlyPending] = useState(true);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [pageNum, setPageNum] = useState(1);
  const [perPage, setPerPage] = useState(50);

  // Helper to convert humanized request type back to reg_type code
  const getRawRegType = (humanizedType: string): string | undefined => {
    if (!humanizedType || humanizedType === "ALL") return undefined;
    const regTypes: Record<string, string> = {
      "Missing Punch": "MISSING_PUNCH",
      "Wrong Punch": "WRONG_PUNCH",
      "Late Login": "LATE_LOGIN",
      "Early Exit": "EARLY_EXIT",
    };
    return regTypes[humanizedType];
  };

  const attendanceFilters = useMemo(
    () => ({
      status: showOnlyPending ? "PENDING" : status !== "ALL" ? status.toUpperCase() : undefined,
      reg_type: getRawRegType(requestType),
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
      search: query.trim() || undefined,
      department: department !== "ALL" ? department : undefined,
      page: pageNum,
      per_page: perPage,
    }),
    [showOnlyPending, status, requestType, dateFrom, dateTo, query, department, pageNum, perPage],
  );

  const {
    rows: attendanceApiRows,
    loading: attendanceLoading,
    error: attendanceError,
    reload: reloadAttendance,
  } = useManagerApprovals(attendanceFilters);

  const apiLeaveRows = useMemo<RequestRow[]>(
    () => teamPendingApplications.map(leaveApiToRow),
    [teamPendingApplications],
  );

  const allRows = useMemo<RequestRow[]>(
    () => [...apiLeaveRows, ...attendanceApiRows, ...localRows],
    [apiLeaveRows, attendanceApiRows, localRows],
  );

  // Selection
  const [selectedIds, setSelectedIds] = useState<Record<string, boolean>>({});
  const selectAllRef = useRef<HTMLInputElement>(null);

  // Drawer
  const [drawerRow, setDrawerRow] = useState<RequestRow | null>(null);
  const [remarks, setRemarks] = useState("");
  const [remarksError, setRemarksError] = useState("");

  // Workflow modals
  const [workflowType, setWorkflowType] = useState("Multi-level approval");
  const [showDelegateModal, setShowDelegateModal] = useState(false);
  const [showWorkflowModal, setShowWorkflowModal] = useState(false);
  const [currentDelegate, setCurrentDelegate] = useState({ delegateName: "Priya Patel", effectiveFrom: "2026-05-19", reason: "Annual leave coverage" });
  const [delegateFormData, setDelegateFormData] = useState({ delegateName: "Priya Patel", effectiveFrom: "2026-05-19", reason: "" });

  // Toast
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" | "info" } | null>(null);
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);
  const showToast = (message: string, type: "success" | "error" | "info" = "success") => setToast({ message, type });

  // Derived filter options
  const departments = useMemo(
    () => ["ALL", ...Array.from(new Set(allRows.map((r) => r.department).filter((d) => d !== "—"))).sort()],
    [allRows]
  );
  const requestTypes = useMemo(
    () => ["ALL", ...Array.from(new Set(allRows.map((r) => r.requestType))).sort()],
    [allRows]
  );

  const filteredRows = useMemo(() => {
    const normQ = query.trim().toLowerCase();
    const from = dateFrom ? new Date(dateFrom).getTime() : 0;
    const to = dateTo ? new Date(dateTo).getTime() + 86_400_000 - 1 : Number.MAX_SAFE_INTEGER;

    return allRows.filter((row) => {
      if (normQ) {
        const blob = `${row.employeeName} ${row.employeeId} ${row.requestId} ${row.requestType} ${row.reason}`.toLowerCase();
        if (!blob.includes(normQ)) return false;
      }
      if (requestType !== "ALL" && row.requestType !== requestType) return false;
      if (category !== "ALL" && row.category !== category) return false;
      if (showOnlyPending) {
        if (row.status !== "Pending") return false;
      } else {
        if (status !== "ALL" && row.status !== status) return false;
      }
      if (department !== "ALL" && row.department !== department) return false;
      const submitted = new Date(row.submittedOn).getTime();
      if (submitted < from || submitted > to) return false;
      return true;
    });
  }, [query, requestType, category, status, department, showOnlyPending, dateFrom, dateTo, allRows]);

  const selectedCount = Object.values(selectedIds).filter(Boolean).length;
  const allVisibleSelected = filteredRows.length > 0 && filteredRows.every((r) => selectedIds[r.id]);
  const someVisibleSelected = filteredRows.some((r) => selectedIds[r.id]);

  useEffect(() => {
    if (selectAllRef.current) selectAllRef.current.indeterminate = someVisibleSelected && !allVisibleSelected;
  }, [someVisibleSelected, allVisibleSelected]);

  const toggleAll = () => {
    const next = { ...selectedIds };
    if (allVisibleSelected) filteredRows.forEach((r) => delete next[r.id]);
    else filteredRows.forEach((r) => { next[r.id] = true; });
    setSelectedIds(next);
  };

  // --- Action handlers ---
  const applyLocalAction = (id: string, action: RequestStatus, actionRemarks?: string) => {
    setLocalRows((cur) =>
      cur.map((row) =>
        row.id === id
          ? {
              ...row,
              status: action,
              currentApprover: action === "Approved" ? "Completed" : row.currentApprover,
              timeline: [
                ...row.timeline,
                { step: action === "Sent Back" ? "Sent Back" : action, date: new Date().toISOString().slice(0, 10), actor: "You", status: action, remarks: actionRemarks },
              ],
            }
          : row
      )
    );
  };

  const handleRowAction = async (row: RequestRow, action: "Approved" | "Rejected" | "Sent Back", inlineRemarks?: string) => {
    const finalRemarks = inlineRemarks !== undefined ? inlineRemarks : remarks;
    if ((action === "Rejected" || action === "Sent Back") && !finalRemarks.trim() && inlineRemarks === undefined) {
      setRemarksError("Remarks are required for this action.");
      return;
    }

    if (row.source === "api-leave" && row._apiLeave) {
      if (action === "Approved") {
        try {
          await approveLeave.mutate(row._apiLeave.id);
          refreshTeam();
          showToast(`${row.requestId} approved.`);
        } catch {
          showToast("Failed to approve.", "error");
        }
      } else if (action === "Rejected") {
        setApiRejectTarget(row);
        setDrawerRow(null);
        return;
      } else {
        showToast(`${row.requestId} sent back.`, "info");
      }
    } else if (row.source === "api-reg" && row.attendanceRegId) {
      try {
        if (action === "Approved") {
          await approveManagerRegularization(row.attendanceRegId, { remarks: finalRemarks });
          showToast(`${row.requestId} approved.`);
        } else if (action === "Rejected") {
          setAttendanceRejectTarget(row);
          setDrawerRow(null);
          return;
        } else {
          showToast("Send back is not supported for attendance workflow.", "info");
        }
        reloadAttendance();
      } catch (err) {
        showToast(
          err instanceof ManagerAttendanceApiError ? err.message : "Action failed.",
          "error",
        );
      }
    } else if (row.source === "api-ot" && row.attendanceOtId) {
      try {
        if (action === "Approved") {
          await approveManagerOvertime(row.attendanceOtId, {
            remarks: finalRemarks,
            approved_ot_mins: row.claimedOtMins,
          });
          showToast(`${row.requestId} approved.`);
        } else if (action === "Rejected") {
          setAttendanceRejectTarget(row);
          setDrawerRow(null);
          return;
        } else {
          showToast("Send back is not supported for attendance workflow.", "info");
        }
        reloadAttendance();
      } catch (err) {
        showToast(
          err instanceof ManagerAttendanceApiError ? err.message : "Action failed.",
          "error",
        );
      }
    } else {
      applyLocalAction(row.id, action as RequestStatus, finalRemarks);
      showToast(`Request ${row.requestId} ${action.toLowerCase()} successfully.`);
    }

    setDrawerRow(null);
    setRemarks("");
    setRemarksError("");
  };

  const handleBulkAction = async (action: "Approved" | "Rejected" | "Sent Back") => {
    const selected = allRows.filter((r) => selectedIds[r.id]);
    if (!selected.length) return;

    const actionLabel = action === "Approved" ? "approved" : action === "Rejected" ? "rejected" : "sent back";

    for (const row of selected) {
      if (row.source === "api-leave" && row._apiLeave) {
        if (action === "Approved") {
          try { await approveLeave.mutate(row._apiLeave.id); } catch { /* continue */ }
        }
      } else if (row.source === "api-reg" && row.attendanceRegId && action === "Approved") {
        try {
          await approveManagerRegularization(row.attendanceRegId, { remarks: "Bulk approve" });
        } catch { /* continue */ }
      } else if (row.source === "api-ot" && row.attendanceOtId && action === "Approved") {
        try {
          await approveManagerOvertime(row.attendanceOtId, {
            remarks: "Bulk approve",
            approved_ot_mins: row.claimedOtMins,
          });
        } catch { /* continue */ }
      } else if (row.source === "local") {
        applyLocalAction(row.id, action as RequestStatus, "Bulk action");
      }
    }
    refreshTeam();
    reloadAttendance();
    setSelectedIds({});
    showToast(`${selected.length} requests ${actionLabel} successfully.`);
  };

  const handleQuickApprove = async (row: RequestRow, e: React.MouseEvent) => {
    e.stopPropagation();
    if (row.source === "api-leave" && row._apiLeave) {
      try {
        await approveLeave.mutate(row._apiLeave.id);
        refreshTeam();
        showToast(`${row.requestId} approved.`);
      } catch {
        showToast("Failed to approve.", "error");
      }
    } else if (row.source === "api-reg" && row.attendanceRegId) {
      try {
        await approveManagerRegularization(row.attendanceRegId, { remarks: "Quick approve" });
        reloadAttendance();
        showToast(`${row.requestId} approved.`);
      } catch (err) {
        showToast(err instanceof ManagerAttendanceApiError ? err.message : "Failed to approve.", "error");
      }
    } else if (row.source === "api-ot" && row.attendanceOtId) {
      try {
        await approveManagerOvertime(row.attendanceOtId, {
          remarks: "Quick approve",
          approved_ot_mins: row.claimedOtMins,
        });
        reloadAttendance();
        showToast(`${row.requestId} approved.`);
      } catch (err) {
        showToast(err instanceof ManagerAttendanceApiError ? err.message : "Failed to approve.", "error");
      }
    } else {
      applyLocalAction(row.id, "Approved", "Approved from quick actions");
      showToast(`${row.requestId} approved.`);
    }
  };

  const handleQuickReject = (row: RequestRow, e: React.MouseEvent) => {
    e.stopPropagation();
    if (row.source === "api-leave") {
      setApiRejectTarget(row);
    } else if (row.source === "api-reg" || row.source === "api-ot") {
      setAttendanceRejectTarget(row);
    } else {
      applyLocalAction(row.id, "Rejected", "Rejected from quick actions");
      showToast(`${row.requestId} rejected.`);
    }
  };

  const openDrawer = async (row: RequestRow) => {
    setDrawerRow(row);
    if (row.source !== "api-reg" && row.source !== "api-ot") return;

    setDetailLoading(true);
    try {
      if (row.source === "api-reg" && row.attendanceRegId) {
        const detail = await fetchManagerRegularizationDetail(row.attendanceRegId);
        setDrawerRow((current) =>
          current?.id === row.id ? mergeRegularizationDetail(row, detail) : current,
        );
      } else if (row.source === "api-ot" && row.attendanceOtId) {
        const detail = await fetchManagerOvertimeDetail(row.attendanceOtId);
        setDrawerRow((current) => (current?.id === row.id ? mergeOvertimeDetail(row, detail) : current));
      }
    } catch (err) {
      showToast(
        err instanceof ManagerAttendanceApiError ? err.message : "Could not load request details.",
        "error",
      );
    } finally {
      setDetailLoading(false);
    }
  };

  const handleExport = () => {
    const csv = [
      ["Request ID", "Employee", "Category", "Request Type", "Status", "Days", "Submitted On"].join(","),
      ...filteredRows.map((r) =>
        [r.requestId, r.employeeName, r.category, r.requestType, r.status, r.daysAffected, r.submittedOn].join(",")
      ),
    ].join("\n");
    saveFile(csv, "approvals-export.csv", "text/csv");
    showToast("Exported successfully to CSV.");
  };

  const resetFilters = () => {
    setQuery("");
    setRequestType("ALL");
    setCategory("ALL");
    setStatus("ALL");
    setDepartment("ALL");
    setDateFrom("");
    setDateTo("");
    setPageNum(1);
    setShowOnlyPending(false);
  };

  const applySavedView = (view: "Pending" | "Leave" | "Attendance") => {
    resetFilters();
    setShowOnlyPending(true);
    setStatus("Pending");
    if (view === "Leave") setCategory("Leave");
    if (view === "Attendance") setCategory("Attendance");
  };

  const filtersActive = query || requestType !== "ALL" || category !== "ALL" || status !== "ALL" || department !== "ALL";

  return (
    <div className="space-y-6 pb-24">
      {/* Toast */}
      {toast && (
        <div className="fixed top-4 right-4 z-50 flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 text-sm text-foreground shadow-2xl animate-in slide-in-from-top-2">
          {toast.type === "success" && <CheckCircle2 className="h-5 w-5 text-emerald-500" />}
          {toast.type === "error" && <XCircle className="h-5 w-5 text-rose-500" />}
          {toast.type === "info" && <Info className="h-5 w-5 text-blue-500" />}
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Manage your approval requests here.</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap justify-end">
          {/* <select
            value={workflowType}
            onChange={(e) => {
              const value = e.target.value;
              if (value === "Delegate Approval Authority") {
                setDelegateFormData({ delegateName: currentDelegate.delegateName, effectiveFrom: currentDelegate.effectiveFrom, reason: "" });
                setShowDelegateModal(true);
              } else if (value === "Approval Workflow Configuration") {
                setShowWorkflowModal(true);
              }
              setWorkflowType("Multi-level approval");
            }}
            className="h-9 rounded-lg border border-border bg-card px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30"
          >
            <option value="Multi-level approval">Approval Configuration</option>
            <option value="Delegate Approval Authority">Delegate Approval Authority</option>
            <option value="Approval Workflow Configuration">Approval Workflow Configuration</option>
          </select> */}
          <Button size="sm" className="bg-foreground text-background hover:bg-foreground/90">
            Requests
          </Button>
          <Button variant="outline" size="sm" onClick={() => { setLocalRows(MOCK_REQUESTS.map((r) => ({ ...r, source: "local" as RowSource }))); refreshTeam(); reloadAttendance(); }}>
            <RefreshCw className={cn("mr-2 h-4 w-4", attendanceLoading && "animate-spin")} />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export Excel
          </Button>
        </div>
      </div>

      {attendanceError ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300">
          {attendanceError}
        </div>
      ) : null}

      {/* Filter bar */}
      <div className="rounded-lg border border-border bg-card p-2 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search employee, ID, request..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="h-10 w-full border border-border bg-background pl-9 text-sm"
            />
          </div>
          <div className="h-6 w-px bg-border hidden md:block" />
          <select value={requestType} onChange={(e) => setRequestType(e.target.value)} className="h-10 rounded-lg border border-border bg-card px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30">
            {requestTypes.map((opt) => <option key={opt} value={opt}>{opt === "ALL" ? "Type" : opt}</option>)}
          </select>
          <select value={category} onChange={(e) => setCategory(e.target.value as any)} className="h-10 rounded-lg border border-border bg-card px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30">
            <option value="ALL">Category</option>
            <option value="Attendance">Attendance</option>
            <option value="Leave">Leave</option>
            <option value="Other">Other</option>
          </select>
          {!showOnlyPending && (
            <select value={status} onChange={(e) => setStatus(e.target.value as any)} className="h-10 rounded-lg border border-border bg-card px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30">
              <option value="ALL">Status</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
              <option value="Sent Back">Sent Back</option>
            </select>
          )}
          <select value={department} onChange={(e) => setDepartment(e.target.value)} className="h-10 rounded-lg border border-border bg-card px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30 hidden sm:block">
            {departments.map((opt) => <option key={opt} value={opt}>{opt === "ALL" ? "Department" : opt}</option>)}
          </select>
          <div className="h-6 w-px bg-border hidden lg:block" />
          <div className="hidden lg:flex items-center gap-2 px-2">
            <Button variant="ghost" size="sm" className={cn("h-8 text-muted-foreground hover:text-foreground", showOnlyPending && category === "ALL" && "text-foreground font-semibold")} onClick={() => applySavedView("Pending")}>Pending</Button>
            <Button variant="ghost" size="sm" className={cn("h-8 text-muted-foreground hover:text-foreground", category === "Leave" && "text-foreground font-semibold")} onClick={() => applySavedView("Leave")}>Leave</Button>
            <Button variant="ghost" size="sm" className={cn("h-8 text-muted-foreground hover:text-foreground", category === "Attendance" && "text-foreground font-semibold")} onClick={() => applySavedView("Attendance")}>Attendance</Button>
          </div>
          {filtersActive && (
            <Button variant="ghost" size="sm" onClick={resetFilters} className="text-[#EF4444] hover:text-[#DC2626] h-8 ml-auto">
              Clear
            </Button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="space-y-4">
        {filteredRows.length > 0 && (
          <div className="flex items-center justify-between rounded-lg border border-border bg-card px-6 py-3 shadow-sm">
            <label className="flex items-center gap-3 cursor-pointer">
              <input ref={selectAllRef} type="checkbox" checked={allVisibleSelected} onChange={toggleAll} className="h-5 w-5 rounded border-border bg-background accent-primary" aria-label="Select all visible requests" />
              <span className="text-sm font-medium text-foreground">Select All</span>
              <span className="text-sm text-muted-foreground">{filteredRows.length} requests</span>
            </label>
            <span className="text-sm font-semibold text-foreground">{selectedCount} selected</span>
          </div>
        )}

        <div className="overflow-hidden rounded-xl border border-border bg-card">
          {/* Column headers — mirrors row layout exactly */}
          <div className="hidden lg:grid grid-cols-12 items-center border-b border-border bg-muted/40 px-6 py-3 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
            <div className="col-span-4 flex items-center gap-3">
              {/* spacer: checkbox w-4 + gap-3 + avatar w-10 + gap-3 */}
              <span className="w-4 shrink-0" />
              <span className="w-10 shrink-0" />
              <span>Employee</span>
            </div>
            <div className="col-span-2">Request</div>
            <div className="col-span-2">Date / Duration</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-2 text-right">Actions</div>
          </div>

          <div className="divide-y divide-border">
            {attendanceLoading && filteredRows.length === 0 ? (
              <div className="px-6 py-12 text-center text-sm text-muted-foreground">Loading attendance approvals…</div>
            ) : null}
            {filteredRows.map((row) => {
              const isSelected = !!selectedIds[row.id];
              const isApiLeave = row.source === "api-leave";
              const isApiReg = row.source === "api-reg";
              const isApiOt = row.source === "api-ot";

              return (
                <div key={row.id} className={cn("group transition-all hover:bg-muted/30", isSelected && "bg-primary/5")}>
                  <div className="grid grid-cols-1 lg:grid-cols-12 items-center px-6 py-4">

                    {/* Employee — col-span-4 to match header */}
                    <div className="col-span-4 flex items-start gap-3 min-w-0">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => { e.stopPropagation(); setSelectedIds((c) => ({ ...c, [row.id]: e.target.checked })); }}
                        onClick={(e) => e.stopPropagation()}
                        className="mt-1 h-4 w-4 rounded border-border bg-background accent-primary"
                      />
                      <img src={row.photoUrl} alt={row.employeeName} className="h-10 w-10 rounded-full border border-border object-cover shrink-0" />
                      <div className="min-w-0 cursor-pointer" onClick={() => void openDrawer(row)}>
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-semibold text-foreground truncate">{row.employeeName}</p>
                          {isApiLeave && (
                            <span className="shrink-0 rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold text-blue-700 dark:bg-blue-900 dark:text-blue-300">Leave</span>
                          )}
                          {isApiReg && (
                            <span className="shrink-0 rounded-full bg-indigo-100 px-2 py-0.5 text-[10px] font-semibold text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300">Regularization</span>
                          )}
                          {isApiOt && (
                            <span className="shrink-0 rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-semibold text-violet-700 dark:bg-violet-900 dark:text-violet-300">Overtime</span>
                          )}
                        </div>
                        <div className="flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
                          <span>{row.employeeId}</span>
                          {row.department !== "—" && <><span>•</span><span>{row.department}</span></>}
                        </div>
                        <p className="mt-1 text-xs text-muted-foreground line-clamp-1">"{row.reason}"</p>
                      </div>
                    </div>

                    {/* Request type */}
                    <div className="col-span-2 flex flex-wrap gap-2">
                      {isApiLeave && row.leaveTypeCode ? (
                        <div className="flex items-center gap-2">
                          <LeaveTypePill code={row.leaveTypeCode} />
                          <span className="text-sm text-foreground">{row.leaveTypeName}</span>
                        </div>
                      ) : (
                        <span className={cn("inline-flex rounded-md px-2 py-1 text-[11px] font-medium", TYPE_COLORS[row.requestType] || TYPE_COLORS.default)}>
                          {row.requestType}
                        </span>
                      )}
                    </div>

                    {/* Date / duration */}
                    <div className="col-span-2 text-sm">
                      {isApiLeave && row.fromDate ? (
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-1 text-muted-foreground">
                            <CalendarDays className="h-3.5 w-3.5" />
                            <span>{formatLeaveShortDate(row.fromDate)}</span>
                            {row.toDate && row.toDate !== row.fromDate && (
                              <><span>→</span><span>{formatLeaveShortDate(row.toDate)}</span></>
                            )}
                          </div>
                          <p className="text-xs font-semibold tabular-nums text-foreground">{row.daysAffected} day{row.daysAffected !== 1 ? "s" : ""}</p>
                        </div>
                      ) : (
                        <div>
                          <div className="flex items-center gap-1 text-foreground">
                            <CalendarDays className="h-3.5 w-3.5 text-muted-foreground" />
                            {row.daysAffected > 0 ? `${row.daysAffected} day(s)` : formatDate(row.requestDate)}
                          </div>
                          {row.waitingDays > 0 && row.status === "Pending" && (
                            <div className="mt-1 flex items-center gap-1 text-xs text-[#DC2626]">
                              <Clock className="h-3 w-3" />
                              {row.waitingDays}d wait
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Status */}
                    <div className="col-span-2">
                      {isApiLeave && row._apiLeave ? (
                        <EmployeeLeaveStatusBadge status={row._apiLeave.status} />
                      ) : (
                        <span className={cn("inline-flex rounded-md px-2 py-1 text-[11px] font-medium", STATUS_STYLES[row.status])}>
                          {row.status}
                        </span>
                      )}
                      <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                        {row.attachments.length > 0 && <div className="flex items-center gap-1"><Paperclip className="h-3.5 w-3.5" />{row.attachments.length}</div>}
                        {row.commentsCount > 0 && <div className="flex items-center gap-1"><MessageSquare className="h-3.5 w-3.5" />{row.commentsCount}</div>}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="col-span-2 flex items-center justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8"
                        onClick={() => void openDrawer(row)}
                      >
                        Details
                      </Button>

                      {row.status === "Pending" && (
                        <>
                          <Button
                            size="sm"
                            className="h-8 bg-red-500 px-3 text-white hover:bg-red-600"
                            onClick={(e) => handleQuickReject(row, e)}
                          >
                            Reject
                          </Button>

                          <Button
                            size="sm"
                            className="h-8 bg-emerald-500 px-3 text-white hover:bg-emerald-600"
                            onClick={(e) => handleQuickApprove(row, e)}
                          >
                            Approve
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {filteredRows.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-card py-24 text-center shadow-sm">
            <div className="rounded-full bg-[#10B981] p-4 text-white">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-foreground">You're all caught up!</h3>
            <p className="mt-1 text-sm text-muted-foreground">No requests match these filters.</p>
            <Button variant="outline" className="mt-6" onClick={resetFilters}>Clear Filters</Button>
          </div>
        )}
      </div>

      {/* Bulk action bar */}
      {selectedCount > 0 && (
        <div className="fixed bottom-6 left-1/2 z-40 flex w-[calc(100%-2rem)] max-w-4xl -translate-x-1/2 flex-wrap items-center gap-3 rounded-lg border border-border bg-card px-5 py-3 shadow-2xl animate-in slide-in-from-bottom-5">
          <span className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <span className="flex h-6 min-w-6 items-center justify-center rounded-full bg-primary px-2 text-xs text-primary-foreground">{selectedCount}</span>
            {selectedCount} {selectedCount === 1 ? "request" : "requests"} selected
          </span>
          <div className="h-5 w-px bg-border" />
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm" className="bg-[#10B981] text-white hover:bg-[#059669]" onClick={() => handleBulkAction("Approved")}>
              <ThumbsUp className="mr-2 h-4 w-4" /> Approve Selected
            </Button>
            <Button size="sm" className="bg-[#EF4444] text-white hover:bg-[#DC2626]" onClick={() => handleBulkAction("Rejected")}>
              <ThumbsDown className="mr-2 h-4 w-4" /> Reject Selected
            </Button>
            <Button size="sm" className="bg-[#3B82F6] text-white hover:bg-[#2563EB]" onClick={() => handleBulkAction("Sent Back")}>
              <CornerUpLeft className="mr-2 h-4 w-4" /> Send Back Selected
            </Button>
            <Button variant="outline" size="sm" onClick={() => setSelectedIds({})}>Clear Selection</Button>
          </div>
        </div>
      )}

      {/* Detail drawer */}
      <Drawer open={!!drawerRow} onOpenChange={(open) => { if (!open) { setDrawerRow(null); setRemarks(""); setRemarksError(""); } }}>
        <DrawerContent className="w-full sm:w-[500px] md:w-[600px] border-l border-border bg-background text-foreground">
          <DrawerHeader className="border-b border-border bg-card sticky top-0 z-20 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <DrawerTitle className="text-lg font-semibold text-foreground">Request Details</DrawerTitle>
                <DrawerDescription className="text-xs text-muted-foreground mt-1">{drawerRow?.requestId}</DrawerDescription>
              </div>
              <DrawerClose asChild>
                <button className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground">
                  <X className="h-5 w-5" />
                </button>
              </DrawerClose>
            </div>
          </DrawerHeader>

          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            {detailLoading ? (
              <p className="text-sm text-muted-foreground">Loading full request details…</p>
            ) : null}
            {/* Employee snapshot */}
            <section className="flex items-center gap-4">
              <img src={drawerRow?.photoUrl} alt="Avatar" className="h-16 w-16 rounded-full border border-border object-cover bg-secondary" />
              <div>
                <h2 className="text-xl font-semibold text-foreground">{drawerRow?.employeeName}</h2>
                {drawerRow?.designation !== "—" && (
                  <p className="text-sm text-muted-foreground mt-0.5">{drawerRow?.designation} • {drawerRow?.department}</p>
                )}
                <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><User className="h-3.5 w-3.5" /> {drawerRow?.employeeId}</span>
                  {drawerRow?.reportingTo !== "—" && (
                    <span className="flex items-center gap-1"><Building className="h-3.5 w-3.5" /> Reports to {drawerRow?.reportingTo}</span>
                  )}
                </div>
              </div>
            </section>

            {/* Request summary */}
            <section className="rounded-lg border border-border bg-card p-5">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
                <FileText className="h-4 w-4" /> Request Summary
              </h3>
              <div className="grid grid-cols-2 gap-y-4 gap-x-8 mb-5">
                <div>
                  <p className="text-xs text-muted-foreground">Type</p>
                  <div className="mt-1 flex items-center gap-2">
                    {drawerRow?.source === "api-leave" && drawerRow.leaveTypeCode ? (
                      <><LeaveTypePill code={drawerRow.leaveTypeCode} /><span className="text-sm font-medium text-foreground">{drawerRow.leaveTypeName}</span></>
                    ) : (
                      <span className={cn("inline-flex rounded-md px-2 py-1 text-[11px] font-medium", TYPE_COLORS[drawerRow?.requestType ?? ""] || TYPE_COLORS.default)}>
                        {drawerRow?.requestType}
                      </span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Dates / Duration</p>
                  <p className="text-sm font-medium text-foreground mt-1">
                    {drawerRow?.source === "api-leave" && drawerRow.fromDate
                      ? `${formatLeaveDate(drawerRow.fromDate)}${drawerRow.toDate && drawerRow.toDate !== drawerRow.fromDate ? ` — ${formatLeaveDate(drawerRow.toDate)}` : ""} · ${drawerRow.daysAffected} day${drawerRow.daysAffected !== 1 ? "s" : ""}`
                      : drawerRow?.daysAffected
                      ? `${formatDate(drawerRow.effectiveDate)} (${drawerRow.daysAffected} days)`
                      : drawerRow ? formatDate(drawerRow.effectiveDate) : "—"}
                  </p>
                </div>
                <div className="col-span-2">
                  <p className="text-xs text-muted-foreground">Reason</p>
                  <p className="text-sm text-foreground mt-1 leading-relaxed bg-secondary/60 p-3 rounded-lg border border-border">{drawerRow?.reason}</p>
                </div>
              </div>
              {drawerRow?.attachments && drawerRow.attachments.length > 0 && (
                <div>
                  <p className="text-xs text-muted-foreground mb-2">Attachments</p>
                  <div className="flex flex-wrap gap-2">
                    {drawerRow.attachments.map((att) => (
                      <a key={att} href="#" className="inline-flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2 text-xs font-semibold text-[#2563EB] hover:bg-secondary/80">
                        <Paperclip className="h-3.5 w-3.5" /> {att}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </section>

            {/* Context */}
            <section className="rounded-lg border border-border bg-card p-5">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
                <Info className="h-4 w-4" /> Context Information
              </h3>
              <div className="grid gap-3 text-sm">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 rounded-full bg-[#3B82F6] p-1 text-white"><CalendarDays className="h-4 w-4" /></div>
                  <div><p className="font-medium text-foreground">Existing Data</p><p className="text-muted-foreground mt-0.5">{drawerRow?.existingData}</p></div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 rounded-full bg-[#10B981] p-1 text-white"><Calendar className="h-4 w-4" /></div>
                  <div><p className="font-medium text-foreground">Balance</p><p className="text-muted-foreground mt-0.5">{drawerRow?.leaveBalance}</p></div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 rounded-full bg-[#7C3AED] p-1 text-white"><RefreshCw className="h-4 w-4" /></div>
                  <div><p className="font-medium text-foreground">Previous Requests</p><p className="text-muted-foreground mt-0.5">{drawerRow?.previousRequests}</p></div>
                </div>
              </div>
            </section>

            {/* Timeline */}
            <section className="rounded-lg border border-border bg-card p-5">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
                <Clock className="h-4 w-4" /> Timeline
              </h3>
              <div className="relative pl-4 border-l border-border space-y-6">
                {drawerRow?.timeline.map((step, idx) => (
                  <div key={idx} className="relative">
                    <div className={cn("absolute -left-[21px] flex h-2.5 w-2.5 items-center justify-center rounded-full border-2 border-background",
                      step.status === "Approved" ? "bg-emerald-500" : step.status === "Rejected" ? "bg-rose-500" : step.status === "Pending" ? "bg-amber-500" : "bg-muted-foreground"
                    )} />
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-foreground">{step.step}</p>
                      <span className="text-xs text-muted-foreground">{step.date}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{step.actor}</p>
                    {step.remarks && (
                      <div className="mt-2 rounded-md bg-secondary/60 p-2 text-xs text-foreground border border-border italic">"{step.remarks}"</div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Decision panel */}
          {drawerRow?.status === "Pending" ? (
            <DrawerFooter className="border-t border-border bg-card p-6 flex-col gap-4">
              <div className="w-full">
                <textarea
                  value={remarks}
                  onChange={(e) => { setRemarks(e.target.value); setRemarksError(""); }}
                  rows={2}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary focus:ring-2 focus:ring-primary/30 resize-none"
                  placeholder="Add remarks before taking action (optional for approve)..."
                />
                {remarksError && <p className="mt-1 text-xs font-semibold text-[#EF4444] flex items-center gap-1"><AlertCircle className="h-3 w-3" /> {remarksError}</p>}
              </div>
              <div className="flex items-center gap-3 w-full">
                {drawerRow.source === "local" && (
                  <Button className="flex-1 bg-[#3B82F6] text-white hover:bg-[#2563EB]" onClick={() => drawerRow && handleRowAction(drawerRow, "Sent Back")}>
                    <CornerUpLeft className="mr-2 h-4 w-4" /> Send Back
                  </Button>
                )}
                <Button variant="destructive" className="flex-1 bg-[#EF4444] text-white hover:bg-[#DC2626] border-none" onClick={() => drawerRow && handleRowAction(drawerRow, "Rejected")}>
                  <ThumbsDown className="mr-2 h-4 w-4" /> Reject
                </Button>
                <Button className="flex-1 bg-[#10B981] text-white hover:bg-[#059669]" onClick={() => drawerRow && handleRowAction(drawerRow, "Approved")}>
                  <ThumbsUp className="mr-2 h-4 w-4" /> Approve
                </Button>
              </div>
            </DrawerFooter>
          ) : (
            <DrawerFooter className="border-t border-border bg-card p-6">
              <div className="flex items-center justify-between w-full p-3 rounded-lg bg-secondary/60 border border-border">
                <div>
                  <p className="text-sm font-medium text-foreground">Request Closed</p>
                  <p className="text-xs text-muted-foreground mt-0.5">Current status: {drawerRow?.status}</p>
                </div>
                <span className={cn("inline-flex rounded-md px-3 py-1.5 text-xs font-semibold", STATUS_STYLES[drawerRow?.status as RequestStatus])}>
                  {drawerRow?.status}
                </span>
              </div>
            </DrawerFooter>
          )}
        </DrawerContent>
      </Drawer>

      {/* API leave reject dialog */}
      {apiRejectTarget && (
        <ApiLeaveRejectDialog
          row={apiRejectTarget}
          onClose={() => setApiRejectTarget(null)}
          onDone={() => {
            setApiRejectTarget(null);
            refreshTeam();
            showToast(`${apiRejectTarget.requestId} rejected.`);
          }}
        />
      )}

      {attendanceRejectTarget && (
        <ApiAttendanceRejectDialog
          row={attendanceRejectTarget}
          onClose={() => setAttendanceRejectTarget(null)}
          onDone={() => {
            setAttendanceRejectTarget(null);
            reloadAttendance();
            showToast(`${attendanceRejectTarget.requestId} rejected.`);
          }}
        />
      )}

      {/* Delegate modal */}
      {showDelegateModal && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center animate-in fade-in">
          <div className="bg-card border border-border rounded-lg w-full max-w-md mx-4 shadow-2xl animate-in slide-in-from-bottom-5">
            <div className="border-b border-border bg-card px-6 py-4">
              <h2 className="text-lg font-semibold text-foreground">Delegate Approval Authority</h2>
              <p className="text-xs text-muted-foreground mt-1">Assign your approvals to another manager during your absence.</p>
            </div>
            <div className="portal-page admin-dashboard">
              <div className="rounded-lg border border-border bg-background p-4">
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Current Delegate</p>
                <div className="space-y-2">
                  <div><p className="text-xs text-muted-foreground">Name</p><p className="text-sm font-medium text-foreground mt-1">{currentDelegate.delegateName}</p></div>
                  <div><p className="text-xs text-muted-foreground">Effective From</p><p className="text-sm font-medium text-foreground mt-1">{formatDate(currentDelegate.effectiveFrom)}</p></div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-foreground">Edit Delegate</h3>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Delegate To *</label>
                  <select value={delegateFormData.delegateName} onChange={(e) => setDelegateFormData({ ...delegateFormData, delegateName: e.target.value })} className="mt-2 w-full h-9 rounded-lg border border-border bg-background px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30">
                    <option value="Priya Patel">Priya Patel - Manager</option>
                    <option value="Rohit Sharma">Rohit Sharma - Manager</option>
                    <option value="Radha Singh">Radha Singh - Manager</option>
                    <option value="Riya Menon">Riya Menon - Manager</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Effective From *</label>
                  <input type="date" value={delegateFormData.effectiveFrom} onChange={(e) => setDelegateFormData({ ...delegateFormData, effectiveFrom: e.target.value })} className="mt-2 w-full h-9 rounded-lg border border-border bg-background px-3 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Reason (Optional)</label>
                  <textarea value={delegateFormData.reason} onChange={(e) => setDelegateFormData({ ...delegateFormData, reason: e.target.value })} rows={3} placeholder="E.g., On leave, medical emergency, etc." className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-primary/30 resize-none" />
                </div>
              </div>
            </div>
            <div className="border-t border-border bg-card px-6 py-4 flex items-center gap-3 justify-end">
              <Button variant="outline" size="sm" onClick={() => setShowDelegateModal(false)}>Cancel</Button>
              <Button size="sm" className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={() => {
                setCurrentDelegate({ delegateName: delegateFormData.delegateName, effectiveFrom: delegateFormData.effectiveFrom, reason: delegateFormData.reason || currentDelegate.reason });
                showToast(`Delegation updated to ${delegateFormData.delegateName}`, "success");
                setShowDelegateModal(false);
              }}>Save Changes</Button>
            </div>
          </div>
        </div>
      )}

      {/* Workflow modal */}
      {showWorkflowModal && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center animate-in fade-in">
          <div className="bg-card border border-border rounded-lg w-full max-w-2xl mx-4 shadow-2xl max-h-[80vh] overflow-y-auto animate-in slide-in-from-bottom-5">
            <div className="border-b border-border bg-card px-6 py-4 sticky top-0">
              <h2 className="text-lg font-semibold text-foreground">Approval Workflow Configuration</h2>
              <p className="text-xs text-muted-foreground mt-1">Workflow configured by admin — Read only view</p>
            </div>
            <div className="portal-page admin-dashboard">
              <div className="rounded-lg border border-border bg-background p-4">
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">Workflow Type</p>
                <p className="text-sm font-medium text-foreground">Multi-level Approval</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">Approval Steps</p>
                <div className="space-y-3">
                  {[
                    { step: 1, level: "Manager Review", approvers: "Direct Manager", duration: "2 days", condition: "Auto-escalate if not approved" },
                    { step: 2, level: "HR Review", approvers: "HR Manager", duration: "1 day", condition: "Parallel review" },
                    { step: 3, level: "Finance Sign-off", approvers: "Finance Lead", duration: "1 day", condition: "For leave requests > 5 days" },
                  ].map((item) => (
                    <div key={item.step} className="relative pl-8 pb-4 border-l-2 border-primary/30">
                      <div className="absolute -left-[13px] top-0 h-6 w-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-semibold">{item.step}</div>
                      <div>
                        <h4 className="text-sm font-semibold text-foreground">{item.level}</h4>
                        <div className="mt-2 space-y-1 text-xs text-muted-foreground">
                          <p><span className="font-medium text-foreground">Approvers:</span> {item.approvers}</p>
                          <p><span className="font-medium text-foreground">SLA:</span> {item.duration}</p>
                          <p><span className="font-medium text-foreground">Condition:</span> {item.condition}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-lg border border-border bg-background p-4">
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Auto-Approval Rules</p>
                <ul className="space-y-2 text-sm text-foreground">
                  <li className="flex items-center gap-2"><span className="text-emerald-500">✓</span> Leave ≤ 1 day: Auto-approve if balance available</li>
                  <li className="flex items-center gap-2"><span className="text-emerald-500">✓</span> Attendance: Manual review required</li>
                  <li className="flex items-center gap-2"><span className="text-amber-500">⊘</span> Escalation: Yes, after 3 days pending</li>
                </ul>
              </div>
              <div className="rounded-lg border border-border bg-background p-4">
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Notifications</p>
                <ul className="space-y-1 text-xs text-muted-foreground">
                  <li>• Email notification on new approval request</li>
                  <li>• Reminder on SLA breach (1 day before)</li>
                  <li>• SMS alert for High priority requests</li>
                </ul>
              </div>
            </div>
            <div className="border-t border-border bg-card px-6 py-4 sticky bottom-0">
              <p className="text-xs text-muted-foreground mb-3">To edit workflow configuration, contact your administrator.</p>
              <Button size="sm" className="w-full" onClick={() => setShowWorkflowModal(false)}>Close</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}