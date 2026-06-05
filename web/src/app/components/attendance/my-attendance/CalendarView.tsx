import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameMonth,
  isToday,
  startOfWeek,
  endOfWeek,
  isAfter,
} from "date-fns";
import { motion } from "motion/react";
import { DailyAttendance } from "../../../modules/attendance/types";
import { useAttendanceStore } from "../../../modules/attendance/store";

interface CalendarViewProps {
  records: DailyAttendance[];
  currentDate: Date;
  searchTerm: string;
  onRegularize: (date: string) => void;
  onSwipeDetails?: (record: DailyAttendance) => void;
}

export function CalendarView({
  records,
  currentDate,
  searchTerm,
  onSwipeDetails,
}: CalendarViewProps) {
  const { selectedDate, setSelectedDate } = useAttendanceStore();

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(monthStart);

  const startDate = startOfWeek(monthStart);
  const endDate = endOfWeek(monthEnd);

  const calendarDays = eachDayOfInterval({
    start: startDate,
    end: endDate,
  });

  const getStatusColor = (status?: string) => {
    switch (status) {
      case "Present":
        return "#10B981";
      case "Absent":
        return "#EF4444";
      case "Half Day":
        return "#F97316";
      case "Holiday":
        return "#3B82F6";
      case "Week Off":
        return "#9CA3AF";
      default:
        return "#9CA3AF";
    }
  };

  return (
    <div className="w-full rounded-[24px] overflow-hidden border border-[rgba(15,23,42,0.06)] dark:border-[rgba(255,255,255,0.06)] bg-white/72 dark:bg-[#0F172A]/72 backdrop-blur-md shadow-sm transition-all duration-300">

      {/* Week Header */}
      <div className="grid grid-cols-7 border-b border-[rgba(15,23,42,0.06)] dark:border-[rgba(255,255,255,0.06)] px-4 py-3">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div
            key={day}
            className="text-center text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 dark:text-slate-400"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1.5 p-1.5 bg-black/[0.02] dark:bg-white/[0.02]">
        {calendarDays.map((day) => {
          const dateStr = format(day, "yyyy-MM-dd");

          const record = records.find((r) => r.date === dateStr);

          const isCurrentMonth = isSameMonth(day, monthStart);

          const isTodayDate = isToday(day);

          const isFuture = isAfter(day, new Date());

          const isSelected = selectedDate === dateStr;

          const isMatchingSearch =
            !searchTerm ||
            (record &&
              (record.status
                .toLowerCase()
                .includes(searchTerm.toLowerCase()) ||
                record.date.includes(searchTerm)));

          const isRestrictedStatus =
            record?.status === "Absent" ||
            record?.status === "Week Off" ||
            record?.status === "Holiday";

          return (
            <motion.button
              key={dateStr}
              type="button"
              disabled={!isCurrentMonth}
              initial={{ opacity: 0 }}
              animate={{
                opacity: isMatchingSearch ? 1 : 0.35,
              }}
              whileHover={{
                scale: isCurrentMonth ? 1.025 : 1,
                y: isCurrentMonth ? -1.5 : 0,
              }}
              transition={{
                duration: 0.2,
                ease: "easeOut",
              }}
              onClick={() => {
                setSelectedDate(dateStr);

                if (isFuture) {
                  onSwipeDetails?.({
                    id: `future-${dateStr}`,
                    employeeId: "",
                    employeeName: "",
                    department: "",
                    designation: "",
                    team: "",
                    date: dateStr,
                    status: "Present",
                    workMode: "WFO",
                    shiftName: "General Shift",
                    firstIn: "",
                    lastOut: "",
                    workHours: 0,
                    lateMins: 0,
                    earlyExitMins: 0,
                    lop: 0,
                    otMins: 0,
                    exception: false,
                    approvalPending: false,
                    geoViolation: false,
                    locked: false,
                    isLate: false,
                    isAbsent: false,
                    isHalfDay: false,
                  });
                  return;
                }

                if (!record) return;
                onSwipeDetails?.(record);
              }}
              className={`
                relative
                h-[94px]
                w-full
                overflow-hidden
                rounded-2xl
                border
                p-2.5
                flex
                flex-col
                justify-between
                text-left
                transition-all
                duration-300

                ${
                  isTodayDate
                    ? "bg-[#6366F1]/8 dark:bg-[#6366F1]/15 border-[#6366F1]/40 dark:border-[#6366F1]/50 shadow-[0_0_12px_rgba(99,102,241,0.15)]"
                    : isFuture || !record
                    ? "bg-white/40 dark:bg-[#0F172A]/40 border-[rgba(15,23,42,0.04)] dark:border-[rgba(255,255,255,0.04)]"
                    : record.status === "Present"
                    ? "bg-[#10B981]/5 dark:bg-[#10B981]/10 border-[#10B981]/10 dark:border-[#10B981]/20"
                    : record.status === "Absent"
                    ? "bg-[#EF4444]/5 dark:bg-[#EF4444]/10 border-[#EF4444]/10 dark:border-[#EF4444]/20"
                    : record.status === "Half Day"
                    ? "bg-[#F97316]/5 dark:bg-[#F97316]/10 border-[#F97316]/10 dark:border-[#F97316]/20"
                    : record.status === "Holiday"
                    ? "bg-[#3B82F6]/5 dark:bg-[#3B82F6]/10 border-[#3B82F6]/10 dark:border-[#3B82F6]/20"
                    : record.status === "Week Off"
                    ? "bg-[#9CA3AF]/5 dark:bg-[#9CA3AF]/10 border-[#9CA3AF]/10 dark:border-[#9CA3AF]/20"
                    : "bg-white/72 dark:bg-[#0F172A]/72 border-[rgba(15,23,42,0.06)] dark:border-[rgba(255,255,255,0.06)]"
                }

                ${
                  !isCurrentMonth
                    ? "opacity-25"
                    : ""
                }

                ${
                  isSelected
                    ? "ring-2 ring-[#6366F1]/50 z-10"
                    : ""
                }
              `}
            >
              {/* Today Highlight Subtle Glow Overlay */}
              {isTodayDate && (
                <div className="absolute inset-0 bg-gradient-to-br from-[#6366F1]/10 to-violet-500/10 dark:from-[#6366F1]/15 dark:to-violet-500/15 pointer-events-none rounded-2xl" />
              )}

              {/* Top Row: Date & Status Dot */}
              <div className="relative z-10 flex items-center justify-between w-full">
                <div
                  className={`
                    flex items-center justify-center
                    w-6 h-6
                    rounded-full
                    text-xs
                    font-bold
                    transition-all

                    ${
                      isTodayDate
                        ? "bg-[#6366F1] text-white shadow-md shadow-[#6366F1]/30"
                        : "text-[#0F172A] dark:text-[#F8FAFC]"
                    }
                  `}
                >
                  {format(day, "d")}
                </div>

                {!isFuture && record && (
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: getStatusColor(record.status) }}
                  />
                )}
              </div>

              {/* Bottom Row: Status Text & Regularization Indicator */}
              <div className="relative z-10 flex items-center justify-between w-full mt-auto">
                <span
                  className="text-[11px] font-bold tracking-wide uppercase"
                  style={{ color: isFuture ? "#9CA3AF" : getStatusColor(record?.status) }}
                >
                  {isFuture ? "09:00 - 18:00" : record ? record.status : ""}
                </span>

                {/* Regularization pending indicator: ONLY small yellow dot */}
                {!isFuture && record?.approvalPending && (
                  <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse" title="Regularization Pending" />
                )}
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}