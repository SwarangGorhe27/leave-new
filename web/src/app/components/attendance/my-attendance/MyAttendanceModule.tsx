import { useState, useMemo, useEffect } from "react";
import { isSameMonth, parseISO } from "date-fns";
import { SummaryCards } from "./SummaryCards";
import { Filters } from "./Filters";
import { CalendarView } from "./CalendarView";
import { ListView } from "./ListView";
import { RegularizationTab } from "./RegularizationTab";
import { RegularizationHistoryTab } from "./RegularizationHistoryTab";
import { SwipeDetailsDrawer } from "./SwipeDetailsDrawer";
import { AttendanceCharts } from "./AttendanceCharts";
import { Legend } from "./Legend";
import { calculateMetrics, AttendanceMetrics } from "./utils";
import { AttendanceRequest, DailyAttendance } from "../../../modules/attendance/types";
import { attendanceDataset } from "../../../modules/attendance/store";
import { motion, AnimatePresence } from "motion/react";
import type { PunchDetailsResponse, RegularizationBulkPayload } from "../../../../api/employeeAttendanceClient";
 
interface MyAttendanceModuleProps {
  employeeId: string;
  title?: string;
  subtitle?: string;
  readOnly?: boolean;
  showTitle?: boolean;
  /** When set, uses API-backed records instead of the local mock dataset. */
  externalRecords?: DailyAttendance[];
  externalRegularizationRequests?: AttendanceRequest[];
  externalMetrics?: AttendanceMetrics;
  externalLoading?: boolean;
  externalError?: string | null;
  onPeriodChange?: (date: Date) => void;
  onFetchPunchDetails?: (date: string) => Promise<PunchDetailsResponse>;
  onSubmitRegularization?: (payload: RegularizationBulkPayload) => Promise<void>;
}
 
