import { leavePortalBasePath } from "../../../modules/leaves/leavePortalConfig";
import { LeaveApplyPage } from "../../leaves/portal/LeaveApplyPage";
import { useManagerLeaveData } from "./ManagerLeaveDataContext";

export function ManagerLeaveApplyPage() {
  return <LeaveApplyPage basePath={leavePortalBasePath("manager")} useLeaveData={useManagerLeaveData} />;
}
