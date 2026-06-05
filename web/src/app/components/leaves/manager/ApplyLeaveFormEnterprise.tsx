import type { ElementType, ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { CalendarDays, FileUp, MessageSquare, Phone, Send, Shield } from "lucide-react";
import type { LeaveBalanceAPI } from "../../../modules/leaves/types";
import { useApplyLeave, useLeaveTypes } from "../../../modules/leaves/useLeaves";
import { Button } from "../../ui/button";
import { cn } from "../../ui/utils";
import { LeaveTypePill } from "./LeaveTypePill";

function SectionHeading({
  icon: Icon,
  title,
  description,
}: {
  icon: ElementType;
  title: string;
  description?: string;
}) {
  return (
    <div className="mb-3 flex items-start gap-3">
      <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-2xl border border-border bg-secondary">
        <Icon className="h-4 w-4 text-foreground" aria-hidden />
      </div>
      <div className="min-w-0">
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
        {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
      </div>
    </div>
  );
}

function FormSection({
  icon: Icon,
  title,
  description,
  children,
}: {
  icon: ElementType;
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <section className="pb-6">
      <SectionHeading icon={Icon} title={title} description={description} />
      {children}
      <div className="mt-6 h-px bg-border" />
    </section>
  );
}

const ACCEPTED_MIMES = new Set([
  "application/pdf",
  "image/jpeg",
  "image/png",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]);
const ACCEPTED_EXTS = [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"];

function isAcceptedAttachment(file: File) {
  const name = file.name.toLowerCase();
  const extOk = ACCEPTED_EXTS.some((ext) => name.endsWith(ext));
  const mimeOk = ACCEPTED_MIMES.has(file.type);
  return extOk || mimeOk;
}

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
  const applyLeave = useApplyLeave(employee);

  const [leaveType, setLeaveType] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [fromHalf, setFromHalf] = useState<"FULL" | "AM" | "PM">("FULL");
  const [toHalf, setToHalf] = useState<"FULL" | "AM" | "PM">("FULL");
  const [reason, setReason] = useState("");
  const [contactDuringLeave, setContactDuringLeave] = useState("");
  const [attachment, setAttachment] = useState<File | null>(null);
  const [attachmentError, setAttachmentError] = useState<string | null>(null);
  const [attachmentPreviewUrl, setAttachmentPreviewUrl] = useState<string | null>(null);
  const [isDraggingAttachment, setIsDraggingAttachment] = useState(false);
  const submitModeRef = useRef<"DRAFT" | "SUBMITTED">("SUBMITTED");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!prefillLeaveType) return;
    if (leaveTypes.some((lt) => lt.id === prefillLeaveType)) {
      setLeaveType(prefillLeaveType);
    }
  }, [prefillLeaveType, leaveTypes]);

  useEffect(() => {
    return () => {
      if (attachmentPreviewUrl) URL.revokeObjectURL(attachmentPreviewUrl);
    };
  }, [attachmentPreviewUrl]);

  const handleAttachmentFile = (f: File | null) => {
    if (!f) {
      setAttachment(null);
      setAttachmentError(null);
      setAttachmentPreviewUrl(null);
      return;
    }
    if (!isAcceptedAttachment(f)) {
      setAttachmentError("Unsupported file type. Upload PDF, JPG, PNG, DOC, or DOCX.");
      setAttachment(null);
      setAttachmentPreviewUrl(null);
      return;
    }
    setAttachmentError(null);
    setAttachment(f);
    setAttachmentPreviewUrl(f.type.startsWith("image/") ? URL.createObjectURL(f) : null);
  };

  const totalDays = useMemo(() => {
    if (!fromDate || !toDate) return 0;
    const from = new Date(fromDate);
    const to = new Date(toDate);
    if (to < from) return 0;
    let days = Math.ceil((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    if (fromHalf !== "FULL") days -= 0.5;
    if (toHalf !== "FULL" && fromDate !== toDate) days -= 0.5;
    return Math.max(days, 0.5);
  }, [fromDate, toDate, fromHalf, toHalf]);

  const selectedBalance = useMemo(() => {
    if (!leaveType) return null;
    return balances.find((b) => b.leave_type === leaveType) ?? null;
  }, [leaveType, balances]);

  const selectedType = useMemo(
    () => leaveTypes.find((lt) => lt.id === leaveType) ?? null,
    [leaveTypes, leaveType],
  );

  const exceedsBalance = selectedBalance
    ? totalDays > Number(selectedBalance.available || 0)
    : false;
  const attachmentPayload = attachment ? attachment.name : undefined;

  const canSubmit =
    !!leaveType && !!fromDate && !!toDate && !!reason.trim() && totalDays > 0 && !exceedsBalance;

  const selectedLeaveName =
    selectedType?.name ?? selectedBalance?.leave_type_detail.name ?? "Selected leave";
  const selectedLeaveCode = selectedType?.code ?? selectedBalance?.leave_type_detail.code ?? "";
  const selectedLeaveLabel = selectedLeaveCode
    ? `${selectedLeaveName} (${selectedLeaveCode})`
    : selectedLeaveName;

  const applyingRangeLabel =
    fromDate && toDate
      ? `${new Date(fromDate).toLocaleDateString("en-GB", {
          day: "numeric",
          month: "short",
        })} → ${new Date(toDate).toLocaleDateString("en-GB", { day: "numeric", month: "short" })}`
      : "—";

  const sessionLabel =
    fromHalf === "FULL" && toHalf === "FULL"
      ? "Full days"
      : `${fromHalf === "FULL" ? "Full" : fromHalf === "AM" ? "First half" : "Second half"} → ${
          toHalf === "FULL" ? "Full" : toHalf === "AM" ? "First half" : "Second half"
        }`;

  const totalVisibleBalance = selectedBalance
    ? Number(selectedBalance.used) + Number(selectedBalance.available)
    : 0;
  const usedPercent =
    totalVisibleBalance > 0
      ? Math.round((Number(selectedBalance?.used || 0) / totalVisibleBalance) * 100)
      : 0;
  const remainingAfterApproval = selectedBalance
    ? Math.max(0, Number(selectedBalance.available) - totalDays)
    : 0;
  const expiryDate = selectedBalance?.period_end ? new Date(selectedBalance.period_end) : null;
  const expiryLabel = expiryDate
    ? expiryDate.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })
    : "—";
  const expiryDays = expiryDate
    ? Math.ceil((expiryDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    : null;
  const carryExpirySoon =
    selectedBalance?.carry_forwarded && expiryDays !== null && expiryDays > 0 && expiryDays <= 15;

  return (
    <form
      className="lg:grid lg:grid-cols-[minmax(0,1fr)_320px] gap-6 rounded-3xl border border-border bg-card p-4 sm:p-5"
      onSubmit={(e) => {
        e.preventDefault();
        const submitMode = submitModeRef.current;
        if (submitMode === "SUBMITTED" && !canSubmit) return;
        if (
          submitMode === "DRAFT" &&
          (!leaveType || !fromDate || !toDate || !reason.trim() || totalDays <= 0)
        )
          return;

        applyLeave.mutate(
          {
            leave_type: leaveType,
            from_date: fromDate,
            to_date: toDate,
            from_half: fromHalf,
            to_half: toHalf,
            total_days: totalDays,
            reason: reason.trim(),
            contact_during_leave: contactDuringLeave.trim() || undefined,
            document_url: attachmentPayload,
            status: submitMode,
          },
          {
            onSuccess: () => {
              setLeaveType("");
              setFromDate("");
              setToDate("");
              setFromHalf("FULL");
              setToHalf("FULL");
              setReason("");
              setContactDuringLeave("");
              setAttachment(null);
              setAttachmentError(null);
              setAttachmentPreviewUrl(null);
              onSuccess();
            },
          },
        );
      }}
    >
      <div className="space-y-5">
        <FormSection icon={Shield} title="Leave type">
          <select
            value={leaveType}
            onChange={(e) => setLeaveType(e.target.value)}
            className="flat-input w-full cursor-pointer appearance-none rounded-2xl border border-border bg-background px-3 py-3 text-sm"
            required
          >
            <option value="">Select leave type</option>
            {leaveTypes.map((lt) => (
              <option key={lt.id} value={lt.id}>
                {lt.name} ({lt.code})
              </option>
            ))}
          </select>
        </FormSection>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-border bg-background p-3">
            <p className="text-xs uppercase tracking-wider font-medium text-muted-foreground mb-2">From date</p>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="form-control w-full"
              required
            />
          </div>
          <div className="rounded-lg border border-border bg-background p-3">
            <p className="text-xs uppercase tracking-wider font-medium text-muted-foreground mb-2">To date</p>
            <input
              type="date"
              value={toDate}
              min={fromDate || undefined}
              onChange={(e) => setToDate(e.target.value)}
              className="form-control w-full"
              required
            />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-border bg-background p-3">
            <p className="text-xs uppercase tracking-wider font-medium text-muted-foreground mb-2">From session</p>
            <select
              value={fromHalf}
              onChange={(e) => setFromHalf(e.target.value as "FULL" | "AM" | "PM")}
              className="form-control form-control--select w-full"
            >
              <option value="FULL">Full day</option>
              <option value="AM">First half</option>
              <option value="PM">Second half</option>
            </select>
          </div>
          <div className="rounded-lg border border-border bg-background p-3">
            <p className="text-xs uppercase tracking-wider font-medium text-muted-foreground mb-2">To session</p>
            <select
              value={toHalf}
              onChange={(e) => setToHalf(e.target.value as "FULL" | "AM" | "PM")}
              className="form-control form-control--select w-full"
            >
              <option value="FULL">Full day</option>
              <option value="AM">First half</option>
              <option value="PM">Second half</option>
            </select>
          </div>
        </div>

        <FormSection icon={MessageSquare} title="Reason">
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            className="flat-input w-full resize-none rounded-2xl border border-border bg-background px-3 py-3 text-sm"
            placeholder="Enter your reason"
            required
          />
        </FormSection>

        <FormSection icon={FileUp} title="Attachment">
          <div
            role="button"
            tabIndex={0}
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") fileInputRef.current?.click();
            }}
            onDragEnter={(e) => {
              e.preventDefault();
              setIsDraggingAttachment(true);
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDraggingAttachment(true);
            }}
            onDragLeave={() => setIsDraggingAttachment(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDraggingAttachment(false);
              const f = e.dataTransfer.files?.[0] ?? null;
              handleAttachmentFile(f);
            }}
            className={cn(
              "rounded-2xl border border-dashed px-4 py-6 transition-colors cursor-pointer select-none",
              isDraggingAttachment
                ? "border-foreground/40 bg-secondary/25"
                : "border-border bg-background hover:border-foreground/50",
            )}
          >
            <div className="flex flex-col items-center gap-2 text-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-secondary">
                <FileUp className="h-4 w-4 text-foreground" aria-hidden />
              </div>
              <p className="text-xs text-muted-foreground">Drag & drop, or click to browse.</p>
              <p className="text-[11px] text-muted-foreground">PDF, JPG, PNG, DOC, DOCX</p>

              {attachment ? (
                <div className="mt-3 w-full">
                  {attachmentPreviewUrl && (
                    <img
                      src={attachmentPreviewUrl}
                      alt="Attachment preview"
                      className="mx-auto h-20 w-20 rounded-2xl border border-border bg-background object-cover"
                    />
                  )}
                  <div className="mt-3 flex items-center justify-between gap-3">
                    <p className="truncate text-sm font-semibold text-foreground">
                      {attachment.name}
                    </p>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="h-8 rounded-full border border-border bg-background hover:bg-secondary/40"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAttachmentFile(null);
                        if (fileInputRef.current) fileInputRef.current.value = "";
                      }}
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="mt-1 text-[11px] text-muted-foreground">No file attached.</p>
              )}
            </div>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,application/pdf,image/jpeg,image/png,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={(e) => {
              const f = e.target.files?.[0] ?? null;
              handleAttachmentFile(f);
            }}
          />
          {attachmentError && (
            <p className="mt-3 rounded-2xl border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {attachmentError}
            </p>
          )}
        </FormSection>

        <FormSection icon={Phone} title="Contact details">
          <input
            type="text"
            value={contactDuringLeave}
            onChange={(e) => setContactDuringLeave(e.target.value)}
            className="flat-input w-full rounded-2xl border border-border bg-background px-3 py-3 text-sm"
            placeholder="Phone or email"
          />
        </FormSection>

        <div className="rounded-2xl border border-border bg-background p-4 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Total days</span>
            <span className="font-semibold text-foreground">
              {totalDays > 0 ? `${totalDays}` : "—"}
            </span>
          </div>
          <div className="mt-3 flex items-center justify-between gap-3 text-xs text-muted-foreground">
            <span>Balance after request</span>
            <span>
              {selectedBalance
                ? `${Math.max(0, Number(selectedBalance.available) - totalDays)} days`
                : "—"}
            </span>
          </div>
        </div>

        {applyLeave.isError && (
          <div className="rounded-2xl border border-destructive/40 bg-destructive/10 px-3 py-3 text-sm text-destructive">
            {(applyLeave.error as Error)?.message || "Failed to submit leave application."}
          </div>
        )}

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
          <Button
            type="submit"
            variant="outline"
            className="h-11 rounded-full border-border font-semibold"
            disabled={
              applyLeave.isPending ||
              !leaveType ||
              !fromDate ||
              !toDate ||
              !reason.trim() ||
              totalDays <= 0
            }
            onClick={() => {
              submitModeRef.current = "DRAFT";
            }}
          >
            Save draft
          </Button>
          <Button
            type="submit"
            className="h-11 rounded-full bg-foreground font-semibold text-primary-foreground hover:bg-foreground/90"
            disabled={applyLeave.isPending || !canSubmit}
            onClick={() => {
              submitModeRef.current = "SUBMITTED";
            }}
          >
            <Send className="mr-2 h-4 w-4" />
            {applyLeave.isPending ? "Submitting…" : "Submit for approval"}
          </Button>
        </div>
      </div>

      <aside className="lg:sticky lg:top-6">
        <div className="space-y-4">
          <div className="rounded-3xl border border-border bg-background p-5 shadow-sm">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="mt-2 text-base font-semibold text-foreground">{selectedLeaveLabel}</p>
              </div>
              {selectedType && <LeaveTypePill code={selectedType.code} />}
            </div>

            <div className="mt-5 space-y-4">
              <div className="rounded-full bg-border/50 h-2 overflow-hidden">
                <div
                  className="h-full rounded-full bg-foreground"
                  style={{ width: `${usedPercent}%` }}
                />
              </div>
              <div className="text-sm font-medium text-foreground">
                {Number(selectedBalance?.used || 0)} used /{" "}
                {Number(selectedBalance?.available || 0)} available
              </div>
            </div>

            <div className="mt-5 grid gap-3 text-sm text-foreground">
              <div className="flex items-center justify-between rounded-2xl bg-secondary/50 px-3 py-3">
                <span className="text-muted-foreground">Total allocated</span>
                <span className="font-semibold">
                  {selectedBalance ? Number(selectedBalance.total_allocated) : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-2xl bg-secondary/50 px-3 py-3">
                <span className="text-muted-foreground">Used</span>
                <span className="font-semibold">
                  {selectedBalance ? Number(selectedBalance.used) : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-2xl bg-secondary/50 px-3 py-3">
                <span className="text-muted-foreground">Remaining available</span>
                <span className="font-semibold">
                  {selectedBalance ? Number(selectedBalance.available) : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-2xl bg-secondary/50 px-3 py-3">
                <span className="text-muted-foreground">Expiry date</span>
                <span className="font-semibold">{selectedBalance ? expiryLabel : "—"}</span>
              </div>
            </div>

            <div className="mt-4 space-y-2 text-xs text-muted-foreground">
              <div>Applying: {applyingRangeLabel}</div>
              <div>Total: {totalDays > 0 ? `${totalDays} days` : "—"}</div>
              <div>Session: {sessionLabel}</div>
              <div>Holidays/weekends excluded when applicable.</div>
            </div>

            <div className="mt-4 space-y-2">
              {exceedsBalance && (
                <div className="rounded-2xl border border-amber-200/80 bg-amber-100/70 px-3 py-2 text-sm text-amber-900">
                  Insufficient balance for selected dates.
                </div>
              )}
              {!exceedsBalance &&
                selectedBalance &&
                remainingAfterApproval <= 1 &&
                remainingAfterApproval >= 0 && (
                  <div className="rounded-2xl border border-amber-200/80 bg-amber-100/70 px-3 py-2 text-sm text-amber-900">
                    Only {remainingAfterApproval} day remaining after this request.
                  </div>
                )}
              {carryExpirySoon && (
                <div className="rounded-2xl border border-amber-200/80 bg-amber-100/70 px-3 py-2 text-sm text-amber-900">
                  {selectedBalance?.carry_forwarded} carry-forward leaves expire in {expiryDays}{" "}
                  days.
                </div>
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-border bg-background p-4 text-sm shadow-sm">
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
              Other leave types
            </p>
            <div className="mt-3 grid gap-2">
              {balances.map((balance) => (
                <div
                  key={balance.id}
                  className="flex items-center justify-between rounded-2xl border border-border bg-secondary/50 px-3 py-2"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-foreground">
                      {balance.leave_type_detail.name}
                    </p>
                    <p className="text-xs text-muted-foreground">{balance.leave_type_detail.code}</p>
                  </div>
                  <span className="text-sm font-semibold text-foreground">
                    {Number(balance.available)} left
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </aside>
    </form>
  );
}
