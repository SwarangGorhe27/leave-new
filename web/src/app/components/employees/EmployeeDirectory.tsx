import { useMemo, useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";
import {
  Search,
  ChevronDown,
  Mail,
  MapPin,
  Calendar,
  Info,
  Users,
  X,
  LayoutGrid,
  List as ListIcon,
} from "lucide-react";
import { Employee, normalizeLegacyEmployee } from "./mockData";
import { useDispatch } from "react-redux";
import { setAdminEmployees } from "@/store/slices/adminSlice";
import {
  useEmployeeDirectoryList,
  useOrganizationDepartments,
  useOrganizationDesignations,
  useOrganizationTeams,
  type MasterOption,
  type EmployeeDirectoryItem,
} from "@hooks/useEmployees";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "../ui/pagination";

type ViewMode = "card" | "list";
const EMPLOYEE_PAGE_SIZE = 8;
// Fetch a full page from the API so client-side filtering + pagination has the
// complete dataset (this repo's directory hook returns a paginated object).
const DIRECTORY_FETCH_SIZE = 100;

interface DirectoryFilters {
  search: string;
  department: string;
  team: string;
  designation: string;
  statusFilter: string;
  joiningFrom: string;
  joiningTo: string;
}

function StatusBadge({ status }: { status: Employee["status"] }) {
  const styles = {
    Active:     "bg-[#212529] text-[#F8F9FA]",
    Inactive:   "bg-[#CED4DA] text-[#212529]",
    "On Leave": "bg-[#6C757D] text-white",
  };
  return (
    <span className={`text-[10px] px-2.5 py-1 rounded-md uppercase tracking-wider font-semibold ${styles[status]}`}>
      {status}
    </span>
  );
}

function EmployeeAvatar({ employee, size = "md" }: { employee: Employee; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "w-8 h-8 text-xs", md: "w-10 h-10 text-sm", lg: "w-14 h-14 text-base" };
  if (employee.avatar) {
    return (
      <img
        src={employee.avatar}
        alt={employee.name}
        className={`${sizes[size]} rounded-lg object-cover flex-shrink-0 border border-border`}
      />
    );
  }
  return (
    <div
      className={`${sizes[size]} rounded-lg flex items-center justify-center text-white flex-shrink-0 border border-border font-bold`}
      style={{ backgroundColor: employee.avatarColor }}
    >
      {employee.initials}
    </div>
  );
}

function SelectFilter({
  value,
  onChange,
  options,
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
  placeholder: string;
}) {
  const isActive = value !== "";
  
  return (
    <div className="relative min-w-0 group">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`flat-input h-9 w-full min-w-0 appearance-none pl-3 pr-8 text-sm cursor-pointer font-medium
          transition-all duration-150
          ${isActive
            ? 'bg-secondary border border-foreground/30 text-foreground shadow-sm'
            : 'hover:border-border/80 focus:border-foreground/50 focus:shadow-sm'
          }
          hover:bg-secondary/50 focus:outline-none`}
      >
        <option value="">
          {placeholder.startsWith("All") ? placeholder : `All ${placeholder.split(" ").slice(1).join(" ") || "Options"}`}
        </option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <ChevronDown className={`absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 pointer-events-none transition-colors ${
        isActive 
          ? 'text-foreground' 
          : 'text-muted-foreground group-hover:text-foreground/70'
      }`} />
    </div>
  );
}

import { useEmployee } from "../../context/EmployeeContext";

function optionLabel(item: MasterOption) {
  return item.name ?? item.title ?? item.label ?? item.code ?? String(item.id);
}

function masterOptions(items: MasterOption[]) {
  return items.map((item) => ({ value: String(item.id), label: optionLabel(item) }));
}

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return (parts[0]?.[0] ?? "E") + (parts[1]?.[0] ?? "");
}

function employeeStatus(status: string): Employee["status"] {
  const normalized = status.toUpperCase();
  if (normalized === "ACTIVE") return "Active";
  if (normalized === "ON_NOTICE") return "On Leave";
  return "Inactive";
}

