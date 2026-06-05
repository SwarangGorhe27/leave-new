import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, AreaChart, Area, Cell, PieChart, Pie
} from "recharts";
import { DailyAttendance } from "../../../modules/attendance/types";
import { useMemo } from "react";
import { format, parseISO } from "date-fns";

interface AttendanceChartsProps {
  records: DailyAttendance[];
}

export function AttendanceCharts({ records }: AttendanceChartsProps) {
  const trendData = useMemo(() => {
    return records
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(-15) // Last 15 days
      .map(r => ({
        date: format(parseISO(r.date), "dd MMM"),
        hours: r.workHours || 0
      }));
  }, [records]);

  const distribution = useMemo(() => {
    const counts: Record<string, number> = {};
    records.forEach(r => {
      counts[r.status] = (counts[r.status] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [records]);

  // Premium HRMS status colors matching the theme specification
  const COLORS = {
    Present: "#10B981",
    Absent: "#EF4444",
    Leave: "#F59E0B",
    "Half Day": "#F97316",
    Holiday: "#3B82F6",
    "Week Off": "#9CA3AF",
    "Work From Home": "#8B5CF6"
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 gap-6">
      {/* Work Hours Trend Area Chart */}
      <div className="p-6 rounded-[24px] bg-white/72 dark:bg-[#0F172A]/72 border border-[rgba(15,23,42,0.06)] dark:border-[rgba(255,255,255,0.06)] backdrop-blur-md shadow-sm flex flex-col justify-between transition-all duration-300 hover:shadow-md hover:scale-[1.01]">
        <div>
          <h3 className="text-sm font-bold text-[#0F172A] dark:text-[#F8FAFC] tracking-tight mb-4">Work Hours Trend</h3>
        </div>
        <div className="h-52 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="colorHours" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.06} />
              <XAxis dataKey="date" fontSize={10} axisLine={false} tickLine={false} tick={{ fill: '#64748B', fontWeight: 500 }} />
              <YAxis fontSize={10} axisLine={false} tickLine={false} tick={{ fill: '#64748B', fontWeight: 500 }} />
              <Tooltip 
                contentStyle={{ 
                  borderRadius: '16px', 
                  border: '1px solid rgba(15,23,42,0.06)', 
                  backgroundColor: 'rgba(255,255,255,0.92)',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05)',
                  fontSize: '11px',
                  fontWeight: 600
                }}
              />
              <Area 
                type="monotone" 
                dataKey="hours" 
                stroke="#6366F1" 
                strokeWidth={3} 
                fillOpacity={1} 
                fill="url(#colorHours)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Status Distribution Pie Chart */}
      <div className="p-6 rounded-[24px] bg-white/72 dark:bg-[#0F172A]/72 border border-[rgba(15,23,42,0.06)] dark:border-[rgba(255,255,255,0.06)] backdrop-blur-md shadow-sm flex flex-col items-center justify-between transition-all duration-300 hover:shadow-md hover:scale-[1.01]">
        <h3 className="text-sm font-bold text-[#0F172A] dark:text-[#F8FAFC] tracking-tight w-full text-left mb-2">Status Mix</h3>
        <div className="h-44 w-full relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie 
                data={distribution} 
                innerRadius={48} 
                outerRadius={60} 
                paddingAngle={6} 
                dataKey="value"
              >
                {distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || "#9CA3AF"} stroke="none" />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-2xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">{records.length}</span>
            <span className="text-[9px] font-bold text-[#334155] dark:text-[#CBD5E1] uppercase tracking-wider">Logs</span>
          </div>
        </div>
        <div className="flex flex-wrap justify-center gap-2 mt-4 w-full">
          {distribution.map(d => (
            <div key={d.name} className="flex items-center gap-1.5 bg-slate-500/5 dark:bg-white/5 px-2.5 py-1 rounded-full">
              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: COLORS[d.name as keyof typeof COLORS] || "#9CA3AF" }} />
              <span className="text-[9px] font-bold text-[#334155] dark:text-[#CBD5E1] uppercase tracking-wider">{d.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
