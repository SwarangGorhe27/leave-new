import { useEffect, useMemo, useRef, useState } from "react";
import {
  CalendarDays,
  FileText,
  MessageSquareText,
  Paperclip,
  ShieldCheck,
  Timer,
  X,
} from "lucide-react";

import { cn } from "../../../../../components/ui/utils";

import type {
  AdminLeaveRequestRow,
  LeaveRequestStatus,
} from "../../../../../modules/adminLeave/types";

import { useAdminLeaveRequestsStore } from "../../../../../modules/adminLeave/store";
import { Textarea } from "../../../../../components/ui/textarea";

function SectionTitle({
  icon: Icon,
  title,
  sub,
}: {
  icon: React.ElementType;
  title: string;
  sub?: string;
}) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div className="min-w-0">
        <p className="text-sm font-semibold text-foreground">
          {title}
        </p>

        {sub && (
          <p className="text-xs text-muted-foreground mt-0.5">
            {sub}
          </p>
        )}
      </div>

      <div className="w-10 h-10 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-muted-foreground" />
      </div>
    </div>
  );
}

function Pill({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <span className="text-[11px] font-semibold text-muted-foreground bg-secondary border border-border px-2 py-0.5 rounded-md">
      {children}
    </span>
  );
}

export function AdminLeaveRequestDrawer({
  row,
  open,
  onOpenChange,
}: {
  row: AdminLeaveRequestRow | null;
  open: boolean;
  onOpenChange: (o: boolean) => void;
}) {
  const { runAction } = useAdminLeaveRequestsStore();

  const [tab, setTab] = useState<
    | "overview"
    | "timeline"
    | "comments"
    | "attachments"
    | "audit"
  >("overview");

  const [comment, setComment] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [attachments, setAttachments] = useState<
    { id: string; name: string; type: string }[]
  >([]);

  const [form, setForm] = useState({
    from_date: "",
    to_date: "",
    total_days: "",
    duration: "",
    reason: "",
    applied_on: "",
    backup_employee: "",
    current_approver: "",
    workflow_level: 1,
    payroll_lock: "",
    priority: "",
    workflow_stage: "",
    status: "SUBMITTED" as LeaveRequestStatus,
  });

  useEffect(() => {
    if (!row) return;

    setForm({
      from_date: row.from_date,
      to_date: row.to_date,
      total_days: String(row.total_days),
      duration: row.duration,
      reason: row.reason,
      applied_on: row.applied_on,
      backup_employee: row.backup_employee ?? "",
      current_approver: row.current_approver ?? "",
      workflow_level: row.workflow_level,
      payroll_lock: row.payroll_lock,
      priority: row.priority ?? "",
      workflow_stage: row.workflow_stage ?? "",
      status: row.status,
    });

    setAttachments(
      row.attachments.map((a) => ({
        id: a.id,
        name: a.name,
        type: a.type,
      }))
    );
  }, [row]);

  const header = useMemo(() => {
    if (!row) return null;

    return {
      title: `${row.employee.employee_name} · ${row.leave_type.name}`,
      sub: `${row.employee.employee_code} · ${row.employee.department}`,
    };
  }, [row]);

  const handleSave = () => {
    console.log("Updated Form", form);
    // integrate API/store update here
  };

  const handleQuickAction = (
    action: "APPROVE" | "REJECT" | "REQUEST_INFO"
  ) => {
    if (!row) return;

    if (action === "REQUEST_INFO") {
      // REQUEST_INFO is not a store action — handle via API/custom logic
      console.log("Request Info for", row.id);
      return;
    }

    runAction(
      row.id,
      action,
      { name: "Superadmin", role: "superadmin" },
      `Quick action: ${action} from superadmin modal`
    );

    onOpenChange(false);
  };

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = Array.from(e.target.files ?? []);

    const newAttachments = files.map((f) => ({
      id: `${Date.now()}-${f.name}`,
      name: f.name,
      type: f.name.split(".").pop() ?? "file",
    }));

    setAttachments((prev) => [...prev, ...newAttachments]);
    e.target.value = "";
  };

  const handleRemoveAttachment = (id: string) => {
    setAttachments((prev) => prev.filter((a) => a.id !== id));
  };

  if (!open) return null;

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={() => onOpenChange(false)}
    >
      {/* Modal panel */}
      <div
        className="relative bg-background border border-border rounded-xl shadow-xl flex flex-col w-[92vw] max-w-3xl max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >

        {/* HEADER */}
        <div className="border-b border-border bg-card px-5 pt-5 pb-0 flex-shrink-0">

          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h2 className="text-base font-semibold text-foreground leading-snug">
                {header?.title ?? "Leave Request"}
              </h2>

              <p className="text-xs text-muted-foreground mt-1">
                {header?.sub ?? "—"}
              </p>

              {row && (
                <div className="mt-3 flex flex-wrap gap-2">
                  <Pill>Status: {form.status}</Pill>
                  <Pill>Workflow: L{form.workflow_level}</Pill>
                  <Pill>Payroll: {form.payroll_lock}</Pill>
                </div>
              )}
            </div>

            <button
              type="button"
              onClick={() => onOpenChange(false)}
              className="w-9 h-9 flex items-center justify-center rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors flex-shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Tabs */}
          <div className="mt-4 flex gap-1 p-1 bg-secondary rounded-lg overflow-x-auto">
            {[
              { id: "overview",    label: "Overview" },
              { id: "timeline",    label: "Approval History" },
              { id: "comments",    label: "Comments" },
              { id: "attachments", label: "Attachments" },
              { id: "audit",       label: "Audit Trail" },
            ].map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id as any)}
                className={cn(
                  "px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-150 whitespace-nowrap",
                  tab === t.id
                    ? "bg-card text-foreground shadow-sm border border-border"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* BODY — scrollable */}
        <div className="p-5 space-y-5 overflow-y-auto flex-1">

          {!row ? (
            <div className="flat-card bg-card p-8">
              <p className="text-sm font-semibold text-foreground">
                No request selected
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Select a row to see details.
              </p>
            </div>
          ) : (
            <>
              {/* OVERVIEW */}
              {tab === "overview" && (
                <div className="space-y-4">
                  <div className="flat-card bg-card p-5">
                    <SectionTitle
                      icon={CalendarDays}
                      title="Editable Request Summary"
                      sub="Admin can edit leave request details"
                    />

                    <div className="mt-4 grid grid-cols-2 gap-3">

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          From Date
                        </label>
                        <input
                          type="date"
                          value={form.from_date}
                          onChange={(e) => setForm((prev) => ({ ...prev, from_date: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          To Date
                        </label>
                        <input
                          type="date"
                          value={form.to_date}
                          onChange={(e) => setForm((prev) => ({ ...prev, to_date: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Total Days
                        </label>
                        <input
                          type="number"
                          value={form.total_days}
                          onChange={(e) => setForm((prev) => ({ ...prev, total_days: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Duration
                        </label>
                        <input
                          value={form.duration}
                          onChange={(e) => setForm((prev) => ({ ...prev, duration: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Status
                        </label>
                        <select
                          value={form.status}
                          onChange={(e) => setForm((prev) => ({ ...prev, status: e.target.value as LeaveRequestStatus }))}
                          className="flat-input h-10 w-full mt-2"
                        >
                          <option value="DRAFT">Draft</option>
                          <option value="SUBMITTED">Submitted</option>
                          <option value="APPROVED">Approved</option>
                          <option value="REJECTED">Rejected</option>
                          <option value="CANCELLED">Cancelled</option>
                          <option value="REVOKED">Revoked</option>
                        </select>
                      </div>

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Priority
                        </label>
                        <input
                          value={form.priority}
                          onChange={(e) => setForm((prev) => ({ ...prev, priority: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>
                    </div>

                    <div className="mt-4 p-4 rounded-xl border border-border bg-background">
                      <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                        Reason
                      </label>
                      <Textarea
                        value={form.reason}
                        onChange={(e) => setForm((prev) => ({ ...prev, reason: e.target.value }))}
                        className="mt-2 min-h-24"
                      />
                    </div>

                    <div className="mt-4 grid grid-cols-2 gap-3">
                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Backup Employee
                        </label>
                        <input
                          value={form.backup_employee}
                          onChange={(e) => setForm((prev) => ({ ...prev, backup_employee: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Current Approver
                        </label>
                        <input
                          value={form.current_approver}
                          onChange={(e) => setForm((prev) => ({ ...prev, current_approver: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Workflow Stage
                        </label>
                        <input
                          value={form.workflow_stage}
                          onChange={(e) => setForm((prev) => ({ ...prev, workflow_stage: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>

                      <div className="p-4 rounded-xl border border-border bg-background">
                        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                          Payroll Lock
                        </label>
                        <input
                          value={form.payroll_lock}
                          onChange={(e) => setForm((prev) => ({ ...prev, payroll_lock: e.target.value }))}
                          className="flat-input h-10 w-full mt-2"
                        />
                      </div>
                    </div>

                    <div className="mt-5 flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => onOpenChange(false)}
                        className="px-4 py-2 rounded-lg border border-border text-sm font-semibold"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={handleSave}
                        className="px-4 py-2 rounded-lg bg-foreground text-primary-foreground text-sm font-semibold"
                      >
                        Save Changes
                      </button>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="flat-card bg-card p-5">
                    <SectionTitle
                      icon={ShieldCheck}
                      title="Quick Actions"
                      sub="Admin workflow controls"
                    />
                    <div className="mt-4 flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => handleQuickAction("APPROVE")}
                        className="px-3 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground"
                      >
                        Approve
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickAction("REJECT")}
                        className="px-3 py-2 rounded-lg text-xs font-semibold bg-secondary border border-border"
                      >
                        Reject
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickAction("REQUEST_INFO")}
                        className="px-3 py-2 rounded-lg text-xs font-semibold bg-secondary border border-border"
                      >
                        Request Info
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* TIMELINE */}
              {tab === "timeline" && (
                <div className="flat-card bg-card p-5">
                  <SectionTitle
                    icon={Timer}
                    title="Approval History"
                    sub="Workflow steps and actions"
                  />
                  <div className="mt-4 space-y-3">
                    {row.approval_history.map((s) => (
                      <div key={s.level} className="p-4 rounded-xl border border-border bg-background">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-foreground">
                            Level {s.level}
                          </p>
                          <Pill>{s.status}</Pill>
                        </div>
                        <input defaultValue={s.approver} className="flat-input h-10 w-full mt-3" />
                        {s.remarks && <Textarea defaultValue={s.remarks} className="mt-3" />}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* COMMENTS */}
              {tab === "comments" && (
                <div className="flat-card bg-card p-5 space-y-4">
                  <SectionTitle
                    icon={MessageSquareText}
                    title="Comments"
                    sub="Discussion and clarifications"
                  />
                  <div className="space-y-2">
                    {row.comments.map((c) => (
                      <div key={c.id} className="p-4 rounded-xl border border-border bg-background">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-foreground">{c.author}</p>
                          <Pill>{new Date(c.created_at).toLocaleString()}</Pill>
                        </div>
                        <Textarea defaultValue={c.message} className="mt-3" />
                      </div>
                    ))}
                  </div>
                  <div className="p-4 rounded-xl border border-border bg-background">
                    <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                      Add Comment
                    </p>
                    <Textarea
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Write a comment…"
                      className="min-h-20"
                    />
                    <div className="mt-3 flex justify-end">
                      <button
                        type="button"
                        className="px-3 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground"
                        onClick={() => setComment("")}
                      >
                        Post Comment
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* ATTACHMENTS */}
              {tab === "attachments" && (
                <div className="flat-card bg-card p-5">
                  <SectionTitle
                    icon={Paperclip}
                    title="Attachments"
                    sub="Manage uploaded files"
                  />

                  <div className="mt-4 space-y-2">
                    {attachments.map((a) => (
                      <div
                        key={a.id}
                        className="flex items-center justify-between p-4 rounded-xl border border-border bg-background"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-secondary border border-border flex items-center justify-center">
                            <FileText className="w-4 h-4 text-muted-foreground" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-foreground">{a.name}</p>
                            <p className="text-xs text-muted-foreground mt-0.5">{a.type.toUpperCase()}</p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveAttachment(a.id)}
                          className="px-3 py-1 rounded-md border border-border text-xs hover:bg-secondary transition-colors"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* Hidden file input, triggered by button */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    className="hidden"
                    onChange={handleFileChange}
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="mt-4 w-full px-4 py-2.5 rounded-lg border border-dashed border-border text-xs font-semibold text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
                  >
                    + Choose File
                  </button>
                </div>
              )}

              {/* AUDIT */}
              {tab === "audit" && (
                <div className="flat-card bg-card p-5">
                  <SectionTitle
                    icon={FileText}
                    title="Audit Trail"
                    sub="Immutable event stream"
                  />
                  <div className="mt-4 space-y-2">
                    {row.audit.map((e) => (
                      <div key={e.id} className="p-4 rounded-xl border border-border bg-background">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-foreground">{e.action}</p>
                          <Pill>{new Date(e.at).toLocaleString()}</Pill>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">Actor: {e.actor}</p>
                        {e.meta && <Textarea defaultValue={e.meta} className="mt-3" />}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}