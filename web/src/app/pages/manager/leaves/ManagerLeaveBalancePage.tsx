import { LeaveBalancePage } from "../../leaves/portal/LeaveBalancePage";
import { useManagerLeaveData } from "./ManagerLeaveDataContext";

export function ManagerLeaveBalancePage() {
  return <LeaveBalancePage useLeaveData={useManagerLeaveData} />;
}
