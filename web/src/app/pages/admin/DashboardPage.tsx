import { useState } from "react";
import { useNavigate } from "react-router";
import {
  Users, UserCheck, CalendarOff, ClipboardCheck,
  Cake, CalendarDays, CheckSquare, ChevronRight,
  UserPlus, ShieldCheck, Hourglass, TrendingUp,
} from "lucide-react";
import {
  PortalPage,
  SectionLabel,
  KpiCard,
  WidgetHeader,
  KPI_ICON_TONES,
  type KpiTone,
} from "../../../components/design-system";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, PieChart, Pie,
} from "recharts";
import { employees } from "../../components/employees/mockData";
import { leaveRequests, attendanceRecords } from "../../components/employees/mockAdminData";

/* Enterprise chart palette */
const CHART = {
  primary: "#6366F1",
  secondary: "#8B5CF6",
  accent: "#A855F7",
  success: "#753cd1",
  warning: "#F59E0B",
  danger: "#EF4444",
  info: "#3B82F6",
  muted: "#94A3B8",
};

/* ── Derived stats ─────────────────────────────────────────── */
const totalEmployees = employees.length;
const todayRecords = attendanceRecords.filter((r) => r.date === "2026-05-05");
const presentToday = todayRecords.filter((r) => r.status === "Present").length;
const onLeaveToday = todayRecords.filter((r) => r.status === "On Leave").length;
const halfDayToday = todayRecords.filter((r) => r.status === "Half Day").length;
const notLoggedIn = todayRecords.filter((r) => r.status === "Absent").length;
const pendingCount = leaveRequests.filter((l) => l.status === "Pending").length;

const donutData = [
  { name: "Present", value: presentToday, color: CHART.success },
  { name: "On Leave", value: onLeaveToday, color: CHART.secondary },
  { name: "Not Logged In", value: notLoggedIn, color: CHART.muted },
  { name: "Half Day", value: halfDayToday, color: CHART.info },
];

const deptData = Object.entries(
  employees.reduce<Record<string, number>>((acc, e) => {
    acc[e.department] = (acc[e.department] || 0) + 1;
    return acc;
  }, {})
).map(([dept, count]) => ({
  dept: dept.length > 9 ? dept.slice(0, 9) + "…" : dept,
  count,
}));

const BAR_COLORS = [
  CHART.primary,
  CHART.secondary,
  CHART.accent,
  CHART.info,
  CHART.primary,
  CHART.secondary,
  CHART.accent,
];

const EVENTS = {
  meetings: [
    {
      id: "m1",
      title: "Q2 Quarterly Review",
      desc: "Conference Room A",
      time: "2:00 PM",
      tag: "Today",
      tagType: "today" as const
    },
    {
      id: "m2",
      title: "Sprint Planning — Frontend",
      desc: "Zoom Call",
      time: "11:00 AM",
      tag: "Today",
      tagType: "today" as const
    },
    {
      id: "m3",
      title: "1:1 with Eng Lead",
      desc: "Manager's Office",
      time: "May 7",
      tag: "In 2 days",
      tagType: "soon" as const
    },
    {
      id: "m4",
      title: "HR Policy Review",
      desc: "HR Conf. Room",
      time: "May 10",
      tag: "In 5 days",
      tagType: "soon" as const
    },
  ],

  birthdays: [
    {
      id: "b1",
      title: "Rajesh Kumar",
      desc: "DevOps Engineer",
      time: "Today",
      tag: "Today",
      tagType: "today" as const
    },
    {
      id: "b2",
      title: "Vikram Mehta",
      desc: "Product Manager",
      time: "May 15",
      tag: "In 10 days",
      tagType: "soon" as const
    },
    {
      id: "b3",
      title: "Divya Pillai",
      desc: "Finance Executive",
      time: "May 28",
      tag: "In 23 days",
      tagType: "later" as const
    },
  ],

  holidays: [
    {
      id: "h1",
      title: "Eid al-Adha",
      desc: "National Holiday",
      time: "May 27",
      tag: "In 22 days",
      tagType: "later" as const
    },
    {
      id: "h2",
      title: "Independence Day",
      desc: "National Holiday",
      time: "Aug 15",
      tag: "~102 days",
      tagType: "later" as const
    },
    {
      id: "h3",
      title: "Gandhi Jayanti",
      desc: "National Holiday",
      time: "Oct 2",
      tag: "~150 days",
      tagType: "later" as const
    },
  ],
};

const ALL_EVENTS = [
  ...EVENTS.meetings.map((e) => ({ ...e, category: "meeting" })),
  ...EVENTS.birthdays.map((e) => ({ ...e, category: "birthday" })),
  ...EVENTS.holidays.map((e) => ({ ...e, category: "holiday" })),
].sort((a) => (a.tag === "Today" ? -1 : 0));

