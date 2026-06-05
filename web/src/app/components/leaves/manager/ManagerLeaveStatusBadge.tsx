import type { LeaveApplicationStatus } from "../../../modules/leaves/types";
import { cn } from "../../ui/utils";

const DISPLAY: Record<string, string> = {
  DRAFT: "Draft",
  SUBMITTED: "Pending",
  PENDING: "Pending",
  APPROVED: "Approved",
  REJECTED: "Rejected",
  CANCELLED: "Cancelled",
  REVOKED: "Withdrawn",
  WITHDRAWN: "Withdrawn",
  ESCALATED: "Escalated",
  AUTO_APPROVED: "Auto Approved",
};

const STYLE: Record<string, string> = {
  DRAFT: "bg-muted/80 text-foreground border-border",
  SUBMITTED: "bg-secondary text-foreground border-border",
  PENDING: "bg-secondary text-foreground border-border",
  APPROVED: "bg-foreground/5 text-foreground border-foreground/20",
  REJECTED: "bg-secondary text-foreground border-destructive/30",
  CANCELLED: "bg-muted/50 text-muted-foreground border-border",
  REVOKED: "bg-muted/50 text-muted-foreground border-border",
  WITHDRAWN: "bg-muted/50 text-muted-foreground border-border",
  ESCALATED: "bg-secondary text-foreground border-foreground/25",
  AUTO_APPROVED: "bg-foreground/5 text-foreground border-foreground/20",
};

function normalizeKey(status: string): string {
  const u = status.toUpperCase();
  if (u in DISPLAY) return u;
  return status;
}

export function employeeLeaveStatusLabel(status: LeaveApplicationStatus | string): string {
  const k = normalizeKey(String(status));
  return DISPLAY[k] ?? status;
}

export function ManagerLeaveStatusBadge({
  status,
  className,
}: {
  status: LeaveApplicationStatus | string;
  className?: string;
}) {
  const k = normalizeKey(String(status));
  const label = DISPLAY[k] ?? status;
  const style = STYLE[k] ?? "bg-secondary text-foreground border-border";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-semibold tracking-wide",
        "transition-colors duration-150",
        style,
        className,
      )}
    >
      <span className="h-1 w-1 rounded-full bg-current opacity-50" aria-hidden />
      {label}
    </span>
  );
}
