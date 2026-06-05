import React from "react";
import { BarChart3, TrendingUp, Users, PieChart } from "lucide-react";

export function AnalyticsHubPage() {
  return (
    <div className="p-8 h-full overflow-auto space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-black text-foreground tracking-tight">Analytics Hub</h1>
        <p className="text-sm font-medium text-muted-foreground uppercase tracking-widest">Real-time organization insights & data visualization</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: "Total Headcount", val: "1,284", change: "+12%", icon: Users, color: "text-blue-500", bg: "bg-blue-500/10" },
          { label: "Turnover Rate", val: "4.2%", change: "-0.5%", icon: TrendingUp, color: "text-emerald-500", bg: "bg-emerald-500/10" },
          { label: "Open Positions", val: "24", change: "+4", icon: BarChart3, color: "text-indigo-500", bg: "bg-indigo-500/10" },
          { label: "Engagement Score", val: "88%", change: "+2%", icon: PieChart, color: "text-amber-500", bg: "bg-amber-500/10" },
        ].map((s, i) => (
          <div key={i} className="flat-card p-6 border border-border bg-card flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className={`w-10 h-10 rounded-xl ${s.bg} flex items-center justify-center ${s.color}`}>
                <s.icon size={20} />
              </div>
              <span className={`text-xs font-black ${s.change.startsWith('+') ? 'text-emerald-500' : 'text-rose-500'}`}>
                {s.change}
              </span>
            </div>
            <div>
              <p className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em]">{s.label}</p>
              <p className="text-2xl font-black text-foreground mt-1">{s.val}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flat-card p-8 border border-border bg-card min-h-[400px] flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 rounded-[2rem] bg-secondary flex items-center justify-center mb-4">
            <BarChart3 size={32} className="text-muted-foreground/30" />
          </div>
          <h3 className="text-lg font-black text-foreground">Workforce Growth Trend</h3>
          <p className="text-sm text-muted-foreground mt-2 max-w-sm">Detailed visualization of employee growth and attrition over time.</p>
          <div className="mt-8 flex gap-2">
             <div className="w-8 h-32 bg-indigo-500/20 rounded-t-lg" />
             <div className="w-8 h-40 bg-indigo-500/40 rounded-t-lg" />
             <div className="w-8 h-24 bg-indigo-500/30 rounded-t-lg" />
             <div className="w-8 h-56 bg-indigo-500/60 rounded-t-lg" />
             <div className="w-8 h-48 bg-indigo-500/50 rounded-t-lg" />
          </div>
        </div>

        <div className="flat-card p-8 border border-border bg-card flex flex-col items-center justify-center text-center">
           <div className="w-16 h-16 rounded-[2rem] bg-secondary flex items-center justify-center mb-4">
            <PieChart size={32} className="text-muted-foreground/30" />
          </div>
          <h3 className="text-lg font-black text-foreground">Departmental Distribution</h3>
          <p className="text-sm text-muted-foreground mt-2">Breakdown of employees across different business units.</p>
          <div className="mt-8 relative w-32 h-32 rounded-full border-8 border-indigo-500/20 flex items-center justify-center">
            <div className="absolute inset-0 border-8 border-indigo-500 rounded-full clip-path-half" style={{ clipPath: 'polygon(0 0, 100% 0, 100% 50%, 0 50%)' }} />
            <span className="text-lg font-black">64%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
