import { LeaveHolidaysPage } from "../../leaves/portal/LeaveHolidaysPage";
import { useManagerLeaveData } from "./ManagerLeaveDataContext";

export function ManagerLeaveHolidaysPage() {
  return <LeaveHolidaysPage useLeaveData={useManagerLeaveData} />;
}
