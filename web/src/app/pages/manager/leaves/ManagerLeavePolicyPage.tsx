import { LeavePolicyPage } from "../../leaves/portal/LeavePolicyPage";
import { useManagerLeaveData } from "./ManagerLeaveDataContext";

export function ManagerLeavePolicyPage() {
  return <LeavePolicyPage useLeaveData={useManagerLeaveData} />;
}
