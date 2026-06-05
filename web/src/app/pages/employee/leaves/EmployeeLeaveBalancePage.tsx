import { LeaveBalancePage } from "../../leaves/portal/LeaveBalancePage";
import { useEmployeeLeaveData } from "./EmployeeLeaveDataContext";

export function EmployeeLeaveBalancePage() {
  return <LeaveBalancePage useLeaveData={useEmployeeLeaveData} />;
}
