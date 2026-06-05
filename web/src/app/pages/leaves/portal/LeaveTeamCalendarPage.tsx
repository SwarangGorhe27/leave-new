import { Users } from "lucide-react";
import { LeaveEmptyState } from "../../../components/leaves/employee/LeaveEmptyState";
import { LeaveTypePill } from "../../../components/leaves/employee/LeaveTypePill";
import { formatLeaveShortDate } from "../../../components/leaves/employee/leaveDateUtils";
import { EmployeeLeaveStatusBadge } from "../../../components/leaves/employee/EmployeeLeaveStatusBadge";
import type { LeavePortalDataContextValue } from "../LeavePortalDataContext";

export function LeaveTeamCalendarPage({
  useLeaveData,
}: {
  useLeaveData: () => Pick<LeavePortalDataContextValue, "teamApplications">;
}) {
  const { teamApplications } = useLeaveData();
  const today = new Date().toISOString().slice(0, 10);
  const rows = [...teamApplications]
    .filter((a) => a.to_date >= today)
    .sort((a, b) => a.from_date.localeCompare(b.from_date));

  return (
    <div className="space-y-6">
      <header className="mb-2">
        <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">Team calendar</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Approved team leave visible to you — helps plan handovers and coverage.
        </p>
      </header>

      {rows.length === 0 ? (
        <LeaveEmptyState
          icon={Users}
          title="No team leave data"
          description="When colleagues publish approved time off, it will surface here for coordination."
        />
      ) : (
        <div className="flat-card overflow-hidden bg-card">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left">
              <thead className="sticky top-0 z-10 bg-secondary/95 backdrop-blur-sm">
                <tr className="border-b border-border">
                  {["Team member", "Leave", "From", "To", "Days", "Status"].map((h) => (
                    <th
                      key={h}
                      className="whitespace-nowrap px-4 py-2.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {rows.map((a) => (
                  <tr key={a.id} className="transition-colors hover:bg-secondary/50">
                    <td className="px-4 py-2.5 text-sm font-medium text-foreground">{a.employee_name}</td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <LeaveTypePill code={a.leave_type_detail?.code ?? "—"} />
                        <span className="text-sm text-foreground">{a.leave_type_detail?.name}</span>
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-4 py-2.5 text-xs text-muted-foreground">
                      {formatLeaveShortDate(a.from_date)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2.5 text-xs text-muted-foreground">
                      {formatLeaveShortDate(a.to_date)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2.5 text-sm font-semibold tabular-nums">{a.total_days}</td>
                    <td className="px-4 py-2.5">
                      <EmployeeLeaveStatusBadge status={a.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