const LIFECYCLE = [
  {
    id: "lc1",
    icon: UserPlus,
    title: "Onboarding Due",
    desc: "New joiners pending document submission",
    count: 2,
    employees: ["Ananya Iyer", "Rajesh Kumar"],
  },
  {
    id: "lc2",
    icon: ShieldCheck,
    title: "Confirmation Pending",
    desc: "Employees completing probation this month",
    count: 1,
    employees: ["Sneha Krishnan"],
  },
  {
    id: "lc3",
    icon: Hourglass,
    title: "Probation Ending Soon",
    desc: "Probation period ends within 30 days",
    count: 3,
    employees: ["Arjun Sharma", "Priya Nair", "Karthik Reddy"],
  },
];

type EventTab = "all" | "meetings" | "birthdays" | "holidays";

function DonutCenter({
  cx,
  cy,
  total,
}: {
  cx: number;
  cy: number;
  total: number;
}) {
  return (
    <g>
      <text
        x={cx}
        y={cy - 3}
        textAnchor="middle"
        style={{
          fontSize: "18px",
          fontWeight: 700,
          fill: "var(--foreground)",
        }}
      >
        {total}
      </text>

      <text
        x={cx}
        y={cy + 11}
        textAnchor="middle"
        style={{
          fontSize: "9px",
          fill: "var(--muted-foreground)",
          fontWeight: 500,
        }}
      >
        Total
      </text>
    </g>
  );
}

function DonutStat({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="dashboard-stat-chip">
      <div
        className="w-1.5 h-1.5 rounded-full flex-shrink-0"
        style={{ background: color }}
      />
      <div className="min-w-0">
        <p className="text-[9px] font-semibold text-muted-foreground uppercase tracking-wider leading-none mb-0.5">
          {label}
        </p>
        <p className="text-sm font-bold text-foreground leading-none">
          {value}
        </p>
      </div>
    </div>
  );
}

const BarTooltip = ({ active, payload, label }: { active?: boolean; payload?: { value: number }[]; label?: string }) => {
  if (!active || !payload?.length) return null;

  return (
    <div className="rounded-md border border-border bg-card px-2.5 py-1.5 text-[11px] shadow-md">
      <p className="text-muted-foreground mb-0.5">{label}</p>
      <p className="font-semibold text-foreground">{payload[0].value} employees</p>
    </div>
  );
};

const tagStyle = (type: "today" | "soon" | "later"): string => {
  if (type === "today") return "dashboard-badge-today";
  if (type === "soon") return "dashboard-badge-soon";
  return "dashboard-badge-later";
};

const categoryIcon = (cat: string) => {
  if (cat === "meeting") return <CheckSquare className="w-3 h-3 text-primary" />;
  if (cat === "birthday") return <Cake className="w-3 h-3 text-accent" />;
  return <CalendarDays className="w-3 h-3 text-muted-foreground" />;
};

