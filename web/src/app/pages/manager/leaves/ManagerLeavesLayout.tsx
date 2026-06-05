import { ManagerLeaveDataProvider } from "./ManagerLeaveDataContext";
import { LeavesPortalLayout } from "../../../components/leaves/shared/LeavesPortalLayout";
import { leavePortalBasePath } from "../../../modules/leaves/leavePortalConfig";

export function ManagerLeavesLayout() {
  return (
    <ManagerLeaveDataProvider>
      <LeavesPortalLayout basePath={leavePortalBasePath("manager")} />
    </ManagerLeaveDataProvider>
  );
}
