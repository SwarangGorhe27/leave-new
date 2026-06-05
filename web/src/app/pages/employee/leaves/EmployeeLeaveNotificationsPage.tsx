import { LeaveNotificationsPage } from "../../leaves/portal/LeaveNotificationsPage";
import { useEmployeeLeaveData } from "./EmployeeLeaveDataContext";

export function EmployeeLeaveNotificationsPage() {
  return <LeaveNotificationsPage useLeaveData={useEmployeeLeaveData} />;
}
