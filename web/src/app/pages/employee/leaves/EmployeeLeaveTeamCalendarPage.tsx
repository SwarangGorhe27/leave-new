import { LeaveTeamCalendarPage } from "../../leaves/portal/LeaveTeamCalendarPage";
import { useEmployeeLeaveData } from "./EmployeeLeaveDataContext";

export function EmployeeLeaveTeamCalendarPage() {
  return <LeaveTeamCalendarPage useLeaveData={useEmployeeLeaveData} />;
}
