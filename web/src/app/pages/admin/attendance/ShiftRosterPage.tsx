import { useState, useMemo, useEffect } from "react";
import { 
  Download, 
  Plus, 
  RotateCw, 
  CheckCircle, 
  RefreshCw, 
  Home, 
  ChevronRight,
  Info,
  Calendar as CalendarIcon,
  Search,
  Check,
  AlertTriangle
} from "lucide-react";
import { Button } from "../../../components/ui/button";
import {
  useRosterCalendar,
  usePublishRoster,
  useShiftDefinitions,
  resolveRosterShiftDefinitions,
  useBulkShiftAssignment,
  useCreateShiftAssignment,
  useUnpublishRoster,
  useExportRoster,
  useMatrixCycleBounds,
} from "../../../modules/attendance/hooks";
import { AlertCircle, Loader2 } from "lucide-react";
import { cn } from "../../../components/ui/utils";
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isWeekend, addMonths, subMonths, isWithinInterval, parseISO } from "date-fns";
import { RosterFilterBar } from "../../../components/attendance/roster/RosterFilterBar";
import { RosterAnalytics } from "../../../components/attendance/roster/RosterAnalytics";
import { RosterGrid } from "../../../components/attendance/roster/RosterGrid";
import { RosterLegend } from "../../../components/attendance/roster/RosterLegend";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "../../../components/ui/dialog";
import { Label } from "../../../components/ui/label";
import { Input } from "../../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Checkbox } from "../../../components/ui/checkbox";
import { toast } from "sonner";
import { RosterRecord, ShiftDefinition } from "../../../modules/attendance/types";
import type { RosterCalendarApi } from "../../../modules/attendance/apiTypes";

