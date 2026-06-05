import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { CheckCircle2, Clock, XCircle, Calendar as CalendarIcon, HelpCircle, Search, Plane, MapPinOff } from "lucide-react";
import { useAttendanceFilterOptions } from "../../modules/attendance/hooks";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { Button } from "../ui/button";
import { Calendar } from "../ui/calendar";
import { format } from "date-fns";
import { cn } from "../ui/utils";
import { Input } from "../ui/input";
import { KebabMenu } from "../ui/KebabMenu";
import { Download, Megaphone, Printer, FileSpreadsheet } from "lucide-react";
import { toast } from "sonner";
import { 
  Tooltip as UITooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from "../ui/tooltip";

interface WhosInTodayProps {
  data: {
    onTime: number;
    lateIn: number;
    notYetIn: number;
    onLeave: number;
    outOfOffice: number;
  };
  filters: {
    date: Date;
    department: string;
    designation: string;
    team: string;
    search: string;
  };
  setFilters: (filters: any) => void;
}

export function WhosInToday({ data, filters, setFilters }: WhosInTodayProps) {
  const { data: filterOpts } = useAttendanceFilterOptions();
  const departments = filterOpts?.departments ?? [];
  const teams = filterOpts?.teams ?? [];

  const chartData = [
    { name: "On Time", value: data.onTime, color: "#10b981" },
    { name: "Late In", value: data.lateIn, color: "#f59e0b" },
    { name: "Not Yet In", value: data.notYetIn, color: "#ef4444" },
    { name: "On Leave", value: data.onLeave, color: "#3b82f6" },
    { name: "Out of Office", value: data.outOfOffice, color: "#6366f1" },
  ];

  const updateFilter = (key: string, value: any) => {
    setFilters((prev: any) => ({ ...prev, [key]: value }));
  };

  const totalPresent = data.onTime + data.lateIn;

  return (
    <Card className="shadow-sm border-border h-full flex flex-col">
      <CardHeader className="pb-4 border-b border-border/50">
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6">
          <div className="space-y-1">
            <CardTitle className="text-base font-black text-foreground flex items-center gap-2 uppercase tracking-wider">
              Who's In Today
              <TooltipProvider>
                <UITooltip>
                  <TooltipTrigger asChild>
                    <HelpCircle className="w-3.5 h-3.5 text-muted-foreground cursor-help" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="text-[10px] font-bold">Real-time attendance status for the selected date.</p>
                  </TooltipContent>
                </UITooltip>
              </TooltipProvider>
            </CardTitle>
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">{format(filters.date, "EEEE, MMMM dd, yyyy")}</p>
          </div>
          
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative group flex-1 min-w-[150px]">
               <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground dark:text-muted-foreground group-focus-within:text-emerald-500 transition-colors" />
               <Input 
                placeholder="Search..." 
                value={filters.search}
                onChange={(e) => updateFilter("search", e.target.value)}
                className="h-9 pl-9 text-xs font-bold bg-secondary/20 border-transparent focus:bg-background transition-all"
               />
            </div>

            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className={cn(
                    "h-9 justify-start text-left font-bold text-[11px] w-[150px] rounded-xl bg-secondary/20 border-transparent hover:bg-secondary/40",
                    !filters.date && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-3.5 w-3.5 text-emerald-500" />
                  {filters.date ? format(filters.date, "dd MMM yyyy") : <span>Pick date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="end">
                <Calendar
                  mode="single"
                  selected={filters.date}
                  onSelect={(d) => d && updateFilter("date", d)}
                  initialFocus
                />
              </PopoverContent>
            </Popover>

            <Select value={filters.department} onValueChange={(v) => updateFilter("department", v)}>
              <SelectTrigger className="h-9 w-[120px] text-[11px] font-bold rounded-xl bg-secondary/20 border-transparent">
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
              <SelectTrigger className="h-9 w-[120px] text-[11px] font-bold rounded-xl bg-secondary/20 border-transparent">
                <SelectValue placeholder="Team" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Teams</SelectItem>
                {teams.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="flex items-center gap-2">
              <KebabMenu 
                items={[
                  { label: "Export PDF", icon: Download, onClick: () => toast.success("PDF Report Generated") },
                  { label: "Export Excel", icon: FileSpreadsheet, onClick: () => toast.success("Excel Sheet Exported") },
                  { label: "Print View", icon: Printer, onClick: () => window.print() },
                  { label: "Broadcast Alert", icon: Megaphone, separator: true, onClick: () => toast.info("Opening alert composer...") },
                ]}
              />
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-8 flex-1 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Side: Centered Donut Chart */}
          <div className="h-[300px] relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="value"
                  animationBegin={0}
                  animationDuration={1000}
                  stroke="none"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--card)', 
                    borderColor: 'var(--border)',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-4xl font-black text-foreground tracking-tighter">{totalPresent}</span>
              <span className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground font-black">Present</span>
            </div>
          </div>

          {/* Right Side: Clean Status Cards */}
          <div className="grid grid-cols-1 gap-3">
            {[
              { label: "On Time", value: data.onTime, color: "text-emerald-500", bg: "bg-emerald-500/10", icon: CheckCircle2, desc: "Early/On schedule" },
              { label: "Late In", value: data.lateIn, color: "text-amber-500", bg: "bg-amber-500/10", icon: Clock, desc: "After grace period" },
              { label: "Not Yet In", value: data.notYetIn, color: "text-red-500", bg: "bg-red-500/10", icon: XCircle, desc: "Pending/Absent" },
              { label: "On Leave", value: data.onLeave, color: "text-blue-500", bg: "bg-blue-500/10", icon: Plane, desc: "Approved time off" },
              { label: "Out of Office", value: data.outOfOffice, color: "text-indigo-500", bg: "bg-indigo-500/10", icon: MapPinOff, desc: "External work/duty" },
            ].map((status) => (
              <div key={status.label} className="flex items-center justify-between p-3.5 rounded-2xl border border-border/50 bg-secondary/5 group hover:bg-secondary/10 transition-colors">
                <div className="flex items-center gap-3.5">
                  <div className={cn("w-9 h-9 rounded-xl flex items-center justify-center transition-transform group-hover:rotate-12", status.bg)}>
                    <status.icon className={cn("w-4.5 h-4.5", status.color)} />
                  </div>
                  <div>
                    <span className="text-[10px] font-black text-foreground uppercase tracking-wider block">{status.label}</span>
                    <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">{status.desc}</span>
                  </div>
                </div>
                <div className="text-right">
                   <span className="text-xl font-black text-foreground block leading-none">{status.value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
