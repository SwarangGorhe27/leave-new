import { useMemo, useState } from "react";
import { Palmtree } from "lucide-react";
import type { HolidayAPI } from "../../../modules/leaves/types";
import { cn } from "../../ui/utils";

const MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function HolidayYearOverview({ holidays, year }: { holidays: HolidayAPI[]; year: number }) {
  const [hover, setHover] = useState<string | null>(null);

  const byMonth = useMemo(() => {
    const arr: HolidayAPI[][] = Array.from({ length: 12 }, () => []);
    for (const h of holidays) {
      if (!h.date.startsWith(String(year))) continue;
      const m = Number(h.date.slice(5, 7)) - 1;
      if (m >= 0 && m < 12) arr[m].push(h);
    }
    return arr;
  }, [holidays, year]);

  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="flat-card overflow-hidden bg-card">
      <div className="border-b border-border px-4 py-3">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <Palmtree className="h-4 w-4 text-muted-foreground" aria-hidden />
          Year at a glance · {year}
        </h3>
        <p className="mt-0.5 text-xs text-muted-foreground">Dense view of holiday density by month.</p>
      </div>
      <div className="grid gap-2 p-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {byMonth.map((items, mi) => (
          <div
            key={MONTH_SHORT[mi]}
            className={cn(
              "rounded-xl border border-border bg-background/80 p-3 transition-shadow duration-150",
              items.some((h) => h.date >= today) && "ring-1 ring-foreground/10",
            )}
          >
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-semibold text-foreground">{MONTH_SHORT[mi]}</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                {items.length} hol.
              </span>
            </div>
            <div className="space-y-1.5">
              {items.length === 0 ? (
                <p className="text-[11px] text-muted-foreground/70">—</p>
              ) : (
                items.slice(0, 4).map((h) => {
                  const upcoming = h.date >= today;
                  return (
                    <button
                      key={h.id}
                      type="button"
                      onMouseEnter={() => setHover(h.id)}
                      onMouseLeave={() => setHover(null)}
                      className={cn(
                        "flex w-full items-start gap-2 rounded-lg border border-transparent px-1.5 py-1 text-left text-[11px] transition-colors",
                        hover === h.id && "border-border bg-secondary",
                        upcoming && "font-medium",
                      )}
                    >
                      <span className="tabular-nums text-muted-foreground">{h.date.slice(8)}</span>
                      <span className="min-w-0 flex-1 truncate text-foreground">{h.name}</span>
                    </button>
                  );
                })
              )}
              {items.length > 4 && (
                <p className="text-[10px] font-semibold text-muted-foreground">+{items.length - 4} more</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
