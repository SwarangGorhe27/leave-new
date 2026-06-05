import { useState } from "react";
import { useNavigate } from "react-router";
import {
  Users, UserCheck, CalendarOff, ClipboardCheck,
  Cake, CalendarDays, CheckSquare, ChevronRight,
  UserPlus, ShieldCheck, Hourglass,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, PieChart, Pie,
} from "recharts";
import { employees } from "../../components/employees/mockData";
import { leaveRequests, attendanceRecords } from "../../components/employees/mockAdminData";

/* ── Palette (monochrome) ──────────────────────────────────── */
const P = {
  darkest: "#212529",
  dark: "#343A40",
  mid: "#495057",
  muted: "#6C757D",
  light: "#ADB5BD",
  lighter: "#CED4DA",
  lightest: "#F8F9FA",
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
  { name: "Present", value: presentToday, color: P.darkest },
  { name: "On Leave", value: onLeaveToday, color: P.mid },
  { name: "Not Logged In", value: notLoggedIn, color: P.lighter },
  { name: "Half Day", value: halfDayToday, color: P.muted },
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

const BAR_COLORS = [P.darkest, P.dark, P.mid, P.muted, P.light, P.lighter, "#DEE2E6"];

const EVENTS = {
  meetings: [
    { id: "m1", title: "Q2 Quarterly Review", desc: "Conference Room A", time: "2:00 PM", tag: "Today", tagType: "today" as const },
    { id: "m2", title: "Sprint Planning — Frontend", desc: "Zoom Call", time: "11:00 AM", tag: "Today", tagType: "today" as const },
    { id: "m3", title: "1:1 with Eng Lead", desc: "Manager's Office", time: "May 7", tag: "In 2 days", tagType: "soon" as const },
    { id: "m4", title: "HR Policy Review", desc: "HR Conf. Room", time: "May 10", tag: "In 5 days", tagType: "soon" as const },
  ],
  birthdays: [
    { id: "b1", title: "Rajesh Kumar", desc: "DevOps Engineer", time: "Today", tag: "Today", tagType: "today" as const },
    { id: "b2", title: "Vikram Mehta", desc: "Product Manager", time: "May 15", tag: "In 10 days", tagType: "soon" as const },
    { id: "b3", title: "Divya Pillai", desc: "Finance Executive", time: "May 28", tag: "In 23 days", tagType: "later" as const },
  ],
  holidays: [
    { id: "h1", title: "Eid al-Adha", desc: "National Holiday", time: "May 27", tag: "In 22 days", tagType: "later" as const },
    { id: "h2", title: "Independence Day", desc: "National Holiday", time: "Aug 15", tag: "~102 days", tagType: "later" as const },
    { id: "h3", title: "Gandhi Jayanti", desc: "National Holiday", time: "Oct 2", tag: "~150 days", tagType: "later" as const },
  ],
};

const ALL_EVENTS = [
  ...EVENTS.meetings.map((e) => ({ ...e, category: "meeting" })),
  ...EVENTS.birthdays.map((e) => ({ ...e, category: "birthday" })),
  ...EVENTS.holidays.map((e) => ({ ...e, category: "holiday" })),
].sort((a) => (a.tag === "Today" ? -1 : 0));

const LIFECYCLE = [
  {
    id: "lc1", icon: UserPlus, title: "Onboarding Due",
    desc: "New joiners pending document submission",
    count: 2, employees: ["Ananya Iyer", "Rajesh Kumar"],
  },
  {
    id: "lc2", icon: ShieldCheck, title: "Confirmation Pending",
    desc: "Employees completing probation this month",
    count: 1, employees: ["Sneha Krishnan"],
  },
  {
    id: "lc3", icon: Hourglass, title: "Probation Ending Soon",
    desc: "Probation period ends within 30 days",
    count: 3, employees: ["Arjun Sharma", "Priya Nair", "Karthik Reddy"],
  },
];

type EventTab = "all" | "meetings" | "birthdays" | "holidays";

/* ── Sub-components ────────────────────────────────────────── */
function SectionLabel({ label }: { label: string }) {
  return (
    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-widest mb-4">
      {label}
    </p>
  );
}

function KpiCard({
  icon: Icon, label, value, sub,
}: {
  icon: React.ElementType; label: string; value: number | string; sub: string;
}) {
  return (
    <div className="flat-card flat-card-hover bg-card p-5 flex items-start gap-4">
      <div className="w-11 h-11 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-foreground" />
      </div>
      <div>
        <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-bold text-foreground mt-0.5">{value}</p>
        <p className="text-xs text-muted-foreground mt-1">{sub}</p>
      </div>
    </div>
  );
}

function DonutCenter({ cx, cy, total }: { cx: number; cy: number; total: number }) {
  return (
    <g>
      <text x={cx} y={cy - 4} textAnchor="middle"
        style={{ fontSize: "22px", fontWeight: 700, fill: "var(--foreground)" }}
      >{total}</text>
      <text x={cx} y={cy + 14} textAnchor="middle"
        style={{ fontSize: "11px", fill: "var(--muted-foreground)", fontWeight: 500 }}
      >Total</text>
    </g>
  );
}

function DonutStat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-background border border-border rounded-lg">
      <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
      <div>
        <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider leading-none mb-1">{label}</p>
        <p className="text-lg font-bold text-foreground leading-none">{value}</p>
      </div>
    </div>
  );
}

const BarTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-foreground text-primary-foreground text-xs px-3 py-2 rounded-lg shadow-lg">
      <p className="text-muted mb-0.5">{label}</p>
      <p className="font-semibold">{payload[0].value} employees</p>
    </div>
  );
};

const tagStyle = (type: "today" | "soon" | "later"): string => {
  if (type === "today") return "bg-foreground text-primary-foreground";
  if (type === "soon") return "bg-secondary text-foreground border border-border";
  return "bg-background text-muted-foreground border border-border";
};

const categoryIcon = (cat: string) => {
  if (cat === "meeting") return <CheckSquare className="w-3.5 h-3.5 text-foreground" />;
  if (cat === "birthday") return <Cake className="w-3.5 h-3.5 text-muted-foreground" />;
  return <CalendarDays className="w-3.5 h-3.5 text-muted-foreground" />;
};

/* ── Main Page ─────────────────────────────────────────────── */
export function DashboardPage() {
  const navigate = useNavigate();
  const [eventTab, setEventTab] = useState<EventTab>("all");

  const displayEvents =
    eventTab === "all" ? ALL_EVENTS
      : eventTab === "meetings" ? EVENTS.meetings.map((e) => ({ ...e, category: "meeting" }))
        : eventTab === "birthdays" ? EVENTS.birthdays.map((e) => ({ ...e, category: "birthday" }))
          : EVENTS.holidays.map((e) => ({ ...e, category: "holiday" }));

  const tabs: { id: EventTab; label: string }[] = [
    { id: "all", label: "All" },
    { id: "meetings", label: "Meetings" },
    { id: "birthdays", label: "Birthdays" },
    { id: "holidays", label: "Holidays" },
  ];

  return (
    <div className="p-6 space-y-8">

      {/* ── KPI Cards ──────────────────────────────────── */}
      <section>
        <SectionLabel label="Overview" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard icon={Users} label="Total Employees" value={totalEmployees} sub="Across all departments" />
          <KpiCard icon={UserCheck} label="Present Today" value={presentToday} sub="Checked in today" />
          <KpiCard icon={CalendarOff} label="On Leave Today" value={onLeaveToday} sub="Approved absences" />
          <KpiCard icon={ClipboardCheck} label="Pending Approvals" value={pendingCount} sub="Awaiting your action" />
        </div>
      </section>

      {/* ── Charts ─────────────────────────────────────── */}
      <section>
        <SectionLabel label="Analytics" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

          {/* Attendance donut */}
          <div className="flat-card bg-card p-6">
            <h2 className="text-base font-semibold text-foreground mb-1">Attendance Summary</h2>
            <p className="text-xs text-muted-foreground mb-6">Today's workforce status breakdown</p>
            <div className="flex flex-col sm:flex-row items-center gap-6">
              <div className="flex-shrink-0">
                <ResponsiveContainer width={180} height={180}>
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%" cy="50%"
                      innerRadius={58} outerRadius={78}
                      paddingAngle={3} dataKey="value"
                      strokeWidth={0} cornerRadius={3}
                    >
                      {donutData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                    </Pie>
                    <DonutCenter cx={90} cy={90} total={todayRecords.length} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-3 flex-1 w-full">
                <DonutStat label="Present" value={presentToday} color={P.darkest} />
                <DonutStat label="On Leave" value={onLeaveToday} color={P.mid} />
                <DonutStat label="Not Logged In" value={notLoggedIn} color={P.lighter} />
                <DonutStat label="Half Day" value={halfDayToday} color={P.muted} />
              </div>
            </div>
          </div>

          {/* Dept bar chart */}
          <div className="flat-card bg-card p-6">
            <h2 className="text-base font-semibold text-foreground mb-1">Employees by Department</h2>
            <p className="text-xs text-muted-foreground mb-6">Headcount across teams</p>
            <ResponsiveContainer width="100%" height={190}>
              <BarChart data={deptData} barSize={24} margin={{ top: 4, right: 4, left: -22, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="dept" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip content={<BarTooltip />} cursor={{ fill: "var(--secondary)" }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {deptData.map((_, i) => <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* ── Reminders & Alerts ─────────────────────────── */}
      <section>
        <SectionLabel label="Reminders & Alerts" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

          {/* Events feed */}
          <div className="flat-card bg-card p-6 flex flex-col">
            <h2 className="text-base font-semibold text-foreground mb-1">Events & Reminders</h2>
            <p className="text-xs text-muted-foreground mb-5">Tasks, birthdays & holidays</p>

            {/* Tab strip */}
            <div className="flex gap-1 p-1 bg-secondary rounded-lg mb-4">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setEventTab(tab.id)}
                  className={`flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-150 ${eventTab === tab.id
                      ? "bg-card text-foreground shadow-sm border border-border"
                      : "text-muted-foreground hover:text-foreground"
                    }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="space-y-2 overflow-y-auto max-h-[240px] pr-1">
              {displayEvents.map((ev) => (
                <div
                  key={ev.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-border
                    hover:bg-secondary transition-colors cursor-pointer group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-md bg-secondary border border-border flex items-center justify-center flex-shrink-0">
                      {categoryIcon((ev as any).category)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground">{ev.title}</p>
                      <p className="text-xs text-muted-foreground">{ev.desc} · {ev.time}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wider ${tagStyle((ev as any).tagType)}`}>
                    {ev.tag}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Lifecycle alerts */}
          <div className="flat-card bg-card p-6 flex flex-col">
            <h2 className="text-base font-semibold text-foreground mb-1">Lifecycle Alerts</h2>
            <p className="text-xs text-muted-foreground mb-5">Employee milestones requiring attention</p>

            <div className="space-y-4">
              {LIFECYCLE.map((alert) => {
                const Icon = alert.icon;
                return (
                  <div key={alert.id} className="p-4 rounded-lg border border-border bg-background hover:bg-secondary transition-colors">
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
                        <Icon className="w-5 h-5 text-foreground" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <p className="text-sm font-semibold text-foreground">{alert.title}</p>
                          <span className="w-5 h-5 rounded-md bg-foreground text-primary-foreground text-[10px] font-bold flex items-center justify-center flex-shrink-0">
                            {alert.count}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mb-3">{alert.desc}</p>
                        <div className="flex flex-wrap gap-1.5 mb-3">
                          {alert.employees.map((name) => (
                            <span key={name} className="text-xs font-medium text-foreground bg-secondary border border-border px-2 py-0.5 rounded-md">
                              {name}
                            </span>
                          ))}
                        </div>
                        <button
                          onClick={() => navigate("/admin/employees")}
                          className="flex items-center gap-1 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
                        >
                          Take Action <ChevronRight className="w-3.5 h-3.5" />
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
    </div>
  );
}
