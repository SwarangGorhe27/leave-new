import { 
  Activity, 
  LogIn, 
  LogOut, 
  AlertCircle, 
  Clock, 
  Smartphone, 
  Building2 
} from "lucide-react";
import { cn } from "../../ui/utils";

interface SwipeLogsAnalyticsProps {
  data: {
    totalSwipesToday: number;
    totalInEntries: number;
    totalOutEntries: number;
    missingPunchCount: number;
    lateEntryCount: number;
    wfhAttendanceCount: number;
    officeAttendanceCount: number;
  };
}

function MetricCard({ icon: Icon, label, value, subtext, color, trend }: any) {
  const colorMap = {
    emerald: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20",
    blue: "bg-blue-500/10 text-blue-600 border-blue-500/20",
    amber: "bg-amber-500/10 text-amber-600 border-amber-500/20",
    red: "bg-red-500/10 text-red-600 border-red-500/20",
    purple: "bg-purple-500/10 text-purple-600 border-purple-500/20",
    indigo: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20",
    slate: "bg-slate-500/10 text-slate-600 border-slate-500/20",
  };

  return (
    <div className="flex-1 min-w-[180px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-sm hover:shadow-md transition-all group relative overflow-hidden">
      <div className="flex items-start justify-between mb-3 relative z-10">
        <div className={cn("p-2 rounded-xl border transition-transform group-hover:scale-110 duration-300", colorMap[color as keyof typeof colorMap])}>
          <Icon className="w-4 h-4" />
        </div>
        {trend && (
          <span className={cn(
            "text-[9px] font-bold px-1.5 py-0.5 rounded-full border",
            trend > 0 ? "bg-emerald-50 text-emerald-600 border-emerald-100" : "bg-red-50 text-red-600 border-red-100"
          )}>
            {trend > 0 ? "+" : ""}{trend}%
          </span>
        )}
      </div>
      <div className="space-y-1 relative z-10">
        <h4 className="text-xl font-bold text-slate-900 dark:text-slate-100">{value}</h4>
        <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest leading-tight">{label}</p>
        <p className="text-[9px] font-medium text-slate-500 mt-1">{subtext}</p>
      </div>
      
      {/* Decorative Background Icon */}
      <Icon className="absolute -bottom-2 -right-2 w-16 h-16 text-slate-50 dark:text-slate-800/50 -rotate-12 transition-transform group-hover:scale-110 group-hover:rotate-0 duration-500" />
    </div>
  );
}

export function SwipeLogsAnalytics({ data }: SwipeLogsAnalyticsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4">
      <MetricCard 
        icon={Activity} 
        label="Total Swipes" 
        value={data.totalSwipesToday} 
        subtext="Logs captured today" 
        color="blue"
        trend={12}
      />
      <MetricCard 
        icon={LogIn} 
        label="Check-Ins" 
        value={data.totalInEntries} 
        subtext="Arrival logs" 
        color="emerald"
        trend={5}
      />
      <MetricCard 
        icon={LogOut} 
        label="Check-Outs" 
        value={data.totalOutEntries} 
        subtext="Departure logs" 
        color="purple"
        trend={-2}
      />
      <MetricCard 
        icon={AlertCircle} 
        label="Missing Punch" 
        value={data.missingPunchCount} 
        subtext="Requires action" 
        color="amber"
      />
      <MetricCard 
        icon={Clock} 
        label="Late Entries" 
        value={data.lateEntryCount} 
        subtext="Post shift start" 
        color="red"
      />
      <MetricCard 
        icon={Smartphone} 
        label="Mobile/WFH" 
        value={data.wfhAttendanceCount} 
        subtext="App attendance" 
        color="indigo"
      />
      <MetricCard 
        icon={Building2} 
        label="Office" 
        value={data.officeAttendanceCount} 
        subtext="In-premise logs" 
        color="emerald"
      />
    </div>
  );
}
