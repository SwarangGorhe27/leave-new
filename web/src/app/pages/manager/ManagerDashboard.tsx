import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../../context/AuthContext";
import { employees } from "../../components/employees/mockData";
import {
  LogIn,
  LogOut,
  CalendarDays,
  Wallet,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Users,
  ClipboardCheck,
  ChevronRight,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  PortalPage,
  SectionLabel,
  KpiCard,
  WidgetHeader,
  ChartTooltip,
  STATUS_BADGE_CLASS,
} from "../../../components/design-system";

const RECENT_ACTIVITY = [
  { day: "Mon 5 May", status: "Present", checkIn: "09:10 AM", checkOut: "06:05 PM", hours: "8h 55m" },
  { day: "Tue 6 May", status: "Present", checkIn: "09:02 AM", checkOut: "06:12 PM", hours: "9h 10m" },
  { day: "Wed 7 May", status: "Leave", checkIn: "—", checkOut: "—", hours: "—" },
  { day: "Thu 8 May", status: "Present", checkIn: "09:25 AM", checkOut: "06:00 PM", hours: "8h 35m" },
  { day: "Fri 9 May", status: "Present", checkIn: "09:08 AM", checkOut: "06:20 PM", hours: "9h 12m" },
];

const WEEKLY_HOURS = [
  { day: "Mon", hours: 8.9 },
  { day: "Tue", hours: 9.2 },
  { day: "Wed", hours: 0 },
  { day: "Thu", hours: 8.6 },
  { day: "Fri", hours: 9.2 },
];

const UPCOMING = {
  Events: [
    { title: "Team Lunch", date: "Tomorrow, 1 PM" },
    { title: "Townhall Q2", date: "Friday, 10 AM" },
    { title: "1:1 — Sprint Review", date: "May 15" },
  ],
  Holidays: [
    { title: "Eid al-Adha", date: "May 27" },
    { title: "Independence Day", date: "Aug 15" },
  ],
  Birthdays: [
    { title: "Rajesh Kumar", date: "Today" },
    { title: "Divya Pillai", date: "May 28" },
  ],
};

type FeedTab = "Events" | "Holidays" | "Birthdays";

function LiveClock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <span className="font-mono text-lg font-bold text-foreground tabular-nums">
      {time.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
    </span>
  );
}

