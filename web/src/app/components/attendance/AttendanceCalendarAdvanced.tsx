import { attendanceDataset, useAttendanceStore } from "../../modules/attendance/store";

const statusColor: Record<string, string> = {
  Present: "bg-slate-100 text-slate-700",
  Absent: "bg-rose-100 text-rose-700",
  "Half Day": "bg-amber-100 text-amber-800",
  Leave: "bg-indigo-100 text-indigo-700",
  Holiday: "bg-sky-100 text-sky-700",
  "Week Off": "bg-slate-200 text-slate-700",
};

export function AttendanceCalendarAdvanced() {
  const { setSelectedDate } = useAttendanceStore();
  const days = Array.from({ length: 31 }).map((_, i) => `2026-05-${String(i + 1).padStart(2, "0")}`);

  return (
    <div className="flat-card bg-card p-3">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-semibold text-foreground">Advanced Attendance Calendar</p>
        <p className="text-[11px] text-muted-foreground">Monthly Summary: Present 18 | Absent 2 | Leave 3 | LOP 2.5</p>
      </div>
      <div className="grid grid-cols-7 gap-1.5">
        {days.map((date) => {
          const dayRecords = attendanceDataset.records.filter((r) => r.date === date);
          const record = dayRecords[0];
          const avgWorkHours = dayRecords.length ? dayRecords.reduce((s, x) => s + x.workHours, 0) / dayRecords.length : 0;
          const intensity = Math.min(80, Math.round(avgWorkHours * 8));
          return (
            <button
              key={date}
              onClick={() => setSelectedDate(date)}
              title={record ? `Punch: ${record.firstIn}-${record.lastOut} | Work ${Math.round(record.workHours * 60)} mins | LOP ${record.lop}` : "No data"}
              className="rounded-lg border border-border p-1.5 text-left hover:bg-secondary transition-colors"
              style={{ background: `linear-gradient(180deg, rgba(15,23,42,0.${Math.max(1, Math.floor(intensity / 10))}) 0%, transparent 35%)` }}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-muted-foreground">{date.slice(-2)}</span>
                {date === "2026-05-06" && <span className="text-[9px] px-1 rounded bg-foreground text-primary-foreground">Today</span>}
              </div>
              {record ? (
                <>
                  <span className={`inline-flex px-1.5 py-0.5 rounded text-[9px] font-medium ${statusColor[record.status]}`}>{record.status}</span>
                  <p className="text-[9px] text-foreground mt-0.5">{record.firstIn} - {record.lastOut}</p>
                  <p className="text-[9px] text-muted-foreground">{Math.floor(record.workHours)}h {Math.round((record.workHours % 1) * 60)}m · {record.shiftName}</p>
                  <div className="flex gap-1 mt-1 flex-wrap">
                    {record.lateMins > 0 && (
                      <span className="text-[9px] px-1 rounded bg-rose-100 text-rose-700">Late</span>
                    )}
                    {record.earlyExitMins > 0 && (
                      <span className="text-[9px] px-1 rounded bg-amber-100 text-amber-800">Early</span>
                    )}
                    {record.exception && (
                      <span className="text-[9px] px-1 rounded bg-yellow-100 text-yellow-800">Exception</span>
                    )}
                    {record.otMins > 0 && (
                      <span className="text-[9px] px-1 rounded bg-slate-100 text-slate-700">OT</span>
                    )}
                    {record.approvalPending && (
                      <span className="text-[9px] px-1 rounded bg-sky-100 text-sky-700">Pending</span>
                    )}
                    {record.geoViolation && (
                      <span className="text-[9px] px-1 rounded bg-slate-100 text-slate-700">Geo</span>
                    )}
                    {record.locked && (
                      <span className="text-[9px] px-1 rounded bg-slate-100 text-slate-700">Locked</span>
                    )}
                    <span className="text-[9px] px-1 rounded border border-border">{record.workMode}</span>
                  </div>
                </>
              ) : (
                <span className="text-[9px] text-muted-foreground">No shifts</span>
              )}
            </button>
          );
        })}
      </div>
      <div className="mt-2 p-1.5 rounded border border-border text-[11px] text-muted-foreground">
        Week summary: W1 42h (5P) · W2 39h (1 late streak) · W3 44h · W4 38h
      </div>
    </div>
  );
}
