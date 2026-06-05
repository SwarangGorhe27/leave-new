import { EmployeeLeaveDataProvider } from "./EmployeeLeaveDataContext";
import { LeavesPortalLayout } from "../../../components/leaves/shared/LeavesPortalLayout";
import { leavePortalBasePath } from "../../../modules/leaves/leavePortalConfig";

export function EmployeeLeavesLayout() {
  return (
    <EmployeeLeaveDataProvider>
      <LeavesPortalLayout basePath={leavePortalBasePath("employee")} />
    </EmployeeLeaveDataProvider>
  );
}
