import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Input } from "../ui/input";
import { Search } from "lucide-react";
import { useAttendanceFilterOptions } from "../../modules/attendance/hooks";

interface AttendanceFilterBarProps {
  filters: {
    month: string;
    year: string;
    department: string;
    designation: string;
    team: string;
    search: string;
  };
  setFilters: (filters: any) => void;
}

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const YEARS = ["2023", "2024", "2025", "2026"];

export function AttendanceFilterBar({ filters, setFilters }: AttendanceFilterBarProps) {
  const { data: filterOpts } = useAttendanceFilterOptions();
  const departments = filterOpts?.departments ?? [];
  const designations = filterOpts?.designations ?? [];
  const teams = filterOpts?.teams ?? [];

  const updateFilter = (key: string, value: string) => {
    setFilters((prev: any) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="flex flex-wrap gap-3 items-end justify-end">
      {/* Month Selector */}
      <div className="space-y-1 flex-1 min-w-[120px]">
        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider px-1">Month</label>
        <Select value={filters.month} onValueChange={(v) => updateFilter("month", v)}>
          <SelectTrigger className="h-8 text-xs">
            <SelectValue placeholder="Select Month" />
          </SelectTrigger>
          <SelectContent>
            {MONTHS.map((m, i) => (
              <SelectItem key={m} value={String(i + 1)} className="text-xs">{m}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Year Selector */}
      <div className="space-y-1 flex-1 min-w-[90px]">
        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider px-1">Year</label>
        <Select value={filters.year} onValueChange={(v) => updateFilter("year", v)}>
          <SelectTrigger className="h-8 text-xs">
            <SelectValue placeholder="Select Year" />
          </SelectTrigger>
          <SelectContent>
            {YEARS.map((y) => (
              <SelectItem key={y} value={y} className="text-xs">{y}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Department Dropdown */}
      <div className="space-y-1 flex-1 min-w-[140px]">
        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider px-1">Department</label>
        <Select value={filters.department} onValueChange={(v) => updateFilter("department", v)}>
          <SelectTrigger className="h-8 text-xs">
            <SelectValue placeholder="All Departments" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all" className="text-xs">All Departments</SelectItem>
            {departments.map((d) => (
              <SelectItem key={d.id} value={d.id} className="text-xs">{d.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Team Dropdown */}
      <div className="space-y-1 flex-1 min-w-[140px]">
        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider px-1">Team</label>
        <Select value={filters.team} onValueChange={(v) => updateFilter("team", v)}>
          <SelectTrigger className="h-8 text-xs">
            <SelectValue placeholder="All Teams" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all" className="text-xs">All Teams</SelectItem>
            {teams.map((t) => (
              <SelectItem key={t.id} value={t.id} className="text-xs">{t.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Designation Dropdown */}
      <div className="space-y-1 flex-1 min-w-[140px]">
        <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider px-1">Designation</label>
        <Select value={filters.designation} onValueChange={(v) => updateFilter("designation", v)}>
          <SelectTrigger className="h-8 text-xs">
            <SelectValue placeholder="All Designations" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all" className="text-xs">All Designations</SelectItem>
            {designations.map((d) => (
              <SelectItem key={d.id} value={d.id} className="text-xs">{d.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Employee Search */}
      <div className="space-y-1 flex-[1.5] min-w-[180px]">
        <label className="text-[10px] font-semibold text-muted-foreground dark:text-muted-foreground uppercase tracking-wider px-1">Employee Search</label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground dark:text-muted-foreground" />
          <Input 
            className="pl-9 h-8 text-xs dark:bg-slate-900 dark:text-white dark:border-slate-700 dark:placeholder:text-slate-400" 
            placeholder="Search by name or ID..." 
            value={filters.search}
            onChange={(e) => updateFilter("search", e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}
