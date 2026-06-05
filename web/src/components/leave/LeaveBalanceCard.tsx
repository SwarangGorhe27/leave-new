import type { LeaveBalance } from "@types/leave";

type Props = {
  balance: LeaveBalance;
};

export default function LeaveBalanceCard({ balance }: Props) {
  const used = Number(balance.used_days || 0);
  const total = Number(balance.total_days || 0);
  const remaining = Number(balance.remaining_days || 0);
  const percent = total > 0 ? Math.min(100, (used / total) * 100) : 0;

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="font-semibold">{balance.leave_type?.name ?? "Leave"}</h3>
      <p className="text-sm text-muted-foreground">
        {used} / {total} days used
      </p>
      <div className="mt-2 h-2 rounded bg-secondary">
        <div className="h-2 rounded bg-primary" style={{ width: `${percent}%` }} />
      </div>
      <p className="mt-2 text-sm font-medium">Remaining: {remaining}</p>
    </div>
  );
}
