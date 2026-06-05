import { format, parseISO, startOfMonth, endOfMonth, isWithinInterval } from "date-fns";
import { useMemo, useState } from "react";
import { 
  Eye, 
  Send, 
  Monitor,
  Fingerprint
} from "lucide-react";
import { DailyAttendance } from "../../../modules/attendance/types";
import { getStatusColor } from "./utils";
import { motion } from "motion/react";

interface ListViewProps {
  records: DailyAttendance[];
  onSwipeDetails: (record: DailyAttendance) => void;
  onRegularize: (date: string) => void;
  readOnly?: boolean;
}

export function ListView({ records, onSwipeDetails, onRegularize, readOnly = false }: ListViewProps) {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [rangeFilter, setRangeFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");

  const sortedRecords = useMemo(() => {
    let data = [...records].sort((a, b) => b.date.localeCompare(a.date));

    if (statusFilter !== "all") {
      data = data.filter((record) => record.status === statusFilter);
    }

    if (rangeFilter !== "all") {
      const now = new Date();
      const ranges: Record<string, { start: Date; end: Date }> = {
        "this-month": { start: startOfMonth(now), end: endOfMonth(now) },
        "last-30": { start: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30), end: now },
      };
      const range = ranges[rangeFilter];
      if (range) {
        data = data.filter((record) => isWithinInterval(parseISO(record.date), range));
      }
    }

    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      data = data.filter((record) =>
        record.date.toLowerCase().includes(term) ||
        record.status.toLowerCase().includes(term) ||
        (record.shiftName || "").toLowerCase().includes(term) ||
        (record.workMode || "").toLowerCase().includes(term)
      );
    }

    return data;
  }, [records, statusFilter, rangeFilter, searchTerm]);

  return (
    <div className="space-y-4">
      <div className="attendance-list-card p-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search date, status, or shift..."
            className="flat-input h-9 px-3 text-sm"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flat-input h-9 px-3 text-sm"
          >
            <option value="all">All Status</option>
            <option value="Present">Present</option>
            <option value="Absent">Absent</option>
            <option value="Half Day">Half Day</option>
            <option value="Leave">Leave</option>
            <option value="Holiday">Holiday</option>
            <option value="Week Off">Week Off</option>
          </select>
          <select
            value={rangeFilter}
            onChange={(e) => setRangeFilter(e.target.value)}
            className="flat-input h-9 px-3 text-sm"
          >
            <option value="all">All Dates</option>
            <option value="this-month">This Month</option>
            <option value="last-30">Last 30 Days</option>
          </select>
        </div>
        <div className="text-xs text-muted-foreground font-medium">
          {sortedRecords.length} record{sortedRecords.length !== 1 ? "s" : ""}
        </div>
      </div>

      <div className="attendance-list-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-muted-foreground">Date</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-muted-foreground">Timing</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-muted-foreground">Work Mode</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-muted-foreground">Hours</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-muted-foreground">Status</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-muted-foreground text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedRecords.map((record, idx) => (
                <motion.tr 
                  key={record.date}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="attendance-list-row group transition-all cursor-pointer"
                  onClick={() => onSwipeDetails(record)}
                >
                  <td className="px-8 py-6">
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold text-foreground">{format(parseISO(record.date), "dd MMM, yyyy")}</span>
                      <span className="text-[10px] font-medium text-muted-foreground uppercase">{format(parseISO(record.date), "EEEE")}</span>
                    </div>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex items-center gap-4">
                      <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-muted-foreground uppercase leading-none">In</span>
                        <span className="text-sm font-semibold text-violet-600 dark:text-violet-300">{record.firstIn || "--:--"}</span>
                      </div>
                      <div className="w-[1px] h-6 bg-foreground/10" />
                      <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-muted-foreground uppercase leading-none">Out</span>
                        <span className="text-sm font-semibold text-indigo-600 dark:text-indigo-300">{record.lastOut || "--:--"}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex items-center gap-2">
                      {record.workMode === "WFO" ? <Fingerprint size={14} className="text-blue-500" /> : <Monitor size={14} className="text-purple-500" />}
                      <span className="text-xs font-semibold text-foreground">{record.workMode || "Office"}</span>
                    </div>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold text-foreground">{record.workHours.toFixed(1)}h</span>
                      {record.otMins > 0 && <span className="text-[9px] font-semibold text-violet-500">+{record.otMins}m OT</span>}
                    </div>
                  </td>
                  <td className="px-8 py-6">
                    <span className={`attendance-status-pill px-4 py-1.5 text-[10px] font-semibold uppercase tracking-widest shadow-sm ${getStatusColor(record.status)}`}>
                      {record.status}
                    </span>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex items-center justify-end gap-2">
                      <button 
                        onClick={(e) => { e.stopPropagation(); onSwipeDetails(record); }}
                        className="attendance-row-action p-2.5 transition-all text-muted-foreground"
                      >
                        <Eye size={16} />
                      </button>
                      {!readOnly && (
                        <button 
                          onClick={(e) => { e.stopPropagation(); onRegularize(record.date); }}
                          className="attendance-row-action p-2.5 transition-all text-muted-foreground"
                        >
                          <Send size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                </motion.tr>
              ))}
              {sortedRecords.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-8 py-16 text-center">
                    <p className="text-sm font-semibold text-foreground">No attendance records found</p>
                    <p className="text-xs text-muted-foreground mt-1">Try changing the month, status, or date filters.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
