import { LeaveTeamCalendarPage } from "../../leaves/portal/LeaveTeamCalendarPage";
import { useManagerLeaveData } from "./ManagerLeaveDataContext";

export function ManagerLeaveTeamCalendarPage() {
  return <LeaveTeamCalendarPage useLeaveData={useManagerLeaveData} />;
}