function normalizeText(value: string) {
  return value.trim().toLowerCase().replace(/\s+/g, " ");
}

function normalizeDateValue(value: string | null | undefined) {
  const raw = value?.trim();
  if (!raw) return "";
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
  const match = raw.match(/^(\d{2})[-/](\d{2})[-/](\d{4})$/);
  if (!match) return "";
  const [, day, month, year] = match;
  return `${year}-${month}-${day}`;
}

function isWithinDateRange(value: string, from: string, to: string) {
  const date = normalizeDateValue(value);
  const normalizedFrom = normalizeDateValue(from);
  const normalizedTo = normalizeDateValue(to);
  const start = normalizedFrom || normalizedTo;
  const end = normalizedTo || normalizedFrom;
  if (!date) return false;
  if (start && date < start) return false;
  if (end && date > end) return false;
  return true;
}

function toDirectoryEmployee(item: EmployeeDirectoryItem): Employee {
  return normalizeLegacyEmployee({
    id: String(item.id),
    name: item.full_name || [item.first_name, item.middle_name, item.last_name].filter(Boolean).join(" "),
    firstName: item.first_name,
    middleName: item.middle_name,
    lastName: item.last_name,
    employeeId: item.employee_code,
    designation: item.designation || "",
    designationId: item.designation_id || "",
    department: item.department || "",
    departmentId: item.department_id || "",
    team: item.team || "",
    teamId: item.team_id || "",
    email: item.work_email || "",
    phone: item.phone || "",
    joiningDate: item.date_of_joining || "",
    location: item.location || "",
    status: employeeStatus(item.status || item.status_display || ""),
    avatar: item.profile_photo || undefined,
    initials: initials(item.full_name || item.employee_code),
    avatarColor: "#334155",
    dateOfBirth: "",
    gender: "",
    maritalStatus: "",
    bloodGroup: "",
    nationality: "",
    bankName: "",
    accountNumber: "",
    ifscCode: "",
    pfNumber: "",
    esiNumber: "",
    family: [],
    passportNumber: "",
    passportExpiry: "",
    visaType: "",
    visaExpiry: "",
    visaCountry: "",
    positionHistory: [],
    basicSalary: 0,
    hra: 0,
    conveyance: 0,
    medicalAllowance: 0,
    specialAllowance: 0,
    grossSalary: 0,
    pf: 0,
    tds: 0,
    netSalary: 0,
  });
}

function formatJoiningDate(value: string) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function visiblePageNumbers(currentPage: number, pageCount: number) {
  const maxVisible = 5;
  if (pageCount <= maxVisible) return Array.from({ length: pageCount }, (_, index) => index + 1);

  const start = Math.max(1, Math.min(currentPage - 2, pageCount - maxVisible + 1));
  return Array.from({ length: maxVisible }, (_, index) => start + index);
}

