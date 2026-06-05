import { Fragment, useMemo, useState } from "react";
import { attendanceDataset, useAttendanceStore } from "../../modules/attendance/store";
import { KebabMenu } from "../ui/KebabMenu";
import { Eye, Maximize2, Minimize2, Edit, FileText, Trash2 } from "lucide-react";
import { toast } from "sonner";

export function AttendanceTable({ employeeId }: { employeeId?: string }) {
  const { filters, setSelectedDate } = useAttendanceStore();
  const [page, setPage] = useState(1);
  const [sortAsc, setSortAsc] = useState(false);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const pageSize = 10;

  const rows = useMemo(() => {
    const employeesMap = new Map(attendanceDataset.employees.map((entry) => [entry.id, entry]));
    let dataset = attendanceDataset.records.filter((record) => !employeeId || record.employeeId === employeeId);
    dataset = dataset.filter((record) => {
      const employee = employeesMap.get(record.employeeId);
      if (!employee) return false;
      if (filters.employeeId !== "all" && record.employeeId !== filters.employeeId) return false;
      if (filters.department !== "all" && employee.department !== filters.department) return false;
      if (filters.location !== "all" && employee.location !== filters.location) return false;
      if (filters.status !== "all" && record.status !== filters.status) return false;
      if (filters.workMode !== "all" && record.workMode !== filters.workMode) return false;
      if (filters.shift !== "all" && record.shiftName !== filters.shift) return false;
      if (filters.exceptionType !== "all") {
        const hasException = attendanceDataset.exceptions.some(
          (entry) => entry.employeeId === record.employeeId && entry.date === record.date && entry.type === filters.exceptionType,
        );
        if (!hasException) return false;
      }
      return record.date >= filters.from && record.date <= filters.to;
    });
    dataset.sort((a, b) => (sortAsc ? a.date.localeCompare(b.date) : b.date.localeCompare(a.date)));
    return dataset;
  }, [employeeId, filters, sortAsc]);

  const paged = rows.slice((page - 1) * pageSize, page * pageSize);
  const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));

  return (
    <div className="flat-card bg-card overflow-hidden">
      <div className="overflow-auto max-h-[500px]">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-secondary z-10 text-[11px]">
            <tr>
              <th className="p-2 px-3 font-semibold text-left cursor-pointer" onClick={() => setSortAsc((value) => !value)}>Date</th>
              <th className="p-2 px-3 font-semibold text-left">Employee Name</th>
              <th className="p-2 px-3 font-semibold text-left">Shift</th>
              <th className="p-2 px-3 font-semibold text-left">First In</th>
              <th className="p-2 px-3 font-semibold text-left">Last Out</th>
              <th className="p-2 px-3 font-semibold text-left">Work Hours</th>
              <th className="p-2 px-3 font-semibold text-left">Late</th>
              <th className="p-2 px-3 font-semibold text-left">Early Exit</th>
              <th className="p-2 px-3 font-semibold text-left">Status</th>
              <th className="p-2 px-3 font-semibold text-left">LOP</th>
              <th className="p-2 px-3 font-semibold text-left">Exceptions</th>
              <th className="p-2 px-3 font-semibold text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((row) => {
              const rowException = attendanceDataset.exceptions.find((entry) => entry.employeeId === row.employeeId && entry.date === row.date);
              const expanded = expandedRow === row.id;
              return (
                <Fragment key={row.id}>
                  <tr className="border-t border-border hover:bg-secondary/50">
                    <td className="p-2 px-3 text-xs">{row.date}</td>
                    <td className="p-2 px-3 text-xs">{attendanceDataset.employees.find((employee) => employee.id === row.employeeId)?.name}</td>
                    <td className="p-2 px-3 text-xs">{row.shiftName}</td>
                    <td className="p-2 px-3 text-xs">{row.firstIn}</td>
                    <td className="p-2 px-3 text-xs">{row.lastOut}</td>
                    <td className="p-2 px-3 text-xs">{row.workHours.toFixed(1)}</td>
                    <td className="p-2 px-3 text-xs">{row.lateMins}m</td>
                    <td className="p-2 px-3 text-xs">{row.earlyExitMins}m</td>
                    <td className="p-2 px-3 text-xs">{row.status}</td>
                    <td className="p-2 px-3 text-xs">{row.lop}</td>
                    <td className="p-2 px-3 text-xs">{rowException?.type || "—"}</td>
                    <td className="p-2 px-3 text-xs" onClick={(e) => e.stopPropagation()}>
                      <KebabMenu 
                        size="sm"
                        items={[
                          { label: "View Details", icon: Eye, onClick: () => setSelectedDate(row.date) },
                          { label: expanded ? "Collapse Row" : "Expand Row", icon: expanded ? Minimize2 : Maximize2, onClick: () => setExpandedRow(expanded ? null : row.id) },
                          { label: "Regularize Punch", icon: Edit, onClick: () => toast.info("Redirecting to regularization...") },
                          { label: "View Log File", icon: FileText, onClick: () => toast.info("Opening raw log file") },
                          { label: "Delete Record", icon: Trash2, variant: "destructive", separator: true, onClick: () => {
                            if (confirm("Permanently delete this attendance record?")) toast.error("Record deleted");
                          }},
                        ]}
                      />
                    </td>
                  </tr>
                  {expanded && (
                    <tr className="border-t border-border bg-secondary/30">
                      <td className="p-2 px-3 text-[11px] text-muted-foreground" colSpan={12}>
                        Sessions: {row.firstIn} - 13:00, 13:30 - {row.lastOut} | OT: {row.otMins} mins | Work mode: {row.workMode}
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="p-2 px-3 border-t border-border flex items-center justify-between">
        <span className="text-[11px] text-muted-foreground">Page {page} of {totalPages}</span>
        <div className="flex gap-1.5">
          <button disabled={page === 1} onClick={() => setPage((value) => value - 1)} className="px-2 py-1 text-[11px] border border-border rounded disabled:opacity-50">Prev</button>
          <button disabled={page === totalPages} onClick={() => setPage((value) => value + 1)} className="px-2 py-1 text-[11px] border border-border rounded disabled:opacity-50">Next</button>
        </div>
      </div>
    </div>
  );
}