export function ManagerDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<FeedTab>("Events");
  const [checkedIn, setCheckedIn] = useState(true);
  const [checkInTime] = useState("09:12 AM");
  const [elapsed] = useState("6h 32m");

  const emp = employees.find((e) => e.id === user?.employeeId) || employees[0];
  const firstName = emp.name.split(" ")[0];
  const feed = UPCOMING[activeTab] || [];
  const feedTabs: FeedTab[] = ["Events", "Holidays", "Birthdays"];

  return (
    <PortalPage>
      <section>
        <SectionLabel label="Today" />
        <div className="dashboard-widget">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="min-w-0">
              <h2 className="text-[15px] font-semibold text-foreground">Good morning, {firstName}</h2>
              <p className="text-[11px] text-muted-foreground mt-1">
                {new Date().toLocaleDateString("en-IN", {
                  weekday: "long",
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })}
              </p>
              <div className="flex flex-wrap items-center gap-2 mt-3">
                <span
                  className={`inline-flex items-center gap-1.5 text-[10px] font-semibold px-2 py-1 rounded ${
                    checkedIn ? "dashboard-badge-today" : "dashboard-badge-later"
                  }`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${checkedIn ? "bg-primary-foreground" : "bg-muted-foreground"}`} />
                  {checkedIn ? `Working · Checked in ${checkInTime}` : "Not checked in"}
                </span>
                {checkedIn && (
                  <span className="text-[10px] font-medium text-foreground bg-secondary border border-border px-2 py-1 rounded">
                    {elapsed} elapsed
                  </span>
                )}
              </div>
            </div>
            <div className="flex flex-col items-start md:items-end gap-2 flex-shrink-0">
              <LiveClock />
              <button
                type="button"
                onClick={() => setCheckedIn(!checkedIn)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-[12px] font-semibold transition-opacity ${
                  checkedIn
                    ? "bg-secondary text-foreground border border-border hover:opacity-90"
                    : "bg-primary text-primary-foreground hover:opacity-90"
                }`}
              >
                {checkedIn ? (
                  <>
                    <LogOut className="w-3.5 h-3.5" /> Check Out
                  </>
                ) : (
                  <>
                    <LogIn className="w-3.5 h-3.5" /> Check In
                  </>
                )}
              </button>
            </div>
          </div>
          {checkedIn && (
            <div className="mt-4 pt-4 border-t border-border">
              <div className="relative h-1.5 bg-secondary rounded-full overflow-hidden">
                <div className="absolute left-0 top-0 h-full bg-primary rounded-full" style={{ width: "72.5%" }} />
              </div>
              <div className="flex justify-between mt-2 text-[10px] text-muted-foreground font-medium">
                <span>Scheduled: 9h</span>
                <span className="font-semibold text-foreground">{elapsed} worked</span>
                <span>Remaining: 2h 28m</span>
              </div>
            </div>
          )}
        </div>
      </section>

      <section>
        <SectionLabel label="Team Overview" />
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
          <KpiCard icon={Users} label="Team Size" value={12} sub="Direct reports" tone="purple" />
          <KpiCard icon={CheckCircle2} label="Present Today" value={10} sub="Team checked in" tone="green" />
          <KpiCard icon={ClipboardCheck} label="Pending Approvals" value={4} sub="Leave & attendance" tone="red" />
          <KpiCard icon={AlertCircle} label="Needs Attention" value={2} sub="Late / absent today" tone="orange" />
        </div>
      </section>

      <section>
        <SectionLabel label="Analytics" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          <div className="dashboard-widget lg:col-span-2">
            <WidgetHeader icon={TrendingUp} title="My Weekly Hours" subtitle="Your hours worked this week" tone="purple" />
            <ResponsiveContainer width="100%" height={152}>
              <AreaChart data={WEEKLY_HOURS} margin={{ top: 2, right: 4, left: -24, bottom: 0 }}>
                <defs>
                  <linearGradient id="mgrHoursGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="day" tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} domain={[0, 10]} width={28} />
                <Tooltip content={<ChartTooltip valueSuffix="h" />} cursor={{ stroke: "var(--border)" }} />
                <Area
                  type="monotone"
                  dataKey="hours"
                  stroke="var(--primary)"
                  strokeWidth={2}
                  fill="url(#mgrHoursGrad)"
                  dot={{ fill: "var(--primary)", r: 2, strokeWidth: 0 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="dashboard-widget flex flex-col min-h-0">
            <WidgetHeader icon={CalendarDays} title="What's Coming" subtitle="Team events & reminders" tone="green" />
            <div className="dashboard-tab-strip">
              {feedTabs.map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={`dashboard-tab-btn ${activeTab === tab ? "is-active" : ""}`}
                >
                  {tab}
                </button>
              ))}
            </div>
            <div className="space-y-1.5 max-h-[220px] overflow-y-auto flex-1 min-h-0">
              {feed.map((item, i) => (
                <div key={i} className="dashboard-event-row">
                  <p className="text-[12px] font-medium text-foreground truncate">{item.title}</p>
                  <span className="dashboard-badge-soon flex-shrink-0 px-1.5 py-0.5 rounded text-[9px] font-semibold">
                    {item.date}
                  </span>
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={() => navigate("/manager/approvals")}
              className="mt-3 flex items-center gap-0.5 text-[10px] font-semibold text-primary hover:opacity-80 transition-opacity"
            >
              Review approvals
              <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </section>

      <section>
        <SectionLabel label="My Attendance" />
        <div className="dashboard-widget p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between gap-3">
            <div>
              <h2 className="dashboard-widget-title">Recent Attendance</h2>
              <p className="dashboard-widget-subtitle">Last 5 working days</p>
            </div>
            <button
              type="button"
              onClick={() => navigate("/manager/attendance")}
              className="flex items-center gap-0.5 text-[10px] font-semibold text-primary hover:opacity-80 transition-opacity"
            >
              View all
              <ChevronRight className="w-3 h-3" />
            </button>
          </div>
          <div className="hrms-table-wrap">
            <table className="w-full">
              <thead>
                <tr>
                  {["Day", "Status", "Check In", "Check Out", "Hours"].map((h) => (
                    <th key={h}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {RECENT_ACTIVITY.map((row, i) => (
                  <tr key={i}>
                    <td className="font-medium">{row.day}</td>
                    <td>
                      <span
                        className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded font-semibold uppercase tracking-wide ${
                          STATUS_BADGE_CLASS[row.status] ?? "dashboard-badge-later"
                        }`}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td>
                      {row.checkIn !== "—" ? (
                        <span className="inline-flex items-center gap-1">
                          <LogIn className="w-3 h-3 text-muted-foreground" />
                          {row.checkIn}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      {row.checkOut !== "—" ? (
                        <span className="inline-flex items-center gap-1">
                          <LogOut className="w-3 h-3 text-muted-foreground" />
                          {row.checkOut}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="font-medium">{row.hours}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </PortalPage>
  );
}
