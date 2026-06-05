import { useMemo, useState } from "react";
import { Download, Search } from "lucide-react";
import { Input } from "../../../../components/ui/input";
import { useAdminLeaveRequestsStore } from "../../../../modules/adminLeave/store";
import type {
  AdminLeaveRequestRow,
  LeaveCategory,
  LeaveRequestStatus,
} from "../../../../modules/adminLeave/types";
import { AdminLeaveRequestDrawer } from "./components/AdminLeaveRequestDrawer";

const STATUS_OPTIONS: Array<
  LeaveRequestStatus | "ALL"
> = [
  "ALL",
  "PENDING",
  "SUBMITTED",
  "DRAFT",
  "APPROVED",
  "REJECTED",
  "CANCELLED",
  "REVOKED",
];

const CATEGORY_OPTIONS: Array<LeaveCategory | "ALL"> = [
  "ALL",
  "LEAVE",
  "COMP_OFF",
  "SHORT_LEAVE",
  "OUT_DUTY",
  "WFH",
  "GATE_PASS",
  "OVERTIME",
];

function categoryLabel(value: LeaveCategory | "ALL") {
  if (value === "ALL") return "All Leave Types";
  return value.replaceAll("_", " ");
}

function StatusPill({
  status,
}: {
  status: LeaveRequestStatus;
}) {
  const statusColors: Record<LeaveRequestStatus, { bg: string; text: string; border: string }> = {
    "APPROVED": { bg: "bg-green-500/10", text: "text-green-600", border: "border-green-200" },
    "REJECTED": { bg: "bg-red-500/10", text: "text-red-600", border: "border-red-200" },
    "SUBMITTED": { bg: "bg-blue-500/10", text: "text-blue-600", border: "border-blue-200" },
    "DRAFT": { bg: "bg-amber-500/10", text: "text-amber-600", border: "border-amber-200" },
    "CANCELLED": { bg: "bg-gray-500/10", text: "text-gray-600", border: "border-gray-200" },
    "REVOKED": { bg: "bg-red-500/10", text: "text-red-600", border: "border-red-200" },
  };
  
  const colors = statusColors[status] || { bg: "bg-secondary", text: "text-muted-foreground", border: "border-border" };
  
  return (
    <span className={`text-[10px] font-bold px-2.5 py-1.5 rounded-lg border uppercase tracking-wide ${colors.bg} ${colors.text} ${colors.border}`}>
      {status}
    </span>
  );
}

