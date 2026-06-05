import { useMemo } from "react";
import { Bell, CalendarDays, FileText, Palmtree } from "lucide-react";
import type { HolidayAPI, LeaveApplicationAPI } from "../../../modules/leaves/types";
import { cn } from "../../ui/utils";
import { employeeLeaveStatusLabel } from "./EmployeeLeaveStatusBadge";
import { formatLeaveShortDate } from "./leaveDateUtils";

type Notif = {
  id: string;
  category: "leave" | "holiday" | "system";
  title: string;
  body: string;
  time: string;
  sortAt: number;
  unread?: boolean;
};

function timeLabel(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  if (diff < 86_400_000) return d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short" });
}

export function LeaveNotificationCenter({
  applications,
  holidays,
}: {
  applications: LeaveApplicationAPI[];
  holidays: HolidayAPI[];
}) {
  const items = useMemo(() => {
    const list: Notif[] = [];
    const today = new Date().toISOString().slice(0, 10);

    for (const h of holidays) {
      if (h.date >= today) {
        list.push({
          id: `h-${h.id}`,
          category: "holiday",
          title: `Upcoming: ${h.name}`,
          body: `${formatLeaveShortDate(h.date)} · ${h.holiday_type}${h.is_optional ? " · Optional" : ""}`,
          time: timeLabel(`${h.date}T09:00:00`),
          sortAt: new Date(`${h.date}T09:00:00`).getTime(),
          unread: false,
        });
      }
    }

    for (const a of applications) {
      list.push({
        id: `a-${a.id}`,
        category: "leave",
        title: `${a.leave_type_detail?.name ?? "Leave"} · ${employeeLeaveStatusLabel(a.status)}`,
        body: `${formatLeaveShortDate(a.from_date)} — ${formatLeaveShortDate(a.to_date)} · ${a.total_days}d`,
        time: timeLabel(`${a.applied_on}T12:00:00`),
        sortAt: new Date(`${a.applied_on}T12:00:00`).getTime(),
        unread: a.status === "SUBMITTED" || a.status === "DRAFT",
      });
    }

    list.sort((a, b) => b.sortAt - a.sortAt);
    return list;
  }, [applications, holidays]);

  const unread = items.filter((n) => n.unread).length;

  return (
    <div className="flat-card overflow-hidden bg-card">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-secondary">
            <Bell className="h-4 w-4 text-foreground" aria-hidden />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-foreground">Notifications</h2>
            <p className="text-xs text-muted-foreground">
              {unread > 0 ? `${unread} need attention` : "You are up to date"}
            </p>
          </div>
        </div>
      </div>

      <div className="divide-y divide-border">
        {items.length === 0 ? (
          <div className="px-4 py-12 text-center text-sm text-muted-foreground">No notifications yet.</div>
        ) : (
          items.map((n) => (
            <div
              key={n.id}
              className={cn(
                "flex gap-3 px-4 py-3 transition-colors hover:bg-secondary/50",
                n.unread && "bg-secondary/25",
              )}
            >
              <div className="mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border border-border bg-background">
                {n.category === "holiday" ? (
                  <Palmtree className="h-4 w-4 text-muted-foreground" />
                ) : n.category === "leave" ? (
                  <FileText className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <CalendarDays className="h-4 w-4 text-muted-foreground" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-medium text-foreground">{n.title}</p>
                  {n.unread && <span className="h-1.5 w-1.5 rounded-full bg-foreground" aria-label="Unread" />}
                </div>
                <p className="mt-0.5 text-xs text-muted-foreground">{n.body}</p>
                <p className="mt-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {n.time}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