/* ── Main Page ─────────────────────────────────────────────── */
export function DashboardPage() {
  const navigate = useNavigate();
  const [eventTab, setEventTab] = useState<EventTab>("all");

  const displayEvents =
    eventTab === "all"
      ? ALL_EVENTS
      : eventTab === "meetings"
        ? EVENTS.meetings.map((e) => ({
          ...e,
          category: "meeting",
        }))
        : eventTab === "birthdays"
          ? EVENTS.birthdays.map((e) => ({
            ...e,
            category: "birthday",
          }))
          : EVENTS.holidays.map((e) => ({
            ...e,
            category: "holiday",
          }));

  const tabs: {
    id: EventTab;
    label: string;
  }[] = [
      { id: "all", label: "All" },
      { id: "meetings", label: "Meetings" },
      { id: "birthdays", label: "Birthdays" },
      { id: "holidays", label: "Holidays" },
    ];

  return (
    <PortalPage>
      {/* TOP — KPI row (unchanged cards) */}
      <section>
        <SectionLabel label="Overview" />
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
          <KpiCard
            icon={Users}
            label="Total Employees"
            value={totalEmployees}
            sub="Across all departments"
            tone="purple"
          />

          <KpiCard
            icon={UserCheck}
            label="Present Today"
            value={presentToday}
            sub="Checked in today"
            tone="green"
          />

          <KpiCard
            icon={CalendarOff}
            label="On Leave Today"
            value={onLeaveToday}
            sub="Approved absences"
            tone="orange"
          />

          <KpiCard
            icon={ClipboardCheck}
            label="Pending Approvals"
            value={pendingCount}
            sub="Awaiting your action"
            tone="red"
          />
        </div>
      </section>

      {/* MIDDLE — Analytics */}
      <section>
        <SectionLabel label="Analytics" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          <div className="dashboard-widget">
            <WidgetHeader
              icon={CheckSquare}
              title="Attendance Summary"
              subtitle="Today's workforce status breakdown"
              tone="green"
            />
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <div className="flex-shrink-0">
                <ResponsiveContainer width={148} height={148}>
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%"
                      cy="50%"
                      innerRadius={46}
                      outerRadius={62}
                      paddingAngle={2}
                      dataKey="value"
                      strokeWidth={0}
                      cornerRadius={2}
                    >
                      {donutData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <DonutCenter cx={74} cy={74} total={todayRecords.length} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-2 flex-1 w-full">
                <DonutStat label="Present" value={presentToday} color={CHART.success} />
                <DonutStat label="On Leave" value={onLeaveToday} color={CHART.secondary} />
                <DonutStat label="Not Logged In" value={notLoggedIn} color={CHART.muted} />
                <DonutStat label="Half Day" value={halfDayToday} color={CHART.info} />
              </div>
            </div>
          </div>

          <div className="dashboard-widget">
            <WidgetHeader
              icon={TrendingUp}
              title="Employees by Department"
              subtitle="Headcount across teams"
              tone="purple"
            />
            <ResponsiveContainer width="100%" height={152}>
              <BarChart
                data={deptData}
                barSize={18}
                margin={{ top: 2, right: 4, left: -24, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis
                  dataKey="dept"
                  tick={{ fontSize: 9, fill: "var(--muted-foreground)" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 9, fill: "var(--muted-foreground)" }}
                  axisLine={false}
                  tickLine={false}
                  allowDecimals={false}
                  width={28}
                />
                <Tooltip content={<BarTooltip />} cursor={{ fill: "var(--secondary)" }} />
                <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                  {deptData.map((_, i) => (
                    <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* BOTTOM — Events & lifecycle */}
      <section>
        <SectionLabel label="Reminders & Alerts" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          <div className="dashboard-widget flex flex-col min-h-0">
            <WidgetHeader
              icon={CalendarDays}
              title="Events & Reminders"
              subtitle="Tasks, birthdays & holidays"
              tone="purple"
            />
            <div className="dashboard-tab-strip">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setEventTab(tab.id)}
                  className={`dashboard-tab-btn ${eventTab === tab.id ? "is-active" : ""}`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <div className="space-y-1.5 max-h-[280px] overflow-y-auto flex-1 min-h-0">
              {displayEvents.map((ev) => (
                <div key={ev.id} className="dashboard-event-row">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="w-7 h-7 rounded-md bg-secondary border border-border flex items-center justify-center flex-shrink-0">
                      {categoryIcon((ev as { category: string }).category)}
                    </div>
                    <div className="min-w-0">
                      <p className="text-[12px] font-medium text-foreground truncate">{ev.title}</p>
                      <p className="text-[10px] text-muted-foreground truncate">
                        {ev.desc} · {ev.time}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`flex-shrink-0 px-1.5 py-0.5 rounded text-[9px] font-semibold uppercase tracking-wide ${tagStyle(
                      (ev as { tagType: "today" | "soon" | "later" }).tagType
                    )}`}
                  >
                    {ev.tag}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="dashboard-widget flex flex-col">
            <WidgetHeader
              icon={Hourglass}
              title="Lifecycle Alerts"
              subtitle="Employee milestones requiring attention"
              tone="orange"
            />
            <div className="space-y-2">
              {LIFECYCLE.map((alert, idx) => {
                const Icon = alert.icon;
                const tones: KpiTone[] = ["purple", "green", "orange"];
                const tone = tones[idx % tones.length];
                const iconTone = KPI_ICON_TONES[tone];

                return (
                  <div key={alert.id} className="dashboard-lifecycle-card">
                    <div className="flex items-start gap-3">
                      <div
                        className="dashboard-widget-icon w-8 h-8"
                        style={{
                          background: iconTone.background,
                          boxShadow: iconTone.boxShadow,
                        }}
                      >
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2 mb-0.5">
                          <p className="text-[12px] font-semibold text-foreground">{alert.title}</p>
                          <span className="min-w-[18px] h-[18px] px-1 rounded bg-primary text-primary-foreground text-[9px] font-bold flex items-center justify-center flex-shrink-0">
                            {alert.count}
                          </span>
                        </div>
                        <p className="text-[10px] text-muted-foreground mb-2">{alert.desc}</p>
                        <div className="flex flex-wrap gap-1 mb-2">
                          {alert.employees.map((name) => (
                            <span
                              key={name}
                              className="text-[10px] font-medium text-foreground bg-secondary border border-border px-1.5 py-0.5 rounded"
                            >
                              {name}
                            </span>
                          ))}
                        </div>
                        <button
                          type="button"
                          onClick={() => navigate("/admin/employees")}
                          className="flex items-center gap-0.5 text-[10px] font-semibold text-primary hover:opacity-80 transition-opacity"
                        >
                          Take Action
                          <ChevronRight className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>
    </PortalPage>
  );
}