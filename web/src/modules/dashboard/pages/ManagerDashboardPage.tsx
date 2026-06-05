import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../../../app/context/AuthContext";
import { employees } from "../../../app/components/employees/mockData";
import {
  Clock, LogIn, LogOut, CalendarDays, Wallet,
  TrendingUp, CheckCircle2, AlertCircle,
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";

/* ── Mock data ─────────────────────────────────────────────── */
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
    { title: "Project Alpha Sync", date: "May 15" },
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

const STATUS_BADGE: Record<string, string> = {
  Present: "bg-[#212529] text-[#F8F9FA]",
  Leave: "bg-[#CED4DA] text-[#212529]",
  Absent: "bg-[#ADB5BD] text-[#212529]",
};

/* ── Custom Tooltip ────────────────────────────────────────── */
const ChartTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-foreground text-primary-foreground text-xs px-3 py-2 rounded-lg shadow-lg">
      <p className="text-primary-foreground/60 mb-0.5">{label}</p>
      <p className="font-semibold">{payload[0].value}h worked</p>
    </div>
  );
};

/* ── Live Clock ─────────────────────────────────────────────── */
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

/* ── Main Component ─────────────────────────────────────────── */
export function ManagerDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<"Events" | "Holidays" | "Birthdays">("Events");
  const [checkedIn, setCheckedIn] = useState(true);
  const [checkInTime] = useState("09:12 AM");
  const [elapsed] = useState("6h 32m");

  const emp = employees.find((e) => e.id === user?.employeeId) || employees[0];
  const firstName = emp.name.split(" ")[0];
  const feed = UPCOMING[activeTab] || [];

  return (
    <div className="p-6 space-y-6">

      {/* ── Hero / Greeting ─────────────────────────────── */}
      <div className="flat-card bg-card p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight">
              Good morning, {firstName}
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })}
            </p>

            <div className="flex flex-wrap items-center gap-3 mt-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-secondary border border-border rounded-lg">
                <div className={`w-2 h-2 rounded-full ${checkedIn ? "bg-[#212529]" : "bg-[#ADB5BD]"} animate-pulse`} />
                <span className="text-sm font-medium text-foreground">
                  {checkedIn ? `Working · Checked in ${checkInTime}` : "Not checked in"}
                </span>
              </div>
              {checkedIn && (
                <div className="px-3 py-1.5 bg-secondary border border-border rounded-lg">
                  <span className="text-sm font-mono font-medium text-foreground">{elapsed} elapsed</span>
                </div>
              )}
            </div>
          </div>

          {/* Live clock + Check-in/out */}
          <div className="flex flex-col items-start md:items-end gap-3">
            <LiveClock />
            <button
              onClick={() => setCheckedIn(!checkedIn)}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors ${checkedIn
                  ? "bg-secondary text-foreground border border-border hover:bg-[#CED4DA]"
                  : "bg-foreground text-primary-foreground hover:bg-accent"
                }`}
            >
              {checkedIn
                ? <><LogOut className="w-4 h-4" /> Check Out</>
                : <><LogIn className="w-4 h-4" /> Check In</>
              }
            </button>
          </div>
        </div>

        {/* Progress bar */}
        {checkedIn && (
          <div className="mt-6">
            <div className="relative h-2 bg-secondary rounded-full overflow-hidden border border-border">
              <div className="absolute left-0 top-0 h-full bg-foreground rounded-full" style={{ width: "72.5%" }} />
            </div>
            <div className="flex justify-between mt-2 text-xs text-muted-foreground font-medium">
              <span>Scheduled: 9h</span>
              <span className="font-semibold text-foreground">{elapsed} worked</span>
              <span>Remaining: 2h 28m</span>
            </div>
          </div>
        )}
      </div>

      {/* ── KPI quick stats ─────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { icon: CheckCircle2, label: "Present This Month", value: "19 / 28", },
          { icon: CalendarDays, label: "Leave Balance", value: "12 days" },
          { icon: AlertCircle, label: "Late Arrivals", value: "2 times" },
          { icon: Wallet, label: "Last Net Salary", value: "₹58,500" },
        ].map(({ icon: Icon, label, value }) => (
          <div key={label} className="flat-card bg-card p-4 flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
              <Icon className="w-4 h-4 text-foreground" />
            </div>
            <div>
              <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">{label}</p>
              <p className="text-lg font-bold text-foreground mt-0.5">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── Charts + Feed ───────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Weekly hours chart */}
        <div className="flat-card bg-card p-5 lg:col-span-2">
          <h2 className="text-sm font-semibold text-foreground mb-1">Weekly Hours</h2>
          <p className="text-xs text-muted-foreground mb-5">Hours worked this week</p>
          <ResponsiveContainer width="100%" height={160}>
            <AreaChart data={WEEKLY_HOURS} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
              <defs>
                <linearGradient id="hoursGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--foreground)" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="var(--foreground)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} domain={[0, 10]} />
              <Tooltip content={<ChartTooltip />} cursor={{ stroke: "var(--border)" }} />
              <Area
                type="monotone" dataKey="hours"
                stroke="var(--foreground)" strokeWidth={2}
                fill="url(#hoursGrad)"
                dot={{ fill: "var(--foreground)", r: 3, strokeWidth: 0 }}
                activeDot={{ fill: "var(--foreground)", r: 5, strokeWidth: 0 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Upcoming feed */}
        <div className="flat-card bg-card p-5 flex flex-col">
          <h2 className="text-sm font-semibold text-foreground mb-4">What's Coming</h2>

          <div className="flex gap-1 p-1 bg-secondary rounded-lg mb-4">
            {(["Events", "Holidays", "Birthdays"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 px-2 py-1.5 rounded-md text-xs font-medium transition-all duration-150 ${activeTab === tab
                    ? "bg-card text-foreground shadow-sm border border-border"
                    : "text-muted-foreground hover:text-foreground"
                  }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="flex-1 space-y-2 overflow-y-auto">
            {feed.map((item, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-secondary transition-colors"
              >
                <span className="text-sm font-medium text-foreground">{item.title}</span>
                <span className="text-[11px] font-semibold text-muted-foreground bg-secondary border border-border px-2 py-0.5 rounded-md">
                  {item.date}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Recent Activity Table ────────────────────────── */}
      <div className="flat-card bg-card overflow-hidden">
        <div className="px-6 py-4 border-b border-border flex items-start justify-between gap-4">
          <div>
            <h2 className="text-sm font-semibold text-foreground">Recent Attendance</h2>
            <p className="text-xs text-muted-foreground mt-0.5">Last 5 working days</p>
          </div>
          <button
            type="button"
            onClick={() => navigate("/employee/attendance")}
            className="text-xs font-semibold text-foreground/80 hover:text-foreground transition-colors rounded-full px-3 py-1.5 bg-secondary border border-border"
          >
            View all
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-secondary border-b border-border">
                {["Day", "Status", "Check In", "Check Out", "Hours"].map((h) => (
                  <th key={h} className="text-left px-6 py-3 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {RECENT_ACTIVITY.map((row, i) => (
                <tr key={i} className="hover:bg-secondary transition-colors duration-150">
                  <td className="px-6 py-3.5 text-sm font-medium text-foreground">{row.day}</td>
                  <td className="px-6 py-3.5">
                    <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-md font-medium ${STATUS_BADGE[row.status] || ""}`}>
                      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
                      {row.status}
                    </span>
                  </td>
                  <td className="px-6 py-3.5">
                    {row.checkIn !== "—" ? (
                      <div className="flex items-center gap-1.5">
                        <LogIn className="w-3.5 h-3.5 text-muted-foreground" />
                        <span className="text-sm text-foreground">{row.checkIn}</span>
                      </div>
                    ) : <span className="text-sm text-muted-foreground">—</span>}
                  </td>
                  <td className="px-6 py-3.5">
                    {row.checkOut !== "—" ? (
                      <div className="flex items-center gap-1.5">
                        <LogOut className="w-3.5 h-3.5 text-muted-foreground" />
                        <span className="text-sm text-foreground">{row.checkOut}</span>
                      </div>
                    ) : <span className="text-sm text-muted-foreground">—</span>}
                  </td>
                  <td className="px-6 py-3.5 text-sm font-medium text-foreground">{row.hours}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