export function ShiftRosterPage() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const month = selectedDate.getMonth() + 1;
  const year = selectedDate.getFullYear();
  const [filters, setFilters] = useState({
    search: "",
    department: "all",
    designation: "all",
    team: "all",
    location: "all",
    shift: "all",
    workMode: "all",
  });
  const deptId = filters.department !== "all" ? filters.department : undefined;
  const { data: rosterQuery, isLoading: rosterLoading, isError: rosterError, error: rosterErr, refetch: refetchRoster } =
    useRosterCalendar(month, year, deptId);
  const rosterMeta = rosterQuery?.meta as RosterCalendarApi | undefined;
  const { data: fallbackShiftDefinitions = [] } = useShiftDefinitions(month, year, {
    enabled: !rosterMeta?.shift_options?.length,
  });
  const shiftDefinitions = useMemo(
    () => resolveRosterShiftDefinitions(rosterMeta, fallbackShiftDefinitions),
    [rosterMeta, fallbackShiftDefinitions],
  );

  /** Legend options for cell picker (includes Week Off), same list as roster legend. */
  const rosterPickerShifts = useMemo((): ShiftDefinition[] => {
    const hasOff = shiftDefinitions.some(
      (s) => s.code === "OFF" || s.name.toLowerCase().includes("week off"),
    );
    if (hasOff) return shiftDefinitions;
    const weekOff: ShiftDefinition = {
      id: "__week_off__",
      code: "OFF",
      name: "Week Off",
      startTime: "00:00",
      endTime: "00:00",
      color: "bg-slate-200",
      type: "General",
    };
    return [...shiftDefinitions, weekOff];
  }, [shiftDefinitions]);
  const { data: cycleBounds } = useMatrixCycleBounds(year, month);
  const publishRosterMutation = usePublishRoster();
  const unpublishRosterMutation = useUnpublishRoster();
  const bulkAssignMutation = useBulkShiftAssignment();
  const createShiftAssignment = useCreateShiftAssignment();
  const exportRosterMutation = useExportRoster();
  const [rosterData, setRosterData] = useState<RosterRecord[]>([]);

  const cycleId =
    (rosterQuery?.meta as { cycle_id?: string } | undefined)?.cycle_id ??
    (cycleBounds as { cycle_id?: string } | undefined)?.cycle_id;

  useEffect(() => {
    if (rosterQuery?.records) setRosterData(rosterQuery.records);
    if (rosterQuery?.meta) {
      const meta = rosterQuery.meta as { is_published?: boolean; is_locked?: boolean };
      setPublishStatus({
        isPublished: !!meta.is_published,
        timestamp: new Date().toISOString(),
        publishedBy: "Admin",
      });
    }
  }, [rosterQuery]);
  // UI States
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [isBulkAssigning, setIsBulkAssigning] = useState(false);

  // Modal States
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showBulkAssignModal, setShowBulkAssignModal] = useState(false);
  const [showPublishModal, setShowPublishModal] = useState(false);

  // Bulk Assign Form State
  const [bulkAssignForm, setBulkAssignForm] = useState({
    employeeIds: [] as string[],
    startDate: format(new Date(2026, 4, 1), "yyyy-MM-dd"),
    endDate: format(new Date(2026, 4, 31), "yyyy-MM-dd"),
    shiftCode: "GEN",
    note: ""
  });

  // Publish Status
  const [publishStatus, setPublishStatus] = useState<{
    isPublished: boolean;
    timestamp?: string;
    publishedBy?: string;
  }>({ isPublished: false });

  const monthStart = startOfMonth(selectedDate);
  const monthEnd = endOfMonth(selectedDate);
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refetchRoster();
    setTimeout(() => {
      setIsRefreshing(false);
      toast.success("Roster data refreshed");
    }, 800);
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const blob = await exportRosterMutation.mutateAsync({
        month,
        year,
        format: 'csv',
        department_id: deptId,
      });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `Shift_Roster_${format(selectedDate, 'MMMM_yyyy')}.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
      toast.success('Export successful! Download started.');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  // GENERATE ROSTER FUNCTIONALITY
  const handleGenerateRoster = () => {
    setIsGenerating(true);
    setTimeout(() => {
      const newRoster = rosterData.map(record => {
        const newShifts = { ...record.shifts };
        let working = 0;
        let off = 0;

        days.forEach(day => {
          const dateStr = format(day, "yyyy-MM-dd");
          if (isWeekend(day)) {
            newShifts[dateStr] = "OFF";
            off++;
          } else {
            // Simple logic: Rotate shifts if rotational
            const rand = Math.random();
            if (rand > 0.8) newShifts[dateStr] = "NS";
            else if (rand > 0.7) newShifts[dateStr] = "FS";
            else {
              newShifts[dateStr] = "GEN";
              working++;
            }
          }
        });

        return { ...record, shifts: newShifts, workingDays: working, weekOffs: off };
      });

      setRosterData(newRoster);
      setIsGenerating(false);
      setShowGenerateModal(false);
      toast.success(`Roster generated for ${format(selectedDate, "MMMM yyyy")}`);
    }, 2000);
  };

  // BULK ASSIGN FUNCTIONALITY
  const handleBulkAssign = async () => {
    const { employeeIds, startDate, endDate, shiftCode } = bulkAssignForm;
    const shiftDef = shiftDefinitions.find((s) => s.code === shiftCode);
    if (!shiftDef?.id) {
      toast.error("Select a valid shift from the roster");
      return;
    }
    const targets =
      employeeIds.length > 0
        ? rosterData.filter((r) => employeeIds.includes(r.employeeId))
        : rosterData;
    if (targets.length === 0) {
      toast.error("No employees selected for bulk assignment");
      return;
    }

    setIsBulkAssigning(true);
    try {
      if (cycleId) {
        await bulkAssignMutation.mutateAsync({
          assignment_type: "date_range",
          cycle_id: cycleId,
          date_from: startDate,
          date_to: endDate,
          assignments: targets.map((r) => ({
            employee_id: r.employeeId,
            shift_id: shiftDef.id,
            is_week_off: shiftCode === "OFF",
          })),
        });
        await refetchRoster();
        toast.success(`Bulk assignment queued for ${targets.length} employees`);
      } else {
        const start = parseISO(startDate);
        const end = parseISO(endDate);
        const newRoster = rosterData.map((record) => {
          if (employeeIds.length === 0 || employeeIds.includes(record.employeeId)) {
            const newShifts = { ...record.shifts };
            days.forEach((day) => {
              if (isWithinInterval(day, { start, end })) {
                newShifts[format(day, "yyyy-MM-dd")] =
                  shiftCode === "OFF" ? "OFF" : (shiftDef?.name ?? shiftCode);
              }
            });
            let working = 0;
            let off = 0;
            Object.values(newShifts).forEach((s) => {
              if (s === "OFF") off++;
              else if (s !== "HL") working++;
            });
            return { ...record, shifts: newShifts, workingDays: working, weekOffs: off };
          }
          return record;
        });
        setRosterData(newRoster);
        toast.success(`Bulk assignment applied locally for ${targets.length} employees`);
      }
      setShowBulkAssignModal(false);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Bulk assignment failed");
    } finally {
      setIsBulkAssigning(false);
    }
  };

  // PUBLISH SCHEDULE FUNCTIONALITY
  const handlePublish = async () => {
    setIsPublishing(true);
    try {
      await publishRosterMutation.mutateAsync({
        start_date: format(monthStart, "yyyy-MM-dd"),
        end_date: format(monthEnd, "yyyy-MM-dd"),
        company_wide: true,
      });
      setPublishStatus({
        isPublished: true,
        timestamp: new Date().toISOString(),
        publishedBy: "Admin User",
      });
      setShowPublishModal(false);
      toast.success("Shift roster published successfully!");
      refetchRoster();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Publish failed");
    } finally {
      setIsPublishing(false);
    }
  };

  const handleUpdateShift = async (employeeId: string, date: string, shiftCode: string) => {
    const isWeekOff = shiftCode === "OFF";
    const shiftDef = isWeekOff
      ? shiftDefinitions.find((s) => s.code !== "OFF") ?? shiftDefinitions[0]
      : shiftDefinitions.find((s) => s.code === shiftCode);

    if (!shiftDef?.id || shiftDef.id.startsWith("__")) {
      toast.error("Select a valid shift");
      return;
    }
    if (!cycleId) {
      toast.error("Attendance cycle not configured for this month");
      return;
    }

    const displayName = isWeekOff
      ? "OFF"
      : (rosterPickerShifts.find((s) => s.code === shiftCode)?.name ?? shiftCode);

    setRosterData((prev) =>
      prev.map((row) => {
        if (row.employeeId !== employeeId) return row;
        const shifts = { ...row.shifts, [date]: displayName };
        let working = 0;
        let off = 0;
        Object.values(shifts).forEach((v) => {
          if (v === "OFF" || v === "Week Off") off++;
          else if (v) working++;
        });
        return { ...row, shifts, workingDays: working, weekOffs: off };
      }),
    );

    try {
      await createShiftAssignment.mutateAsync({
        employee_id: employeeId,
        shift_id: shiftDef.id,
        roster_date: date,
        cycle_id: cycleId,
        is_week_off: isWeekOff,
      });
      await refetchRoster();
      toast.success(`Updated to ${displayName}`);
    } catch (e) {
      await refetchRoster();
      toast.error(e instanceof Error ? e.message : "Failed to update shift");
    }
  };

  const filteredRoster = useMemo(() => {
    return rosterData.filter(record => {
      const matchesSearch = !filters.search || 
        record.employeeName.toLowerCase().includes(filters.search.toLowerCase()) ||
        record.employeeCode.toLowerCase().includes(filters.search.toLowerCase());
      
      const matchesDept = filters.department === "all" || record.department === filters.department;
      const matchesDesig = filters.designation === "all" || record.designation === filters.designation;
      const matchesTeam = filters.team === "all" || record.team === filters.team;

      return matchesSearch && matchesDept && matchesDesig && matchesTeam;
    });
  }, [filters, rosterData]);

  const analyticsData = useMemo(() => {
    const totalEmployees = filteredRoster.length;
    let totalWorking = 0;
    let totalOff = 0;
    let nightShift = 0;
    let rotational = 0;
    let flexible = 0;

    filteredRoster.forEach(r => {
      totalWorking += r.workingDays;
      totalOff += r.weekOffs;
      
      const uniqueShifts = new Set(Object.values(r.shifts));
      if (uniqueShifts.has("NS")) nightShift++;
      if (uniqueShifts.has("FS") || uniqueShifts.has("SS")) rotational++;
      if (uniqueShifts.has("WFH")) flexible++;
    });

    return {
      totalEmployees,
      totalWorkingDays: totalWorking,
      totalWeekOffs: totalOff,
      nightShiftEmployees: nightShift,
      rotationalShiftEmployees: rotational,
      flexibleShiftEmployees: flexible
    };
  }, [filteredRoster]);

  return (
    <div className="flex flex-col h-full bg-[#f8fafc] dark:bg-slate-950/50 relative overflow-hidden">
      {rosterError && (
        <div className="mx-6 mt-4 flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {rosterErr instanceof Error ? rosterErr.message : "Failed to load shift roster."}
        </div>
      )}
      {rosterLoading && (
        <div className="mx-6 mt-4 flex items-center gap-2 text-slate-500 text-sm">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading roster…
        </div>
      )}
      {/* Top Header */}
      <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 py-3 shadow-sm sticky top-0 z-40">
        <div className="flex items-center justify-between gap-4">
          {/* Left: status badge */}
          <div className="flex items-center gap-2">
            {publishStatus.isPublished ? (
              <div className="px-1.5 py-0.5 rounded text-[9px] bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-500/20 font-bold uppercase flex items-center gap-1">
                <Check className="w-2.5 h-2.5" /> Published
              </div>
            ) : (
              <div className="px-1.5 py-0.5 rounded text-[9px] bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-100 dark:border-amber-500/20 font-bold uppercase">
                Draft
              </div>
            )}
          </div>

          {/* Right: action buttons */}
          <div className="flex items-center gap-2 shrink-0">
            <Button 
              variant="outline" 
              size="sm" 
              className="h-8 gap-1.5 font-bold text-[10px] px-3 rounded-lg border-slate-200 dark:border-slate-800"
              onClick={handleExport}
              disabled={isExporting}
            >
              <Download className={cn("w-3 h-3 text-blue-500", isExporting && "animate-bounce")} /> 
              {isExporting ? "EXPORTING..." : "EXPORT"}
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              className="h-8 gap-1.5 font-bold text-[10px] px-3 rounded-lg border-slate-200 dark:border-slate-800"
              onClick={() => setShowGenerateModal(true)}
            >
              <RotateCw className="w-3 h-3 text-indigo-500" /> GENERATE
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              className="h-8 gap-1.5 font-bold text-[10px] px-3 rounded-lg border-slate-200 dark:border-slate-800"
              onClick={() => setShowBulkAssignModal(true)}
            >
              <Plus className="w-3 h-3 text-emerald-500" /> BULK ASSIGN
            </Button>
            <Button 
              className="h-8 gap-1.5 font-bold text-[10px] px-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/20"
              onClick={() => setShowPublishModal(true)}
              disabled={publishStatus.isPublished}
            >
              <CheckCircle className="w-3 h-3" /> {publishStatus.isPublished ? "PUBLISHED" : "PUBLISH"}
            </Button>
            <Button 
              variant="outline" 
              size="icon" 
              className="h-8 w-8 rounded-lg border-slate-200 dark:border-slate-800"
              onClick={handleRefresh}
            >
              <RefreshCw className={cn("w-3 h-3 text-slate-500", isRefreshing && "animate-spin text-emerald-500")} />
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto no-scrollbar scroll-smooth">
        {/* Correctly Aligned Sticky Filter Bar */}
        <RosterFilterBar 
          filters={filters} 
          setFilters={setFilters} 
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
        />

        <div className="p-4 space-y-4 max-w-[1600px] mx-auto w-full">
          {/* Analytics Section */}
          <RosterAnalytics data={analyticsData} />

          {/* Conflict Warning or Status Info */}
          {publishStatus.isPublished ? (
            <div className="bg-emerald-50 dark:bg-emerald-500/5 border border-emerald-200/50 dark:border-emerald-500/20 p-2.5 rounded-xl flex items-center gap-3">
              <div className="w-7 h-7 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <Check className="w-3.5 h-3.5 text-emerald-600" />
              </div>
              <div className="flex-1">
                <p className="text-[10px] font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider">Schedule Live</p>
                <p className="text-[10px] text-emerald-700 dark:text-emerald-500 font-medium">
                  This roster was published by {publishStatus.publishedBy} on {format(parseISO(publishStatus.timestamp!), "dd MMM yyyy, hh:mm a")}.
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-[10px] font-bold text-emerald-600 hover:bg-emerald-500/10"
                onClick={async () => {
                  try {
                    await unpublishRosterMutation.mutateAsync({
                      start_date: format(monthStart, 'yyyy-MM-dd'),
                      end_date: format(monthEnd, 'yyyy-MM-dd'),
                    });
                    setPublishStatus({ isPublished: false });
                    refetchRoster();
                    toast.success('Roster unpublished');
                  } catch (e) {
                    toast.error(e instanceof Error ? e.message : 'Unpublish failed');
                  }
                }}
              >
                UNPUBLISH TO EDIT
              </Button>
            </div>
          ) : (
            <div className="bg-amber-50 dark:bg-amber-500/5 border border-amber-200/50 dark:border-amber-500/20 p-2.5 rounded-xl flex items-center gap-3">
              <div className="w-7 h-7 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Info className="w-3.5 h-3.5 text-amber-600" />
              </div>
              <div className="flex-1">
                <p className="text-[10px] font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wider">Draft Mode</p>
                <p className="text-[10px] text-amber-700 dark:text-amber-500 font-medium">Changes are saved as draft. Click Publish to make them visible to employees.</p>
              </div>
            </div>
          )}

          {/* Main Roster Grid */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
            <RosterGrid 
              roster={filteredRoster} 
              days={days} 
              shiftDefinitions={rosterPickerShifts} 
              isPublished={publishStatus.isPublished}
              onUpdateShift={handleUpdateShift}
            />
          </div>

          {/* Legend Section */}
          <RosterLegend shiftDefinitions={shiftDefinitions} />
        </div>
      </div>

      {/* GENERATE ROSTER MODAL */}
      <Dialog open={showGenerateModal} onOpenChange={setShowGenerateModal}>
        <DialogContent className="sm:max-w-[450px] rounded-2xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold flex items-center gap-2">
              <RotateCw className="w-4 h-4 text-indigo-500" /> Generate Shift Roster
            </DialogTitle>
            <DialogDescription className="text-xs text-slate-500">
              Auto-generate shifts for the selected criteria using organizational rotation rules.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-3 py-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Month</Label>
                <Select defaultValue="5">
                  <SelectTrigger className="h-8 rounded-lg text-xs">
                    <SelectValue placeholder="Select Month" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5" className="text-xs">May</SelectItem>
                    <SelectItem value="6" className="text-xs">June</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Year</Label>
                <Select defaultValue="2026">
                  <SelectTrigger className="h-8 rounded-lg text-xs">
                    <SelectValue placeholder="Select Year" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="2026" className="text-xs">2026</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Rotation Type</Label>
              <Select defaultValue="weekly">
                <SelectTrigger className="h-8 rounded-lg text-xs">
                  <SelectValue placeholder="Select Rotation" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="weekly" className="text-xs">Weekly Rotation</SelectItem>
                  <SelectItem value="monthly" className="text-xs">Monthly Rotation</SelectItem>
                  <SelectItem value="cyclic" className="text-xs">Cyclic (Custom)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Shift Pattern</Label>
              <Select defaultValue="gen-off">
                <SelectTrigger className="h-8 rounded-lg text-xs">
                  <SelectValue placeholder="Select Pattern" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gen-off" className="text-xs">5 Days GEN + 2 OFF</SelectItem>
                  <SelectItem value="rotational" className="text-xs">FS → SS → NS Rotation</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setShowGenerateModal(false)} className="rounded-lg h-8 font-bold text-xs">CANCEL</Button>
            <Button 
              className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg h-8 px-6 font-bold text-xs"
              onClick={handleGenerateRoster}
              disabled={isGenerating}
            >
              {isGenerating ? "GENERATING..." : "GENERATE ROSTER"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* BULK ASSIGN MODAL */}
      <Dialog open={showBulkAssignModal} onOpenChange={setShowBulkAssignModal}>
        <DialogContent className="sm:max-w-[500px] rounded-2xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold flex items-center gap-2">
              <Plus className="w-4 h-4 text-emerald-500" /> Bulk Assign Shifts
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-3">
            <div className="space-y-1.5">
              <Label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest px-1">Selected Employees</Label>
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800 text-[11px] font-bold text-slate-600 dark:text-slate-400">
                {bulkAssignForm.employeeIds.length === 0 ? "All Filtered Employees (10)" : `${bulkAssignForm.employeeIds.length} Employees Selected`}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest px-1">Start Date</Label>
                <Input 
                  type="date" 
                  className="rounded-lg h-8 text-xs" 
                  value={bulkAssignForm.startDate}
                  onChange={(e) => setBulkAssignForm({...bulkAssignForm, startDate: e.target.value})}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest px-1">End Date</Label>
                <Input 
                  type="date" 
                  className="rounded-lg h-8 text-xs" 
                  value={bulkAssignForm.endDate}
                  onChange={(e) => setBulkAssignForm({...bulkAssignForm, endDate: e.target.value})}
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest px-1">Shift to Assign</Label>
              <Select value={bulkAssignForm.shiftCode} onValueChange={(v) => setBulkAssignForm({...bulkAssignForm, shiftCode: v})}>
                <SelectTrigger className="h-8 rounded-lg text-xs bg-slate-50 dark:bg-slate-800/50">
                  <SelectValue placeholder="Select Shift" />
                </SelectTrigger>
                <SelectContent>
                  {shiftDefinitions.map(s => (
                    <SelectItem key={s.id} value={s.code} className="text-xs">{s.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter className="gap-2">
            <Button variant="ghost" onClick={() => setShowBulkAssignModal(false)} className="rounded-lg h-8 font-bold text-xs">CANCEL</Button>
            <Button 
              className="bg-emerald-600 hover:bg-emerald-700 text-white h-8 rounded-lg px-8 font-bold text-xs"
              onClick={handleBulkAssign}
              disabled={isBulkAssigning}
            >
              {isBulkAssigning ? "ASSIGNING..." : "APPLY SHIFTS"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* PUBLISH CONFIRMATION MODAL */}
      <Dialog open={showPublishModal} onOpenChange={setShowPublishModal}>
        <DialogContent className="sm:max-w-[400px] rounded-2xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-2xl">
          <div className="flex flex-col items-center text-center p-3 space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-500/10 flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-emerald-600" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Publish Roster Schedule?</h3>
              <p className="text-xs text-slate-500">
                Are you sure you want to publish this roster? Once published, employees can see their schedules and rows will be locked for editing.
              </p>
            </div>
            <div className="w-full flex flex-col gap-2 pt-3">
              <Button 
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg h-9 font-bold shadow-lg shadow-emerald-500/20 text-xs"
                onClick={handlePublish}
                disabled={isPublishing}
              >
                {isPublishing ? "PUBLISHING..." : "YES, PUBLISH SCHEDULE"}
              </Button>
              <Button 
                variant="ghost" 
                className="w-full h-9 rounded-lg text-slate-500 font-bold text-xs"
                onClick={() => setShowPublishModal(false)}
              >
                BACK TO DRAFT
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
