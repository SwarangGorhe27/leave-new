import { useState, useMemo, useEffect } from "react";
import { 
  Download, 
  RefreshCw, 
  Home, 
  ChevronRight,
  Filter,
  FileSpreadsheet,
  Printer,
  Plus,
  ArrowRightLeft,
  Calendar as CalendarIcon,
  Activity,
  User,
  History,
  Cpu,
  ShieldCheck,
  Check,
  ChevronDown,
  FileText,
  Zap,
  MoreHorizontal,
  Trash2,
  Eye,
  Settings,
  AlertTriangle
} from "lucide-react";
import { Button } from "../../../components/ui/button";
import { KebabMenu } from "../../../components/ui/KebabMenu";
import {
  useSwipeLogs,
  useSwipeLiveSummary,
  useAttendanceEmployees,
  useCreateSwipeLog,
  useDeviceDistribution,
} from "../../../modules/attendance/hooks";
import { fetchSwipeLogsLive } from "../../../modules/attendance/api";
import { AlertCircle } from "lucide-react";
import { cn } from "../../../components/ui/utils";
import { SwipeLogsFilterBar } from "../../../components/attendance/swipe/SwipeLogsFilterBar";
import { SwipeLogsAnalytics } from "../../../components/attendance/swipe/SwipeLogsAnalytics";
import { SwipeLogsTable } from "../../../components/attendance/swipe/SwipeLogsTable";
import { SwipeDetailsDrawer } from "../../../components/attendance/swipe/SwipeDetailsDrawer";
import { toast } from "sonner";
import { SwipeLog, DeviceHealth } from "../../../modules/attendance/types";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "../../../components/ui/dialog";
import { Label } from "../../../components/ui/label";
import { Input } from "../../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../../../components/ui/dropdown-menu";
import { format } from "date-fns";
import * as XLSX from "xlsx";
import { jsPDF } from "jspdf";

