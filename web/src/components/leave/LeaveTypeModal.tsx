import { useState } from "react";
import {
  useCreateLeaveType,
  useUpdateLeaveType,
} from "@hooks/useLeave";
import type { LeaveType, LeaveTypePayload } from "@types/leave";

type Props = {
  open: boolean;
  mode: "create" | "edit";
  initial?: LeaveType | null;
  onClose: () => void;
};

export default function LeaveTypeModal({ open, mode, initial, onClose }: Props) {
  const createMutation = useCreateLeaveType();
  const updateMutation = useUpdateLeaveType();
  const [form, setForm] = useState<LeaveTypePayload>({
    name: initial?.name ?? "",
    code: initial?.code ?? "",
    max_days_per_year: Number(initial?.max_days_per_year ?? 0),
    carry_forward: initial?.carry_forward ?? false,
    is_active: initial?.is_active ?? true,
  });

  if (!open) return null;

  const submit = () => {
    const payload = { ...form, code: form.code.toUpperCase().replace(/\s+/g, "") };
    if (mode === "create") {
      createMutation.mutate(payload, { onSuccess: onClose });
      return;
    }
    if (initial?.id) {
      updateMutation.mutate({ id: initial.id, payload }, { onSuccess: onClose });
    }
  };

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-lg bg-card p-4">
        <h3 className="text-lg font-semibold">{mode === "create" ? "Create" : "Edit"} Leave Type</h3>
        <div className="mt-3 grid gap-2">
          <input className="rounded border p-2" placeholder="Name" value={form.name} onChange={(e) => setForm((s) => ({ ...s, name: e.target.value }))} />
          <input className="rounded border p-2" placeholder="Code" value={form.code} onChange={(e) => setForm((s) => ({ ...s, code: e.target.value }))} />
          <input className="rounded border p-2" type="number" placeholder="Max Days" value={form.max_days_per_year} onChange={(e) => setForm((s) => ({ ...s, max_days_per_year: Number(e.target.value) }))} />
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.carry_forward} onChange={(e) => setForm((s) => ({ ...s, carry_forward: e.target.checked }))} /> Carry Forward</label>
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm((s) => ({ ...s, is_active: e.target.checked }))} /> Is Active</label>
        </div>
        <div className="mt-3 flex justify-end gap-2">
          <button className="rounded border px-3 py-2" onClick={onClose}>Cancel</button>
          <button className="rounded bg-primary px-3 py-2 text-primary-foreground" onClick={submit}>Save</button>
        </div>
      </div>
    </div>
  );
}
