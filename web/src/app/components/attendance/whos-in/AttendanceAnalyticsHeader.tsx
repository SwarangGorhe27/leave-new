import { ArrowUpRight, TrendingDown, Users, Clock, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "../../ui/utils";

interface AnalyticsCardProps {
  percentage: number;
  count: number;
  label: string;
  color: "red" | "amber" | "green" | "blue";
  icon: any;
}

function AnalyticsCard({ percentage, count, label, color, icon: Icon }: AnalyticsCardProps) {
  const colorMap = {
    red: "text-red-500 bg-red-500/10 border-red-500/20",
    amber: "text-amber-500 bg-amber-500/10 border-amber-500/20",
    green: "text-green-500 bg-green-500/10 border-green-500/20",
    blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
  };

  return (
    <div className="flex-1 min-w-[200px] bg-white/50 dark:bg-black/20 border border-black/[0.05] dark:border-white/5 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all duration-300 group">
      <div className="flex items-start justify-between mb-4">
        <div className={cn("p-2.5 rounded-xl border shadow-inner", colorMap[color])}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-black/5 dark:bg-white/5 border border-black/[0.05] dark:border-white/5">
          <span className="text-[10px] font-bold text-muted-foreground">{percentage}%</span>
          <ArrowUpRight className="w-2.5 h-2.5 text-muted-foreground" />
        </div>
      </div>
      <div className="space-y-1">
        <h4 className="text-2xl font-bold text-foreground group-hover:text-primary transition-colors">{count}</h4>
        <p className="text-[11px] font-bold text-muted-foreground uppercase tracking-widest leading-relaxed">
          {label}
        </p>
      </div>
    </div>
  );
}

interface AttendanceAnalyticsHeaderProps {
  stats: {
    notYetIn: { count: number; percentage: number; label: string };
    lateArrivals: { count: number; percentage: number; label: string };
    onTime: { count: number; percentage: number; label: string };
    outOfOffice: { count: number; percentage: number; label: string };
  };
}

export function AttendanceAnalyticsHeader({ stats }: AttendanceAnalyticsHeaderProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-1 px-1">
        <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">
          Operational Metrics Overview
        </h3>
      </div>
      <div className="flex flex-wrap gap-6">
        <AnalyticsCard 
          percentage={stats.notYetIn.percentage} 
          count={stats.notYetIn.count} 
          label={stats.notYetIn.label} 
          color="red" 
          icon={AlertCircle}
        />
        <AnalyticsCard 
          percentage={stats.lateArrivals.percentage} 
          count={stats.lateArrivals.count} 
          label={stats.lateArrivals.label} 
          color="amber" 
          icon={Clock}
        />
        <AnalyticsCard 
          percentage={stats.onTime.percentage} 
          count={stats.onTime.count} 
          label={stats.onTime.label} 
          color="green" 
          icon={CheckCircle2}
        />
        <AnalyticsCard 
          percentage={stats.outOfOffice.percentage} 
          count={stats.outOfOffice.count} 
          label={stats.outOfOffice.label} 
          color="blue" 
          icon={Users}
        />
      </div>
    </div>
  );
}
