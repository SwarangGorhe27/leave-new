import { useMemo, useState } from "react";
import { Palmtree } from "lucide-react";
import { cn } from "../ui/utils";
import type { HolidayAPI } from "../../modules/leaves/types";

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

function isoDate(year: number, monthIndex: number, day: number): string {
  const dd = String(day).padStart(2, "0");
  const mm = String(monthIndex + 1).padStart(2, "0");
  return `${year}-${mm}-${dd}`;
}

export function HolidayCalendarView({
  holidays,
  initialYear,
}: {
  holidays: HolidayAPI[];
  initialYear: number;
}) {
  const currentDate = new Date();
  const [selectedMonth, setSelectedMonth] = useState(currentDate.getMonth());
  const [selectedYear, setSelectedYear] = useState(initialYear);

  const holidayByDate = useMemo(() => {
    const map = new Map<string, HolidayAPI[]>();
    for (const h of holidays) {
      map.set(h.date, [...(map.get(h.date) ?? []), h]);
    }
    return map;
  }, [holidays]);

  const totalDays = new Date(selectedYear, selectedMonth + 1, 0).getDate();
  const firstDay = new Date(selectedYear, selectedMonth, 1).getDay();

  const calendarDays = [
    ...Array(firstDay).fill(null),
    ...Array.from({ length: totalDays }, (_, i) => i + 1),
  ];

  const years = useMemo(() => {
    const start = Math.max(2024, initialYear - 2);
    return Array.from({ length: 6 }, (_, i) => start + i);
  }, [initialYear]);

  return (
    <div className="flat-card bg-card overflow-hidden">
      <div className="px-6 py-5 border-b border-border flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0">
          <h2 className="text-base font-semibold text-foreground flex items-center gap-2">
            <Palmtree className="w-4 h-4 text-muted-foreground" />
            Holiday Calendar
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Monthly calendar view of holidays
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(Number(e.target.value))}
            className="flat-input px-3 py-2 text-sm font-medium cursor-pointer appearance-none"
          >
            {MONTHS.map((m, idx) => (
              <option key={m} value={idx}>
                {m}
              </option>
            ))}
          </select>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="flat-input px-3 py-2 text-sm font-medium cursor-pointer appearance-none"
          >
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="px-6 py-4">
        <div className="mb-2 grid grid-cols-7">
          {WEEK_DAYS.map((d) => (
            <div
              key={d}
              className="py-2 text-center text-[11px] font-semibold uppercase tracking-wider text-muted-foreground"
            >
              {d}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 overflow-hidden rounded-2xl border border-border">
          {calendarDays.map((day, index) => {
            if (!day) {
              return <div key={index} className="min-h-[110px] border border-border bg-background" />;
            }

            const date = isoDate(selectedYear, selectedMonth, day);
            const dayHolidays = holidayByDate.get(date) ?? [];

            const isToday =
              currentDate.getDate() === day &&
              currentDate.getMonth() === selectedMonth &&
              currentDate.getFullYear() === selectedYear;

            return (
              <div
                key={date}
                className={cn(
                  "min-h-[110px] border border-border bg-card p-3 text-left transition-colors hover:bg-secondary",
                )}
              >
                <div className="mb-2 flex items-start justify-between gap-2">
                  <span
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold",
                      isToday ? "bg-foreground text-primary-foreground" : "text-foreground",
                    )}
                  >
                    {day}
                  </span>

                  {dayHolidays.length > 0 && (
                    <span className="rounded-full border border-border bg-secondary px-2 py-0.5 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                      Holiday
                    </span>
                  )}
                </div>

                {dayHolidays.length > 0 ? (
                  <div className="space-y-2">
                    {dayHolidays.slice(0, 2).map((h) => (
                      <div
                        key={h.id}
                        className={cn(
                          "rounded-xl border border-border bg-background px-3 py-2",
                          h.is_optional && "border-dashed",
                        )}
                        title={`${h.name} · ${h.holiday_type}${h.is_optional ? " · Optional" : ""}`}
                      >
                        <p className="text-xs font-semibold text-foreground truncate">{h.name}</p>
                        <p className="text-[10px] text-muted-foreground mt-0.5">
                          {h.holiday_type}{h.is_optional ? " · Optional" : ""}
                        </p>
                      </div>
                    ))}

                    {dayHolidays.length > 2 && (
                      <p className="text-[11px] font-semibold text-muted-foreground">
                        +{dayHolidays.length - 2} more
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="mt-8 flex items-center justify-center">
                    <span className="text-xs text-muted-foreground/40">—</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

