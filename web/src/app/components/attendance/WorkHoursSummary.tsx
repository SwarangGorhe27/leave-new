import { BarChart, Bar, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, ReferenceLine } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Clock, TrendingUp, TrendingDown, Target, HelpCircle } from "lucide-react";
import { Tooltip as UITooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";
import { cn } from "../ui/utils";

interface WorkHoursSummaryProps {
  data: { day: string; hours: number; employees: number }[];
}

export function WorkHoursSummary({ data }: WorkHoursSummaryProps) {
  // Calculate stats
  const avgHours = data.length > 0 ? data.reduce((acc, curr) => acc + curr.hours, 0) / data.length : 0;
  const highestDay = data.length > 0 ? Math.max(...data.map(d => d.hours)) : 0;
  const lowestDay = data.length > 0 ? Math.min(...data.filter(d => d.hours > 0).map(d => d.hours)) : 0;
  const targetAchievement = (avgHours / 8) * 100;

  const getBarColor = (hours: number) => {
    if (hours === 0) return "var(--muted)";
    if (hours < 8) return "#f59e0b"; // Amber
    if (hours === 8) return "#10b981"; // Emerald
    return "#0ea5e9"; // Peacock Blue
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border p-2 rounded-lg shadow-xl space-y-1">
          <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">{label}</p>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: getBarColor(payload[0].value) }} />
            <p className="text-xs font-bold text-foreground">{payload[0].value} Hours Worked</p>
          </div>
          <p className="text-[9px] font-bold text-muted-foreground">{payload[0].payload.employees} Employees Counted</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="shadow-sm border-border h-full">
      <CardHeader className="pb-2 border-b border-border/50 p-4">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <CardTitle className="text-sm font-black text-foreground flex items-center gap-1.5">
              Monthly Work Hours Trend
              <TooltipProvider>
                <UITooltip>
                  <TooltipTrigger asChild>
                    <HelpCircle className="w-3 h-3 text-muted-foreground cursor-help" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="text-[10px]">Average number of hours worked per employee each day.</p>
                  </TooltipContent>
                </UITooltip>
              </TooltipProvider>
            </CardTitle>
            <p className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">Target: 8 Hours Per Day</p>
          </div>
          <div className="flex items-center gap-3 text-[9px] font-black uppercase tracking-tighter">
            <div className="flex items-center gap-1">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-500" /> <span className="text-slate-500">Below</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> <span className="text-slate-500">Target</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-1.5 h-1.5 rounded-full bg-sky-500" /> <span className="text-slate-500">Above</span>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-4 p-4">
        {/* Summary Chips */}
        <div className="grid grid-cols-4 gap-3 mb-4">
          {[
            { label: "Avg Work Hours", value: `${avgHours.toFixed(1)}h`, icon: Clock, color: "text-blue-500", bg: "bg-blue-500/10" },
            { label: "Highest Day", value: `${highestDay.toFixed(1)}h`, icon: TrendingUp, color: "text-emerald-500", bg: "bg-emerald-500/10" },
            { label: "Lowest Day", value: `${lowestDay.toFixed(1)}h`, icon: TrendingDown, color: "text-amber-500", bg: "bg-amber-500/10" },
            { label: "Achievement", value: `${targetAchievement.toFixed(0)}%`, icon: Target, color: "text-purple-500", bg: "bg-purple-500/10" },
          ].map((chip) => (
            <div key={chip.label} className="flex flex-col p-2 rounded-xl bg-secondary/20 border border-border/50">
              <div className="flex items-center gap-1.5 mb-0.5">
                <chip.icon className={cn("w-3 h-3", chip.color)} />
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">{chip.label}</span>
              </div>
              <span className="text-base font-black text-foreground">{chip.value}</span>
            </div>
          ))}
        </div>

        <div className="h-[200px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" opacity={0.5} />
              <XAxis 
                dataKey="day" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 9, fill: 'var(--muted-foreground)', fontWeight: 700 }}
                interval={Math.floor(data.length / 10)}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 9, fill: 'var(--muted-foreground)', fontWeight: 700 }}
                domain={[0, 12]}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--secondary)', opacity: 0.4 }} />
              <ReferenceLine 
                y={8} 
                stroke="#10b981" 
                strokeDasharray="4 4" 
                strokeWidth={2}
                label={{ 
                  position: 'right', 
                  value: 'TARGET', 
                  fill: '#10b981', 
                  fontSize: 9, 
                  fontWeight: 900 
                }} 
              />
              <Bar 
                dataKey="hours" 
                radius={[4, 4, 0, 0]}
                barSize={data.length > 20 ? 10 : 20}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.hours)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
