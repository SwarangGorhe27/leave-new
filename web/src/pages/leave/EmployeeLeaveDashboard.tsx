import { useState } from "react";
import ApplyLeaveModal from "@components/leave/ApplyLeaveModal";
import LeaveBalanceCard from "@components/leave/LeaveBalanceCard";
import LeaveRequestTable from "@components/leave/LeaveRequestTable";
import { useMyLeaveBalances, useMyLeaveRequests } from "@hooks/useLeave";

export default function EmployeeLeaveDashboard() {
  const [openModal, setOpenModal] = useState(false);
  const { data: balances = [] } = useMyLeaveBalances();
  const { data: requests = [] } = useMyLeaveRequests();

  return (
    <div className="space-y-6 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Leave Dashboard</h1>
        <button className="rounded bg-primary px-3 py-2 text-primary-foreground" onClick={() => setOpenModal(true)}>
          Apply Leave
        </button>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        {balances.map((balance) => (
          <LeaveBalanceCard key={String(balance.id)} balance={balance} />
        ))}
      </div>
      <LeaveRequestTable rows={requests} />
      <ApplyLeaveModal open={openModal} onClose={() => setOpenModal(false)} balances={balances} />
    </div>
  );
}
