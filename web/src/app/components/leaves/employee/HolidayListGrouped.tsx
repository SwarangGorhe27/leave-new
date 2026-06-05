import { useMemo } from "react";
import { Palmtree } from "lucide-react";
import type { HolidayAPI } from "../../../modules/leaves/types";
import { cn } from "../../ui/utils";
import { Badge } from "../../ui/badge";
import { LeaveEmptyState } from "./LeaveEmptyState";
import { formatLeaveDate } from "./leaveDateUtils";

export function HolidayListGrouped({ holidays }: { holidays: HolidayAPI[] }) {
  if (holidays.length === 0) {
    return (
      <LeaveEmptyState
        icon={Palmtree}
        title="No holidays"
        description="Your organization's holiday list will display here when published."
      />
    );
  }

  const grouped = useMemo(() => {
    const sorted = [...holidays].sort((a, b) => a.date.localeCompare(b.date));
    const map = new Map<string, HolidayAPI[]>();
    for (const h of sorted) {
      const m = new Date(h.date).toLocaleDateString("en-IN", { month: "long", year: "numeric" });
      map.set(m, [...(map.get(m) ?? []), h]);
    }
    return Array.from(map.entries());
  }, [holidays]);

  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="space-y-3">
      {grouped.map(([month, items]) => (
        <div key={month} className="flat-card overflow-hidden bg-card">
          <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
            <p className="text-sm font-semibold text-foreground">{month}</p>
            <span className="rounded-md border border-border bg-secondary px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
              {items.length}
            </span>
          </div>
          <div className="divide-y divide-border">
            {items.map((h) => {
              const d = new Date(h.date);
              const day = d.toLocaleDateString("en-IN", { weekday: "short" });
              const isPast = h.date < today;
              const isUpcoming = h.date >= today;
              return (
                <div
                  key={h.id}
                  className={cn(
                    "flex items-center justify-between gap-4 px-4 py-2.5 transition-colors",
                    isPast && "opacity-55",
                    isUpcoming && h.date === today && "bg-secondary/40",
                  )}
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-foreground">{h.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {day} · {formatLeaveDate(h.date)} · {h.holiday_type}
                    </p>
                  </div>
                  <div className="flex flex-shrink-0 items-center gap-2">
                    {h.is_optional && (
                      <Badge variant="secondary" className="text-[10px] font-semibold uppercase tracking-wide">
                        Optional
                      </Badge>
                    )}
                    <span className="rounded-md border border-border bg-secondary px-2 py-0.5 text-[11px] font-semibold tabular-nums text-muted-foreground">
                      {d.getDate().toString().padStart(2, "0")}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}