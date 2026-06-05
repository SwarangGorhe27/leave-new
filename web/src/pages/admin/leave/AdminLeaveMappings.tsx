import { useMemo, useState } from "react";
import LeaveMappingModal from "@components/leave/LeaveMappingModal";
import { useDeleteLeaveMapping, useLeaveMappings } from "@hooks/useLeave";
import type { LeaveMapping } from "@types/leave";

export default function AdminLeaveMappings() {
  const [role, setRole] = useState("");
  const { data = [] } = useLeaveMappings(role || undefined);
  const deleteMutation = useDeleteLeaveMapping();
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<LeaveMapping | null>(null);

  const roles = useMemo(() => Array.from(new Set(data.map((item) => item.role))), [data]);

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Leave Mappings</h1>
        <button className="rounded bg-primary px-3 py-2 text-primary-foreground" onClick={() => { setEditing(null); setModalOpen(true); }}>
          Add
        </button>
      </div>
      <select className="rounded border border-border p-2" value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="">All Roles</option>
        {roles.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="bg-secondary/40 text-left">
            <tr>
              <th className="p-3">Role</th>
              <th className="p-3">Leave Type</th>
              <th className="p-3">Allowed Days</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={String(item.id)} className="border-t border-border">
                <td className="p-3">{item.role}</td>
                <td className="p-3">{item.leave_type?.name}</td>
                <td className="p-3">{item.allowed_days}</td>
                <td className="p-3">
                  <div className="flex gap-2">
                    <button className="rounded border px-2 py-1" onClick={() => { setEditing(item); setModalOpen(true); }}>
                      Edit
                    </button>
                    <button className="rounded bg-destructive px-2 py-1 text-white" onClick={() => deleteMutation.mutate(item.id)}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <LeaveMappingModal open={modalOpen} mode={editing ? "edit" : "create"} initial={editing} onClose={() => setModalOpen(false)} />
    </div>
  );
}
