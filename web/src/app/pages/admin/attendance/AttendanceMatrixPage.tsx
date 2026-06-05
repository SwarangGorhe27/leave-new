import { useState, useMemo, useEffect, useCallback, memo } from "react";
import {
  Download,
  Upload,
  RefreshCw,
  Home,
  ChevronRight,
  FileSpreadsheet,
  Printer,
  ChevronDown,
  Search,
  Filter,
  Calendar as CalendarIcon,
  Info,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  User,
  Building2,
  Users,
  Briefcase,
  Zap,
  Edit2,
  Lock,
  Unlock,
  Eye,
  FileText,
  SlidersHorizontal,
  Mail,
  Phone,
  Calendar,
  ShieldCheck,
  History,
  TrendingUp,
  X,
  Plus,
  Save,
  Check,
  Trash2
} from "lucide-react";
import { Button } from "../../../components/ui/button";
import { KebabMenu } from "../../../components/ui/KebabMenu";
import { useEmployee } from "../../../context/EmployeeContext";
import * as XLSX from "xlsx";
import { useMatrixGrid, useMatrixDepartments, useUpdateMatrixDayStatus, useImportMatrix } from "../../../modules/attendance/hooks";
import { AlertCircle, Loader2 } from "lucide-react";
import { cn } from "../../../components/ui/utils";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription
} from "../../../components/ui/dialog";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "../../../components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger
} from "../../../components/ui/popover";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger
} from "../../../components/ui/tooltip";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription
} from "../../../components/ui/sheet";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
  ContextMenuSeparator
} from "../../../components/ui/context-menu";
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, addMonths, subMonths } from "date-fns";
import { motion, AnimatePresence } from "motion/react";

// --- Types & Constants ---
const STATUS_CODES: any = {
  P: { label: "Present", color: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  A: { label: "Absent", color: "bg-red-100 text-red-700 border-red-200" },
  L: { label: "Leave", color: "bg-orange-100 text-orange-700 border-orange-200" },
  H: { label: "Holiday", color: "bg-purple-100 text-purple-700 border-purple-200" },
  WO: { label: "Week Off", color: "bg-slate-100 text-slate-500 border-slate-200" },
  HD: { label: "Half Day", color: "bg-amber-100 text-amber-700 border-amber-200" },
  CL: { label: "Casual Leave", color: "bg-orange-50 text-orange-600 border-orange-100" },
  SL: { label: "Sick Leave", color: "bg-rose-50 text-rose-600 border-rose-100" },
  OD: { label: "On Duty", color: "bg-cyan-100 text-cyan-700 border-cyan-200" },
  WFH: { label: "Work From Home", color: "bg-blue-100 text-blue-700 border-blue-200" },
  OT: { label: "Overtime", color: "bg-emerald-50 text-emerald-600 border-emerald-100" },
  MR: { label: "Missing Record", color: "bg-yellow-100 text-yellow-700 border-yellow-200" },
};

// --- Sub-components ---

const MatrixCell = memo(({ emp, day, onUpdate, onOpenDrawer }: any) => {
  const { selectEmployee } = useEmployee();
  const dateKey = format(day, "yyyy-MM-dd");
  const cellData = emp.attendance?.[dateKey] || { status: "MR" };
  const status = cellData.status || "MR";
  const config = STATUS_CODES[status] || STATUS_CODES.MR;

  return (
    <Popover>
      <PopoverTrigger asChild>
        <div
          className={cn(
            "w-full h-full min-h-[32px] rounded-md border flex items-center justify-center text-[10px] font-black cursor-pointer transition-all duration-200 hover:scale-110 active:scale-95 group relative overflow-hidden shadow-sm",
            config.color
          )}
        >
          {status}
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-3 rounded-2xl shadow-2xl border-slate-200 bg-white/95 backdrop-blur-md z-[100]">
        <div className="space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <div className="flex flex-col">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{format(day, "dd MMM yyyy")}</span>
              <span className="text-[9px] font-bold text-slate-400 truncate w-32">{emp.name}</span>
            </div>
            <span className={cn("px-2 py-0.5 rounded text-[10px] font-black uppercase", config.color)}>{config.label}</span>
          </div>

          <div className="grid grid-cols-4 gap-1.5">
            {Object.keys(STATUS_CODES).slice(0, 12).map(code => (
              <button
                key={code}
                className={cn(
                  "h-8 flex items-center justify-center rounded-lg text-[10px] font-black border transition-all hover:scale-110 active:scale-90",
                  STATUS_CODES[code].color,
                  status === code ? "ring-2 ring-slate-900 ring-offset-1" : "opacity-60 hover:opacity-100"
                )}
                onClick={() => onUpdate(emp, dateKey, code)}
              >
                {code}
              </button>
            ))}
          </div>

          <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2">
            <Button variant="outline" size="sm" className="h-8 text-[10px] font-black gap-2 rounded-xl" onClick={() => selectEmployee(emp.id)}>
              <User className="w-3 h-3 text-blue-500" /> PROFILE
            </Button>
            <Button variant="outline" size="sm" className="h-8 text-[10px] font-black gap-2 rounded-xl">
              <Plus className="w-3 h-3 text-emerald-500" /> REMARK
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
});

const PersonalAttendanceCalendar = ({ emp, month }: any) => {
  const days = useMemo(() => {
    const start = startOfMonth(month);
    const end = endOfMonth(month);
    return eachDayOfInterval({ start, end });
  }, [month]);

  return (
    <div className="grid grid-cols-7 gap-2">
      {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
        <div key={d} className="text-center text-[9px] font-black text-slate-400 uppercase py-1">{d}</div>
      ))}
      {Array.from({ length: days[0].getDay() }).map((_, i) => <div key={`empty-${i}`} />)}
      {days.map(day => {
        const dateKey = format(day, "yyyy-MM-dd");
        const cellData = emp.attendance?.[dateKey] || { status: "MR" };
        const config = STATUS_CODES[cellData.status] || STATUS_CODES.MR;
        return (
          <div key={dateKey} className={cn("aspect-square rounded-xl border flex flex-col items-center justify-center relative group transition-all hover:scale-105", config.color)}>
            <span className="text-[10px] font-black">{format(day, "d")}</span>
          </div>
        );
      })}
    </div>
  );
};

