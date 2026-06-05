import { PieChart } from "lucide-react";
import type { LeaveBalanceAPI } from "../../../modules/leaves/types";
import { cn } from "../../ui/utils";
import { LeaveEmptyState } from "./LeaveEmptyState";
import { LeaveTypePill } from "./LeaveTypePill";
import { formatLeaveShortDate } from "./leaveDateUtils";

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
      {balances.map((b) => {
        const code = b.leave_type_detail?.code ?? "—";
        const name = b.leave_type_detail?.name ?? "Leave";
        const total = Number(b.total_allocated) || 0;
        const used = Number(b.used) || 0;
        const available = Number(b.available) || 0;
        const pending = Number(b.pending_approval) || 0;
        const pct = total > 0 ? Math.min((used / total) * 100, 100) : 0;

        return (
          <div
            key={b.id}
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
                    {code} · {b.leave_type_detail?.is_paid ? "Paid" : "Unpaid"}
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
                  <p className="text-base font-bold tabular-nums text-foreground">{total}</p>
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

              <p className="text-[11px] text-muted-foreground">
                Period {formatLeaveShortDate(b.period_start)} — {formatLeaveShortDate(b.period_end)}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
