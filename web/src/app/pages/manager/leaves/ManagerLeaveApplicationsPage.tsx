import { LeaveApplicationsPage } from "../../leaves/portal/LeaveApplicationsPage";
import { useManagerLeaveData } from "./ManagerLeaveDataContext";

export function ManagerLeaveApplicationsPage() {
  return <LeaveApplicationsPage useLeaveData={useManagerLeaveData} />;
}
