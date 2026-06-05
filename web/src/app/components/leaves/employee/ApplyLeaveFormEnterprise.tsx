import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, FileUp, Paperclip, X, AlertCircle, AlertTriangle, Info } from "lucide-react";
import type { LeaveBalanceAPI } from "../../../modules/leaves/types";
import { useApplyLeave, useLeaveTypes } from "../../../../hooks/useLeave";

import { Button } from "../../ui/button";
import { LeaveTypePill } from "./LeaveTypePill";

// ─── Design tokens ────────────────────────────────────────────────────────────
// All reusable class strings are declared once here. Updating a token cascades
// through every instance, giving us a real design system without a separate file.

const input =
  "h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 text-sm text-slate-900 shadow-sm outline-none transition-all placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 hover:border-slate-300";

const selectBase =
  "h-11 w-full appearance-none rounded-lg border border-slate-200 bg-white px-3.5 pr-9 text-sm text-slate-900 shadow-sm outline-none transition-all focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 hover:border-slate-300";

const label =
  "mb-1.5 block text-[11px] font-semibold uppercase tracking-widest text-slate-400";

const fieldset = "space-y-1.5";

const alertBase =
  "flex items-start gap-2.5 rounded-lg border px-3.5 py-3 text-sm leading-snug";

const alerts = {
  warning: `${alertBase} border-amber-200 bg-amber-50 text-amber-800`,
  error:   `${alertBase} border-red-200   bg-red-50   text-red-700`,
  info:    `${alertBase} border-slate-200  bg-slate-50  text-slate-600`,
};

// ─── SelectWrapper ─────────────────────────────────────────────────────────────
function SelectWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative">
      {children}
      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
    </div>
  );
}

// ─── SectionLabel ──────────────────────────────────────────────────────────────
function SectionLabel({ children, required }: { children: React.ReactNode; required?: boolean }) {
  return (
    <label className={label}>
      {children}
      {required && <span className="ml-1 text-red-400">*</span>}
    </label>
  );
}