export function MyAttendanceModule({
  employeeId,
  title = "My Attendance",
  subtitle = "Track your work hours, presence, and punctuality insights.",
  readOnly = false,
  showTitle = true,
  externalRecords,
  externalRegularizationRequests,
  externalMetrics,
  externalLoading = false,
  externalError = null,
  onPeriodChange,
  onFetchPunchDetails,
  onSubmitRegularization,
}: MyAttendanceModuleProps) {
  const [view, setView] = useState<"calendar" | "list" | "regularization" | "regularization-history">("calendar");
  const [currentDate, setCurrentDate] = useState(() =>
    externalRecords !== undefined ? new Date() : new Date(2026, 4, 1),
  );
  const [searchTerm, setSearchTerm] = useState("");
 
  const [isSwipeOpen, setIsSwipeOpen] = useState(false);
  const [selectedDateForRegularize, setSelectedDateForRegularize] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<DailyAttendance | null>(null);

  useEffect(() => {
    onPeriodChange?.(currentDate);
  }, [currentDate, onPeriodChange]);

  const usesExternalData = externalRecords !== undefined;

  // Filter records for the current employee and selected month
  const employeeRecords = useMemo(() => {
    let records = usesExternalData
      ? (externalRecords ?? [])
      : attendanceDataset.records.filter(r => r.employeeId === employeeId);

    // Filter by month/year unless in regularization/history tab where we might need historical data
    if (view !== "regularization" && view !== "regularization-history") {
      records = records.filter(r => isSameMonth(parseISO(r.date), currentDate));
    }
 
    // Apply search filter
    if (searchTerm.trim()) {
      const s = searchTerm.toLowerCase();
      records = records.filter(r =>
        r.date.toLowerCase().includes(s) ||
        r.status.toLowerCase().includes(s) ||
        (r.shiftName && r.shiftName.toLowerCase().includes(s)) ||
        (r.workMode && r.workMode.toLowerCase().includes(s)) ||
        (r.exceptionType && r.exceptionType.toLowerCase().includes(s))
      );
    }
 
    return records;
  }, [employeeId, currentDate, searchTerm, view, usesExternalData, externalRecords]);
 
  const metrics = useMemo(
    () => externalMetrics ?? calculateMetrics(employeeRecords),
    [externalMetrics, employeeRecords],
  );
 
  const handleRegularize = (date: string) => {
    setSelectedDateForRegularize(date);
    setView("regularization");
  };
 
  const handleSwipeDetails = (record: DailyAttendance) => {
    setSelectedRecord(record);
    setIsSwipeOpen(true);
  };
 
  return (
    <div className="attendance-workspace space-y-7 pb-12">
 
      {externalError ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300">
          {externalError}
        </div>
      ) : null}
 
      {externalLoading ? (
        <div className="attendance-empty flex min-h-[120px] items-center justify-center text-sm text-muted-foreground">
          Loading attendance…
        </div>
      ) : null}
 
       {/* Filters & View Switcher */}
      <div className="sticky top-4 z-50 attendance-sticky-tools">
        <Filters
          view={view}
          onViewChange={(newView) => {
            setView(newView);
            if (newView !== "regularization" && newView !== "regularization-history") setSelectedDateForRegularize(null);
          }}
          currentDate={currentDate}
          onDateChange={setCurrentDate}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
        />
      </div>
 
 
      {/* Summary Cards */}
      <SummaryCards metrics={metrics} />
 
     
      {/* Main Content Area */}
      <div className="relative">
        <AnimatePresence mode="wait">
          {externalLoading ? null : employeeRecords.length > 0 || view === "regularization" || view === "regularization-history" ? (
            <motion.div
              key={view + currentDate.getTime()}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {view === "calendar" ? (
                <div className="grid grid-cols-1 lg:grid-cols-[65%_35%] gap-6 items-start">
                  <div className="w-full">
                    <CalendarView
                      records={employeeRecords}
                      currentDate={currentDate}
                      searchTerm={searchTerm}
                      onRegularize={handleRegularize}
                      onSwipeDetails={handleSwipeDetails}
                    />
                  </div>
                  <div className="w-full lg:sticky lg:top-[90px] space-y-6">
                    <div className="flex items-center gap-3">
                      <div className="attendance-section-icon p-2 bg-[#6366F1]/10 rounded-2xl shadow-sm">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M3 3v18h18" />
                          <path d="m19 9-5 5-4-4-3 3" />
                        </svg>
                      </div>
                      <h2 className="text-lg font-semibold text-foreground tracking-tight">Performance Analytics</h2>
                    </div>
                    <AttendanceCharts records={employeeRecords} />
                  </div>
                </div>
              ) : view === "list" ? (
                <ListView
                  records={employeeRecords}
                  onSwipeDetails={handleSwipeDetails}
                  onRegularize={handleRegularize}
                  readOnly={readOnly}
                />
              ) : view === "regularization" ? (
                <RegularizationTab
                  records={usesExternalData ? employeeRecords : attendanceDataset.records.filter(r => r.employeeId === employeeId)}
                  initialDate={selectedDateForRegularize}
                  readOnly={readOnly}
                  onSubmitRegularization={onSubmitRegularization}
                />
              ) : (
                <RegularizationHistoryTab
                  requests={externalRegularizationRequests ?? attendanceDataset.requests}
                  employeeId={employeeId}
                />
              )}
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
                className="attendance-empty flex flex-col items-center justify-center py-20"
            >
              <div className="w-24 h-24 rounded-[2rem] flex items-center justify-center mb-4 attendance-empty-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
                  <rect x="3" y="4" width="18" height="16" rx="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-foreground">No attendance records found</h3>
              <p className="text-sm text-muted-foreground mt-1 text-center max-w-md">
                We couldn't find any attendance logs for the selected period. Please try adjusting your filters or contact HR if you believe this is an error.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
 
      {/* Legend */}
      {view !== "regularization" && <Legend />}

      {/* Analytics & Trends Section */}
      {view !== "regularization" && view !== "calendar" && (
        <div className="attendance-analytics pt-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="attendance-section-icon p-2.5 rounded-2xl shadow-sm">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18" /><path d="m19 9-5 5-4-4-3 3" /></svg>
            </div>
            <h2 className="text-2xl font-semibold text-foreground tracking-tight">Performance Analytics</h2>
          </div>
          <AttendanceCharts records={employeeRecords} />
        </div>
      )}
 
      {/* Modals & Drawers */}
      {/* AI Insights modal removed */}
      <SwipeDetailsDrawer
        isOpen={isSwipeOpen}
        onOpenChange={setIsSwipeOpen}
        record={selectedRecord}
        onFetchPunchDetails={onFetchPunchDetails}
      />
    </div>
  );
}