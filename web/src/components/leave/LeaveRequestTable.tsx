import { useCancelLeave } from "@hooks/useLeave";
import { LeaveStatus, type LeaveRequest } from "@types/leave";

type Props = {
  rows: LeaveRequest[];
};

const STATUS_CLASSES: Record<LeaveStatus, string> = {
  [LeaveStatus.PENDING]: "bg-yellow-100 text-yellow-800",
  [LeaveStatus.APPROVED]: "bg-green-100 text-green-800",
  [LeaveStatus.REJECTED]: "bg-red-100 text-red-800",
  [LeaveStatus.CANCELLED]: "bg-gray-200 text-gray-800",
};

export default function LeaveRequestTable({ rows }: Props) {
  const cancelMutation = useCancelLeave();

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead className="bg-secondary/40 text-left">
          <tr>
            <th className="p-3">Leave Type</th>
            <th className="p-3">From</th>
            <th className="p-3">To</th>
            <th className="p-3">Days</th>
            <th className="p-3">Status</th>
            <th className="p-3">Applied On</th>
            <th className="p-3">Action</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((item) => (
            <tr key={String(item.id)} className="border-t border-border">
              <td className="p-3">{item.leave_type?.name}</td>
              <td className="p-3">{item.start_date}</td>
              <td className="p-3">{item.end_date}</td>
              <td className="p-3">{item.total_days}</td>
              <td className="p-3">
                <span className={`rounded px-2 py-1 text-xs ${STATUS_CLASSES[item.status]}`}>
                  {item.status}
                </span>
              </td>
              <td className="p-3">{new Date(item.applied_on).toLocaleDateString()}</td>
              <td className="p-3">
                {item.status === LeaveStatus.PENDING ? (
                  <button
                    className="rounded bg-destructive px-2 py-1 text-xs text-white"
                    onClick={() => cancelMutation.mutate(item.id)}
                  >
                    Cancel
                  </button>
                ) : (
                  "-"
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
