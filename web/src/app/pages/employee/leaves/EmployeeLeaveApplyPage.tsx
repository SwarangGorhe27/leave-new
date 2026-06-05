import { leavePortalBasePath } from "../../../modules/leaves/leavePortalConfig";
import { LeaveApplyPage } from "../../leaves/portal/LeaveApplyPage";
import { useEmployeeLeaveData } from "./EmployeeLeaveDataContext";

export function EmployeeLeaveApplyPage() {
  return <LeaveApplyPage basePath={leavePortalBasePath("employee")} useLeaveData={useEmployeeLeaveData} />;
}
