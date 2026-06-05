import { useMemo, useState } from "react";
import { Plus, Search, SlidersHorizontal } from "lucide-react";
import { Input } from "../../../../components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../../components/ui/table";
import { cn } from "../../../../components/ui/utils";
import { LEAVE_TYPE_MASTER } from "../../../../modules/adminLeave/mock";
import type { LeaveTypeMasterRecord } from "../../../../modules/adminLeave/types";

function BoolPill({ v }: { v: boolean }) {
  return (
    <span className={cn(
      "text-[11px] font-semibold px-2 py-0.5 rounded-md border",
      v ? "bg-foreground text-primary-foreground border-border" : "bg-secondary text-muted-foreground border-border",
    )}>
      {v ? "Yes" : "No"}
    </span>
  );
}

export function AdminLeaveTypeMaster({ onAddNewLeaveType }: { onAddNewLeaveType?: () => void }) {
  const [query, setQuery] = useState("");
  const [activeOnly, setActiveOnly] = useState(true);

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return LEAVE_TYPE_MASTER.filter((r) => {
      if (activeOnly && !r.is_active) return false;
      if (!q) return true;
      return (
        r.code.toLowerCase().includes(q) ||
        r.name.toLowerCase().includes(q) ||
        (r.description ?? "").toLowerCase().includes(q)
      );
    });
  }, [query, activeOnly]);

  const openCreate = () => {
    if (onAddNewLeaveType) {
      onAddNewLeaveType();
      return;
    }
    alert("Create/Edit drawer form is next. UI scaffold is ready.");
  };

  const openEdit = (_row: LeaveTypeMasterRecord) => {
    alert("Edit drawer form is next. UI scaffold is ready.");
  };

  return (
    <div className="space-y-5">
      <div className="flat-card bg-card overflow-hidden">
        <div className="px-6 py-4 border-b border-border flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-sm font-semibold text-foreground">Leave Type Master</h2>
            {/* <p className="text-xs text-muted-foreground mt-1">
              Configure leave types, constraints, and payroll applicability.
            </p> */}
          </div>
          <button
            type="button"
            onClick={openCreate}
            className="px-3 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground hover:bg-accent transition-colors inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Leave Type
          </button>
        </div>

        <div className="px-6 py-4 border-b border-border flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
          <div className="relative w-full sm:w-[360px]">
            <Search className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search code, name, description…" className="pl-9" />
          </div>

          <button
            type="button"
            className={cn(
              "px-3 py-2 rounded-lg text-xs font-semibold border transition-colors inline-flex items-center gap-2",
              activeOnly ? "bg-foreground text-primary-foreground border-border" : "bg-secondary text-foreground border-border hover:bg-background",
            )}
            onClick={() => setActiveOnly((v) => !v)}
          >
            <SlidersHorizontal className="w-4 h-4" />
            {activeOnly ? "Active only" : "All"}
          </button>
        </div>

        <div className="overflow-x-auto">
          <Table className="w-full">
            <TableHeader className="sticky top-0 z-10">
              <TableRow className="bg-secondary">
                {[
                  "Code",
                  "Name",
                  "Paid",
                  "Allocation",
                  "Carry Forward",
                  "Encashment",
                  "Attachment Req.",
                  "Half-day",
                  "Hourly",
                  "Gender",
                  "Leave Year",
                  "Active",
                ].map((h) => (
                  <TableHead key={h} className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider px-6 whitespace-nowrap">
                    {h}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((r) => (
                <TableRow key={r.id} className="cursor-pointer" onClick={() => openEdit(r)}>
                  <TableCell className="px-6">
                    <span className="text-sm font-semibold text-foreground">{r.code}</span>
                  </TableCell>
                  <TableCell className="px-6">
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-foreground">{r.name}</p>
                      <p className="text-xs text-muted-foreground truncate max-w-[420px]">{r.description ?? "—"}</p>
                    </div>
                  </TableCell>
                  <TableCell className="px-6"><BoolPill v={r.is_paid} /></TableCell>
                  <TableCell className="px-6 text-sm text-muted-foreground">{r.max_yearly_allocation}</TableCell>
                  <TableCell className="px-6"><BoolPill v={r.carry_forward} /></TableCell>
                  <TableCell className="px-6"><BoolPill v={r.encashment} /></TableCell>
                  <TableCell className="px-6"><BoolPill v={r.attachment_required} /></TableCell>
                  <TableCell className="px-6"><BoolPill v={r.half_day_support} /></TableCell>
                  <TableCell className="px-6"><BoolPill v={r.hourly_leave_support} /></TableCell>
                  <TableCell className="px-6 text-sm text-muted-foreground">{r.gender_applicability}</TableCell>
                  <TableCell className="px-6 text-sm text-muted-foreground">{r.leave_year_type}</TableCell>
                  <TableCell className="px-6"><BoolPill v={r.is_active} /></TableCell>
                </TableRow>
              ))}
              {rows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={12} className="px-6 py-14 text-center">
                    <p className="text-sm font-semibold text-foreground">No leave types found</p>
                    <p className="text-xs text-muted-foreground mt-1">Try changing search or filters.</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}

