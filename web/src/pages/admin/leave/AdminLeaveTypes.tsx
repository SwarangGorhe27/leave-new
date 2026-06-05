import { useState } from "react";
import LeaveTypeModal from "@components/leave/LeaveTypeModal";
import { useDeleteLeaveType, useLeaveTypes } from "@hooks/useLeave";
import type { LeaveType } from "@types/leave";

export default function AdminLeaveTypes() {
  const { data = [] } = useLeaveTypes();
  const deleteMutation = useDeleteLeaveType();
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<LeaveType | null>(null);

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Leave Types</h1>
        <button className="rounded bg-primary px-3 py-2 text-primary-foreground" onClick={() => { setEditing(null); setModalOpen(true); }}>
          Add
        </button>
      </div>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="bg-secondary/40 text-left">
            <tr>
              <th className="p-3">Name</th>
              <th className="p-3">Code</th>
              <th className="p-3">Max Days</th>
              <th className="p-3">Carry Forward</th>
              <th className="p-3">Active</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={String(item.id)} className="border-t border-border">
                <td className="p-3">{item.name}</td>
                <td className="p-3">{item.code}</td>
                <td className="p-3">{item.max_days_per_year}</td>
                <td className="p-3">{item.carry_forward ? "Yes" : "No"}</td>
                <td className="p-3">{item.is_active ? "Yes" : "No"}</td>
                <td className="p-3">
                  <div className="flex gap-2">
                    <button className="rounded border px-2 py-1" onClick={() => { setEditing(item); setModalOpen(true); }}>
                      Edit
                    </button>
                    <button className="rounded bg-destructive px-2 py-1 text-white" onClick={() => deleteMutation.mutate(item.id)}>
                      Deactivate
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <LeaveTypeModal open={modalOpen} mode={editing ? "edit" : "create"} initial={editing} onClose={() => setModalOpen(false)} />
    </div>
  );
}