export function EmployeeDirectory() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { selectEmployee } = useEmployee();
  const dispatch = useDispatch();

  const [filters, setFilters] = useState<DirectoryFilters>({
    search:      searchParams.get("search")      || "",
    department:  searchParams.get("department")  || "",
    team:        searchParams.get("team")        || "",
    designation: searchParams.get("designation") || "",
    statusFilter: searchParams.get("status") || "active",
    joiningFrom: normalizeDateValue(searchParams.get("joiningFrom")) || "",
    joiningTo: normalizeDateValue(searchParams.get("joiningTo")) || "",
  });
  const [viewMode, setViewMode] = useState<ViewMode>((searchParams.get("view") as ViewMode) || "card");
  const [page, setPage] = useState(() => {
    const value = Number(searchParams.get("page") || 1);
    return Number.isFinite(value) && value > 0 ? Math.floor(value) : 1;
  });
  const { data: directoryData, isLoading, isError } = useEmployeeDirectoryList({
    search: filters.search,
    departmentId: filters.department,
    teamId: filters.team,
    designationId: filters.designation,
    status: filters.statusFilter,
    joiningFrom: filters.joiningFrom,
    joiningTo: filters.joiningTo,
    page: 1,
    pageSize: DIRECTORY_FETCH_SIZE,
  });
  const { data: departments = [] } = useOrganizationDepartments();
  const { data: teams = [] } = useOrganizationTeams();
  const { data: designations = [] } = useOrganizationDesignations();
  const mappedEmployees = useMemo(() => {
    const raw = directoryData as unknown;
    let rows: EmployeeDirectoryItem[] = [];
    if (Array.isArray(raw)) {
      rows = raw as EmployeeDirectoryItem[];
    } else if (raw && typeof raw === "object") {
      const candidate = (raw as { results?: unknown }).results;
      if (Array.isArray(candidate)) rows = candidate as EmployeeDirectoryItem[];
    }
    return rows.map(toDirectoryEmployee);
  }, [directoryData]);
  const employees = mappedEmployees;

  useEffect(() => {
    if (mappedEmployees.length) {
      dispatch(setAdminEmployees(mappedEmployees));
    }
  }, [dispatch, mappedEmployees]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.search)      params.set("search", filters.search);
    if (filters.department)  params.set("department", filters.department);
    if (filters.team)        params.set("team", filters.team);
    if (filters.designation) params.set("designation", filters.designation);
    if (filters.statusFilter && filters.statusFilter !== 'active') params.set("status", filters.statusFilter);
    if (filters.joiningFrom) params.set("joiningFrom", filters.joiningFrom);
    if (filters.joiningTo)   params.set("joiningTo", filters.joiningTo);
    if (viewMode !== "card") params.set("view", viewMode);
    if (page > 1)            params.set("page", String(page));
    // Only navigate when the URL actually changes. Without this guard, calling
    // setSearchParams remounts this component (the parent outlet is keyed on
    // location.key), which re-runs this effect and creates an infinite loop.
    if (params.toString() !== searchParams.toString()) {
      setSearchParams(params, { replace: true });
    }
  }, [filters, viewMode, page, searchParams, setSearchParams]);

  const updateFilter = (key: keyof DirectoryFilters, value: string) => {
    setPage(1);
    setFilters((prev) => {
      const next = { ...prev, [key]: normalizeDateValue(value) || value };
      if (key === "joiningFrom" && next.joiningTo && next.joiningFrom > next.joiningTo) {
        next.joiningTo = "";
      }
      if (key === "joiningTo" && next.joiningFrom && next.joiningTo < next.joiningFrom) {
        next.joiningFrom = "";
      }
      return next;
    });
  };

  const filtered = employees.filter((emp) => {
    const s = normalizeText(filters.search);

    // Status filtering: default show Active only
    if (filters.statusFilter === 'inactive_resigned') {
      if (!(emp.status === 'Inactive' || (emp as any).status === 'Resigned')) return false;
    } else {
      if (emp.status !== 'Active') return false;
    }

    // Search and dropdown filters
    if (s) {
      const searchable = normalizeText([
        emp.name,
        emp.employeeId,
        emp.email,
        emp.designation,
        emp.department,
        emp.team,
      ].join(" "));
      if (!searchable.includes(s)) return false;
    }
    if (filters.department && (emp as any).departmentId !== filters.department) return false;
    if (filters.team && (emp as any).teamId !== filters.team) return false;
    if (filters.designation && (emp as any).designationId !== filters.designation) return false;

    // Joining date range filters
    if ((filters.joiningFrom || filters.joiningTo) && !isWithinDateRange(emp.joiningDate, filters.joiningFrom, filters.joiningTo)) return false;

    return true;
  });

  const clearFilters = () => {
    setPage(1);
    setFilters({ search: "", department: "", team: "", designation: "", statusFilter: 'active', joiningFrom: "", joiningTo: "" });
  };

  const hasActiveFilters = Boolean(
    filters.search || filters.department || filters.team || filters.designation ||
    filters.statusFilter !== 'active' || filters.joiningFrom || filters.joiningTo
  );

  const openInformation = (emp: Employee) => {
    selectEmployee(emp.id);
    navigate(`/admin/employees/information/${emp.id}`);
  };

  const pageCount = Math.max(1, Math.ceil(filtered.length / EMPLOYEE_PAGE_SIZE));
  const clampedPage = Math.min(page, pageCount);
  const pagedEmployees = filtered.slice(
    (clampedPage - 1) * EMPLOYEE_PAGE_SIZE,
    clampedPage * EMPLOYEE_PAGE_SIZE,
  );
  const pageStart = filtered.length === 0 ? 0 : (clampedPage - 1) * EMPLOYEE_PAGE_SIZE + 1;
  const pageEnd = Math.min(clampedPage * EMPLOYEE_PAGE_SIZE, filtered.length);

  useEffect(() => {
    if (!isLoading && page !== clampedPage) setPage(clampedPage);
  }, [clampedPage, page, isLoading]);

  return (
    <div className="portal-page admin-dashboard min-h-full flex flex-col">

      <section>
        <p className="dashboard-section-label">Employee Directory</p>
        <div className="dashboard-widget space-y-3">
        {/* Search + filters — compact row, no dead space between controls */}
        <div className="grid w-full grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-[minmax(0,1.35fr)_repeat(4,minmax(0,1fr))_minmax(0,1.1fr)_auto] lg:items-center xl:grid-cols-[minmax(0,1.4fr)_repeat(4,minmax(0,0.9fr))_minmax(0,1.05fr)_auto]">
          <div className="flat-input-group h-9 min-w-0 sm:col-span-2 lg:col-span-1">
            <Search className="flat-input-group__icon h-4 w-4 shrink-0" aria-hidden />
            <input
              type="text"
              placeholder="Search employees…"
              value={filters.search}
              onChange={(e) => updateFilter("search", e.target.value)}
              className="flat-input-field h-9 min-h-0 w-full min-w-0 text-sm"
              autoComplete="off"
              spellCheck={false}
            />
          </div>

          <SelectFilter
            value={filters.department}
            onChange={(v) => updateFilter("department", v)}
            options={masterOptions(departments)}
            placeholder="All Departments"
          />
          <SelectFilter
            value={filters.team}
            onChange={(v) => updateFilter("team", v)}
            options={masterOptions(teams)}
            placeholder="All Teams"
          />
          <SelectFilter
            value={filters.designation}
            onChange={(v) => updateFilter("designation", v)}
            options={masterOptions(designations)}
            placeholder="All Designations"
          />
          <div className="relative min-w-0 shrink-0 group">
            <select
              value={filters.statusFilter}
              onChange={(e) => updateFilter("statusFilter", e.target.value)}
              className={`flat-input h-9 w-full min-w-0 appearance-none pl-3 pr-8 text-sm cursor-pointer font-medium transition-all duration-150 ${filters.statusFilter !== "active" ? "border border-foreground/30 bg-secondary text-foreground shadow-sm" : "hover:border-border/80 focus:border-foreground/50 focus:shadow-sm"}`}
            >
              <option value="active">Active Employees</option>
              <option value="inactive_resigned">Inactive/Resigned</option>
            </select>
            <ChevronDown
              className={`pointer-events-none absolute right-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 transition-colors ${filters.statusFilter !== "active" ? "text-foreground" : "text-muted-foreground group-hover:text-foreground/70"}`}
            />
          </div>

          <div className="flex min-w-0 items-center gap-1.5 sm:col-span-2 lg:col-span-1">
            <span className="shrink-0 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">From</span>
            <input
              type="date"
              value={filters.joiningFrom}
              onChange={(e) => updateFilter("joiningFrom", e.target.value)}
              className="flat-input h-9 min-w-0 flex-1 px-2 text-xs"
            />
            <span className="shrink-0 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">To</span>
            <input
              type="date"
              value={filters.joiningTo}
              onChange={(e) => updateFilter("joiningTo", e.target.value)}
              className="flat-input h-9 min-w-0 flex-1 px-2 text-xs"
            />
          </div>

          <div className="flex shrink-0 items-center justify-end gap-2 sm:col-span-2 lg:col-span-1 lg:justify-start">
            <div className="flex h-9 shrink-0 items-center rounded-md border border-border bg-card p-0.5">
              {([
                { mode: "card" as const, Icon: LayoutGrid, label: "Card view" },
                { mode: "list" as const, Icon: ListIcon, label: "List view" },
              ]).map(({ mode, Icon, label }) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => {
                    setViewMode(mode);
                    setPage(1);
                  }}
                  title={label}
                  aria-label={label}
                  aria-pressed={viewMode === mode}
                  className={`flex h-8 w-8 items-center justify-center rounded transition-all duration-150 ${
                    viewMode === mode
                      ? "bg-foreground text-background shadow-sm"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                </button>
              ))}
            </div>

            {hasActiveFilters && (
              <button
                type="button"
                onClick={clearFilters}
                className="flex h-9 shrink-0 items-center gap-1.5 rounded-md border border-destructive/20 bg-destructive/5 px-3 text-xs font-semibold text-muted-foreground transition-all duration-150 hover:border-destructive/40 hover:bg-destructive/10 hover:text-foreground"
                title="Clear all active filters"
                aria-label="Clear all filters"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>
        </div>
      </section>

      <section className="flex-1 min-h-0 flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-2">
          <p className="dashboard-section-label mb-0">
            {isLoading ? "Loading…" : `Showing ${pageStart}-${pageEnd} of ${filtered.length} employees`}
          </p>
          {hasActiveFilters && (
            <span className="dashboard-badge-today px-2 py-0.5 rounded text-[9px] font-semibold uppercase">
              Filters active
            </span>
          )}
        </div>
        <div className="flex-1 min-h-0 max-h-[calc(100vh-330px)] overflow-y-auto pr-1 sm:pr-2">
        {isLoading ? (
          <div className="admin-loading-state dashboard-widget">
            Loading employees...
          </div>
        ) : isError ? (
          <div className="flex flex-col items-center justify-center h-56 bg-secondary/30 border border-dashed border-border rounded-xl">
            <div className="w-14 h-14 rounded-full bg-secondary border border-border flex items-center justify-center mb-4">
              <Users className="w-7 h-7 text-muted-foreground opacity-60" />
            </div>
            <p className="text-sm font-semibold text-muted-foreground">Employee API did not return data</p>
            <p className="text-xs text-muted-foreground mt-1 text-center max-w-md">
              Check that Django is running and the frontend /api proxy is reaching the tenant backend.
            </p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-56 bg-secondary/30 border border-dashed border-border rounded-xl">
            <div className="w-14 h-14 rounded-full bg-secondary border border-border flex items-center justify-center mb-4">
              <Users className="w-7 h-7 text-muted-foreground opacity-60" />
            </div>
            <p className="text-sm font-semibold text-muted-foreground">No employees found</p>
            <p className="text-xs text-muted-foreground mt-1 text-center max-w-xs">
              Try adjusting your search or filter criteria
            </p>
            {hasActiveFilters && (
              <button 
                onClick={clearFilters} 
                className="mt-4 text-xs font-semibold text-foreground hover:text-accent px-3 py-1.5 rounded-lg bg-secondary border border-border hover:bg-secondary/80 transition-all"
              >
                Clear filters
              </button>
            )}
          </div>
        ) : viewMode === "card" ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {pagedEmployees.map((emp) => (
              <div
                key={emp.id}
                className="flat-card flat-card-hover bg-card p-5 cursor-pointer group transition-all duration-150"
                onClick={() => openInformation(emp)}
              >
                <div className="flex items-start justify-between mb-4">
                  <EmployeeAvatar employee={emp} size="lg" />
                  <StatusBadge status={emp.status} />
                </div>
                <h3 className="text-sm font-bold text-foreground truncate group-hover:text-accent transition-colors">{emp.name}</h3>
                <p className="text-xs font-semibold text-muted-foreground mt-0.5 truncate">{emp.designation}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{emp.department} · {emp.team}</p>

                <div className="mt-4 pt-3 border-t border-border space-y-2">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground font-medium">
                    <Mail className="w-3 h-3 flex-shrink-0" />
                    <span className="truncate">{emp.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground font-medium">
                    <MapPin className="w-3 h-3 flex-shrink-0" />
                    <span className="truncate">{emp.location}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground font-medium">
                    <Calendar className="w-3 h-3 flex-shrink-0" />
                    <span className="truncate">Joined {formatJoiningDate(emp.joiningDate)}</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-border opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <span className="flex items-center justify-center gap-2 py-1.5 text-xs font-semibold text-white bg-secondary border border-border rounded-md group-hover:bg-foreground group-hover:text-white transition-all">
                      <Info className="w-3.5 h-3.5" />
                                  View Details
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="dashboard-widget p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[800px]">
                <thead>
                  <tr className="bg-secondary/50 border-b border-border">
                    {["Employee", "Department", "Designation", "Location", "Joining Date", "Status", ""].map((h) => (
                      <th key={h} className="text-left px-4 sm:px-5 py-3 text-[10px] sm:text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {pagedEmployees.map((emp) => (
                    <tr
                      key={emp.id}
                      className="hover:bg-secondary/40 cursor-pointer transition-colors duration-150 group"
                      onClick={() => openInformation(emp)}
                    >
                      <td className="px-4 sm:px-5 py-4">
                        <div className="flex items-center gap-3">
                          <EmployeeAvatar employee={emp} size="sm" />
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-foreground truncate group-hover:text-accent transition-colors">{emp.name}</p>
                            <p className="text-xs text-muted-foreground">{emp.employeeId}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 sm:px-5 py-4">
                        <p className="text-sm text-foreground font-medium">{emp.department}</p>
                        <p className="text-xs text-muted-foreground">{emp.team}</p>
                      </td>
                      <td className="px-4 sm:px-5 py-4 text-sm text-foreground font-medium">{emp.designation}</td>
                      <td className="px-4 sm:px-5 py-4">
                        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                          <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
                          <span className="truncate">{emp.location}</span>
                        </div>
                      </td>
                      <td className="px-4 sm:px-5 py-4 text-sm text-muted-foreground whitespace-nowrap">
                        {formatJoiningDate(emp.joiningDate)}
                      </td>
                      <td className="px-4 sm:px-5 py-4">
                        <StatusBadge status={emp.status} />
                      </td>
                      <td className="px-4 sm:px-5 py-4 text-right">
                        <button className="flex items-center gap-1.5 text-xs font-semibold text-foreground bg-secondary hover:bg-foreground hover:text-background
                          border border-border px-3 py-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-all ml-auto">
                          <Info className="w-3.5 h-3.5" /> Info
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
        </div>
        {!isLoading && !isError && filtered.length > 0 && (
          <div className="mt-3 flex flex-col gap-3 border-t border-border pt-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs font-medium text-muted-foreground">
              Page {clampedPage} of {pageCount}
            </p>
            <Pagination className="mx-0 justify-end">
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    aria-disabled={clampedPage === 1}
                    className={clampedPage === 1 ? "pointer-events-none opacity-45" : ""}
                    onClick={(e) => {
                      e.preventDefault();
                      setPage((current) => Math.max(1, current - 1));
                    }}
                  />
                </PaginationItem>

                {visiblePageNumbers(clampedPage, pageCount).map((pageNumber) => (
                  <PaginationItem key={pageNumber}>
                    <PaginationLink
                      href="#"
                      isActive={pageNumber === clampedPage}
                      onClick={(e) => {
                        e.preventDefault();
                        setPage(pageNumber);
                      }}
                    >
                      {pageNumber}
                    </PaginationLink>
                  </PaginationItem>
                ))}

                <PaginationItem>
                  <PaginationNext
                    href="#"
                    aria-disabled={clampedPage === pageCount}
                    className={clampedPage === pageCount ? "pointer-events-none opacity-45" : ""}
                    onClick={(e) => {
                      e.preventDefault();
                      setPage((current) => Math.min(pageCount, current + 1));
                    }}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        )}
      </section>
    </div>
  );
}