export function AttendanceMatrixPage() {
  const { selectEmployee } = useEmployee();
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  const matrixMonth = selectedMonth.getMonth() + 1;
  const matrixYear = selectedMonth.getFullYear();

  const [filters, setFilters] = useState({
    search: "",
    department: "all",
    designation: "all"
  });

  const deptFilter = filters.department !== "all" ? filters.department : undefined;
  const { data: matrixRows = [], isLoading: matrixLoading, isError: matrixError, error: matrixErr, refetch: refetchMatrix } =
    useMatrixGrid(matrixYear, matrixMonth, 1, deptFilter, filters.search || undefined);
  const { data: matrixDepartments = [] } = useMatrixDepartments();
  const updateDayStatus = useUpdateMatrixDayStatus();
  const importMatrix = useImportMatrix();
  const [data, setData] = useState<typeof matrixRows>([]);

  useEffect(() => {
    setData(matrixRows);
  }, [matrixRows]);

  // Grid Configuration State
  const [gridConfig, setGridConfig] = useState({
    density: "default",
    stickyEmployee: true,
    showSummaries: true
  });

  const [selectedEmployee, setSelectedEmployee] = useState<any>(null);
  const [showDrawer, setShowDrawer] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importPreview, setImportPreview] = useState<any[] | null>(null);
  const [importFile, setImportFile] = useState<File | null>(null);

  // Performance: Month Days Calculation
  const monthDays = useMemo(() => {
    try {
      const start = startOfMonth(selectedMonth);
      const end = endOfMonth(selectedMonth);
      return eachDayOfInterval({ start, end });
    } catch (e) {
      return [];
    }
  }, [selectedMonth]);

  // --- Filtering Logic (department handled server-side) ---
  const filteredData = useMemo(() => {
    if (!data) return [];
    const searchStr = filters.search.toLowerCase();
    if (!filters.search) return data;
    return data.filter((emp) =>
      emp.name?.toLowerCase().includes(searchStr) ||
      emp.id?.toLowerCase().includes(searchStr) ||
      emp.department?.toLowerCase().includes(searchStr),
    );
  }, [data, filters.search]);

  // --- Attendance Logic ---
  const STATUS_UI_TO_CODE: Record<string, string> = {
    Present: "P",
    Absent: "A",
    Leave: "L",
    Holiday: "H",
    "Week Off": "W",
    "Half Day": "HD",
    P: "P",
    A: "A",
    L: "L",
  };

  const handleUpdateAttendance = useCallback(
    async (emp: { id: string; name: string; employeeUuid?: string }, dateKey: string, newStatus?: string) => {
      if (!newStatus) {
        toast.info("Select a status from right-click menu");
        return;
      }
      const code = STATUS_UI_TO_CODE[newStatus] ?? newStatus;
      try {
        await updateDayStatus.mutateAsync({
          employeeId: emp.employeeUuid ?? emp.id,
          date: dateKey,
          status_code: code,
        });
        setData((prev) =>
          prev.map((item) => {
            if (item.id === emp.id) {
              const updated = { ...item };
              const oldStatus = updated.attendance[dateKey]?.status || "MR";
              updated.attendance[dateKey] = {
                ...updated.attendance[dateKey],
                status: newStatus,
                history: [
                  ...(updated.attendance[dateKey]?.history || []),
                  {
                    time: format(new Date(), "yyyy-MM-dd HH:mm"),
                    user: "Admin",
                    action: "Manual Update",
                    from: oldStatus,
                    to: newStatus,
                  },
                ],
              };
              return updated;
            }
            return item;
          }),
        );
        toast.success(`Updated ${emp.name} to ${newStatus}`);
        refetchMatrix();
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Failed to update status");
      }
    },
    [updateDayStatus, refetchMatrix],
  );

  const openDrawer = useCallback((emp: any) => {
    setSelectedEmployee(emp);
    setShowDrawer(true);
  }, []);

  // --- Excel Import/Export Logic ---
  const handleExport = async () => {
    const toastId = toast.loading("Exporting Attendance Matrix...");
    try {
      const exportRows = filteredData.map(emp => {
        const row: any = { "Employee": emp.name, "ID": emp.id, "Dept": emp.department };
        monthDays.forEach(day => {
          const key = format(day, "yyyy-MM-dd");
          row[format(day, "dd-MM-yyyy")] = emp.attendance[key]?.status || "MR";
        });
        return row;
      });
      const ws = XLSX.utils.json_to_sheet(exportRows);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Attendance");
      const fileName = `Attendance_Matrix_${format(selectedMonth, "MMM_yyyy")}.xlsx`;
      XLSX.writeFile(wb, fileName);
      toast.dismiss(toastId);
      toast.success("Excel exported successfully");
    } catch (e) {
      toast.dismiss(toastId);
      toast.error("Export failed");
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    const toastId = toast.loading("Processing Excel file...");

    try {
      const reader = new FileReader();
      reader.onload = (e) => {
        const raw = e.target?.result;
        const workbook = XLSX.read(raw, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const json: any[] = XLSX.utils.sheet_to_json(worksheet);

        setImportFile(file);
        setImportPreview(json);
        setShowImportModal(false);
        setIsImporting(false);
        toast.dismiss(toastId);
        toast.info(`Parsed ${json.length} rows. Confirm to upload to the server.`);
      };
      reader.readAsArrayBuffer(file);
    } catch {
      setIsImporting(false);
      toast.dismiss(toastId);
      toast.error("Failed to parse Excel file");
    }
  };

  const confirmImport = async () => {
    if (!importFile) {
      toast.error("No file selected for import");
      return;
    }
    const toastId = toast.loading("Uploading attendance matrix…");
    try {
      const formData = new FormData();
      formData.append('file', importFile);
      formData.append('year', String(matrixYear));
      formData.append('month', String(matrixMonth));
      await importMatrix.mutateAsync(formData);
      toast.dismiss(toastId);
      toast.success("Import job queued. Matrix will refresh when processing completes.");
      setImportPreview(null);
      setImportFile(null);
      await refetchMatrix();
    } catch (e) {
      toast.dismiss(toastId);
      toast.error(e instanceof Error ? e.message : "Import failed");
    }
  };

  return (
    <div className="flex flex-col h-full bg-background relative overflow-hidden">
      {matrixError && (
        <div className="mx-6 mt-4 flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {matrixErr instanceof Error ? matrixErr.message : "Failed to load attendance matrix."}
        </div>
      )}
      {matrixLoading && (
        <div className="mx-6 mt-4 flex items-center gap-2 text-muted-foreground text-sm">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading matrix…
        </div>
      )}
      {/* Header Section */}
      <div className="bg-card border-b border-border px-4 py-3 shadow-sm z-[40] sticky top-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
                {/* <Home className="w-2.5 h-2.5" /> */}
                {/* <ChevronRight className="w-2.5 h-2.5" /> */}
                {/* <span>Attendance</span> */}
                {/* <ChevronRight className="w-2.5 h-2.5" /> */}
                {/* <span className="text-emerald-500 font-black">Attendance Matrix</span> */}
              </div>
              <h2 className="text-xl font-bold text-foreground flex items-center gap-3">
                {/* Attendance Matrix */}
              </h2>
            </div>
            
            {/* Filter/Search Bar Inline */}
            <div className="flex items-center gap-3 border-l pl-6 border-border/50">
              <div className="relative w-[250px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground dark:text-muted-foreground" />
                <Input
                  className="pl-8 h-9 rounded-lg bg-secondary border-transparent focus:bg-background transition-all font-bold text-xs shadow-inner"
                  placeholder="Search Employee..."
                  value={filters.search}
                  onChange={e => setFilters({ ...filters, search: e.target.value })}
                />
              </div>
              <div className="w-[150px]">
                <Select value={filters.department} onValueChange={v => setFilters({ ...filters, department: v })}>
                  <SelectTrigger className="h-9 rounded-lg bg-secondary border-transparent font-bold text-xs">
                    <SelectValue placeholder="All Depts" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Departments</SelectItem>
                    {matrixDepartments.map((d) => (
                      <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center bg-secondary rounded-xl p-1 border border-border mr-2">
              <Button variant="ghost" size="sm" className="h-8 text-[11px] font-bold rounded-lg px-3" onClick={() => setSelectedMonth(subMonths(selectedMonth, 1))}>
                <ChevronRight className="w-3.5 h-3.5 rotate-180" />
              </Button>
              <span className="px-4 text-[11px] font-black text-slate-600 dark:text-slate-300 uppercase min-w-[120px] text-center">
                {format(selectedMonth, "MMMM yyyy")}
              </span>
              <Button variant="ghost" size="sm" className="h-8 text-[11px] font-bold rounded-lg px-3" onClick={() => setSelectedMonth(addMonths(selectedMonth, 1))}>
                <ChevronRight className="w-3.5 h-3.5" />
              </Button>
            </div>
            <Button variant="outline" size="sm" className="h-10 gap-2 font-bold text-[11px] border-emerald-100 hover:bg-emerald-50 rounded-xl px-4" onClick={handleExport}>
              <Download className="w-3.5 h-3.5 text-emerald-500" /> EXPORT
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-10 gap-2 font-bold text-[11px] border-blue-100 hover:bg-blue-50 rounded-xl px-4 bg-blue-50/30"
              onClick={() => setShowImportModal(true)}
            >
              <Upload className="w-3.5 h-3.5 text-blue-500" /> IMPORT EXCEL
            </Button>
            <Button variant="outline" size="icon" className="h-10 w-10 rounded-xl" onClick={async () => { setIsRefreshing(true); await refetchMatrix(); setIsRefreshing(false); }}>
              <RefreshCw className={cn("w-4 h-4 text-slate-400", isRefreshing && "animate-spin text-emerald-500")} />
            </Button>
            <KebabMenu
              items={[
                { label: "Matrix Settings", icon: SlidersHorizontal, onClick: () => toast.info("Opening matrix configuration...") },
                { label: "View Audit Trail", icon: History, onClick: () => toast.info("Loading audit trail...") },
                { label: "Lock Attendance", icon: Lock, onClick: () => toast.success("Attendance locked for this month") },
                {
                  label: "Reset Matrix", icon: Trash2, variant: "destructive", separator: true, onClick: () => {
                    if (confirm("Reset all manual updates for this month?")) toast.error("Matrix reset");
                  }
                },
              ]}
            />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col p-4 space-y-4 bg-secondary/30">
        {/* Statistics Widgets */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard title="Total Present" value="142" sub="+12 Today" color="emerald" icon={<CheckCircle2 />} />
          <StatCard title="Total Absent" value="12" sub="-2 Change" color="red" icon={<XCircle />} />
          <StatCard title="On Leave" value="8" sub="4 Pending" color="orange" icon={<Calendar />} />
          <StatCard title="Holidays" value="0" sub="Next: 15 May" color="purple" icon={<Zap />} />
          <StatCard title="Avg Hours" value="8.4h" sub="92% Goal" color="blue" icon={<Clock />} />
          <StatCard title="Punctuality" value="94%" sub="+1.2% Gain" color="cyan" icon={<TrendingUp />} />
        </div>

        {/* Main Matrix Grid Container */}
        <div className="bg-card border border-border rounded-2xl shadow-2xl overflow-hidden flex flex-col relative group/matrix ring-1 ring-border/50">
          <div className="flex-1 overflow-auto custom-scrollbar relative">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 z-[30]">
                <tr className="bg-secondary/90 backdrop-blur-xl border-b border-border">
                  <th className={cn(
                    "w-[220px] min-w-[220px] max-w-[220px] px-4 py-3 border-r border-border z-[35] bg-secondary transition-all duration-300",
                    gridConfig.stickyEmployee ? "sticky left-0 shadow-md" : "relative"
                  )}>
                    <div className="flex flex-col">
                      <span className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.1em]">Employee Details</span>
                      <span className="text-[9px] font-bold text-emerald-500 uppercase mt-0.5">Found {filteredData.length} records</span>
                    </div>
                  </th>
                  {monthDays.map((day, idx) => (
                    <th key={idx} className="w-[36px] text-center py-2 border-r border-border">
                      <div className="flex flex-col items-center">
                        <span className={cn(
                          "text-[11px] font-black leading-tight",
                          (day.getDay() === 0 || day.getDay() === 6) ? "text-red-400" : "text-foreground"
                        )}>
                          {format(day, "dd")}
                        </span>
                        <span className="text-[7px] font-black text-muted-foreground uppercase tracking-tighter">
                          {format(day, "EE")}
                        </span>
                      </div>
                    </th>
                  ))}
                  {gridConfig.showSummaries && (
                    <th className="sticky right-0 z-[30] bg-secondary w-[120px] px-3 py-2 text-center border-l border-border shadow-[-5px_0_15px_rgba(0,0,0,0.02)]">
                      <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">P | A | L</span>
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredData.map((emp, empIdx) => (
                  <tr key={emp.id} className={cn(
                    "group transition-all duration-200 border-b border-border hover:bg-secondary/50",
                    gridConfig.density === 'compact' ? 'h-10' : gridConfig.density === 'relaxed' ? 'h-16' : 'h-12'
                  )}>
                    <td className={cn(
                      "z-[20] bg-card group-hover:bg-secondary/80 border-r border-border px-3 cursor-pointer transition-all duration-300 w-[220px] min-w-[220px] max-w-[220px]",
                      gridConfig.stickyEmployee ? "sticky left-0 shadow-[5px_0_15px_rgba(0,0,0,0.02)]" : "relative shadow-none",
                      gridConfig.density === 'relaxed' ? 'py-3' : gridConfig.density === 'compact' ? 'py-1' : 'py-2'
                    )} onClick={() => selectEmployee(emp.id)}>
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-black shadow-inner flex-shrink-0 border border-emerald-200">
                          {emp.name?.[0]}
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[11px] font-bold text-foreground leading-tight group-hover:text-emerald-600 transition-colors" style={{wordBreak:'break-word'}}>{emp.name}</span>
                          <span className="text-[9px] font-semibold text-muted-foreground mt-0.5">
                            {emp.id} • {emp.department}
                          </span>
                        </div>
                      </div>
                    </td>
                    {monthDays.map((day, dIdx) => (
                      <td key={dIdx} className="p-1 border-r border-border">
                        <MatrixCell
                          emp={emp}
                          day={day}
                          onUpdate={handleUpdateAttendance}
                          onOpenDrawer={openDrawer}
                        />
                      </td>
                    ))}
                    {gridConfig.showSummaries && (
                      <td className="sticky right-0 z-[20] bg-card group-hover:bg-secondary/80 border-l border-border px-2 py-2 shadow-[-5px_0_15px_rgba(0,0,0,0.02)]">
                        <div className="flex items-center justify-around">
                          <div className="flex flex-col items-center">
                            <span className="text-[10px] font-black text-emerald-600">{emp.summary?.P || 0}</span>
                            <div className="w-3 h-0.5 bg-emerald-100 rounded-full" />
                          </div>
                          <div className="flex flex-col items-center">
                            <span className="text-[10px] font-black text-red-600">{emp.summary?.A || 0}</span>
                            <div className="w-3 h-0.5 bg-red-100 rounded-full" />
                          </div>
                          <div className="flex flex-col items-center">
                            <span className="text-[10px] font-black text-orange-600">{emp.summary?.L || 0}</span>
                            <div className="w-3 h-0.5 bg-orange-100 rounded-full" />
                          </div>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Footer Legend & Settings Bar */}
          <div className="bg-secondary/90 backdrop-blur-xl px-6 py-4 border-t border-border flex items-center justify-between">
            <div className="flex items-center gap-6">
              <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                <ShieldCheck className="w-3 h-3" /> Grid Legend:
              </span>
              {Object.entries(STATUS_CODES).slice(0, 8).map(([code, cfg]: any) => (
                <div key={code} className="flex items-center gap-2.5">
                  <div className={cn("w-6 h-6 rounded-lg border flex items-center justify-center text-[9px] font-black shadow-sm", cfg.color)}>
                    {code}
                  </div>
                  <span className="text-[10px] font-bold text-slate-500 whitespace-nowrap">{cfg.label}</span>
                </div>
              ))}
            </div>

          </div>
        </div>
      </div>

      {/* --- Drawers & Modals --- */}

      {/* 1. Employee Details Drawer */}
      <Sheet open={showDrawer} onOpenChange={setShowDrawer}>
        <SheetContent className="sm:max-w-[550px] p-0 border-l-0 overflow-y-auto no-scrollbar shadow-2xl">
          <SheetHeader className="p-0">
            <div className="bg-slate-900 p-10 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 z-10">
                <Button variant="ghost" size="icon" className="text-white/30 hover:text-white" onClick={() => setShowDrawer(false)}>
                  <X className="w-6 h-6" />
                </Button>
              </div>
              <div className="relative z-10 flex flex-col items-center text-center space-y-5">
                <div className="w-28 h-28 rounded-[40px] bg-emerald-500 border-4 border-white/10 p-1 shadow-2xl">
                  <div className="w-full h-full rounded-[34px] bg-white flex items-center justify-center text-3xl font-black text-emerald-600">
                    {selectedEmployee?.name?.[0]}
                  </div>
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white tracking-tight">{selectedEmployee?.name}</h3>
                  <p className="text-[11px] font-black text-emerald-400 uppercase tracking-widest mt-1 opacity-80">{selectedEmployee?.id} • {selectedEmployee?.designation}</p>
                </div>
                <div className="flex items-center gap-6 pt-2">
                  <div className="flex flex-col items-center px-4 border-r border-white/10">
                    <span className="text-xl font-black text-white">92%</span>
                    <span className="text-[9px] font-bold text-white/40 uppercase tracking-widest">On Time</span>
                  </div>
                  <div className="flex flex-col items-center px-4">
                    <span className="text-xl font-black text-white">22</span>
                    <span className="text-[9px] font-bold text-white/40 uppercase tracking-widest">Present</span>
                  </div>
                </div>
              </div>
            </div>
          </SheetHeader>

          <div className="p-8 space-y-10">
            <div className="grid grid-cols-2 gap-8">
              <div className="space-y-1.5">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Department</p>
                <p className="text-sm font-bold text-slate-800 flex items-center gap-2"><Building2 className="w-4 h-4 text-blue-500" /> {selectedEmployee?.department}</p>
              </div>
              <div className="space-y-1.5">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Employment</p>
                <p className="text-sm font-bold text-slate-800 flex items-center gap-2"><Briefcase className="w-4 h-4 text-purple-500" /> Full Time Regular</p>
              </div>
            </div>

            <div className="space-y-5">
              <h4 className="text-[11px] font-black text-slate-900 uppercase tracking-[0.2em] flex items-center gap-3">
                <Calendar className="w-4 h-4 text-emerald-500" /> Monthly Attendance Map
              </h4>
              <div className="bg-slate-50 p-6 rounded-[32px] border border-slate-100 shadow-inner">
                <PersonalAttendanceCalendar emp={selectedEmployee} month={selectedMonth} />
              </div>
            </div>

            <div className="space-y-5">
              <h4 className="text-[11px] font-black text-slate-900 uppercase tracking-[0.2em] flex items-center gap-3">
                <History className="w-4 h-4 text-blue-500" /> Change Logs
              </h4>
              <div className="space-y-4">
                {selectedEmployee?.attendance?.[format(new Date(2026, 4, 11), "yyyy-MM-dd")]?.history?.map((log: any, i: number) => (
                  <div key={i} className="flex gap-4 group">
                    <div className="flex flex-col items-center">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mt-2" />
                      <div className="w-px flex-1 bg-slate-100 mt-2" />
                    </div>
                    <div className="flex-1 space-y-1 bg-slate-50/50 p-3 rounded-2xl border border-transparent hover:border-slate-100 transition-all">
                      <div className="flex items-center justify-between">
                        <p className="text-[11px] font-black text-slate-800">{log.action}</p>
                        <span className="text-[10px] font-bold text-slate-400">{log.time}</span>
                      </div>
                      <p className="text-[10px] text-slate-500 leading-relaxed font-medium">
                        From <span className="font-black text-slate-400">{log.from}</span> to <span className="font-black text-emerald-600">{log.to}</span> by <span className="text-blue-600 font-bold">{log.user}</span>
                      </p>
                    </div>
                  </div>
                )) || <p className="text-[11px] text-slate-400 italic text-center py-4">No recent history for this month</p>}
              </div>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      {/* 2. Excel Import Modal */}
      <Dialog open={showImportModal} onOpenChange={setShowImportModal}>
        <DialogContent className="sm:max-w-[500px] rounded-[40px] p-0 overflow-hidden border-0 shadow-2xl">
          <div className="bg-blue-600 p-8 text-center space-y-2 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-full opacity-10">
              <div className="grid grid-cols-8 gap-4 p-4">
                {Array.from({ length: 32 }).map((_, i) => <div key={i} className="aspect-square bg-white rounded-lg rotate-12" />)}
              </div>
            </div>
            <Upload className="w-12 h-12 text-white mx-auto relative z-10" />
            <h3 className="text-xl font-bold text-white relative z-10">Import Attendance Data</h3>
            <p className="text-[11px] text-blue-100 font-medium opacity-80 relative z-10 uppercase tracking-widest">Upload XLSX or XLS formatted template</p>
          </div>
          <div className="portal-page admin-dashboard">
            <div
              className="py-12 border-2 border-dashed border-slate-200 rounded-[32px] flex flex-col items-center justify-center space-y-4 bg-slate-50/50 hover:bg-slate-50 hover:border-blue-500 transition-all cursor-pointer group"
              onClick={() => document.getElementById('excel-upload')?.click()}
            >
              <input
                type="file"
                id="excel-upload"
                className="hidden"
                accept=".xlsx, .xls"
                onChange={handleFileUpload}
              />
              <div className="w-16 h-16 rounded-3xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-110 transition-transform shadow-sm">
                <FileSpreadsheet className="w-8 h-8" />
              </div>
              <div className="text-center space-y-1">
                <p className="text-sm font-bold text-slate-900">Drop your file here or browse</p>
                <p className="text-[10px] text-slate-400 font-black uppercase tracking-tighter">Support XLSX, XLS (MAX. 5MB)</p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button variant="ghost" className="flex-1 h-12 rounded-2xl font-bold text-slate-500" onClick={() => setShowImportModal(false)}>CANCEL</Button>
              <Button className="flex-1 h-12 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-black shadow-lg" onClick={() => document.getElementById('excel-upload')?.click()}>
                {isImporting ? "PROCESSING..." : "SELECT FILE"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* 3. Final Confirmation Dialog */}
      <Dialog open={!!importPreview} onOpenChange={(open) => !open && setImportPreview(null)}>
        <DialogContent className="sm:max-w-[450px] rounded-[40px] p-8 border-0 shadow-2xl">
          <div className="space-y-6">
            <div className="flex flex-col items-center text-center space-y-3">
              <div className="w-16 h-16 rounded-3xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-inner">
                <ShieldCheck className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Review & Confirm Changes</h3>
              <p className="text-[11px] text-slate-500 font-medium px-4">
                We parsed the Excel file and found matches for <span className="text-emerald-600 font-black">{importPreview?.length} employees</span>.
                Are you sure you want to proceed with the update?
              </p>
            </div>

            <div className="bg-slate-50 rounded-3xl p-5 border border-slate-100 space-y-3">
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <Info className="w-3.5 h-3.5" /> SUMMARY OF UPDATES
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-3 rounded-2xl border border-slate-100">
                  <p className="text-[9px] font-bold text-slate-400 uppercase">Matched Records</p>
                  <p className="text-lg font-black text-emerald-600">{importPreview?.length}</p>
                </div>
                <div className="bg-white p-3 rounded-2xl border border-slate-100">
                  <p className="text-[9px] font-bold text-slate-400 uppercase">Target Period</p>
                  <p className="text-lg font-black text-blue-600">{format(selectedMonth, "MMM yyyy")}</p>
                </div>
              </div>
              <div className="pt-2">
                <p className="text-[10px] text-slate-400 leading-tight">
                  * This action will override existing attendance records for matched dates and create history logs for each change.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <Button variant="ghost" className="flex-1 h-12 rounded-2xl font-bold text-slate-500" onClick={() => setImportPreview(null)}>ABORT</Button>
              <Button className="flex-1 h-12 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl font-black shadow-xl" onClick={confirmImport}>
                YES, CONFIRM UPDATE
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function StatCard({ title, value, sub, icon, color }: any) {
  const colors: any = {
    emerald: "bg-emerald-50 text-emerald-600 border-emerald-100",
    red: "bg-red-50 text-red-600 border-red-100",
    orange: "bg-orange-50 text-orange-600 border-orange-100",
    purple: "bg-purple-50 text-purple-600 border-purple-100",
    blue: "bg-blue-50 text-blue-600 border-blue-100",
    cyan: "bg-cyan-50 text-cyan-600 border-cyan-100",
  };
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="bg-card border border-border p-3.5 rounded-[20px] shadow-sm space-y-3 transition-all cursor-default relative overflow-hidden group"
    >
      <div className="absolute top-0 right-0 w-16 h-16 bg-secondary rounded-bl-full -translate-y-8 translate-x-8 group-hover:scale-150 transition-transform duration-500" />
      <div className="flex items-center justify-between relative z-10">
        <div className={cn("p-2 rounded-xl border", colors[color])}>
          {icon && typeof icon === 'object' ? { ...icon, props: { ...icon.props, className: "w-4 h-4" } } : icon}
        </div>
        <span className="text-xl font-black text-foreground">{value}</span>
      </div>
      <div className="relative z-10 space-y-0.5">
        <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">{title}</p>
        <p className={cn("text-[9px] font-bold", color === 'red' ? 'text-red-400' : 'text-emerald-500')}>{sub}</p>
      </div>
    </motion.div>
  );
}

