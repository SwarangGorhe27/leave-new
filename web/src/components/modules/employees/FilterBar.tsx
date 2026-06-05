import { LayoutGrid, List, Search, Filter, X, ChevronDown, Calendar, Download, Upload } from 'lucide-react';
import { useDepartments, useDesignations, useBranches } from '@hooks/useEmployees';
import { Select } from '@components/ui';
import { cn } from '@utils/utils';
import { EMPLOYMENT_STATUS_OPTIONS, EMPLOYEE_FILTER_OPTIONS } from './admin/constants';

interface FilterState {
  search: string;
  category: string;
  employmentStatus: string;
  employeeFilter: string;
  department: string;
  designation: string;
  team: string;
  dateStart: string;
  dateEnd: string;
}

interface FilterBarProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  viewMode: 'list' | 'card';
  onViewModeChange: (mode: 'list' | 'card') => void;
}

export function FilterBar({ filters, onFilterChange, viewMode, onViewModeChange }: FilterBarProps) {
  const { data: departments = [] } = useDepartments();
  const { data: designations = [] } = useDesignations();
  const { data: teams = [] } = useBranches(); // Using branches as teams

  const updateFilter = (field: keyof FilterState, value: string) => {
    onFilterChange({ ...filters, [field]: value });
  };

  const clearFilters = () => {
    onFilterChange({
      search: '',
      category: '',
      employmentStatus: '',
      employeeFilter: '',
      department: '',
      designation: '',
      team: '',
      dateStart: '',
      dateEnd: '',
    });
  };

  const hasActiveFilters = Object.values(filters).some(v => v !== '');

  return (
    <div className="space-y-4">
      {/* Top row: Search and View Toggle */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <input
            type="text"
            placeholder="Search by name, ID or email..."
            value={filters.search}
            onChange={(e) => updateFilter('search', e.target.value)}
            className="w-full rounded-2xl border border-surface-200 bg-surface-0 py-2.5 pl-10 pr-4 text-sm text-text-primary transition-all focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/10 dark:border-white/5 dark:bg-white/5"
          />
        </div>

        <div className="flex items-center gap-2 rounded-2xl bg-surface-50 p-1.5 dark:bg-white/5">
          <button
            onClick={() => onViewModeChange('list')}
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-xl transition-all",
              viewMode === 'list' 
                ? "bg-surface-0 text-brand-500 shadow-sm dark:bg-white/10" 
                : "text-text-tertiary hover:text-text-secondary"
            )}
            title="List View"
          >
            <List className="h-4.5 w-4.5" />
          </button>
          <button
            onClick={() => onViewModeChange('card')}
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-xl transition-all",
              viewMode === 'card' 
                ? "bg-surface-0 text-brand-500 shadow-sm dark:bg-white/10" 
                : "text-text-tertiary hover:text-text-secondary"
            )}
            title="Card View"
          >
            <LayoutGrid className="h-4.5 w-4.5" />
          </button>
        </div>
      </div>

      {/* Filter Row */}
      <div className="flex flex-wrap items-end gap-3 rounded-2xl border border-surface-200 bg-surface-0/50 p-4 dark:border-white/5 dark:bg-white/[0.02]">
        <div className="flex-1 min-w-[160px]">
          <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-text-tertiary">Category</label>
          <Select
            label=""
            value={filters.category}
            onValueChange={(val) => updateFilter('category', val)}
            placeholder="All"
            options={[{ label: 'All', value: '' }]}
          />
        </div>

        <div className="flex-1 min-w-[160px]">
          <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-text-tertiary">Employment Status</label>
          <Select
            label=""
            value={filters.employmentStatus}
            onValueChange={(val) => updateFilter('employmentStatus', val)}
            placeholder="All"
            options={EMPLOYMENT_STATUS_OPTIONS.map(opt => ({ label: opt.label, value: opt.value }))}
          />
        </div>

        <div className="flex-1 min-w-[160px]">
          <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-text-tertiary">Employee Filter</label>
          <Select
            label=""
            value={filters.employeeFilter}
            onValueChange={(val) => updateFilter('employeeFilter', val)}
            placeholder="All"
            options={EMPLOYEE_FILTER_OPTIONS.map(opt => ({ label: opt.label, value: opt.value }))}
          />
        </div>

        <div className="flex-1 min-w-[160px]">
          <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-text-tertiary">Department</label>
          <Select
            label=""
            value={filters.department}
            onValueChange={(val) => updateFilter('department', val)}
            placeholder="All Departments"
            options={departments.map(d => ({ label: d.name, value: d.name }))}
          />
        </div>

        <div className="flex-1 min-w-[160px]">
          <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-text-tertiary">Designation</label>
          <Select
            label=""
            value={filters.designation}
            onValueChange={(val) => updateFilter('designation', val)}
            placeholder="All Designations"
            options={designations.map(d => ({ label: d.name, value: d.name }))}
          />
        </div>

        <div className="flex-1 min-w-[160px]">
          <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-text-tertiary">Team / Branch</label>
          <Select
            label=""
            value={filters.team}
            onValueChange={(val) => updateFilter('team', val)}
            placeholder="All Teams"
            options={teams.map(t => ({ label: t.name, value: t.name }))}
          />
        </div>

        <div className="flex-[2] min-w-[280px]">
          <label className="mb-1.5 block text-[10px] font-bold uppercase tracking-wider text-text-tertiary">Joining Date Range</label>
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <Calendar className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-tertiary pointer-events-none" />
              <input
                type="date"
                value={filters.dateStart}
                onChange={(e) => updateFilter('dateStart', e.target.value)}
                className="w-full rounded-xl border border-surface-200 bg-surface-0 py-2.5 pl-9 pr-2 text-xs text-text-primary transition-all focus:border-brand-500 focus:outline-none dark:border-white/10 dark:bg-white/5"
              />
            </div>
            <span className="text-text-tertiary text-xs font-medium">to</span>
            <div className="relative flex-1">
              <Calendar className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-tertiary pointer-events-none" />
              <input
                type="date"
                value={filters.dateEnd}
                onChange={(e) => updateFilter('dateEnd', e.target.value)}
                className="w-full rounded-xl border border-surface-200 bg-surface-0 py-2.5 pl-9 pr-2 text-xs text-text-primary transition-all focus:border-brand-500 focus:outline-none dark:border-white/10 dark:bg-white/5"
              />
            </div>
          </div>
        </div>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="flex h-10 items-center gap-2 rounded-xl border border-dashed border-danger-500/30 px-3 text-xs font-semibold text-danger-500 transition-colors hover:bg-danger-500/5"
          >
            <X className="h-3.5 w-3.5" />
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
