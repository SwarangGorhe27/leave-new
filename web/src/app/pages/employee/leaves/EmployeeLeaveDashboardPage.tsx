import { useMemo } from "react";
import { Link, useNavigate } from "react-router";
import {
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  Clock,
  PenLine,
  PieChart,
  Send,
  Users,
  XCircle,
} from "lucide-react";
import { LeaveStatCard } from "../../../components/leaves/employee/LeaveStatCard";
import { EmployeeLeaveStatusBadge } from "../../../components/leaves/employee/EmployeeLeaveStatusBadge";
import { formatLeaveShortDate } from "../../../components/leaves/employee/leaveDateUtils";
import { Button } from "../../../components/ui/button";
import { cn } from "../../../components/ui/utils";
import { useEmployeeLeaveData } from "./EmployeeLeaveDataContext";

const formatDisplayDate = (value: string) =>
  new Date(`${value}T00:00:00`).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

const formatDayName = (value: string) =>
  new Date(`${value}T00:00:00`).toLocaleDateString("en-IN", {
    weekday: "short",
  });

const getDaysRemaining = (value: string) =>
  Math.max(
    0,
    Math.ceil((new Date(`${value}T00:00:00`).getTime() - new Date().setHours(0, 0, 0, 0)) / 86400000),
  );

