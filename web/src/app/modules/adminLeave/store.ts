import { useCallback, useEffect, useMemo, useState } from "react";
import { useAdminLeaveApplications, type AdminLeaveApplicationApiRow } from "./useAdminLeave";
import { ADMIN_LEAVE_REQUESTS } from "./mock";
import type { AdminActorRole, AdminLeaveRequestRow, LeaveRequestStatus } from "./types";
import type { LeaveApplicationAPI } from "../leaves/types";
import { DEMO_APPLICATIONS } from "../leaves/demoData";
import { readStore, writeStore } from "../leaves/storage";

const REQUESTS_KEY = "hrms-admin-superadmin-leave-requests-v1";
const LEAVE_APP_KEY = "hrms-demo-leave-applications";

function mapCategoryFromLeave(app: AdminLeaveSource): AdminLeaveRequestRow["category"] {
  const code = "leave_type_detail" in app
    ? app.leave_type_detail?.code?.toUpperCase() ?? ""
    : app.leave_type_id?.toUpperCase() ?? "";
  if (code === "CO") return "COMP_OFF";
  if (code === "SHL") return "SHORT_LEAVE";
  if (code === "OD") return "OUT_DUTY";
  if (code === "WFH") return "WFH";
  if (code === "GP") return "GATE_PASS";
  if (code === "OT") return "OVERTIME";
  return "LEAVE";
}

function mapLeaveAppToAdminRow(app: AdminLeaveSource, existing?: AdminLeaveRequestRow): AdminLeaveRequestRow {
  const status = "leave_status" in app ? app.leave_status : app.status;
  const normalizedStatus = status === "PENDING" ? "SUBMITTED" : status;
  const leaveTypeCode = "leave_type_detail" in app
    ? app.leave_type_detail?.code ?? "L"
    : app.leave_type_id ?? "L";
  const leaveTypeName = "leave_type_detail" in app
    ? app.leave_type_detail?.name ?? app.leave_type
    : app.leave_type;
  const leaveTypeId = "leave_type_detail" in app
    ? app.leave_type
    : app.leave_type_id;

  const employeeName = "employee_name" in app ? app.employee_name : existing?.employee.employee_name ?? "Employee";
  const employeeCode = "employee_code" in app ? app.employee_code : existing?.employee.employee_code ?? "EMP000";

  return {
    id: app.id,
    employee: {
      employee_code: employeeCode,
      employee_name: employeeName,
      department: existing?.employee.department ?? "General",
      designation: existing?.employee.designation ?? "Employee",
      avatarColor: existing?.employee.avatarColor ?? "#343A40",
      initials: existing?.employee.initials ?? employeeName.split(" ").map((x) => x[0]).join("").slice(0, 2).toUpperCase(),
    },
    leave_type: {
      id: leaveTypeId,
      code: leaveTypeCode,
      name: leaveTypeName,
      is_paid: "leave_type_detail" in app ? app.leave_type_detail?.is_paid ?? true : true,
      is_active: true,
    },
    from_date: app.from_date,
    to_date: app.to_date,
    total_days: app.total_days,
    duration: app.total_days <= 0.5 ? "HALF" : "FULL",
    applied_on: "applied_at" in app ? app.applied_at : app.applied_on,
    reason: "reason" in app ? app.reason : existing?.reason ?? "",
    backup_employee: existing?.backup_employee,
    status: (normalizedStatus as LeaveRequestStatus) ?? "SUBMITTED",
    priority: existing?.priority ?? "MEDIUM",
    workflow_stage:
      normalizedStatus === "APPROVED"
        ? "Completed"
        : normalizedStatus === "REJECTED"
          ? "Closed"
          : normalizedStatus === "CANCELLED"
            ? "Cancelled"
            : "Manager Review",
    category: mapCategoryFromLeave(app),
    current_approver:
      normalizedStatus === "APPROVED" || normalizedStatus === "REJECTED" || normalizedStatus === "CANCELLED"
        ? "—"
        : existing?.current_approver ?? "Manager",
    payroll_lock: existing?.payroll_lock ?? "Unlocked",
    workflow_level: existing?.workflow_level ?? (normalizedStatus === "SUBMITTED" ? 1 : 2),
    deleted_at: existing?.deleted_at ?? null,
    approval_history: existing?.approval_history ?? [],
    comments: existing?.comments ?? [],
    attachments: existing?.attachments ?? [],
    audit: existing?.audit ?? [],
    ledger_impact: existing?.ledger_impact ?? [],
  };
}

function updateLeaveAppStatus(id: string, status: LeaveApplicationAPI["status"]) {
  const apps = readStore(LEAVE_APP_KEY, DEMO_APPLICATIONS);
  let changed = false;
  const updated = apps.map((app) => {
    if (app.id !== id) return app;
    changed = true;
    return {
      ...app,
      status,
      approved_at: status === "APPROVED" ? new Date().toISOString() : app.approved_at,
    };
  });
  if (changed) {
    writeStore(LEAVE_APP_KEY, updated);
  }
}

function readRequests(): AdminLeaveRequestRow[] {
  const localRows = (() => {
    try {
      const raw = localStorage.getItem(REQUESTS_KEY);
      if (!raw) return ADMIN_LEAVE_REQUESTS;
      const parsed = JSON.parse(raw) as AdminLeaveRequestRow[];
      return Array.isArray(parsed) ? parsed : ADMIN_LEAVE_REQUESTS;
    } catch {
      return ADMIN_LEAVE_REQUESTS;
    }
  })();

  const leaveApps = readStore(LEAVE_APP_KEY, DEMO_APPLICATIONS);
  const localById = new Map(localRows.map((r) => [r.id, r]));
  const mappedFromLeave = leaveApps.map((app) => mapLeaveAppToAdminRow(app, localById.get(app.id)));
  const leaveIds = new Set(mappedFromLeave.map((r) => r.id));
  const adminOnlyRows = localRows.filter((r) => !leaveIds.has(r.id));

  return [...mappedFromLeave, ...adminOnlyRows];
}

