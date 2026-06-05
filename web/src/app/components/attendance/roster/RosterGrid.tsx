import { useRef, useState } from "react";
import { format, isWeekend, isToday } from "date-fns";
import { Avatar, AvatarFallback, AvatarImage } from "../../ui/avatar";
import { cn } from "../../ui/utils";
import { ShiftDefinition, RosterRecord } from "../../../modules/attendance/types";
import {
  findShiftDefinition,
  getRosterShiftDisplayLabel,
} from "../../../modules/attendance/mappers";
import { Popover, PopoverContent, PopoverTrigger } from "../../ui/popover";
import { Edit2, Globe } from "lucide-react";

interface RosterGridProps {
  roster: RosterRecord[];
  days: Date[];
  shiftDefinitions: ShiftDefinition[];
  isPublished: boolean;
  onUpdateShift: (employeeId: string, date: string, shiftCode: string) => void | Promise<void>;
}

function isOffLabel(label: string): boolean {
  const u = label.toUpperCase();
  return u === "OFF" || u === "WO" || u === "WEEK OFF" || u === "HL" || u === "HOLIDAY";
}

function shiftButtonStyle(shift: ShiftDefinition, selected: boolean): string {
  if (shift.code === "OFF") {
    return cn(
      "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800/80 dark:text-slate-300 dark:border-slate-700",
      selected && "ring-2 ring-slate-900 ring-offset-1 dark:ring-white",
    );
  }
  return cn(
    "bg-blue-50 text-blue-800 border-blue-100 dark:bg-blue-500/15 dark:text-blue-300 dark:border-blue-500/30",
    selected && "ring-2 ring-emerald-600 ring-offset-1",
  );
}

