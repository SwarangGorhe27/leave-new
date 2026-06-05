import { useState } from "react";
import {
  useCreateLeaveMapping,
  useLeaveTypes,
  useUpdateLeaveMapping,
} from "@hooks/useLeave";
import type { LeaveMapping, LeaveMappingPayload } from "@types/leave";

type Props = {
  open: boolean;
  mode: "create" | "edit";
  initial?: LeaveMapping | null;
  onClose: () => void;
};

export default function LeaveMappingModal({ open, mode, initial, onClose }: Props) {
  const { data: leaveTypes = [] } = useLeaveTypes();
  const createMutation = useCreateLeaveMapping();
  const updateMutation = useUpdateLeaveMapping();
  const [form, setForm] = useState<LeaveMappingPayload>({
    role: initial?.role ?? "",
    leave_type_id: initial?.leave_type?.id ?? "",
    allowed_days: Number(initial?.allowed_days ?? 0),
  });

  if (!open) return null;

  const submit = () => {
    if (mode === "create") {
      createMutation.mutate(form, { onSuccess: onClose });
      return;
    }
    if (initial?.id) {
      updateMutation.mutate({ id: initial.id, payload: form }, { onSuccess: onClose });
    }
  };

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-lg bg-card p-4">
        <h3 className="text-lg font-semibold">{mode === "create" ? "Add" : "Edit"} Leave Mapping</h3>
        <div className="mt-3 grid gap-2">
          <input
            className="rounded border p-2"
            placeholder="Role"
            value={form.role}
            onChange={(e) => setForm((s) => ({ ...s, role: e.target.value }))}
          />
          <select
            className="rounded border p-2"
            value={String(form.leave_type_id)}
            onChange={(e) => setForm((s) => ({ ...s, leave_type_id: e.target.value }))}
          >
            <option value="">Select leave type</option>
            {leaveTypes.map((item) => (
              <option key={String(item.id)} value={String(item.id)}>
                {item.name}
              </option>
            ))}
          </select>
          <input
            className="rounded border p-2"
            type="number"
            placeholder="Allowed Days"
            value={form.allowed_days}
            onChange={(e) => setForm((s) => ({ ...s, allowed_days: Number(e.target.value) }))}
          />
        </div>
        <div className="mt-3 flex justify-end gap-2">
          <button className="rounded border px-3 py-2" onClick={onClose}>
            Cancel
          </button>
          <button className="rounded bg-primary px-3 py-2 text-primary-foreground" onClick={submit}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
