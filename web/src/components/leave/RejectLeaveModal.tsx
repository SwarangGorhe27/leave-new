import { useState } from "react";
import { toast } from "sonner";
import { useRejectLeave } from "@hooks/useLeave";

type Props = {
  open: boolean;
  requestId: number | string | null;
  onClose: () => void;
};

export default function RejectLeaveModal({ open, requestId, onClose }: Props) {
  const [remarks, setRemarks] = useState("");
  const rejectMutation = useRejectLeave();

  if (!open || !requestId) return null;

  const submit = () => {
    if (remarks.trim().length < 10) {
      toast.error("Remarks must be at least 10 characters.");
      return;
    }
    rejectMutation.mutate(
      { id: requestId, remarks: remarks.trim() },
      {
        onSuccess: () => {
          toast.success("Leave request rejected.");
          onClose();
          setRemarks("");
        },
      },
    );
  };

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-lg bg-card p-4">
        <h3 className="text-lg font-semibold">Reject Leave</h3>
        <textarea
          className="mt-3 w-full rounded border border-border p-2"
          rows={4}
          value={remarks}
          onChange={(e) => setRemarks(e.target.value)}
          placeholder="Add rejection remarks"
        />
        <div className="mt-3 flex justify-end gap-2">
          <button className="rounded border border-border px-3 py-2" onClick={onClose}>
            Cancel
          </button>
          <button className="rounded bg-destructive px-3 py-2 text-white" onClick={submit}>
            Reject
          </button>
        </div>
      </div>
    </div>
  );
}
