import { Search, Filter, RefreshCcw, X } from "lucide-react";
import { Input } from "../../ui/input";
import { Button } from "../../ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../ui/select";
import { cn } from "../../ui/utils";
import { useAttendanceFilterOptions } from "../../../modules/attendance/hooks";

interface AttendanceFilterPanelProps {
  filters: any;
  setFilters: (filters: any) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export function AttendanceFilterPanel({ filters, setFilters, onRefresh, isRefreshing }: AttendanceFilterPanelProps) {
  const { data: filterOpts } = useAttendanceFilterOptions();
  const departments = filterOpts?.departments ?? [];
  const designations = filterOpts?.designations ?? [];
  const teams = filterOpts?.teams ?? [];

  const updateFilter = (key: string, value: any) => {
    setFilters((prev: any) => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      date: filters.date, // Keep the selected date
      shift: "all",
      department: "all",
      designation: "all",
      team: "all",
      workMode: "all",
      search: "",
    });
  };

  return (
    <div className="w-full h-full flex flex-col">
      <div className={cn(
        "bg-white/75 dark:bg-white/5 backdrop-blur-xl border border-black/[0.08] dark:border-white/10 rounded-[10px] shadow-sm flex flex-col sticky top-20 max-h-[calc(100vh-100px)] transition-all duration-300"
      )}>
        {/* Header */}
        <div className="p-3 border-b border-black/[0.05] dark:border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-primary" />
            <span className="text-xs font-bold text-foreground">Filters</span>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            className={cn("h-7 w-7 hover:bg-black/5 dark:hover:bg-white/5 rounded-full", isRefreshing && "animate-spin")}
            onClick={onRefresh}
          >
            <RefreshCcw className="w-3 h-3 text-muted-foreground" />
          </Button>
        </div>

        {/* Scrollable Filter Area */}
        <div className="p-4 space-y-3 overflow-y-auto no-scrollbar">
          {/* Search Employee */}
          <div className="space-y-1.5">
            <label className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest px-1">Search Employee</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground dark:text-muted-foreground" />
              <Input 
                className="pl-8 h-8 bg-black/5 dark:bg-white/5 border-transparent focus:bg-transparent focus:border-primary/30 rounded-lg text-xs" 
                placeholder="Name or ID..." 
                value={filters.search}
                onChange={(e) => updateFilter("search", e.target.value)}
              />
            </div>
          </div>

          {/* Shift */}
          <div className="space-y-1.5">
            <label className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest px-1">Shift</label>
            <Select value={filters.shift} onValueChange={(v) => updateFilter("shift", v)}>
              <SelectTrigger className="h-8 bg-black/5 dark:bg-white/5 border-transparent focus:ring-1 focus:ring-primary/30 rounded-lg text-xs">
                <SelectValue placeholder="All Shifts" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all" className="text-xs">All Shifts</SelectItem>
                <SelectItem value="all" className="text-xs">All Shifts</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Department */}
          <div className="space-y-1.5">
            <label className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest px-1">Department</label>
            <Select value={filters.department} onValueChange={(v) => updateFilter("department", v)}>
              <SelectTrigger className="h-8 bg-black/5 dark:bg-white/5 border-transparent focus:ring-1 focus:ring-primary/30 rounded-lg text-xs">
                <SelectValue placeholder="All Departments" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all" className="text-xs">All Departments</SelectItem>
                {departments.map(d => <SelectItem key={d.id} value={d.id} className="text-xs">{d.name}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Work Mode */}
          <div className="space-y-1.5">
            <label className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest px-1">Work Mode</label>
            <Select value={filters.workMode} onValueChange={(v) => updateFilter("workMode", v)}>
              <SelectTrigger className="h-8 bg-black/5 dark:bg-white/5 border-transparent focus:ring-1 focus:ring-primary/30 rounded-lg text-xs">
                <SelectValue placeholder="All Modes" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all" className="text-xs">All Modes</SelectItem>
                <SelectItem value="WFO" className="text-xs">WFO</SelectItem>
                <SelectItem value="WFH" className="text-xs">WFH</SelectItem>
                <SelectItem value="Hybrid" className="text-xs">Hybrid</SelectItem>
                <SelectItem value="Field Work" className="text-xs">Field Work</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Designation */}
          <div className="space-y-1.5">
            <label className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest px-1">Designation</label>
            <Select value={filters.designation} onValueChange={(v) => updateFilter("designation", v)}>
              <SelectTrigger className="h-8 bg-black/5 dark:bg-white/5 border-transparent focus:ring-1 focus:ring-primary/30 rounded-lg text-xs">
                <SelectValue placeholder="All Designations" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all" className="text-xs">All Designations</SelectItem>
                {designations.map(d => <SelectItem key={d.id} value={d.id} className="text-xs">{d.name}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Team */}
          <div className="space-y-1.5">
            <label className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest px-1">Team</label>
            <Select value={filters.team} onValueChange={(v) => updateFilter("team", v)}>
              <SelectTrigger className="h-8 bg-black/5 dark:bg-white/5 border-transparent focus:ring-1 focus:ring-primary/30 rounded-lg text-xs">
                <SelectValue placeholder="All Teams" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all" className="text-xs">All Teams</SelectItem>
                {teams.map(t => <SelectItem key={t.id} value={t.id} className="text-xs">{t.name}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-black/[0.05] dark:border-white/5 mt-auto">
          <Button 
            variant="ghost" 
            className="w-full text-[10px] h-8 font-bold text-muted-foreground hover:text-primary hover:bg-primary/5 transition-all rounded-lg"
            onClick={clearFilters}
          >
            Clear All Filters
          </Button>
        </div>
      </div>
    </div>
  );
}
