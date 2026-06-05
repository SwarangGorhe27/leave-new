import { useState } from "react";
import LeaveApprovalTable from "@components/leave/LeaveApprovalTable";
import { useTeamLeaveRequests } from "@hooks/useLeave";

export default function ManagerLeaveApprovals() {
  const [tab, setTab] = useState<"pending" | "all">("pending");
  const { data = [] } = useTeamLeaveRequests(tab === "pending" ? { status: "PENDING" } : undefined);

  return (
    <div className="space-y-4 p-4">
      <h1 className="text-2xl font-semibold">Leave Approvals</h1>
      <div className="flex gap-2">
        <button className={`rounded px-3 py-2 ${tab === "pending" ? "bg-primary text-primary-foreground" : "bg-secondary"}`} onClick={() => setTab("pending")}>
          Pending
        </button>
        <button className={`rounded px-3 py-2 ${tab === "all" ? "bg-primary text-primary-foreground" : "bg-secondary"}`} onClick={() => setTab("all")}>
          All
        </button>
      </div>
      <LeaveApprovalTable rows={data} />
    </div>
  );
}
