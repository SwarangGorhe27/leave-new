import { useMemo, useState } from "react";
import { attendanceDataset, useAttendanceStore } from "../../modules/attendance/store";

const WEEK_DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const STATUS_COLORS: Record<string, { light: string; dark: string }> = {
  Present: { light: "#10B981", dark: "#10B981" },
  Absent: { light: "#EF4444", dark: "#EF4444" },
  "Half Day": { light: "#F97316", dark: "#F97316" },
  Leave: { light: "#3B82F6", dark: "#3B82F6" },
  Holiday: { light: "#3B82F6", dark: "#3B82F6" },
  "Week Off": { light: "#9CA3AF", dark: "#9CA3AF" },
  "Late In": { light: "#FACC15", dark: "#FACC15" },
  "Regularization Required": { light: "#EAB308", dark: "#EAB308" },
  "Pending Approval": { light: "#8B5CF6", dark: "#8B5CF6" },
};

const STATUS_STYLES: Record<string, string> = {
  Present: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900/60",
  Absent: "bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-900/60",
  "Half Day": "bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/60",
  Leave: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-900/60",
  Holiday: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-900/60",
  "Week Off": "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-950/40 dark:text-gray-300 dark:border-gray-900/60",
};

export function AttendanceCalendar({
  employeeId,
}: {
  employeeId?: string;
}) {
  const { setSelectedDate } = useAttendanceStore();

  const currentDate = new Date();

  const [selectedMonth, setSelectedMonth] = useState(
    currentDate.getMonth()
  );

  const [selectedYear, setSelectedYear] = useState(
    currentDate.getFullYear()
  );

  const records = attendanceDataset.records.filter(
    (record) => !employeeId || record.employeeId === employeeId
  );

  const totalDays = new Date(
    selectedYear,
    selectedMonth + 1,
    0
  ).getDate();

  const firstDay = new Date(
    selectedYear,
    selectedMonth,
    1
  ).getDay();

  const lastDayOfPrevMonth = new Date(
    selectedYear,
    selectedMonth,
    0
  ).getDate();

  // Previous month dates
  const prevMonthDates = Array.from(
    { length: firstDay },
    (_, i) => ({
      day: lastDayOfPrevMonth - firstDay + i + 1,
      isCurrentMonth: false,
    })
  );

  // Current month dates
  const currentMonthDates = Array.from(
    { length: totalDays },
    (_, i) => ({
      day: i + 1,
      isCurrentMonth: true,
    })
  );

  // Next month dates (to fill the grid)
  const remainingCells = 42 - (prevMonthDates.length + currentMonthDates.length);
  const nextMonthDates = Array.from(
    { length: remainingCells },
    (_, i) => ({
      day: i + 1,
      isCurrentMonth: false,
    })
  );

  const allDates = [...prevMonthDates, ...currentMonthDates, ...nextMonthDates];

  const years = useMemo(() => {
    return Array.from({ length: 6 }, (_, i) => 2024 + i);
  }, []);

  return (
    <div className="rounded-3xl border border-neutral-200 bg-white p-6 shadow-sm">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-black">
            Attendance Calendar
          </h2>
          <p className="text-sm text-neutral-500">
            View monthly attendance records
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3">
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(Number(e.target.value))}
            className="rounded-xl border border-neutral-300 bg-white px-4 py-2 text-sm font-medium outline-none transition focus:border-black"
          >
            {MONTHS.map((month, index) => (
              <option key={month} value={index}>
                {month}
              </option>
            ))}
          </select>

          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="rounded-xl border border-neutral-300 bg-white px-4 py-2 text-sm font-medium outline-none transition focus:border-black"
          >
            {years.map((year) => (
              <option key={year}>{year}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Week Header */}
      <div className="mb-2 grid grid-cols-7">
        {WEEK_DAYS.map((day) => (
          <div
            key={day}
            className="py-3 text-center text-xs font-semibold uppercase tracking-wider text-neutral-500"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 overflow-hidden rounded-2xl border border-neutral-200 dark:border-neutral-800">
        {allDates.map((dateObj, index) => {
          const day = dateObj.day;
          const isCurrentMonth = dateObj.isCurrentMonth;

          if (!isCurrentMonth) {
            return (
              <div
                key={index}
                className="min-h-[120px] border border-neutral-100 dark:border-neutral-900 bg-neutral-50 dark:bg-neutral-950/30 opacity-45 dark:opacity-40 flex items-center justify-center"
              >
                <span className="text-neutral-400 dark:text-neutral-600 text-sm font-medium">
                  {day}
                </span>
              </div>
            );
          }

          const formattedDay = String(day).padStart(2, "0");

          const formattedMonth = String(selectedMonth + 1).padStart(2, "0");

          const date = `${selectedYear}-${formattedMonth}-${formattedDay}`;

          const record = records.find((item) => item.date === date);

          const isToday =
            currentDate.getDate() === day &&
            currentDate.getMonth() === selectedMonth &&
            currentDate.getFullYear() === selectedYear;

          return (
            <button
              key={date}
              onClick={() => setSelectedDate(date)}
              className="group min-h-[120px] border border-neutral-100 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-3 text-left transition-all hover:bg-neutral-50 dark:hover:bg-neutral-800"
            >
              {/* Day Number */}
              <div className="mb-3 flex items-center justify-between">
                <span
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${
                    isToday
                      ? "bg-black dark:bg-white text-white dark:text-black"
                      : "text-black dark:text-white"
                  }`}
                >
                  {day}
                </span>

                {record && (
                  <span
                    className={`rounded-full border px-2 py-0.5 text-[10px] font-medium ${STATUS_STYLES[record.status]}`}
                  >
                    {record.status}
                  </span>
                )}
              </div>

              {/* Working Hours */}
              {record ? (
                <div className="mt-4">
                  <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800 px-3 py-2">
                    <p className="text-[10px] uppercase tracking-wide text-neutral-500 dark:text-neutral-400">
                      Working Hours
                    </p>

                    <p className="mt-1 text-lg font-semibold text-black dark:text-white">
                      {record.workHours}h
                    </p>
                  </div>
                </div>
              ) : (
                <div className="mt-6 flex items-center justify-center">
                  <span className="text-xs text-neutral-300 dark:text-neutral-600">—</span>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-8 pt-6 border-t border-neutral-200 dark:border-neutral-800">
        <h3 className="text-xs font-semibold text-black dark:text-white uppercase tracking-widest mb-4">
          Legend
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {Object.entries(STATUS_COLORS).map(([status, colors]) => (
            <div key={status} className="flex items-center gap-3">
              <div
                className="w-4 h-4 rounded-full shadow-sm border border-black/10 dark:border-white/10"
                style={{
                  backgroundColor: colors.light,
                }}
              />
              <span className="text-xs font-medium text-neutral-600 dark:text-neutral-400">
                {status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}