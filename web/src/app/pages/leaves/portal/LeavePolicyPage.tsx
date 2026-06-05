import { ScrollText } from "lucide-react";
import { LeaveTypePill } from "../../../components/leaves/employee/LeaveTypePill";
import type { LeavePortalDataContextValue } from "../LeavePortalDataContext";

export function LeavePolicyPage({
  useLeaveData,
}: {
  useLeaveData: () => Pick<LeavePortalDataContextValue, "leaveTypes">;
}) {
  const { leaveTypes } = useLeaveData();

  return (
    <div className="space-y-6">
      <header className="mb-2">
        {/* <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">Leave policy</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Canonical leave classes enabled for your organization. Detailed legal policy PDFs typically live in Documents.
        </p> */}
      </header>

      <div className="grid gap-3 md:grid-cols-2">
        {leaveTypes.map((lt) => (
          <div key={lt.id} className="flat-card flat-card-hover bg-card p-4 transition-shadow">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border border-border bg-secondary">
                <ScrollText className="h-5 w-5 text-muted-foreground" aria-hidden />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <LeaveTypePill code={lt.code} />
                  <h2 className="text-sm font-semibold text-foreground">{lt.name}</h2>
                </div>
                <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                  {lt.is_paid
                    ? "Paid leave bucket subject to accrual and manager approval. Carry-forward rules follow company schedule."
                    : "Unpaid absence type for exceptional cases. Requires HR acknowledgement and may impact payroll."}
                </p>
                <p className="mt-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Code {lt.code} · {lt.is_paid ? "Paid" : "Unpaid"}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
