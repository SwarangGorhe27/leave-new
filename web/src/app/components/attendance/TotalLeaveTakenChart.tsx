import { BarChart, Bar, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Calendar, TrendingUp, TrendingDown, HelpCircle } from "lucide-react";
import { Tooltip as UITooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";
import { cn } from "../ui/utils";

interface TotalLeaveTakenChartProps {
  data: { month: string; leaveDays: number; approvedCount: number; employees: number }[];
}

export function TotalLeaveTakenChart({ data }: TotalLeaveTakenChartProps) {
  // Calculate stats
  const totalLeaveDays = data.reduce((acc, curr) => acc + curr.leaveDays, 0);
  const highestMonth = data.length > 0 ? data.reduce((prev, current) => (prev.leaveDays > current.leaveDays) ? prev : current) : { month: "N/A" };
  const avgLeavePerMonth = data.length > 0 ? totalLeaveDays / data.length : 0;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border p-2 rounded-lg shadow-xl space-y-1">
          <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">{label}</p>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            <p className="text-xs font-bold text-foreground">{payload[0].value} Leave Days</p>
          </div>
          <div className="space-y-0.5 border-t border-border mt-1 pt-1">
            <p className="text-[9px] font-bold text-muted-foreground">Approved: {payload[0].payload.approvedCount}</p>
            <p className="text-[9px] font-bold text-muted-foreground">Employees on Leave: {payload[0].payload.employees}</p>
          </div>
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
              Total Leave Taken This Year
              <TooltipProvider>
                <UITooltip>
                  <TooltipTrigger asChild>
                    <HelpCircle className="w-3 h-3 text-muted-foreground cursor-help" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="text-[10px]">Summary of all approved leave days across the organization per month.</p>
                  </TooltipContent>
                </UITooltip>
              </TooltipProvider>
            </CardTitle>
            <p className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">Yearly Leave distribution</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-4 p-4">
        {/* Summary Chips */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {[
            { label: "Total Leave Days", value: `${totalLeaveDays}d`, icon: Calendar, color: "text-blue-500", bg: "bg-blue-500/10" },
            { label: "Highest Month", value: highestMonth.month, icon: TrendingUp, color: "text-red-500", bg: "bg-red-500/10" },
            { label: "Avg Per Month", value: `${avgLeavePerMonth.toFixed(1)}d`, icon: TrendingDown, color: "text-amber-500", bg: "bg-amber-500/10" },
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

        <div className="h-[150px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" opacity={0.5} />
              <XAxis 
                dataKey="month" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 9, fill: 'var(--muted-foreground)', fontWeight: 700 }}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 9, fill: 'var(--muted-foreground)', fontWeight: 700 }}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--secondary)', opacity: 0.4 }} />
              <Bar 
                dataKey="leaveDays" 
                radius={[4, 4, 0, 0]}
                barSize={20}
                fill="#3b82f6"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.leaveDays > avgLeavePerMonth ? "#3b82f6" : "#93c5fd"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
