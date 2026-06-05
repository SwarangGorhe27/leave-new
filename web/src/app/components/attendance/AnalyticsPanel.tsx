import { Clock, UserX, Calendar, AlertCircle, Users, Percent, HelpCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Input } from "../ui/input";
import { useAttendanceFilterOptions } from "../../modules/attendance/hooks";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";

interface AnalyticsPanelProps {
  metrics: {
    avgWorkHours: number;
    totalAbsent: number;
    holidays: number;
    lateLogins: number;
    avgAttendance: number;
    totalEmployees: number;
  };
  filters: any;
  setFilters: (filters: any) => void;
}

export function AnalyticsPanel({ metrics, filters, setFilters }: AnalyticsPanelProps) {
  const { data: filterOpts } = useAttendanceFilterOptions();
  const departments = filterOpts?.departments ?? [];
  const teams = filterOpts?.teams ?? [];

  const updateFilter = (key: string, value: string) => {
    setFilters((prev: any) => ({ ...prev, [key]: value }));
  };

  const summaryItems = [
    { label: "Avg Work Hours", value: `${Number(metrics.avgWorkHours).toFixed(1)}h`, icon: Clock, color: "text-blue-500", bg: "bg-blue-500/10", tooltip: "Average number of hours worked per employee." },
    { label: "Total Absent", value: metrics.totalAbsent, icon: UserX, color: "text-red-500", bg: "bg-red-500/10", tooltip: "Total man-days lost due to absence." },
    { label: "Total Holidays", value: metrics.holidays, icon: Calendar, color: "text-purple-500", bg: "bg-purple-500/10", tooltip: "Public holidays in the selected month." },
    { label: "Total Late", value: metrics.lateLogins, icon: AlertCircle, color: "text-amber-500", bg: "bg-amber-500/10", tooltip: "Employees who arrived after their scheduled time." },
    { label: "Attendance %", value: `${Number(metrics.avgAttendance).toFixed(1)}%`, icon: Percent, color: "text-emerald-500", bg: "bg-emerald-500/10", tooltip: "Overall monthly attendance percentage." },
    { label: "Employees", value: metrics.totalEmployees, icon: Users, color: "text-slate-500", bg: "bg-slate-500/10", tooltip: "Total employees considered in this report." },
  ];

  return (
    <Card className="shadow-sm border-border h-full flex flex-col">
      <CardHeader className="pb-3 border-b border-border/50 p-4">
        <CardTitle className="text-sm font-black text-foreground uppercase tracking-wider">
          Monthly Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 p-4 space-y-4 flex-1">
        {/* Internal Filters */}
        <div className="space-y-2">
          <Input 
            placeholder="Search employee..." 
            value={filters.search}
            onChange={(e) => updateFilter("search", e.target.value)}
            className="h-8 text-[11px] font-bold bg-secondary/20 border-transparent focus:bg-background transition-all"
          />
          <div className="grid grid-cols-2 gap-2">
            <Select value={filters.department} onValueChange={(v) => updateFilter("department", v)}>
              <SelectTrigger className="h-8 text-[10px] font-bold bg-secondary/20 border-transparent">
                <SelectValue placeholder="Dept" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Dept</SelectItem>
                {departments.map((d) => (
                  <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filters.team} onValueChange={(v) => updateFilter("team", v)}>
              <SelectTrigger className="h-8 text-[10px] font-bold bg-secondary/20 border-transparent">
                <SelectValue placeholder="Team" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Teams</SelectItem>
                {teams.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Metrics List */}
        <div className="space-y-2">
          <TooltipProvider>
            {summaryItems.map((item) => (
              <div key={item.label} className="flex items-center justify-between group">
                <div className="flex items-center gap-2">
                  <div className={`w-7 h-7 rounded-lg ${item.bg} flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110`}>
                    <item.icon className={`w-3.5 h-3.5 ${item.color}`} />
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">{item.label}</span>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <HelpCircle className="w-2.5 h-2.5 text-muted-foreground/50 cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent side="right">
                        <p className="text-[10px] font-bold">{item.tooltip}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                </div>
                <span className="text-xs font-black text-foreground">{item.value}</span>
              </div>
            ))}
          </TooltipProvider>
        </div>

        {/* Status indicator */}
        <div className="mt-auto pt-4 border-t border-border/50">
          <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/10">
             <p className="text-[9px] font-black text-emerald-600 uppercase tracking-[0.2em] mb-0.5">Health Check</p>
             <p className="text-[11px] font-bold text-emerald-700 leading-relaxed">
               Attendance is trending <span className="underline decoration-2 underline-offset-2">upwards</span> by 4% compared to last month.
             </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
