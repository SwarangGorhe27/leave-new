import { LeaveNotificationCenter } from "../../../components/leaves/employee/LeaveNotificationCenter";
import type { LeavePortalDataContextValue } from "../LeavePortalDataContext";

export function LeaveNotificationsPage({
  useLeaveData,
}: {
  useLeaveData: () => Pick<LeavePortalDataContextValue, "applications" | "holidays">;
}) {
  const { applications, holidays } = useLeaveData();

  return (
    <div className="space-y-6">
      <header className="mb-2">
        {/* <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">Notifications</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Leave lifecycle signals and upcoming holidays in one dense stream.
        </p> */}
      </header>
      <LeaveNotificationCenter applications={applications} holidays={holidays} />
    </div>
  );
}
