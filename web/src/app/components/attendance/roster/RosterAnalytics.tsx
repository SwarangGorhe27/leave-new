import { Users, Calendar, ShieldCheck, Moon, RefreshCcw, LayoutPanelLeft } from "lucide-react";
import { cn } from "../../ui/utils";

interface RosterAnalyticsProps {
  data: {
    totalEmployees: number;
    totalWorkingDays: number;
    totalWeekOffs: number;
    nightShiftEmployees: number;
    rotationalShiftEmployees: number;
    flexibleShiftEmployees: number;
  };
}

function AnalyticsCard({ icon: Icon, label, value, subtext, color }: any) {
  const colorMap = {
    blue: "bg-blue-500/10 text-blue-600 border-blue-500/20",
    emerald: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20",
    indigo: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20",
    amber: "bg-amber-500/10 text-amber-600 border-amber-500/20",
    purple: "bg-purple-500/10 text-purple-600 border-purple-500/20",
    slate: "bg-slate-500/10 text-slate-600 border-slate-500/20",
  };

  return (
    <div className="flex-1 min-w-[200px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-2xl shadow-sm hover:shadow-md transition-all group">
      <div className="flex items-start justify-between mb-3">
        <div className={cn("p-2 rounded-xl border", colorMap[color as keyof typeof colorMap])}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="space-y-1">
        <h4 className="text-xl font-bold text-slate-900 dark:text-slate-100">{value}</h4>
        <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">{label}</p>
        <div className="flex items-center gap-2 mt-2">
          <div className="flex-1 h-1 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div className={cn("h-full rounded-full transition-all duration-1000", color.replace('bg-', ''))} style={{ width: '65%', backgroundColor: 'currentColor' }} />
          </div>
          <span className="text-[10px] font-bold text-slate-500">{subtext}</span>
        </div>
      </div>
    </div>
  );
}

export function RosterAnalytics({ data }: RosterAnalyticsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      <AnalyticsCard 
        icon={Users} 
        label="Total Employees" 
        value={data.totalEmployees} 
        subtext="Headcount" 
        color="blue" 
      />
      <AnalyticsCard 
        icon={Calendar} 
        label="Avg working Days" 
        value={Math.round(data.totalWorkingDays / (data.totalEmployees || 1))} 
        subtext="Per Month" 
        color="emerald" 
      />
      <AnalyticsCard 
        icon={ShieldCheck} 
        label="Total Week Offs" 
        value={data.totalWeekOffs} 
        subtext="Cycle Total" 
        color="slate" 
      />
      <AnalyticsCard 
        icon={Moon} 
        label="Night Shift" 
        value={data.nightShiftEmployees} 
        subtext="Assigned" 
        color="indigo" 
      />
      <AnalyticsCard 
        icon={RefreshCcw} 
        label="Rotational" 
        value={data.rotationalShiftEmployees} 
        subtext="Active" 
        color="amber" 
      />
      <AnalyticsCard 
        icon={LayoutPanelLeft} 
        label="Flexible" 
        value={data.flexibleShiftEmployees} 
        subtext="Support" 
        color="purple" 
      />
    </div>
  );
}