export function EmployeeLeaveDashboardPage() {
  const navigate = useNavigate();
  const { balances, applications, holidays, year, teamApplications, leaveTypes } = useEmployeeLeaveData();

  const today = new Date();
  const todayLabel = today.toLocaleDateString("en-IN", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
  const todayKey = today.toISOString().slice(0, 10);

  const metrics = useMemo(() => {
    const totalAlloc = balances.reduce((s, b) => s + Number(b.total_allocated || 0), 0);
    const used = balances.reduce((s, b) => s + Number(b.used || 0), 0);
    const remaining = balances.reduce((s, b) => s + Number(b.available || 0), 0);
    const pending = applications.filter((a) => ["SUBMITTED", "DRAFT", "PENDING"].includes(a.status)).length;
    const approved = applications.filter((a) => a.status === "APPROVED").length;
    const rejected = applications.filter((a) => a.status === "REJECTED").length;
    const upcomingHol = holidays.filter((h) => h.date >= todayKey).length;
    return { totalAlloc, used, remaining, pending, approved, rejected, upcomingHol };
  }, [balances, applications, holidays, todayKey]);

  const pendingList = useMemo(
    () => applications.filter((a) => ["SUBMITTED", "DRAFT", "PENDING"].includes(a.status)),
    [applications],
  );

  const upcomingHolList = useMemo(
    () => [...holidays]
      .filter((h) => h.date >= todayKey)
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(0, 3),
    [holidays, todayKey],
  );

  const paidRemaining = useMemo(
    () => balances.filter((b) => b.leave_type_detail?.is_paid).reduce((sum, b) => sum + Number(b.available || 0), 0),
    [balances],
  );

  const mostUsedType = useMemo(() => {
    const counts = new Map<string, number>();
    for (const app of applications) {
      const name = app.leave_type_detail?.name ?? "Other";
      counts.set(name, (counts.get(name) ?? 0) + Number(app.total_days || 0));
    }
    const sorted = [...counts.entries()].sort((a, b) => b[1] - a[1]);
    return sorted.length ? `${sorted[0][0]} · ${sorted[0][1]}d` : "No leave taken yet";
  }, [applications]);

  const carryForwardLabel = useMemo(() => {
    const carry = balances.find((b) => Number(b.carry_forwarded) > 0);
    if (!carry) return "No carry-forward set";
    return `${carry.carry_forwarded}d expiring ${formatDisplayDate(carry.period_end)}`;
  }, [balances]);

  const yearStatus = metrics.pending > metrics.approved ? "Review pending approvals" : "On track";

  const nextHoliday = upcomingHolList[0] ?? null;
  const nextHolidayCountdown = nextHoliday ? getDaysRemaining(nextHoliday.date) : null;

  return (
    <div className="space-y-4 overflow-hidden">
      <header className="rounded-3xl border border-border bg-card p-4 shadow-sm">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-xl font-semibold tracking-tight text-foreground">Leave dashboard</h1>
              <span className="rounded-full border border-border bg-secondary/60 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
                {todayLabel}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button asChild variant="outline" size="sm" className="h-10 rounded-3xl border-border px-3 text-sm font-semibold">
              <Link to="/employee/leaves/applications">View applications</Link>
            </Button>
            <Button asChild size="sm" className="h-10 rounded-3xl bg-foreground px-3 text-sm font-semibold text-primary-foreground">
              <Link to="/employee/leaves/apply" className="inline-flex items-center gap-2">
                <PenLine className="h-4 w-4" />
                Apply leave
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-7">
        <LeaveStatCard icon={PieChart} label="Total balance" value={metrics.totalAlloc} sub="Allocated (all types)" />
        <LeaveStatCard icon={Send} label="Used" value={metrics.used} sub="Consumed this cycle" />
        <LeaveStatCard icon={PieChart} label="Remaining" value={metrics.remaining} sub="Available now" />
        <LeaveStatCard icon={Clock} label="Pending" value={metrics.pending} sub="In approval flow" />
        <LeaveStatCard icon={CheckCircle2} label="Approved" value={metrics.approved} sub="Historical count" />
        <LeaveStatCard icon={XCircle} label="Rejected" value={metrics.rejected} sub="Historical count" />
        <LeaveStatCard icon={CalendarDays} label="Holidays" value={metrics.upcomingHol} sub={`Upcoming · ${year}`} />
      </section>

      <div className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <div className="space-y-4">
          <div className="rounded-3xl border border-border bg-card p-4 shadow-sm">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">Upcoming holidays</p>
                <h2 className="mt-2 text-lg font-semibold text-foreground">Holiday overview</h2>
              </div>
              <Link
                to="/employee/leaves/holidays"
                className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-3 py-1.5 text-sm font-semibold text-foreground transition hover:bg-secondary"
              >
                View full calendar
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            <div className="mt-4 space-y-2 max-h-[24rem] overflow-y-auto pr-1">
              {upcomingHolList.length === 0 ? (
                <div className="rounded-3xl border border-border bg-secondary/20 px-4 py-6 text-center text-sm text-muted-foreground">
                  No upcoming holidays found.
                </div>
              ) : (
                upcomingHolList.map((holiday) => {
                  const holidayDate = new Date(`${holiday.date}T00:00:00`);
                  const dayName = formatDayName(holiday.date);
                  const monthName = holidayDate.toLocaleDateString("en-IN", { month: "short" });
                  const dayNumber = holidayDate.getDate();
                  const daysRemaining = getDaysRemaining(holiday.date);

                  return (
                    <div
                      key={holiday.id}
                      className={cn(
                        "group flex items-center gap-3 rounded-3xl border border-border bg-background/70 px-3 py-3 transition hover:border-foreground/20 hover:shadow-lg",
                      )}
                    >
                      <div className="grid h-16 w-16 flex-shrink-0 place-items-center rounded-3xl border border-border bg-card text-center">
                        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">{dayName}</p>
                        <p className="text-2xl font-semibold text-foreground">{dayNumber}</p>
                        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">{monthName}</p>
                      </div>

                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold text-foreground">{holiday.name}</p>
                      </div>

                      <span className="rounded-full border border-border bg-secondary/60 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                        {daysRemaining}d left
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-border bg-card p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">Pending approvals</p>
                <h2 className="mt-2 text-lg font-semibold text-foreground">Waiting for review</h2>
              </div>
              <span className="rounded-full bg-secondary/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                {pendingList.length} pending
              </span>
            </div>

            <div className="mt-4 space-y-2 max-h-[24rem] overflow-y-auto pr-1">
              {pendingList.length === 0 ? (
                <div className="rounded-3xl border border-border bg-secondary/20 px-4 py-6 text-center text-sm text-muted-foreground">
                  Nothing waiting for approval.
                </div>
              ) : (
                pendingList.map((app) => (
                  <div
                    key={app.id}
                    className="group flex items-center gap-3 rounded-3xl border border-border bg-background/80 px-3 py-3 transition hover:border-foreground/20 hover:shadow-lg"
                  >
                    <div className="grid h-12 w-12 flex-shrink-0 place-items-center rounded-3xl border border-border bg-secondary text-foreground">
                      <Clock className="h-4 w-4" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-foreground">{app.leave_type_detail?.name || "Leave request"}</p>
                      <p className="mt-1 text-[11px] text-muted-foreground">
                        {formatLeaveShortDate(app.from_date)} — {formatLeaveShortDate(app.to_date)} · {app.total_days}d
                      </p>
                    </div>

                    <div className="text-right text-[11px] text-muted-foreground">
                      <p>Applied {formatLeaveShortDate(app.applied_on)}</p>
                      <span className="inline-flex rounded-full border border-border bg-secondary/50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.16em]">
                        {app.leave_type_detail?.code ?? "—"}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-3xl border border-border bg-card p-4 shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">Quick actions</p>
              <h2 className="mt-2 text-lg font-semibold text-foreground">Stay productive</h2>
            </div>

            <div className="mt-4 grid gap-2">
              <button
                type="button"
                onClick={() => navigate("/employee/leaves/apply")}
                className="group flex items-center justify-between rounded-3xl border border-border bg-secondary/40 px-3 py-3 text-left transition hover:bg-secondary"
              >
                <div className="flex items-center gap-2">
                  <span className="grid h-10 w-10 place-items-center rounded-3xl border border-border bg-card text-foreground">
                    <PenLine className="h-4 w-4" />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-foreground">New request</p>
                    <p className="text-[11px] text-muted-foreground">Submit leave quickly</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
              </button>

              <button
                type="button"
                onClick={() => navigate("/employee/leaves/holidays")}
                className="group flex items-center justify-between rounded-3xl border border-border bg-secondary/40 px-3 py-3 text-left transition hover:bg-secondary"
              >
                <div className="flex items-center gap-2">
                  <span className="grid h-10 w-10 place-items-center rounded-3xl border border-border bg-card text-foreground">
                    <CalendarDays className="h-4 w-4" />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-foreground">Holiday calendar</p>
                    <p className="text-[11px] text-muted-foreground">Review schedule</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
              </button>

              <button
                type="button"
                onClick={() => navigate("/employee/leaves/team")}
                className="group flex items-center justify-between rounded-3xl border border-border bg-secondary/40 px-3 py-3 text-left transition hover:bg-secondary"
              >
                <div className="flex items-center gap-2">
                  <span className="grid h-10 w-10 place-items-center rounded-3xl border border-border bg-card text-foreground">
                    <Users className="h-4 w-4" />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-foreground">Team availability</p>
                    <p className="text-[11px] text-muted-foreground">See colleague schedules</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
              </button>
            </div>
          </div>

          <div className="rounded-3xl border border-border bg-card p-4 shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-muted-foreground">Leave insights</p>
              <h2 className="mt-2 text-lg font-semibold text-foreground">Year at a glance</h2>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {[
                {
                  label: "Next holiday countdown",
                  value: nextHoliday ? `${nextHolidayCountdown} days until ${nextHoliday.name}` : "No upcoming holiday",
                },
                { label: "Most used leave type", value: mostUsedType },
                { label: "Remaining paid leaves", value: `${paidRemaining}d` },
                { label: "Carry-forward expiry", value: carryForwardLabel },
                { label: "Leave year status", value: yearStatus },
              ].map((item) => (
                <div key={item.label} className="rounded-3xl border border-border bg-background/80 px-3 py-3">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-muted-foreground">{item.label}</p>
                  <p className="mt-1 text-sm font-semibold text-foreground">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
