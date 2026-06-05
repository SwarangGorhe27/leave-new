import { LeavePolicyPage } from "../../leaves/portal/LeavePolicyPage";
import { useEmployeeLeaveData } from "./EmployeeLeaveDataContext";

export function EmployeeLeavePolicyPage() {
  return <LeavePolicyPage useLeaveData={useEmployeeLeaveData} />;
}
