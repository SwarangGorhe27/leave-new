import { PieChart } from "lucide-react";
import type { LeaveBalanceAPI } from "../../../modules/leaves/types";
import { cn } from "../../ui/utils";
import { LeaveEmptyState } from "./LeaveEmptyState";
import { LeaveTypePill } from "./LeaveTypePill";
import { formatLeaveShortDate } from "./leaveDateUtils";

function computeLeaveCode(detail?: { code?: string | null; name?: string | null }, rawName?: string | null) {
  const c = detail?.code?.trim();
  if (c) return c.toUpperCase();
  const n = detail?.name?.trim() || rawName?.trim();
  if (n) return n.split(' ').map((s) => s[0]).join('').slice(0, 2).toUpperCase();
  return 'L';
}

export function EnterpriseBalanceGrid({ balances }: { balances: LeaveBalanceAPI[] }) {
  if (balances.length === 0) {
    return (
      <LeaveEmptyState
        icon={PieChart}
        title="No leave balances"
        description="Once HR configures entitlements, your balances will appear here."
      />
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {balances.map((b, idx) => {
        const name = b.leave_type_detail?.name ?? b.leave_type ?? "Leave";
        const code = computeLeaveCode(b.leave_type_detail, b.leave_type ?? name);
        console.log("Balance Card", b);
        // ── Prefer normalised aliases populated by useLeave's normaliseBalance()
        // ── Fall back to raw serializer fields so the component works even if
        //    the normaliser hasn't run (e.g. admin serializer path).
        const totalAllocated = Number(b.total_allocated ?? b.opening ?? 0);
        const used           = Number(b.used  ?? b.taken   ?? 0);
        const available      = Number(b.available ?? b.balance ?? 0);
        const pending        = Number(b.pending_approval ?? b.pending_days ?? 0);
        const isPaid         = b.leave_type_detail?.is_paid ?? true;

        const pct = totalAllocated > 0 ? Math.min((used / totalAllocated) * 100, 100) : 0;

        // Derive period dates: prefer normalised aliases, fall back to raw fields
        const periodStart = b.period_start ?? b.leave_year_start ?? "";
        const periodEnd   = b.period_end   ?? b.leave_year_end   ?? "";

        return (
          <div
            key={b.leave_type_id ?? b.id ?? idx}
            className={cn(
              "flat-card flat-card-hover bg-card overflow-hidden transition-all duration-200",
            )}
          >
            <div className="flex items-start justify-between gap-3 border-b border-border px-4 py-3">
              <div className="flex min-w-0 items-center gap-2.5">
                <LeaveTypePill code={code} />
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-foreground">{name}</p>
                  <p className="text-[11px] text-muted-foreground">
                    {code} · {isPaid ? "Paid" : "Unpaid"}
                  </p>
                </div>
              </div>
              {pending > 0 && (
                <span className="flex-shrink-0 rounded-md border border-border bg-secondary px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
                  {pending} pending
                </span>
              )}
            </div>

            <div className="space-y-3 px-4 py-3">
              <div className="grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="text-base font-bold tabular-nums text-foreground">{totalAllocated}</p>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Alloc</p>
                </div>
                <div>
                  <p className="text-base font-bold tabular-nums text-foreground/80">{used}</p>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Used</p>
                </div>
                <div>
                  <p className="text-base font-bold tabular-nums text-foreground">{available}</p>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Left</p>
                </div>
              </div>

              <div>
                <div className="mb-1 flex justify-between text-[11px] font-medium text-muted-foreground">
                  <span>Utilization</span>
                  <span className="tabular-nums">{pct.toFixed(0)}%</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full border border-border bg-secondary">
                  <div
                    className="h-full rounded-full bg-foreground/80 transition-[width] duration-500 ease-out"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>

              {periodStart && periodEnd && (
                <p className="text-[11px] text-muted-foreground">
                  Period {formatLeaveShortDate(periodStart)} — {formatLeaveShortDate(periodEnd)}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}