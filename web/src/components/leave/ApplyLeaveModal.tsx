import { useMemo, useState } from "react";
import { toast } from "sonner";
import { useApplyLeave, useLeaveTypes } from "@hooks/useLeave";
import type { LeaveBalance, LeaveRequestPayload } from "@types/leave";

type Props = {
  open: boolean;
  onClose: () => void;
  balances: LeaveBalance[];
};

function calculateWorkingDays(startDate: string, endDate: string) {
  if (!startDate || !endDate) return 0;
  const start = new Date(startDate);
  const end = new Date(endDate);
  let days = 0;
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const weekday = d.getDay();
    if (weekday !== 0 && weekday !== 6) {
      days += 1;
    }
  }
  return days;
}

export default function ApplyLeaveModal({ open, onClose, balances }: Props) {
  const { data: leaveTypes = [] } = useLeaveTypes();
  const mutation = useApplyLeave();
  const [payload, setPayload] = useState<LeaveRequestPayload>({
    leave_type_id: "",
    start_date: "",
    end_date: "",
    reason: "",
  });

  const totalDays = useMemo(
    () => calculateWorkingDays(payload.start_date, payload.end_date),
    [payload.start_date, payload.end_date],
  );

  const remaining = useMemo(() => {
    const found = balances.find((b) => String(b.leave_type?.id) === String(payload.leave_type_id));
    return found ? Number(found.remaining_days) : 0;
  }, [balances, payload.leave_type_id]);

  if (!open) return null;

  const submit = () => {
    if (totalDays <= 0) {
      toast.error("Select a valid date range.");
      return;
    }
    if (remaining < totalDays) {
      toast.error("Insufficient remaining leave balance.");
      return;
    }
    mutation.mutate(payload, {
      onSuccess: () => {
        toast.success("Leave request submitted.");
        onClose();
      },
      onError: () => toast.error("Could not submit leave request."),
    });
  };

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-lg bg-card p-4">
        <h2 className="mb-4 text-lg font-semibold">Apply Leave</h2>
        <div className="grid gap-3">
          <select
            className="rounded border border-border p-2"
            value={String(payload.leave_type_id)}
            onChange={(e) => setPayload((prev) => ({ ...prev, leave_type_id: e.target.value }))}
          >
            <option value="">Select Leave Type</option>
            {leaveTypes.map((item) => (
              <option key={String(item.id)} value={String(item.id)}>
                {item.name}
              </option>
            ))}
          </select>
          <input
            type="date"
            className="rounded border border-border p-2"
            value={payload.start_date}
            onChange={(e) => setPayload((prev) => ({ ...prev, start_date: e.target.value }))}
          />
          <input
            type="date"
            className="rounded border border-border p-2"
            value={payload.end_date}
            onChange={(e) => setPayload((prev) => ({ ...prev, end_date: e.target.value }))}
          />
          <textarea
            className="rounded border border-border p-2"
            placeholder="Reason"
            value={payload.reason}
            onChange={(e) => setPayload((prev) => ({ ...prev, reason: e.target.value }))}
          />
          <p className="text-sm text-muted-foreground">
            Working days: {totalDays} | Remaining: {remaining}
          </p>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button className="rounded border border-border px-3 py-2" onClick={onClose}>
            Close
          </button>
          <button className="rounded bg-primary px-3 py-2 text-primary-foreground" onClick={submit}>
            Submit
          </button>
        </div>
      </div>
    </div>
  );
}