export function SuperadminLeaveRequests({
  title = "Leave Applications",
  defaultCategory = "ALL",
}: {
  title?: string;
  defaultCategory?: LeaveCategory | "ALL";
}) {
  const { activeRows, deletedRows, runAction } =
    useAdminLeaveRequestsStore();

  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<
    LeaveRequestStatus | "ALL"
  >("ALL");

  const [category, setCategory] = useState<
    LeaveCategory | "ALL"
  >(defaultCategory);

  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const [selected, setSelected] = useState<
    Record<string, boolean>
  >({});

  const [drawerRow, setDrawerRow] =
    useState<AdminLeaveRequestRow | null>(null);

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();

    return activeRows.filter((r) => {
      const normalizedCategory =
        r.category ??
        (r.leave_type.code === "SHL"
          ? "SHORT_LEAVE"
          : r.leave_type.code === "CO"
          ? "COMP_OFF"
          : r.leave_type.code === "OD"
          ? "OUT_DUTY"
          : r.leave_type.code === "WFH"
          ? "WFH"
          : r.leave_type.code === "GP"
          ? "GATE_PASS"
          : r.leave_type.code === "OT"
          ? "OVERTIME"
          : "LEAVE");

      const statusOk =
        status === "ALL"
          ? true
          : status === "PENDING"
          ? r.status === "SUBMITTED"
          : r.status === status;

      const leaveTypeCode =
        r.leave_type.code.toUpperCase();

      const leaveTypeName = r.leave_type.name
        .toUpperCase()
        .replaceAll(" ", "_");

      const categoryOk =
        category === "ALL" ||
        normalizedCategory === category ||
        leaveTypeName === category ||
        (category === "SHORT_LEAVE" &&
          (leaveTypeCode === "SHL" ||
            leaveTypeName.includes("SHORT"))) ||
        (category === "COMP_OFF" &&
          (leaveTypeCode === "CO" ||
            leaveTypeName.includes("COMP"))) ||
        (category === "OUT_DUTY" &&
          (leaveTypeCode === "OD" ||
            leaveTypeName.includes("OUT_DUTY"))) ||
        (category === "GATE_PASS" &&
          (leaveTypeCode === "GP" ||
            leaveTypeName.includes("GATE_PASS"))) ||
        (category === "WFH" &&
          (leaveTypeCode === "WFH" ||
            leaveTypeName.includes("WFH"))) ||
        (category === "OVERTIME" &&
          (leaveTypeCode === "OT" ||
            leaveTypeName.includes("OVERTIME")));

      const queryOk =
        !q ||
        r.employee.employee_name
          .toLowerCase()
          .includes(q) ||
        r.employee.employee_code
          .toLowerCase()
          .includes(q) ||
        r.employee.department
          .toLowerCase()
          .includes(q) ||
        (r.employee.designation ?? "")
          .toLowerCase()
          .includes(q) ||
        r.leave_type.name.toLowerCase().includes(q);

      let dateOk = true;

      if (dateFrom || dateTo) {
        if (dateFrom && !dateTo)
          dateOk = r.to_date >= dateFrom;
        else if (!dateFrom && dateTo)
          dateOk = r.from_date <= dateTo;
        else if (dateFrom && dateTo)
          dateOk =
            r.to_date >= dateFrom &&
            r.from_date <= dateTo;
      }

      return (
        statusOk &&
        categoryOk &&
        queryOk &&
        dateOk
      );
    });
  }, [
    activeRows,
    category,
    dateFrom,
    dateTo,
    query,
    status,
  ]);

  const allSelected =
    rows.length > 0 &&
    rows.every((r) => selected[r.id]);

  const selectedRows = rows.filter(
    (r) => selected[r.id]
  );

  const toggleSelectAll = (
    checked: boolean
  ) => {
    if (checked) {
      const updated: Record<string, boolean> = {};

      rows.forEach((r) => {
        updated[r.id] = true;
      });

      setSelected(updated);
    } else {
      setSelected({});
    }
  };

  const bulkAction = (
    action: "APPROVE" | "REJECT" | "DELETE"
  ) => {
    selectedRows.forEach((r) =>
      runAction(
        r.id,
        action,
        {
          name: "Superadmin",
          role: "superadmin",
        },
        "Bulk action from superadmin console"
      )
    );

    setSelected({});
  };

  return (
    <div className="space-y-6">
      <div className="dashboard-widget flex flex-col overflow-hidden">

        {/* Header */}
        <div className="px-6 py-5 border-b border-border/50 flex flex-col lg:flex-row lg:items-center gap-3 justify-between bg-secondary/20">
          <div>
            <h2 className="text-base font-bold text-foreground uppercase tracking-tight">
              {title}
            </h2>
            <p className="text-xs text-muted-foreground mt-1 font-semibold">View and manage all leave requests</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              className="px-4 py-2.5 rounded-lg text-xs font-bold bg-primary text-primary-foreground inline-flex items-center gap-2 hover:opacity-90 transition-opacity shadow-lg shadow-primary/20 uppercase tracking-wide"
              onClick={() => {
                const blob = new Blob(
                  [JSON.stringify(rows, null, 2)],
                  { type: "application/json" }
                );

                const url =
                  URL.createObjectURL(blob);

                const a =
                  document.createElement("a");

                a.href = url;
                a.download =
                  "superadmin-leave-applications.json";

                a.click();

                URL.revokeObjectURL(url);
              }}
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="px-6 py-5 border-b border-border/50 bg-background/30">
          <div className="flex flex-wrap xl:flex-nowrap items-end gap-4 w-full">

            {/* Search */}
            <div className="relative flex-1 min-w-[280px]">
              <Search className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />

              <Input
                value={query}
                onChange={(e) =>
                  setQuery(e.target.value)
                }
                className="pl-9 h-10 text-sm font-medium border-border rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/30"
                placeholder="Search by employee, id, department, designation, leave type"
              />
            </div>

            {/* Status */}
            <div className="min-w-[180px]">
              <label className="text-[10px] font-bold uppercase tracking-wide text-muted-foreground mb-2 block">All Status</label>
              <select
                value={status}
                onChange={(e) =>
                  setStatus(
                    e.target.value as
                      | LeaveRequestStatus
                      | "ALL"
                      | "PENDING"
                  )
                }
                className="w-full h-10 px-3 py-2 text-sm font-medium bg-card border border-border rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all outline-none cursor-pointer"
              >
                {STATUS_OPTIONS.map((v) => (
                  <option key={v} value={v}>
                    {v === "ALL"
                      ? "All Status"
                      : v === "PENDING"
                      ? "PENDING"
                      : v}
                  </option>
                ))}
              </select>
            </div>

            {/* Category */}
            <div className="min-w-[180px]">
              <label className="text-[10px] font-bold uppercase tracking-wide text-muted-foreground mb-2 block">All Leave Types</label>
              <select
                value={category}
                onChange={(e) =>
                  setCategory(
                    e.target.value as
                      | LeaveCategory
                      | "ALL"
                  )
                }
                className="w-full h-10 px-3 py-2 text-sm font-medium bg-card border border-border rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all outline-none cursor-pointer"
              >
                {CATEGORY_OPTIONS.map((v) => (
                  <option key={v} value={v}>
                    {categoryLabel(v)}
                  </option>
                ))}
              </select>
            </div>

            {/* From Date */}
            <div className="min-w-[170px]">
              <label className="text-[10px] font-bold uppercase tracking-wide text-muted-foreground mb-2 block">
                From Date
              </label>

              <input
                type="date"
                value={dateFrom}
                onChange={(e) => {
                  const v = e.target.value;

                  setDateFrom(v);

                  if (
                    v &&
                    dateTo &&
                    dateTo < v
                  ) {
                    setDateTo(v);
                  }
                }}
                className="w-full h-10 px-3 py-2 text-sm font-medium bg-card border border-border rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all outline-none cursor-pointer"
              />
            </div>

            {/* To Date */}
            <div className="min-w-[170px]">
              <label className="text-[10px] font-bold uppercase tracking-wide text-muted-foreground mb-2 block">
                To Date
              </label>

              <input
                type="date"
                value={dateTo}
                min={dateFrom || undefined}
                onChange={(e) => {
                  const v = e.target.value;

                  if (!v) {
                    setDateTo("");
                    return;
                  }

                  if (
                    dateFrom &&
                    v < dateFrom
                  ) {
                    setDateTo(dateFrom);
                    return;
                  }

                  setDateTo(v);
                }}
                className="w-full h-10 px-3 py-2 text-sm font-medium bg-card border border-border rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all outline-none cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Bulk Actions */}
        <div className="px-6 py-4 border-b border-border/50 bg-secondary/40 flex flex-wrap items-center justify-between gap-4">

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={(e) =>
                toggleSelectAll(
                  e.target.checked
                )
              }
              className="h-4 w-4 rounded border border-border cursor-pointer"
            />

            <p className="text-xs font-bold text-foreground uppercase tracking-wide">
              {selectedRows.length} selected
            </p>
          </div>

          <div className="flex flex-wrap gap-2">

            <button
              disabled={!selectedRows.length}
              onClick={() =>
                bulkAction("APPROVE")
              }
              className="px-4 py-2 rounded-lg text-xs font-bold bg-green-500/10 text-green-600 border border-green-200 disabled:opacity-30 hover:bg-green-500/20 transition-colors uppercase tracking-wide"
            >
              Approve
            </button>

            <button
              disabled={!selectedRows.length}
              onClick={() =>
                bulkAction("REJECT")
              }
              className="px-4 py-2 rounded-lg text-xs font-bold bg-red-500/10 text-red-600 border border-red-200 disabled:opacity-30 hover:bg-red-500/20 transition-colors uppercase tracking-wide"
            >
              Reject
            </button>

            <button
              disabled={!selectedRows.length}
              onClick={() =>
                bulkAction("DELETE")
              }
              className="px-4 py-2 rounded-lg text-xs font-bold bg-destructive/10 text-destructive border border-destructive/20 disabled:opacity-30 hover:bg-destructive/20 transition-colors uppercase tracking-wide"
            >
              Delete
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left">

            <thead className="bg-secondary/50 border-b border-border/50 sticky top-0">
              <tr>
                {[
                  "checkbox",
                  "Employee",
                  "Employee ID",
                  "Department",
                  "Designation",
                  "Leave Type",
                  "From",
                  "To",
                  "Days",
                  "Applied On",
                  "Status",
                  "Approver",
                  "Priority",
                  "Workflow Stage",
                ].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest whitespace-nowrap bg-secondary/30"
                  >
                    {h === "checkbox" ? (
                      <input
                        type="checkbox"
                        checked={allSelected}
                        onChange={(e) =>
                          toggleSelectAll(
                            e.target.checked
                          )
                        }
                        className="h-4 w-4 rounded border-border"
                      />
                    ) : (
                      h
                    )}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody className="divide-y divide-border/40">
              {rows.map((r) => (
                <tr
                  key={r.id}
                  className="hover:bg-secondary/20 cursor-pointer transition-colors"
                  onClick={() => setDrawerRow(r)}
                >

                  {/* Checkbox */}
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={!!selected[r.id]}
                      onClick={(e) => e.stopPropagation()}
                      onChange={(e) =>
                        setSelected((prev) => ({
                          ...prev,
                          [r.id]: e.target.checked,
                        }))
                      }
                      className="h-4 w-4 rounded border-border cursor-pointer"
                    />
                  </td>

                  <td
                    className="px-4 py-3 text-sm font-bold text-foreground cursor-pointer"
                  >
                    {r.employee.employee_name}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.employee.employee_code}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.employee.department}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.employee.designation ??
                      "—"}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.leave_type.name}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.from_date}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.to_date}
                  </td>

                  <td className="px-4 py-3 text-sm font-semibold text-foreground">
                    {r.total_days}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.applied_on}
                  </td>

                  <td className="px-4 py-3">
                    <StatusPill
                      status={r.status}
                    />
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.current_approver ??
                      "—"}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.priority ?? "—"}
                  </td>

                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {r.workflow_stage ??
                      "—"}
                  </td>
                </tr>
              ))}

              {rows.length === 0 && (
                <tr>
                  <td
                    colSpan={14}
                    className="px-4 py-10 text-center text-sm text-muted-foreground"
                  >
                    No matching records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Deleted Requests */}
      {deletedRows.length > 0 && (
        <div className="flat-card bg-card p-5">
          <h3 className="text-sm font-semibold text-foreground">
            Restore Deleted Requests
          </h3>

          <div className="mt-3 flex flex-wrap gap-2">
            {deletedRows
              .slice(0, 8)
              .map((r) => (
                <button
                  key={r.id}
                  onClick={() =>
                    runAction(
                      r.id,
                      "RESTORE",
                      {
                        name: "Superadmin",
                        role: "superadmin",
                      },
                      "Restored from trash"
                    )
                  }
                  className="px-3 py-2 rounded-lg text-xs font-semibold bg-secondary border border-border"
                >
                  Restore{" "}
                  {
                    r.employee
                      .employee_code
                  }{" "}
                  ({r.leave_type.code})
                </button>
              ))}
          </div>
        </div>
      )}

      <AdminLeaveRequestDrawer
        row={drawerRow}
        open={!!drawerRow}
        onOpenChange={(o) =>
          !o && setDrawerRow(null)
        }
      />
    </div>
  );
}