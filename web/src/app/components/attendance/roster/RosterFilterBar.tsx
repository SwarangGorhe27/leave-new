import { Search, Calendar as CalendarIcon, ChevronLeft, ChevronRight, Filter } from "lucide-react";
import { Input } from "../../ui/input";
import { Button } from "../../ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../ui/select";
import { cn } from "../../ui/utils";
import { format, addMonths, subMonths } from "date-fns";
import { useAttendanceFilterOptions } from "../../../modules/attendance/hooks";

interface RosterFilterBarProps {
  filters: any;
  setFilters: (filters: any) => void;
  selectedDate: Date;
  setSelectedDate: (date: Date) => void;
}

export function RosterFilterBar({ filters, setFilters, selectedDate, setSelectedDate }: RosterFilterBarProps) {
  const { data: filterOpts } = useAttendanceFilterOptions();
  const departments = filterOpts?.departments ?? [];
  const designations = filterOpts?.designations ?? [];
  const teams = filterOpts?.teams ?? [];

  const updateFilter = (key: string, value: any) => {
    setFilters((prev: any) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="sticky top-0 z-30 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800 px-4 py-2 shadow-sm transition-all duration-300">
      <div className="flex flex-wrap items-center gap-3">
        {/* Date / Month Navigation */}
        <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800/50 p-1 rounded-lg border border-slate-200/50 dark:border-slate-800">
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-7 w-7 rounded-md hover:bg-white dark:hover:bg-slate-800 shadow-sm"
            onClick={() => setSelectedDate(subMonths(selectedDate, 1))}
          >
            <ChevronLeft className="w-3.5 h-3.5 text-slate-500" />
          </Button>
          <div className="px-3 py-1 flex flex-col items-center min-w-[120px]">
            <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest leading-none mb-1">Attendance Cycle</span>
            <span className="text-[11px] font-bold text-slate-900 dark:text-slate-100">{format(selectedDate, "MMMM yyyy")}</span>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-7 w-7 rounded-md hover:bg-white dark:hover:bg-slate-800 shadow-sm"
            onClick={() => setSelectedDate(addMonths(selectedDate, 1))}
          >
            <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
          </Button>
        </div>

        <div className="h-6 w-px bg-slate-200 dark:bg-slate-800 hidden md:block" />

        {/* Employee Search - Left Section */}
        <div className="relative w-[160px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
          <Input 
            className="pl-8 h-8 bg-slate-100/50 dark:bg-slate-800/50 border-transparent focus:bg-white dark:focus:bg-slate-800 rounded-lg text-[11px] font-medium" 
            placeholder="Employee ID or Name..." 
            value={filters.search}
            onChange={(e) => updateFilter("search", e.target.value)}
          />
        </div>

        {/* Filters Group - Right Section */}
        <div className="flex-1 flex items-center justify-end gap-2">
          {/* Department */}
          <Select value={filters.department} onValueChange={(v) => updateFilter("department", v)}>
            <SelectTrigger className="h-8 w-[140px] bg-slate-100/50 dark:bg-slate-800/50 border-transparent rounded-lg text-[11px] font-medium">
              <SelectValue placeholder="Department" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-[11px]">All Departments</SelectItem>
              {departments.map((d) => (
                <SelectItem key={d.id} value={d.id} className="text-[11px]">{d.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Designation */}
          <Select value={filters.designation} onValueChange={(v) => updateFilter("designation", v)}>
            <SelectTrigger className="h-8 w-[140px] bg-slate-100/50 dark:bg-slate-800/50 border-transparent rounded-lg text-[11px] font-medium">
              <SelectValue placeholder="Designation" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-[11px]">All Designations</SelectItem>
              {designations.map((d) => (
                <SelectItem key={d.id} value={d.id} className="text-[11px]">{d.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Team */}
          <Select value={filters.team} onValueChange={(v) => updateFilter("team", v)}>
            <SelectTrigger className="h-8 w-[120px] bg-slate-100/50 dark:bg-slate-800/50 border-transparent rounded-lg text-[11px] font-medium">
              <SelectValue placeholder="Team" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-[11px]">All Teams</SelectItem>
              {teams.map((t) => (
                <SelectItem key={t.id} value={t.id} className="text-[11px]">{t.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Work Mode */}
          <Select value={filters.workMode} onValueChange={(v) => updateFilter("workMode", v)}>
            <SelectTrigger className="h-8 w-[110px] bg-slate-100/50 dark:bg-slate-800/50 border-transparent rounded-lg text-[11px] font-medium">
              <SelectValue placeholder="Work Mode" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-[11px]">All Modes</SelectItem>
              <SelectItem value="WFO" className="text-[11px]">WFO</SelectItem>
              <SelectItem value="WFH" className="text-[11px]">WFH</SelectItem>
              <SelectItem value="Field" className="text-[11px]">Field</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg bg-slate-100/50 dark:bg-slate-800/50 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 text-slate-500 hover:text-emerald-600 transition-all">
            <Filter className="w-3.5 h-3.5" />
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" className="h-8 px-3 text-[10px] font-bold text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-all rounded-lg" onClick={() => setFilters({
            search: "",
            department: "all",
            designation: "all",
            team: "all",
            location: "all",
            shift: "all",
            workMode: "all",
          })}>
            RESET FILTERS
          </Button>
        </div>
      </div>
    </div>
  );
}
