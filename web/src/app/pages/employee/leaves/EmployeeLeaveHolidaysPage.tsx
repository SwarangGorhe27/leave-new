import { LeaveHolidaysPage } from "../../leaves/portal/LeaveHolidaysPage";
import { useEmployeeLeaveData } from "./EmployeeLeaveDataContext";

export function EmployeeLeaveHolidaysPage() {
  return <LeaveHolidaysPage useLeaveData={useEmployeeLeaveData} />;
}