export function RosterGrid({ roster, days, shiftDefinitions, isPublished, onUpdateShift }: RosterGridProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [openCellKey, setOpenCellKey] = useState<string | null>(null);

  const handlePickShift = async (
    cellKey: string,
    employeeId: string,
    dateStr: string,
    shiftCode: string,
  ) => {
    setOpenCellKey(null);
    await onUpdateShift(employeeId, dateStr, shiftCode);
  };

  return (
    <div className="relative flex flex-col h-full overflow-hidden">
      <div
        ref={scrollRef}
        className="overflow-x-auto overflow-y-auto no-scrollbar relative max-h-[800px] border-t border-slate-200 dark:border-slate-800"
      >
        <table className="border-separate border-spacing-0 w-full">
          <thead className="sticky top-0 z-20">
            <tr className="bg-slate-50 dark:bg-slate-800/80 backdrop-blur-sm">
              <th className="sticky left-0 z-30 bg-slate-50 dark:bg-slate-800 border-b border-r border-slate-200 dark:border-slate-700 p-2 min-w-[240px] text-left">
                <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Employee Details</span>
              </th>
              <th className="sticky left-[240px] z-30 bg-slate-50 dark:bg-slate-800 border-b border-r border-slate-200 dark:border-slate-700 p-2 min-w-[90px] text-center">
                <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Working / Off</span>
              </th>

              {days.map((day) => {
                const weekend = isWeekend(day);
                const today = isToday(day);
                return (
                  <th
                    key={day.toISOString()}
                    className={cn(
                      "border-b border-r border-slate-200 dark:border-slate-700 p-1 min-w-[72px] text-center transition-colors",
                      weekend && "bg-slate-100/50 dark:bg-slate-800/30",
                      today && "bg-emerald-50 dark:bg-emerald-500/10",
                    )}
                  >
                    <div className="flex flex-col items-center gap-0">
                      <span
                        className={cn(
                          "text-[9px] font-bold uppercase tracking-tighter",
                          weekend ? "text-slate-400" : "text-slate-500",
                        )}
                      >
                        {format(day, "EE")}
                      </span>
                      <span
                        className={cn(
                          "text-xs font-bold",
                          today ? "text-emerald-600 dark:text-emerald-400" : "text-slate-900 dark:text-slate-100",
                        )}
                      >
                        {format(day, "dd")}
                      </span>
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>

          <tbody>
            {roster.map((record) => (
              <tr key={record.id} className="group hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors">
                <td className="sticky left-0 z-10 bg-white dark:bg-slate-900 border-b border-r border-slate-200 dark:border-slate-800 p-2 transition-colors group-hover:bg-slate-50/80 dark:group-hover:bg-white/[0.04]">
                  <div className="flex items-center gap-2.5">
                    <Avatar className="h-8 w-8 border border-white dark:border-slate-800 shadow-sm">
                      <AvatarImage src={record.avatar} />
                      <AvatarFallback className="bg-emerald-500/10 text-emerald-600 text-[10px] font-bold">
                        {record.employeeName.split(" ").map((n) => n[0]).join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col min-w-0">
                      <span className="text-[11px] font-bold text-slate-900 dark:text-slate-100 truncate group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors flex items-center gap-1.5">
                        {record.employeeName}
                        {isPublished && <Globe className="w-2.5 h-2.5 text-emerald-500" />}
                      </span>
                      <div className="flex items-center gap-1">
                        <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-tight">{record.employeeCode}</span>
                        <span className="text-[9px] text-slate-300">•</span>
                        <span className="text-[9px] font-medium text-slate-500 dark:text-slate-400 truncate">{record.department}</span>
                      </div>
                    </div>
                  </div>
                </td>

                <td className="sticky left-[240px] z-10 bg-white dark:bg-slate-900 border-b border-r border-slate-200 dark:border-slate-800 p-2 transition-colors group-hover:bg-slate-50/80 dark:group-hover:bg-white/[0.04]">
                  <div className="flex flex-col items-center gap-1">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[11px] font-bold text-slate-900 dark:text-slate-100">{record.workingDays}D</span>
                      <span className="text-slate-300 dark:text-slate-700">/</span>
                      <span className="text-[11px] font-bold text-slate-500">{record.weekOffs}O</span>
                    </div>
                    <div className="w-full h-1 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden flex">
                      <div
                        className="h-full bg-emerald-500"
                        style={{
                          width: `${(record.workingDays / (record.workingDays + record.weekOffs || 1)) * 100}%`,
                        }}
                      />
                      <div
                        className="h-full bg-slate-300 dark:bg-slate-600"
                        style={{
                          width: `${(record.weekOffs / (record.workingDays + record.weekOffs || 1)) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </td>

                {days.map((day) => {
                  const dateStr = format(day, "yyyy-MM-dd");
                  const cellValue = record.shifts[dateStr];
                  const shift = findShiftDefinition(shiftDefinitions, cellValue);
                  const displayLabel = getRosterShiftDisplayLabel(cellValue, shiftDefinitions);
                  const off = isOffLabel(displayLabel);
                  const weekend = isWeekend(day);
                  const today = isToday(day);
                  const cellKey = `${record.employeeId}-${dateStr}`;
                  const isOpen = openCellKey === cellKey;

                  return (
                    <td
                      key={day.toISOString()}
                      className={cn(
                        "border-b border-r border-slate-200 dark:border-slate-800 p-0.5 min-w-[72px] relative transition-all group/cell",
                        weekend && "bg-slate-100/30 dark:bg-slate-800/20",
                        today && "bg-emerald-50/30 dark:bg-emerald-500/5",
                        "hover:bg-emerald-50/50 dark:hover:bg-emerald-500/5",
                      )}
                    >
                      <Popover
                        open={isOpen}
                        onOpenChange={(open) => setOpenCellKey(open ? cellKey : null)}
                      >
                        <PopoverTrigger asChild>
                          <button
                            type="button"
                            title={`${displayLabel} — click to change`}
                            className={cn(
                              "w-full h-full min-h-[36px] flex items-center justify-center relative rounded-md border transition-all duration-200 hover:scale-105 active:scale-95 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500",
                              off
                                ? "bg-slate-100 text-slate-600 border-slate-200/80 dark:bg-slate-800/80 dark:text-slate-400 dark:border-slate-700/50"
                                : "bg-blue-100 text-blue-800 border-blue-200/80 dark:bg-blue-500/20 dark:text-blue-300 dark:border-blue-500/30",
                            )}
                          >
                            <span className="text-[8px] font-bold px-1 py-0.5 max-w-[68px] text-center leading-tight line-clamp-2 break-words">
                              {displayLabel}
                            </span>
                            <Edit2 className="absolute top-0.5 right-0.5 w-2 h-2 text-slate-400 opacity-0 group-hover/cell:opacity-100" />
                          </button>
                        </PopoverTrigger>

                        <PopoverContent
                          className="w-80 p-3 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-2xl z-[9999]"
                          align="start"
                          sideOffset={6}
                        >
                          <div className="space-y-3">
                            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                              <div className="flex flex-col min-w-0">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                  {format(day, "dd MMM yyyy")}
                                </span>
                                <span className="text-[9px] font-bold text-slate-500 truncate max-w-[180px]">
                                  {record.employeeName}
                                </span>
                              </div>
                              <span
                                className={cn(
                                  "px-2 py-0.5 rounded text-[9px] font-black uppercase shrink-0 max-w-[120px] truncate",
                                  off
                                    ? "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                                    : "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300",
                                )}
                              >
                                {displayLabel}
                              </span>
                            </div>

                            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">
                              Select shift (legend)
                            </p>

                            <div className="grid grid-cols-2 gap-1.5 max-h-[220px] overflow-y-auto pr-0.5">
                              {shiftDefinitions.map((s) => {
                                const selected =
                                  (off && s.code === "OFF")
                                  || (!off && shift?.id === s.id)
                                  || (!off && cellValue === s.name);
                                return (
                                  <button
                                    key={s.id}
                                    type="button"
                                    title={s.startTime && s.endTime ? `${s.startTime} - ${s.endTime}` : undefined}
                                    className={cn(
                                      "min-h-9 flex items-center justify-center rounded-lg text-[9px] font-bold border px-1.5 transition-all hover:scale-[1.02] active:scale-95",
                                      shiftButtonStyle(s, selected),
                                      !selected && "opacity-75 hover:opacity-100",
                                    )}
                                    onClick={() => handlePickShift(cellKey, record.employeeId, dateStr, s.code)}
                                  >
                                    <span className="line-clamp-2 text-center leading-tight">{s.name}</span>
                                  </button>
                                );
                              })}
                            </div>

                            {isPublished && (
                              <p className="text-[9px] text-amber-600 dark:text-amber-400 font-medium border-t border-slate-100 dark:border-slate-800 pt-2">
                                Schedule is published. Unpublish from the banner above if edits are blocked.
                              </p>
                            )}
                          </div>
                        </PopoverContent>
                      </Popover>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