function writeRequests(rows: AdminLeaveRequestRow[]) {
  localStorage.setItem(REQUESTS_KEY, JSON.stringify(rows));
}

function nowIso() {
  return new Date().toISOString();
}

type AdminLeaveSource = LeaveApplicationAPI | AdminLeaveApplicationApiRow;

type RequestAction =
  | "APPROVE"
  | "REJECT"
  | "FORCE_APPROVE"
  | "FORCE_REJECT"
  | "FORCE_CANCEL"
  | "RESTORE"
  | "DELETE";

const ACTION_TO_STATUS: Record<RequestAction, LeaveRequestStatus | null> = {
  APPROVE: "APPROVED",
  REJECT: "REJECTED",
  FORCE_APPROVE: "APPROVED",
  FORCE_REJECT: "REJECTED",
  FORCE_CANCEL: "CANCELLED",
  RESTORE: null,
  DELETE: null,
};

export function useAdminLeaveRequestsStore() {
  const [rows, setRows] = useState<AdminLeaveRequestRow[]>(() => readRequests());
  const adminLeaveApplicationsQuery = useAdminLeaveApplications();
  const [initialized, setInitialized] = useState(false);

  const refresh = useCallback(() => {
    setRows(readRequests());
    adminLeaveApplicationsQuery.refetch();
  }, [adminLeaveApplicationsQuery]);

  // Initial fetch only
  useEffect(() => {
    if (!initialized) {
      setInitialized(true);
      adminLeaveApplicationsQuery.refetch();
    }
  }, []); // Empty dependency array - runs only once

  useEffect(() => {
    const onFocus = () => refresh();
    const onStorage = (e: StorageEvent) => {
      if (e.key === LEAVE_APP_KEY || e.key === REQUESTS_KEY) {
        refresh();
      }
    };
    window.addEventListener("focus", onFocus);
    window.addEventListener("storage", onStorage);
    return () => {
      window.removeEventListener("focus", onFocus);
      window.removeEventListener("storage", onStorage);
    };
  }, [refresh]);

  useEffect(() => {
    const data = adminLeaveApplicationsQuery.data as
      | import("./useAdminLeave").AdminLeaveApplicationListResponse
      | undefined;

    if (!data?.items) return;

    setRows((currentRows) => {
      const localById = new Map(currentRows.map((row) => [row.id, row]));
      const mappedFromApi = data.items.map((app) =>
        mapLeaveAppToAdminRow(app as any, localById.get(app.id)),
      );
      const leaveIds = new Set(mappedFromApi.map((row) => row.id));
      const adminOnlyRows = currentRows.filter((row) => !leaveIds.has(row.id));
      const nextRows = [...mappedFromApi, ...adminOnlyRows];
      writeRequests(nextRows);
      return nextRows;
    });
  }, [adminLeaveApplicationsQuery.data]);

  const persist = useCallback((next: AdminLeaveRequestRow[]) => {
    setRows(next);
    writeRequests(next);
  }, []);

  const runAction = useCallback(
    (id: string, action: RequestAction, actor: { name: string; role: AdminActorRole }, meta?: string) => {
      const next = rows.map((row) => {
        if (row.id !== id) return row;
        if (action === "DELETE") {
          return {
            ...row,
            deleted_at: nowIso(),
            audit: [
              {
                id: `${row.id}-audit-${Date.now()}`,
                at: nowIso(),
                actor: actor.name,
                actor_role: actor.role,
                action: "REQUEST_DELETED",
                meta: meta ?? "Soft deleted by superadmin",
              },
              ...row.audit,
            ],
          };
        }
        if (action === "RESTORE") {
          return {
            ...row,
            deleted_at: null,
            audit: [
              {
                id: `${row.id}-audit-${Date.now()}`,
                at: nowIso(),
                actor: actor.name,
                actor_role: actor.role,
                action: "REQUEST_RESTORED",
                meta: meta ?? "Restored by superadmin",
              },
              ...row.audit,
            ],
          };
        }

        const status = ACTION_TO_STATUS[action];
        return {
          ...row,
          status: status ?? row.status,
          workflow_stage: status === "APPROVED" ? "Completed" : status === "REJECTED" ? "Closed" : status === "CANCELLED" ? "Cancelled" : row.workflow_stage,
          current_approver: status === "APPROVED" || status === "REJECTED" || status === "CANCELLED" ? "—" : row.current_approver,
          audit: [
            {
              id: `${row.id}-audit-${Date.now()}`,
              at: nowIso(),
              actor: actor.name,
              actor_role: actor.role,
              action,
              meta,
              previous_value: row.status,
              new_value: status ?? row.status,
            },
            ...row.audit,
          ],
        };
      });
      persist(next);

      if (action === "APPROVE" || action === "FORCE_APPROVE") {
        updateLeaveAppStatus(id, "APPROVED");
      } else if (action === "REJECT" || action === "FORCE_REJECT") {
        updateLeaveAppStatus(id, "REJECTED");
      } else if (action === "FORCE_CANCEL") {
        updateLeaveAppStatus(id, "CANCELLED");
      }
    },
    [persist, rows],
  );

  const activeRows = useMemo(() => rows.filter((r) => !r.deleted_at), [rows]);
  const deletedRows = useMemo(() => rows.filter((r) => !!r.deleted_at), [rows]);

  return {
    rows,
    activeRows,
    deletedRows,
    refresh,
    runAction,
    isLoading: adminLeaveApplicationsQuery.isLoading,
  };
}

