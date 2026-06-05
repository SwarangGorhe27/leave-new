import { LeaveNotificationsPage } from "../../leaves/portal/LeaveNotificationsPage";
import { useManagerLeaveData } from "./ManagerLeaveDataContext";

export function ManagerLeaveNotificationsPage() {
  return <LeaveNotificationsPage useLeaveData={useManagerLeaveData} />;
}
