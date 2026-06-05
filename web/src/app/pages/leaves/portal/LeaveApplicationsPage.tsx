import { ApplicationsHistoryTable } from "../../../components/leaves/employee/ApplicationsHistoryTable";
import type { LeavePortalDataContextValue } from "../LeavePortalDataContext";

export function LeaveApplicationsPage({
  useLeaveData,
}: {
  useLeaveData: () => Pick<
    LeavePortalDataContextValue,
    "role" | "applications" | "leaveTypes"
  >;
}) {
  const { applications, leaveTypes } = useLeaveData();
  const leaveTypeOptions = leaveTypes.map((lt) => ({ id: lt.id, name: lt.name, code: lt.code }));

  return (
    <div className="space-y-6">
      <header className="mb-2">
        {/* <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">My applications</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Filterable ledger with export — optimized for dense enterprise review.
        </p> */}
      </header>
      <ApplicationsHistoryTable applications={applications} leaveTypeOptions={leaveTypeOptions} />
    </div>
  );
}
