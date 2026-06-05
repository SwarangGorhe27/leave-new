import { Search, Calendar as CalendarIcon, ChevronDown, RotateCcw, SlidersHorizontal } from "lucide-react";
import { Input } from "../../ui/input";
import { Button } from "../../ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../ui/select";
import { useAttendanceFilterOptions } from "../../../modules/attendance/hooks";
import { format } from "date-fns";
import { Popover, PopoverContent, PopoverTrigger } from "../../ui/popover";
import { Calendar } from "../../ui/calendar";

interface SwipeLogsFilterBarProps {
  filters: any;
  setFilters: (filters: any) => void;
}

export function SwipeLogsFilterBar({ filters, setFilters }: SwipeLogsFilterBarProps) {
  const { data: filterOpts } = useAttendanceFilterOptions();
  const departments = filterOpts?.departments ?? [];

  const updateFilter = (key: string, value: any) => {
    setFilters((prev: any) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="sticky top-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800 px-4 py-2 shadow-sm transition-all duration-300">
      <div className="flex flex-wrap items-center gap-3">
        {/* Search Input */}
        <div className="relative w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
          <Input 
            className="pl-8 h-8 bg-slate-100/50 dark:bg-slate-800/50 border-transparent focus:bg-white dark:focus:bg-slate-800 rounded-lg text-[11px] font-medium shadow-inner transition-all" 
            placeholder="Search Employee..." 
            value={filters.search}
            onChange={(e) => updateFilter("search", e.target.value)}
          />
        </div>

        <div className="h-6 w-px bg-slate-200 dark:bg-slate-800 hidden md:block" />

        {/* Filters Group */}
        <div className="flex-1 flex flex-wrap items-center gap-2">
          {/* Date Picker */}
          <Popover>
            <PopoverTrigger asChild>
              <Button 
                variant="outline" 
                className="h-8 bg-slate-100/50 dark:bg-slate-800/50 border-transparent rounded-lg text-[11px] font-bold gap-1.5 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 px-3"
              >
                <CalendarIcon className="w-3 h-3 text-emerald-500" />
                <span>{filters.dateEnabled ? format(filters.date, "dd MMM yyyy") : "All Dates"}</span>
                <ChevronDown className="w-2.5 h-2.5 opacity-50" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0 z-60 bg-white dark:bg-slate-900" align="start">
              <Calendar
                mode="single"
                selected={filters.date}
                onSelect={(d) => d && setFilters((prev: any) => ({ ...prev, date: d, dateEnabled: true }))}
                initialFocus
              />
            </PopoverContent>
          </Popover>
          <Button
            variant={filters.dateEnabled ? 'outline' : 'secondary'}
            className="h-8 rounded-lg text-[11px] font-bold text-slate-600 dark:text-slate-300 bg-slate-100/50 dark:bg-slate-800/50 border-transparent px-3"
            onClick={() => updateFilter('dateEnabled', !filters.dateEnabled)}
          >
            {filters.dateEnabled ? 'Date Filter On' : 'All Dates'}
          </Button>

          {/* Department */}
          <Select value={filters.department} onValueChange={(v) => updateFilter("department", v)}>
            <SelectTrigger className="h-8 w-[140px] bg-slate-100/50 dark:bg-slate-800/50 border-transparent rounded-lg text-[11px] font-bold text-slate-600 dark:text-slate-400">
              <SelectValue placeholder="Department" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-[11px]">All Departments</SelectItem>
              {departments.map((d) => (
                <SelectItem key={d.id} value={d.id} className="text-[11px]">{d.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Device Type */}
          <Select value={filters.device} onValueChange={(v) => updateFilter("device", v)}>
            <SelectTrigger className="h-8 w-[130px] bg-slate-100/50 dark:bg-slate-800/50 border-transparent rounded-lg text-[11px] font-bold text-slate-600 dark:text-slate-400">
              <SelectValue placeholder="Device Source" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-[11px]">All Sources</SelectItem>
              <SelectItem value="Biometric Device" className="text-[11px]">Biometric</SelectItem>
              <SelectItem value="Mobile App" className="text-[11px]">Mobile App</SelectItem>
              <SelectItem value="Web Login" className="text-[11px]">Web Portal</SelectItem>
              <SelectItem value="QR Attendance" className="text-[11px]">QR Scan</SelectItem>
            </SelectContent>
          </Select>

          {/* Swipe Type */}
          <Select value={filters.type} onValueChange={(v) => updateFilter("type", v)}>
            <SelectTrigger className="h-8 w-[90px] bg-slate-100/50 dark:bg-slate-800/50 border-transparent rounded-lg text-[11px] font-bold text-slate-600 dark:text-slate-400">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-[11px]">IN/OUT</SelectItem>
              <SelectItem value="IN" className="text-[11px]">Punch IN</SelectItem>
              <SelectItem value="OUT" className="text-[11px]">Punch OUT</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg bg-slate-100/50 dark:bg-slate-800/50 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 text-slate-500 hover:text-emerald-600 transition-all">
            <SlidersHorizontal className="w-3.5 h-3.5" />
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" className="h-8 px-3 text-[10px] font-bold text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-all rounded-lg" onClick={() => setFilters({
            search: "",
            department: "all",
            designation: "all",
            team: "all",
            location: "all",
            device: "all",
            type: "all",
            date: new Date(),
            dateEnabled: true,
          })}>
            <RotateCcw className="w-3 h-3 mr-1.5" />
            RESET
          </Button>
        </div>
      </div>
    </div>
  );
}
