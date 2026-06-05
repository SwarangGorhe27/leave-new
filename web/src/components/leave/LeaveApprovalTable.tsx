import { useState } from "react";
import { useApproveLeave } from "@hooks/useLeave";
import type { LeaveRequest } from "@types/leave";
import RejectLeaveModal from "./RejectLeaveModal";

type Props = {
  rows: LeaveRequest[];
};

export default function LeaveApprovalTable({ rows }: Props) {
  const approveMutation = useApproveLeave();
  const [rejectRequestId, setRejectRequestId] = useState<number | string | null>(null);

  return (
    <>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="bg-secondary/40 text-left">
            <tr>
              <th className="p-3">Employee</th>
              <th className="p-3">Leave Type</th>
              <th className="p-3">From</th>
              <th className="p-3">To</th>
              <th className="p-3">Days</th>
              <th className="p-3">Reason</th>
              <th className="p-3">Status</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((item) => (
              <tr key={String(item.id)} className="border-t border-border">
                <td className="p-3">{String(item.employee)}</td>
                <td className="p-3">{item.leave_type?.name}</td>
                <td className="p-3">{item.start_date}</td>
                <td className="p-3">{item.end_date}</td>
                <td className="p-3">{item.total_days}</td>
                <td className="p-3">{item.reason}</td>
                <td className="p-3">{item.status}</td>
                <td className="p-3">
                  {item.status === "PENDING" ? (
                    <div className="flex gap-2">
                      <button
                        className="rounded bg-green-600 px-2 py-1 text-white"
                        onClick={() => approveMutation.mutate({ id: item.id })}
                      >
                        Approve
                      </button>
                      <button
                        className="rounded bg-destructive px-2 py-1 text-white"
                        onClick={() => setRejectRequestId(item.id)}
                      >
                        Reject
                      </button>
                    </div>
                  ) : (
                    "-"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <RejectLeaveModal
        open={Boolean(rejectRequestId)}
        requestId={rejectRequestId}
        onClose={() => setRejectRequestId(null)}
      />
    </>
  );
}