export function SwipeLogsPage() {
  const { data: devices = [] } = useDeviceDistribution();
  const [filters, setFilters] = useState({
    search: "",
    department: "all",
    designation: "all",
    team: "all",
    location: "all",
    device: "all",
    type: "all",
    date: new Date(),
    dateEnabled: true,
  });

  const { data: liveSummary } = useSwipeLiveSummary();
  const { data: employees = [] } = useAttendanceEmployees();
  const createSwipe = useCreateSwipeLog();
  const [localLogs, setLocalLogs] = useState<SwipeLog[]>([]);

  const employeeOptions = useMemo(() => {
    return employees.map((e: { id?: string; name?: string; employee_code?: string; first_name?: string; last_name?: string }) => ({
      id: e.id ?? e.employee_code ?? '',
      name: e.name ?? `${e.first_name ?? ''} ${e.last_name ?? ''}`.trim(),
      code: e.id ?? e.employee_code ?? '',
    }));
  }, [employees]);

  const [sortField, setSortField] = useState<string>("swipeTime");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  const deviceSourceByLabel: Record<string, string | undefined> = {
    "Biometric Device": "BIOMETRIC",
    "Mobile App": "MOBILE",
    "Web Login": "WEB",
    "QR Attendance": undefined,
  };

  const swipeFilters = useMemo(
    () => ({
      search: filters.search || undefined,
      department_id: filters.department !== "all" ? filters.department : undefined,
      punch_type: filters.type !== "all" ? filters.type : undefined,
      punch_source:
        filters.device !== "all"
          ? deviceSourceByLabel[filters.device]
          : undefined,
    }),
    [filters.search, filters.department, filters.type, filters.device],
  );
  const { data: apiLogs = [], isLoading, isError, error, refetch } = useSwipeLogs(
    filters.dateEnabled ? filters.date : undefined,
    filters.dateEnabled ? filters.date : undefined,
    currentPage,
    swipeFilters,
  );
  const logs = useMemo(() => [...localLogs, ...apiLogs], [localLogs, apiLogs]);

  // UI & Modal States
  const [selectedSwipe, setSelectedSwipe] = useState<SwipeLog | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isLiveEnabled, setIsLiveEnabled] = useState(true);
  
  const [showManualEntryModal, setShowManualEntryModal] = useState(false);
  const [showManageDevicesModal, setShowManageDevicesModal] = useState(false);
  const [showAllActivityModal, setShowAllActivityModal] = useState(false);
  const [showBulkActionsModal, setShowBulkActionsModal] = useState(false);

  // Manual Entry Form
  const [manualEntry, setManualEntry] = useState({
    employeeId: "",
    date: format(new Date(), "yyyy-MM-dd"),
    time: format(new Date(), "HH:mm:ss"),
    type: "IN",
    reason: ""
  });

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refetch();
    setIsRefreshing(false);
    toast.success("Swipe logs refreshed");
  };

  // EXPORT FUNCTIONALITY (CSV)
  const handleExportCSV = () => {
    setIsExporting(true);
    setTimeout(() => {
      const headers = ["Log ID", "Employee Name", "Employee Code", "Department", "Swipe Date", "Swipe Time", "Direction", "Shift", "Device Name", "Device Type", "Work Mode", "Location", "Status"];
      const csvRows = [headers.join(",")];
      for (const l of filteredLogs) {
        csvRows.push([
          `"${l.id}"`,
          `"${l.employeeName.replace(/"/g, '""')}"`,
          `"${l.employeeCode}"`,
          `"${l.department}"`,
          `"${l.swipeDate}"`,
          `"${l.swipeTime}"`,
          `"${l.type}"`,
          `"${l.shiftName || ''}"`,
          `"${l.deviceName}"`,
          `"${l.deviceType}"`,
          `"${l.workMode || 'WFO'}"`,
          `"${l.branch.replace(/"/g, '""')}"`,
          `"${l.status || ''}"`
        ].join(","));
      }
      const blob = new Blob([csvRows.join("\n")], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `Swipe_Logs_${format(filters.date, "yyyy_MM_dd")}.csv`;
      link.click();
      setIsExporting(false);
      toast.success("CSV Export Successful");
    }, 1000);
  };

  // EXPORT FUNCTIONALITY (Excel)
  const handleExportExcel = () => {
    setIsExporting(true);
    setTimeout(() => {
      const dataToExport = filteredLogs.map(l => ({
        "Log ID": l.id,
        "Employee Name": l.employeeName,
        "Employee Code": l.employeeCode,
        "Department": l.department,
        "Swipe Date": l.swipeDate,
        "Swipe Time": l.swipeTime,
        "Direction": l.type,
        "Shift": l.shiftName,
        "Device Name": l.deviceName,
        "Device Type": l.deviceType,
        "Work Mode": l.workMode || "WFO",
        "Location": l.branch,
        "Door": l.doorName,
        "Status": l.status,
        "Verification": l.verificationMethod
      }));
      const worksheet = XLSX.utils.json_to_sheet(dataToExport);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, "Swipe Logs");
      XLSX.writeFile(workbook, `Swipe_Logs_${format(filters.date, "yyyy_MM_dd")}.xlsx`);
      setIsExporting(false);
      toast.success("Excel Export Successful");
    }, 1000);
  };

  // EXPORT FUNCTIONALITY (PDF)
  const handleExportPDF = () => {
    setIsExporting(true);
    setTimeout(() => {
      const doc = new jsPDF();
      doc.setFont("helvetica", "bold");
      doc.setFontSize(16);
      doc.setTextColor(16, 185, 129); // emerald-500
      doc.text("HRMS Swipe Logs Report", 14, 15);
      
      doc.setFont("helvetica", "normal");
      doc.setFontSize(9);
      doc.setTextColor(100, 116, 139);
      doc.text(`Date: ${format(filters.date, "dd MMMM yyyy")}`, 14, 21);
      doc.text(`Generated on: ${format(new Date(), "dd MMM yyyy HH:mm")}`, 14, 26);
      doc.text(`Total Records: ${filteredLogs.length}`, 14, 31);
      
      let y = 38;
      doc.setFont("helvetica", "bold");
      doc.setFillColor(241, 245, 249);
      doc.rect(14, y, 182, 7, "F");
      doc.setFontSize(8);
      doc.setTextColor(15, 23, 42);
      doc.text("Employee Name", 16, y + 5);
      doc.text("ID", 55, y + 5);
      doc.text("Time", 75, y + 5);
      doc.text("Type", 95, y + 5);
      doc.text("Device Source", 115, y + 5);
      doc.text("Work Mode", 145, y + 5);
      doc.text("Location", 165, y + 5);
      
      y += 7;
      doc.setFont("helvetica", "normal");
      filteredLogs.slice(0, 35).forEach((l, index) => {
        if (index % 2 === 0) {
          doc.setFillColor(248, 250, 252);
          doc.rect(14, y, 182, 6, "F");
        }
        doc.text(l.employeeName, 16, y + 4.5);
        doc.text(l.employeeCode, 55, y + 4.5);
        doc.text(l.swipeTime, 75, y + 4.5);
        doc.text(l.type, 95, y + 4.5);
        doc.text(l.deviceName, 115, y + 4.5);
        doc.text(l.workMode || "WFO", 145, y + 4.5);
        doc.text(l.branch.split(' ')[0], 165, y + 4.5);
        y += 6;
      });
      
      if (filteredLogs.length > 35) {
        doc.setFont("helvetica", "italic");
        doc.setFontSize(7);
        doc.text(`... and ${filteredLogs.length - 35} more logs. Export to Excel or CSV to view full data.`, 14, y + 4);
      }
      
      doc.save(`Swipe_Logs_${format(filters.date, "yyyy_MM_dd")}.pdf`);
      setIsExporting(false);
      toast.success("PDF Export Successful");
    }, 1000);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleFullScreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        toast.error(`Error enabling full-screen: ${err.message}`);
      });
    } else {
      document.exitFullscreen();
    }
  };

  // Real-Time auto sync hook
  useEffect(() => {
    if (!isLiveEnabled) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetchSwipeLogsLive({ limit: 20 });
        const rows = res.data ?? [];
        if (rows.length) refetch();
      } catch {
        /* live poll optional */
      }
    }, 15000);
    return () => clearInterval(interval);
  }, [isLiveEnabled, refetch]);

  // MANUAL ENTRY FUNCTIONALITY
  const handleAddManualEntry = async () => {
    const employee = employeeOptions.find((e) => e.id === manualEntry.employeeId);
    if (!employee) {
      toast.error("Please select a valid employee");
      return;
    }

    try {
      await createSwipe.mutateAsync({
        employee_id: manualEntry.employeeId,
        punch_type: manualEntry.type,
        punch_time: `${manualEntry.date}T${manualEntry.time}`,
        punch_source: "MANUAL",
        remarks: manualEntry.reason,
      });
      toast.success("Manual punch recorded");
      setShowManualEntryModal(false);
      refetch();
      return;
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to add manual punch");
    }
  };

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      const matchesSearch = !filters.search || 
        log.employeeName.toLowerCase().includes(filters.search.toLowerCase()) ||
        log.employeeCode.toLowerCase().includes(filters.search.toLowerCase()) ||
        log.deviceId.toLowerCase().includes(filters.search.toLowerCase()) ||
        log.deviceName.toLowerCase().includes(filters.search.toLowerCase());
      
      const matchesDept = filters.department === "all" || log.department === filters.department;
      const matchesType = filters.type === "all" || log.type === filters.type;
      const matchesDevice = filters.device === "all" || log.deviceType === filters.device;

      return matchesSearch && matchesDept && matchesType && matchesDevice;
    });
  }, [filters, logs]);

  const sortedLogs = useMemo(() => {
    const sorted = [...filteredLogs];
    sorted.sort((a, b) => {
      const aVal = a[sortField as keyof SwipeLog] ?? "";
      const bVal = b[sortField as keyof SwipeLog] ?? "";
      
      if (sortField === "swipeTime") {
        const aDateTime = `${a.swipeDate} ${a.swipeTime}`;
        const bDateTime = `${b.swipeDate} ${b.swipeTime}`;
        return sortOrder === "asc" ? aDateTime.localeCompare(bDateTime) : bDateTime.localeCompare(aDateTime);
      }

      if (typeof aVal === "string") {
        return sortOrder === "asc" 
          ? aVal.localeCompare(bVal as string) 
          : (bVal as string).localeCompare(aVal);
      } else {
        return sortOrder === "asc" 
          ? (aVal > bVal ? 1 : -1) 
          : (bVal > aVal ? 1 : -1);
      }
    });
    return sorted;
  }, [filteredLogs, sortField, sortOrder]);

  const paginatedLogs = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedLogs.slice(start, start + pageSize);
  }, [sortedLogs, currentPage, pageSize]);

  const analyticsData = useMemo(() => {
    if (liveSummary) return liveSummary;
    return {
      totalSwipesToday: filteredLogs.length,
      totalInEntries: filteredLogs.filter((l) => l.type === "IN").length,
      totalOutEntries: filteredLogs.filter((l) => l.type === "OUT").length,
      missingPunchCount: 0,
      lateEntryCount: 0,
      wfhAttendanceCount: filteredLogs.filter((l) => l.workMode === "WFH").length,
      officeAttendanceCount: filteredLogs.filter((l) => l.workMode === "WFO").length,
    };
  }, [filteredLogs, liveSummary]);

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("desc");
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#f8fafc] dark:bg-slate-950/50 relative overflow-hidden print:bg-white print:p-0">
      {isError && (
        <div className="mx-6 mt-4 flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error instanceof Error ? error.message : "Failed to load swipe logs."}
        </div>
      )}
      {/* Top Header */}
      <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 py-3 shadow-sm sticky top-0 z-50 print:hidden">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-6">
            <div className="space-y-0.5">
              <div className="flex items-center gap-1.5 text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                {/* <Home className="w-2.5 h-2.5" />
                <ChevronRight className="w-2.5 h-2.5" />
                {/* <span>Attendance</span> */}
                {/* <ChevronRight className="w-2.5 h-2.5" /> */}
                {/* <span className="text-emerald-500">Swipe Logs</span> */}
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                {/* Attendance Intelligence */}
                <div 
                  className={cn(
                    "px-2 py-0.5 rounded text-[9px] border font-bold uppercase flex items-center gap-1 cursor-pointer transition-all",
                    isLiveEnabled 
                      ? "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-100 dark:border-emerald-500/20" 
                      : "bg-slate-50 dark:bg-slate-800 text-slate-400 border-slate-100 dark:border-slate-800"
                  )}
                  onClick={() => setIsLiveEnabled(!isLiveEnabled)}
                >
                  <div className={cn("w-1.5 h-1.5 rounded-full", isLiveEnabled ? "bg-emerald-500 animate-pulse" : "bg-slate-300")} />
                  {isLiveEnabled ? "Live" : "Paused"}
                </div>
              </h2>
            </div>

            {/* Inline Filter Bar */}
            <div className="print:hidden">
              <SwipeLogsFilterBar filters={filters} setFilters={setFilters} />
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Button 
              variant="outline" 
              size="sm" 
              className="h-8 gap-1.5 font-bold text-[10px] px-3 rounded-lg border-slate-200 dark:border-slate-800 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 hover:text-emerald-600 transition-all"
              onClick={() => setShowBulkActionsModal(true)}
            >
              <Zap className="w-3 h-3" /> BULK
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-8 gap-1.5 font-bold text-[10px] px-3 rounded-lg border-slate-200 dark:border-slate-800">
                  <FileSpreadsheet className="w-3 h-3 text-blue-500" /> EXPORT <ChevronDown className="w-2.5 h-2.5 opacity-50" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48 p-1 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl">
                <DropdownMenuItem className="gap-2 text-xs font-bold py-2.5 rounded-lg cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800" onClick={handleExportExcel}>
                  <FileSpreadsheet className="w-4 h-4 text-emerald-500" /> Export to Excel (.xlsx)
                </DropdownMenuItem>
                <DropdownMenuItem className="gap-2 text-xs font-bold py-2.5 rounded-lg cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800" onClick={handleExportCSV}>
                  <Download className="w-4 h-4 text-blue-500" /> Download CSV (.csv)
                </DropdownMenuItem>
                <DropdownMenuItem className="gap-2 text-xs font-bold py-2.5 rounded-lg cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800" onClick={handleExportPDF}>
                  <Printer className="w-4 h-4 text-slate-500" /> Print Data (.pdf)
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button 
              className="h-8 gap-1.5 font-bold text-[10px] px-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/20 transition-all"
              onClick={() => setShowManualEntryModal(true)}
            >
              <Plus className="w-3 h-3" /> MANUAL
            </Button>
            
            <Button 
              variant="outline" 
              size="icon" 
              className="h-8 w-8 rounded-lg border-slate-200 dark:border-slate-800"
              onClick={handleRefresh}
            >
              <RefreshCw className={cn("w-3.5 h-3.5 text-slate-500", isRefreshing && "animate-spin text-emerald-500")} />
            </Button>
            <KebabMenu 
              items={[
                { label: "Refresh Data", icon: RefreshCw, onClick: handleRefresh },
                { label: "Export CSV", icon: Download, onClick: handleExportCSV },
                { label: "Export Excel", icon: FileSpreadsheet, onClick: handleExportExcel },
                { label: "Export PDF", icon: FileText, onClick: handleExportPDF },
                { label: "Print Report", icon: Printer, onClick: handlePrint },
                { label: "Toggle Full Screen", icon: Eye, separator: true, onClick: handleFullScreen },
              ]}
            />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto no-scrollbar scroll-smooth">
        <div className="p-4 space-y-4 max-w-[1600px] mx-auto w-full">
          {/* Analytics Section */}
          <div className="print:hidden">
            <SwipeLogsAnalytics data={analyticsData} />
          </div>

          <div className="space-y-6">
            {/* Main Table Section */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden flex flex-col">
              <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between print:bg-white">
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Live Swipe Logs</h3>
                <div className="flex items-center gap-2 print:hidden">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Displaying {filteredLogs.length} Records</span>
                </div>
              </div>
              
              <SwipeLogsTable 
                logs={paginatedLogs} 
                onSelectSwipe={setSelectedSwipe}
                isLoading={isLoading}
                sortField={sortField}
                sortOrder={sortOrder}
                onSort={handleSort}
                currentPage={currentPage}
                setCurrentPage={setCurrentPage}
                pageSize={pageSize}
                setPageSize={setPageSize}
                totalRecords={filteredLogs.length}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Detail Drawer */}
      <SwipeDetailsDrawer 
        swipe={selectedSwipe} 
        onClose={() => setSelectedSwipe(null)} 
      />

      {/* BULK ACTIONS MODAL */}
      <Dialog open={showBulkActionsModal} onOpenChange={setShowBulkActionsModal}>
        <DialogContent className="sm:max-w-[400px] rounded-2xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-500" /> Bulk Operations
            </DialogTitle>
            <DialogDescription className="text-xs font-medium">
              Perform actions on all {filteredLogs.length} currently filtered swipe logs.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <Button 
              variant="outline" 
              className="w-full h-12 rounded-xl border-slate-200 dark:border-slate-700 text-slate-500 font-bold gap-3 flex justify-start px-6"
              onClick={handleExportExcel}
            >
              <FileSpreadsheet className="w-5 h-5 text-emerald-500" /> EXPORT FILTERED DATA
            </Button>
            <Button 
              variant="outline" 
              className="w-full h-12 rounded-xl border-slate-200 dark:border-slate-700 text-slate-500 font-bold gap-3 flex justify-start px-6"
            >
              <Trash2 className="w-5 h-5 text-red-400" /> DELETE FILTERED LOGS
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* MANUAL ENTRY MODAL */}
      <Dialog open={showManualEntryModal} onOpenChange={setShowManualEntryModal}>
        <DialogContent className="sm:max-w-[450px] rounded-2xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold flex items-center gap-2">
              <Plus className="w-5 h-5 text-emerald-500" /> Add Manual Swipe
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Select Employee</Label>
              <Select value={manualEntry.employeeId} onValueChange={(v) => setManualEntry({...manualEntry, employeeId: v})}>
                <SelectTrigger className="h-11 rounded-xl">
                  <SelectValue placeholder="Search Employee" />
                </SelectTrigger>
                <SelectContent>
                  {employeeOptions.map(emp => (
                    <SelectItem key={emp.id} value={emp.id}>{emp.name} ({emp.id})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Swipe Date</Label>
                <Input type="date" className="rounded-xl" value={manualEntry.date} onChange={(e) => setManualEntry({...manualEntry, date: e.target.value})} />
              </div>
              <div className="space-y-2">
                <Label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Swipe Time</Label>
                <Input type="time" step="1" className="rounded-xl" value={manualEntry.time} onChange={(e) => setManualEntry({...manualEntry, time: e.target.value})} />
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Direction</Label>
              <div className="flex gap-2">
                {["IN", "OUT"].map(type => (
                  <Button
                    key={type}
                    variant={manualEntry.type === type ? "default" : "outline"}
                    className={cn(
                      "flex-1 h-10 rounded-xl font-bold",
                      manualEntry.type === type && type === "IN" && "bg-emerald-600 hover:bg-emerald-700",
                      manualEntry.type === type && type === "OUT" && "bg-purple-600 hover:bg-purple-700"
                    )}
                    onClick={() => setManualEntry({...manualEntry, type})}
                  >
                    {type}
                  </Button>
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setShowManualEntryModal(false)} className="rounded-xl font-bold text-xs">CANCEL</Button>
            <Button 
              className="bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl px-8 font-bold text-xs"
              onClick={handleAddManualEntry}
            >
              SAVE SWIPE LOG
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* MANAGE DEVICES MODAL */}
      <Dialog open={showManageDevicesModal} onOpenChange={setShowManageDevicesModal}>
        <DialogContent className="sm:max-w-[600px] rounded-2xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold flex items-center gap-2">
              <Cpu className="w-5 h-5 text-indigo-500" /> Biometric Device Management
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4 max-h-[400px] overflow-y-auto no-scrollbar">
            {devices.map(device => (
              <div key={device.id} className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={cn(
                    "w-12 h-12 rounded-xl flex items-center justify-center border",
                    device.status === "Online" ? "bg-emerald-50 text-emerald-600 border-emerald-100" : "bg-red-50 text-red-600 border-red-100"
                  )}>
                    <Activity className="w-6 h-6" />
                  </div>
                  <div>
                    <h5 className="text-sm font-bold text-slate-900 dark:text-slate-100">{device.name}</h5>
                    <p className="text-[10px] text-slate-500 font-bold uppercase">{device.location} • {device.id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-[10px] font-bold text-slate-400 uppercase">Last Sync</p>
                    <p className="text-xs font-bold text-slate-700 dark:text-slate-300">{device.lastSyncTime}</p>
                  </div>
                  <Button variant="outline" size="sm" className="h-8 rounded-lg text-[10px] font-black">REBOOT</Button>
                </div>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button className="w-full bg-slate-900 dark:bg-white dark:text-slate-900 text-white rounded-xl h-11 font-bold">ADD NEW DEVICE</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* VIEW ALL ACTIVITY MODAL */}
      <Dialog open={showAllActivityModal} onOpenChange={setShowAllActivityModal}>
        <DialogContent className="sm:max-w-[500px] rounded-2xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold flex items-center gap-2">
              <History className="w-5 h-5 text-amber-500" /> System Activity Log
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4 max-h-[450px] overflow-y-auto no-scrollbar">
            {[1,2,3,4,5,6,7,8].map(i => (
              <div key={i} className="flex gap-4 p-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-xl transition-colors">
                <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
                  {i % 3 === 0 ? <AlertTriangle className="w-4 h-4 text-amber-500" /> : <RefreshCw className="w-4 h-4 text-emerald-500" />}
                </div>
                <div className="flex-1 space-y-1">
                  <p className="text-xs font-bold text-slate-800 dark:text-slate-200">
                    {i % 3 === 0 ? "Suspicious Activity Detected" : "Biometric Sync Completed"}
                  </p>
                  <p className="text-[10px] text-slate-500">
                    {i % 3 === 0 ? "Device BioMax-X990 flagged duplicate swipe attempt." : "Successfully imported 42 swipe logs from Pune Office."}
                  </p>
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">{i * 5} minutes ago</p>
                </div>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
