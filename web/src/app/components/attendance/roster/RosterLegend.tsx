import { ShiftDefinition } from "../../../modules/attendance/types";
import { cn } from "../../ui/utils";

interface RosterLegendProps {
  shiftDefinitions: ShiftDefinition[];
}

export function RosterLegend({ shiftDefinitions }: RosterLegendProps) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <div className="w-1 h-4 bg-emerald-500 rounded-full" />
          <h4 className="text-[11px] font-bold text-slate-900 dark:text-slate-100 uppercase tracking-widest">Shift Legend & Codes</h4>
        </div>

        <div className="flex flex-wrap gap-x-8 gap-y-4">
          {shiftDefinitions.map((shift) => (
            <div key={shift.id} className="flex items-center gap-3 group cursor-default">
              <div className="w-2 h-2 rounded-full bg-blue-500 shrink-0" />
              <div className="flex flex-col">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 group-hover:text-emerald-600 transition-colors">
                  {shift.name}
                </span>
                <span className="text-[10px] font-medium text-slate-400 dark:text-slate-500">
                  {shift.startTime === "00:00" && shift.endTime === "00:00"
                    ? "Full Day"
                    : `${shift.startTime} - ${shift.endTime}`}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-slate-100/50 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700" />
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Weekend</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/30" />
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Today</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30" />
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Conflict</span>
          </div>
        </div>
      </div>
    </div>
  );
}