// ─── Main component ────────────────────────────────────────────────────────────
export function ApplyLeaveFormEnterprise({
  employee,
  balances,
  prefillLeaveType,
  onSuccess,
}: {
  employee: { employee_code: string; employee_name: string };
  balances: LeaveBalanceAPI[];
  prefillLeaveType?: string;
  onSuccess: () => void;
}) {
  const { data: leaveTypes = [] } = useLeaveTypes();
  const applyLeave = useApplyLeave();

  const [leaveTypeId, setLeaveTypeId]               = useState("");
  const [fromDate, setFromDate]                     = useState("");
  const [toDate, setToDate]                         = useState("");
  const [fromSession, setFromSession]               = useState<"first_half" | "second_half">("first_half");
  const [toSession, setToSession]                   = useState<"first_half" | "second_half">("second_half");
  const [reason, setReason]                         = useState("");
  const [contactDuringLeave, setContactDuringLeave] = useState("");
  const [attachment, setAttachment]                 = useState<File | null>(null);
  const [attachmentError, setAttachmentError]       = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!prefillLeaveType) return;
    if (leaveTypes.some((lt) => lt.leave_type_id === prefillLeaveType)) {
      setLeaveTypeId(prefillLeaveType);
    }
  }, [prefillLeaveType, leaveTypes]);

  const handleAttachmentFile = (f: File | null) => {
    if (!f) { setAttachment(null); setAttachmentError(null); return; }
    const acceptedExts = [".pdf",".xls",".xlsx",".doc",".docx",".txt",".ppt",".pptx",".gif",".jpg",".jpeg",".png"];
    if (!acceptedExts.some((ext) => f.name.toLowerCase().endsWith(ext))) {
      setAttachmentError("Unsupported file type. Upload PDF, XLS, XLSX, DOC, DOCX, TXT, PPT, PPTX, GIF, JPG, JPEG, PNG.");
      setAttachment(null);
      return;
    }
    setAttachmentError(null);
    setAttachment(f);
  };

  const totalDays = useMemo(() => {
    if (!fromDate || !toDate) return 0;
    const from = new Date(fromDate);
    const to   = new Date(toDate);
    if (to < from) return 0;
    return Math.ceil((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24)) + 1;
  }, [fromDate, toDate]);

  const selectedBalance = useMemo(
    () => balances.find((b) => b.leave_type_id === leaveTypeId) ?? null,
    [leaveTypeId, balances],
  );

  const availableDays          = Number(selectedBalance?.available ?? selectedBalance?.balance ?? 0);
  const exceedsBalance         = selectedBalance ? totalDays > availableDays : false;
  const remainingAfterApproval = Math.max(0, availableDays - totalDays);

  const selectedType = useMemo(
    () => leaveTypes.find((lt) => lt.leave_type_id === leaveTypeId) ?? null,
    [leaveTypeId, leaveTypes],
  );

  const canSubmit =
    !!leaveTypeId && !!fromDate && !!toDate && !!reason.trim() && totalDays > 0 && !exceedsBalance;

  const resetForm = () => {
    setLeaveTypeId(""); setFromDate(""); setToDate("");
    setFromSession("first_half"); setToSession("second_half");
    setReason(""); setContactDuringLeave("");
    setAttachment(null); setAttachmentError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    console.log("prefillLeaveType", prefillLeaveType);
    console.log("leaveTypes", leaveTypes);
    console.log("leaveTypeId", leaveTypeId);
    applyLeave.mutate(
      {
        leave_type_id: leaveTypeId,
        from_date: fromDate,
        to_date: toDate,
        from_session: fromSession,
        to_session: toSession,
        contact_during_leave: contactDuringLeave.trim(),
        reason: reason.trim(),
        attachment: attachment,
      },
      { onSuccess: () => { resetForm(); onSuccess(); } },
    );
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">

      {/* ── Main Form ──────────────────────────────────────────────────────── */}
      <div className="xl:col-span-2">
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

          {/* Form header */}
          {/* <div className="border-b border-slate-100 px-6 py-4">
            <p className="text-sm text-slate-500">
              Applicant:{" "}
              <span className="font-medium text-slate-700">
                {employee.employee_name}
              </span>{" "}
              <span className="text-slate-400">({employee.employee_code})</span>
            </p>
          </div> */}

          <form onSubmit={handleSubmit} className="divide-y divide-slate-100">

            {/* ── Fields ─────────────────────────────────────────────────── */}
            <div className="space-y-5 px-6 py-6">

              {/* Leave Type */}
              <div className={fieldset}>
                <SectionLabel required>Leave Type</SectionLabel>
                <SelectWrapper>
                  <select
                    value={leaveTypeId}
                    onChange={(e) => setLeaveTypeId(e.target.value)}
                    className={selectBase}
                    required
                  >
                    <option value="">Select leave type…</option>
                    {leaveTypes.map((lt) => (
                      <option key={lt.leave_type_id} value={lt.leave_type_id}>
                        {lt.name} ({lt.code})
                      </option>
                    ))}
                  </select>
                </SelectWrapper>
              </div>

              {/* Dates + Sessions */}
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {/* From */}
                <div className="space-y-2">
                  <div className={fieldset}>
                    <SectionLabel required>From Date</SectionLabel>
                    <input
                      type="date"
                      value={fromDate}
                      onChange={(e) => setFromDate(e.target.value)}
                      className={input}
                      required
                    />
                  </div>
                  <div className={fieldset}>
                    <SectionLabel>From Session</SectionLabel>
                    <SelectWrapper>
                      <select
                        value={fromSession}
                        onChange={(e) => setFromSession(e.target.value as "first_half" | "second_half")}
                        className={selectBase}
                      >
                        <option value="first_half">First Half</option>
                        <option value="second_half">Second Half</option>
                      </select>
                    </SelectWrapper>
                  </div>
                </div>

                {/* To */}
                <div className="space-y-2">
                  <div className={fieldset}>
                    <SectionLabel required>To Date</SectionLabel>
                    <input
                      type="date"
                      value={toDate}
                      min={fromDate || undefined}
                      onChange={(e) => setToDate(e.target.value)}
                      className={input}
                      required
                    />
                  </div>
                  <div className={fieldset}>
                    <SectionLabel>To Session</SectionLabel>
                    <SelectWrapper>
                      <select
                        value={toSession}
                        onChange={(e) => setToSession(e.target.value as "first_half" | "second_half")}
                        className={selectBase}
                      >
                        <option value="first_half">First Half</option>
                        <option value="second_half">Second Half</option>
                      </select>
                    </SelectWrapper>
                  </div>
                </div>
              </div>

              {/* Contact During Leave */}
              <div className={fieldset}>
                <SectionLabel>Contact During Leave</SectionLabel>
                <input
                  type="text"
                  value={contactDuringLeave}
                  onChange={(e) => setContactDuringLeave(e.target.value)}
                  placeholder="Phone number or alternate contact"
                  className={input}
                />
              </div>

              {/* Reason */}
              <div className={fieldset}>
                <SectionLabel required>Reason</SectionLabel>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={4}
                  placeholder="Briefly describe the reason for your leave…"
                  className="w-full resize-none rounded-lg border border-slate-200 bg-white px-3.5 py-3 text-sm text-slate-900 shadow-sm outline-none transition-all placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 hover:border-slate-300"
                  required
                />
              </div>

              {/* Attachment */}
              <div className={fieldset}>
                <SectionLabel>Attachment</SectionLabel>
                <div className="flex items-center gap-3">
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".pdf,.xls,.xlsx,.doc,.docx,.txt,.ppt,.pptx,.gif,.jpg,.jpeg,.png"
                    onChange={(e) => handleAttachmentFile(e.target.files?.[0] ?? null)}
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="inline-flex h-9 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-600 shadow-sm transition-all hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  >
                    <Paperclip className="h-3.5 w-3.5" />
                    {attachment ? "Change file" : "Attach file"}
                  </button>
                  {attachment && (
                    <div className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-600">
                      <FileUp className="h-3.5 w-3.5 shrink-0 text-slate-400" />
                      <span className="max-w-[180px] truncate">{attachment.name}</span>
                      <button
                        type="button"
                        onClick={() => { setAttachment(null); setAttachmentError(null); }}
                        className="ml-1 text-slate-400 hover:text-slate-700"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  )}
                </div>
                {attachmentError && (
                  <p className="mt-1.5 flex items-center gap-1.5 text-xs text-red-600">
                    <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                    {attachmentError}
                  </p>
                )}
              </div>

              {/* Leave type pill */}
              {selectedType && <LeaveTypePill code={selectedType.code} />}
            </div>

            {/* ── Alerts ─────────────────────────────────────────────────── */}
            {applyLeave.isError && (
              <div className="px-6 py-4">
                <div className={alerts.error}>
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>
                    {(applyLeave.error as Error)?.message || "Failed to submit leave application."}
                  </span>
                </div>
              </div>
            )}

            {/* ── Footer ─────────────────────────────────────────────────── */}
            <div className="flex items-center justify-end gap-3 px-6 py-4">
              <Button
                type="button"
                variant="outline"
                className="h-10 rounded-lg border-slate-200 px-5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
                onClick={resetForm}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={applyLeave.isPending || !canSubmit}
                className="h-10 rounded-lg bg-indigo-600 px-5 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {applyLeave.isPending ? "Submitting…" : "Submit Application"}
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* ── Sidebar ────────────────────────────────────────────────────────── */}
      <div className="space-y-4 xl:col-span-1">

        {/* Balance card */}
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          {/* Gradient header */}
          <div className="bg-[radial-gradient(ellipse_at_top_left,_#2B1555_0%,_#2B1555_60%,_#6d28d9_100%)] px-5 py-5">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/80">
              Leave Balance
            </p>
            <h3 className="mt-1.5 text-base font-semibold leading-tight text-white">
              {selectedBalance?.leave_type_detail?.name ??
                selectedBalance?.leave_type ??
                "Select a leave type"}
            </h3>
          </div>

          {/* Body */}
          <div className="p-5">
            {selectedBalance ? (
              <div className="space-y-3">

                {/* Stats row */}
                <div className="grid grid-cols-2 divide-x divide-slate-100 overflow-hidden rounded-xl border border-slate-100 bg-slate-50">
                  <div className="px-4 py-3.5">
                    <p className="text-[11px] text-slate-400 uppercase tracking-wide">Used</p>
                    <p className="mt-0.5 text-lg font-semibold text-slate-800">
                      {Number(selectedBalance.used ?? selectedBalance.taken)}
                      <span className="ml-1 text-xs font-normal text-slate-400">days</span>
                    </p>
                  </div>
                  <div className="px-4 py-3.5">
                    <p className="text-[11px] text-slate-400 uppercase tracking-wide">Available</p>
                    <p className="mt-0.5 text-lg font-semibold text-indigo-600">
                      {availableDays}
                      <span className="ml-1 text-xs font-normal text-slate-400">days</span>
                    </p>
                  </div>
                </div>

                {/* After this request */}
                <div className="flex items-center justify-between rounded-xl border border-slate-100 bg-white px-4 py-3">
                  <span className="text-xs font-medium text-slate-500">After this request</span>
                  <span className="text-sm font-semibold text-slate-800">
                    {Math.max(0, availableDays - totalDays)}{" "}
                    <span className="font-normal text-slate-400">days</span>
                  </span>
                </div>

                {/* Contextual alerts */}
                {totalDays > 0 && !exceedsBalance && (
                  <div className={alerts.info}>
                    <Info className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                    <span>
                      Applying for{" "}
                      <span className="font-semibold">{totalDays}</span>{" "}
                      {totalDays === 1 ? "day" : "days"}
                    </span>
                  </div>
                )}

                {exceedsBalance && (
                  <div className={alerts.error}>
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                    <span>
                      Insufficient balance. Only{" "}
                      <span className="font-semibold">{availableDays}</span>{" "}
                      {availableDays === 1 ? "day" : "days"} available.
                    </span>
                  </div>
                )}

                {!exceedsBalance && remainingAfterApproval <= 1 && remainingAfterApproval >= 0 && totalDays > 0 && (
                  <div className={alerts.warning}>
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
                    <span>
                      Only{" "}
                      <span className="font-semibold">{remainingAfterApproval}</span>{" "}
                      {remainingAfterApproval === 1 ? "day" : "days"} remaining after this request.
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <p className="py-2 text-sm text-slate-400">
                Select a leave type to see your balance.
              </p>
            )}
          </div>
        </div>

        {/* Heads Up */}
        <div className="rounded-2xl border border-amber-100 bg-amber-50 p-5">
          <p className="text-[11px] font-semibold uppercase tracking-widest text-amber-600">
            Heads Up
          </p>
          <ul className="mt-3 space-y-2 text-sm text-amber-800">
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
              Apply at least 1 day in advance for planned leaves
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
              Medical leaves may require a certificate
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
              Your manager will be notified automatically
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}