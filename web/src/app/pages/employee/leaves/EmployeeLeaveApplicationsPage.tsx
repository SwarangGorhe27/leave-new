import { LeaveApplicationsPage } from "../../leaves/portal/LeaveApplicationsPage";
import { useEmployeeLeaveData } from "./EmployeeLeaveDataContext";

export function EmployeeLeaveApplicationsPage() {
  return <LeaveApplicationsPage useLeaveData={useEmployeeLeaveData} />;
}
