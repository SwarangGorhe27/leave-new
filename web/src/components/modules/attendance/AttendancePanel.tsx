import { useState, useMemo } from 'react';
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  List,
  Grid3X3,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Coffee,
  Palmtree,
  CalendarOff,
  Edit3,
} from 'lucide-react';
import { Badge, Tabs } from '@components/ui';
import { useAttendanceRecords, useUpcomingHolidays } from '@hooks/useAttendance';
import { useAdminAttendanceRecords } from '@hooks/useAdminAttendance';
import type { AttendanceRecordAPI, HolidayAPI } from '@hooks/useAttendance';
import type { AdminAttendanceRecord } from '@hooks/useAdminAttendance';
import { useUIStore } from '@store/uiStore';
import { AttendanceDetailSheet } from './AttendanceDetailSheet';
import { cn } from '@utils/utils';

/* ------------------------------------------------------------------ */
/*  Status config                                                      */
/* ------------------------------------------------------------------ */

const STATUS_CONFIG: Record<string, { label: string; short: string; color: string; bg: string; icon: React.ElementType }> = {
  PRESENT: { label: 'Present', short: 'P', color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-500/10', icon: CheckCircle2 },
  ABSENT: { label: 'Absent', short: 'A', color: 'text-red-600 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-500/10', icon: XCircle },
  HALF_DAY: { label: 'Half Day', short: 'HD', color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-500/10', icon: AlertTriangle },
  LEAVE: { label: 'Leave', short: 'L', color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-500/10', icon: Coffee },
  HOLIDAY: { label: 'Holiday', short: 'H', color: 'text-purple-600 dark:text-purple-400', bg: 'bg-purple-50 dark:bg-purple-500/10', icon: Palmtree },
  WEEK_OFF: { label: 'Week Off', short: 'WO', color: 'text-surface-400 dark:text-white/30', bg: 'bg-surface-100 dark:bg-white/5', icon: CalendarOff },
  ON_DUTY: { label: 'On Duty', short: 'OD', color: 'text-teal-600 dark:text-teal-400', bg: 'bg-teal-50 dark:bg-teal-500/10', icon: CheckCircle2 },
  NOT_COMPUTED: { label: '—', short: '—', color: 'text-surface-300 dark:text-white/20', bg: '', icon: CalendarOff },
};

function getStatusConfig(status: string) {
  return STATUS_CONFIG[status] ?? STATUS_CONFIG['NOT_COMPUTED'];
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function formatTime(dt: string | null): string {
  if (!dt) return '—';
  const d = new Date(dt);
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
}

function formatDuration(iso: string | null): string {
  if (!iso) return '—';
  // Could be HH:MM:SS or ISO duration
  const parts = iso.split(':');
  if (parts.length >= 2) {
    const h = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10);
    return `${h}h ${m}m`;
  }
  return iso;
}

const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/* ------------------------------------------------------------------ */
/*  Summary Stats Bar                                                  */
/* ------------------------------------------------------------------ */

function SummaryStats({ records }: { records: AttendanceRecordAPI[] }) {
  const stats = useMemo(() => {
    let present = 0, absent = 0, halfDay = 0, leave = 0, late = 0, weekOff = 0, holiday = 0;
    let totalEffSecs = 0, effCount = 0;
    for (const r of records) {
      switch (r.status) {
        case 'PRESENT': present++; break;
        case 'ABSENT': absent++; break;
        case 'HALF_DAY': halfDay++; break;
        case 'LEAVE': leave++; break;
        case 'WEEK_OFF': weekOff++; break;
        case 'HOLIDAY': holiday++; break;
      }
      if (r.late_mins > 0) late++;
      if (r.effective_hours) {
        const parts = r.effective_hours.split(':');
        if (parts.length >= 2) {
          totalEffSecs += parseInt(parts[0], 10) * 3600 + parseInt(parts[1], 10) * 60;
          effCount++;
        }
      }
    }
    const avgHrs = effCount > 0 ? (totalEffSecs / effCount / 3600).toFixed(1) : '—';
    return { present, absent, halfDay, leave, late, weekOff, holiday, avgHrs };
  }, [records]);

  const items = [
    { label: 'Present', value: stats.present, tone: 'text-emerald-600 dark:text-emerald-400' },
    { label: 'Absent', value: stats.absent, tone: 'text-red-600 dark:text-red-400' },
    { label: 'Half Day', value: stats.halfDay, tone: 'text-amber-600 dark:text-amber-400' },
    { label: 'Leave', value: stats.leave, tone: 'text-blue-600 dark:text-blue-400' },
    { label: 'Late', value: stats.late, tone: 'text-orange-600 dark:text-orange-400' },
    { label: 'Avg. Work Hrs', value: stats.avgHrs, tone: 'text-brand-600 dark:text-brand-400' },
    { label: 'Week Off', value: stats.weekOff, tone: 'text-surface-500 dark:text-white/40' },
    { label: 'Holiday', value: stats.holiday, tone: 'text-purple-600 dark:text-purple-400' },
  ];

  return (
    <div className="grid grid-cols-4 gap-3 lg:grid-cols-8">
      {items.map((s) => (
        <div key={s.label} className="surface-card rounded-xl border border-surface-100 p-3 text-center dark:border-white/5">
          <p className={cn('text-lg font-bold', s.tone)}>{s.value}</p>
          <p className="text-2xs text-surface-500 dark:text-white/40">{s.label}</p>
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Calendar View                                                      */
/* ------------------------------------------------------------------ */

function CalendarView({ records, month, year }: { records: AttendanceRecordAPI[]; month: number; year: number }) {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  const recordMap = useMemo(() => {
    const map: Record<string, AttendanceRecordAPI> = {};
    for (const r of records) map[r.date] = r;
    return map;
  }, [records]);

  const selectedRecord = selectedDate ? recordMap[selectedDate] : null;

  // Build calendar grid
  const firstDay = new Date(year, month - 1, 1);
  const startDayOfWeek = firstDay.getDay(); // 0=Sun
  const daysInMonth = new Date(year, month, 0).getDate();

  const cells: (number | null)[] = [];
  for (let i = 0; i < startDayOfWeek; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);

  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

  return (
    <div className="flex flex-col gap-4 lg:flex-row">
      {/* Calendar grid */}
      <div className="min-w-0 flex-1">
        <div className="hrms-reference-calendar grid grid-cols-7 gap-2 rounded-3xl border border-white/60 bg-white/60 p-4 shadow-sm backdrop-blur-[18px] dark:border-white/10 dark:bg-slate-900/70">
          {/* Day headers */}
          {DAY_NAMES.map((d) => (
            <div key={d} className="py-2 text-center text-[10px] font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-300">
              {d}
            </div>
          ))}
          {/* Day cells */}
          {cells.map((day, idx) => {
            if (day === null) {
              return <div key={`empty-${idx}`} className="h-24 rounded-2xl border border-slate-200/70 bg-white/35 dark:border-white/5 dark:bg-slate-950/20" />;
            }
            const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const rec = recordMap[dateStr];
            const sc = rec ? getStatusConfig(rec.status) : null;
            const isToday = dateStr === todayStr;
            const isSelected = dateStr === selectedDate;

            return (
              <button
                key={dateStr}
                type="button"
                onClick={() => setSelectedDate(isSelected ? null : dateStr)}
                className={cn(
                  'relative h-24 rounded-2xl border border-slate-200/70 bg-white/70 p-2.5 text-left shadow-[inset_0_1px_0_rgba(255,255,255,.72)] transition-all duration-200 ease-out hover:-translate-y-0.5 hover:bg-white dark:border-white/5 dark:bg-slate-950/30 dark:hover:bg-slate-800/55',
                  isSelected && 'border-brand-500/30 ring-1 ring-brand-500/20',
                )}
              >
                <span className={cn(
                  'absolute right-2 top-2 inline-flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold',
                  isToday ? 'bg-gradient-to-br from-indigo-500 to-blue-600 text-white shadow-[0_8px_18px_rgba(37,99,235,.24),0_0_0_7px_rgba(99,102,241,.10)]' : 'text-slate-500 dark:text-slate-200',
                )}>
                  {day}
                </span>
                {rec && rec.status !== 'NOT_COMPUTED' && (
                  <div className="mt-9 space-y-1">
                    <span className={cn('inline-flex rounded-full px-2 py-0.5 text-[9px] font-bold', sc?.color)}>{sc?.short}</span>
                    {rec.first_in && (
                      <p className="truncate text-[10px] text-slate-500 dark:text-slate-300">
                        {formatTime(rec.first_in)}
                      </p>
                    )}
                  </div>
                )}
                {rec && rec.late_mins > 0 && (
                  <div className="absolute bottom-2 left-1/2 h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-[#FACC15]" title={`Late ${rec.late_mins} min`} />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Side panel - selected day detail */}
      <div className="w-full lg:w-72">
        {selectedRecord ? (
          <DayDetail record={selectedRecord} />
        ) : (
          <div className="surface-card flex h-full flex-col items-center justify-center rounded-xl border border-surface-100 p-6 text-center dark:border-white/5">
            <Calendar className="h-8 w-8 text-surface-300 dark:text-white/20" />
            <p className="mt-2 text-sm text-surface-500 dark:text-white/40">Select a date to view details</p>
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Day Detail Panel                                                   */
/* ------------------------------------------------------------------ */

function DayDetail({ record }: { record: AttendanceRecordAPI }) {
  const sc = getStatusConfig(record.status);
  const StatusIcon = sc.icon;
  const d = new Date(record.date);
  const dayName = d.toLocaleDateString('en-IN', { weekday: 'long' });
  const dateStr = d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });

  return (
    <div className="surface-card rounded-xl border border-surface-100 p-4 dark:border-white/5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-surface-900 dark:text-white">{dateStr}</p>
          <p className="text-xs text-surface-500 dark:text-white/40">{dayName}</p>
        </div>
        <Badge variant={record.status === 'PRESENT' ? 'success' : record.status === 'ABSENT' ? 'danger' : record.status === 'LEAVE' ? 'info' : 'neutral'} size="sm" dot>
          <StatusIcon className="mr-1 h-3 w-3" />
          {sc.label}
        </Badge>
      </div>

      <div className="space-y-3">
        <DetailRow label="Shift" value={record.shift_name || '—'} />
        <DetailRow label="First In" value={formatTime(record.first_in)} />
        <DetailRow label="Last Out" value={formatTime(record.last_out)} />
        <DetailRow label="Effective Hours" value={formatDuration(record.effective_hours)} />
        {record.late_mins > 0 && (
          <DetailRow label="Late" value={`${record.late_mins} min`} warn />
        )}
        {record.early_leave_mins > 0 && (
          <DetailRow label="Early Leave" value={`${record.early_leave_mins} min`} warn />
        )}
        {record.overtime_mins > 0 && (
          <DetailRow label="Overtime" value={`${record.overtime_mins} min`} />
        )}
        {record.remarks && <DetailRow label="Remarks" value={record.remarks} />}
        {record.is_regularized && (
          <div className="flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="h-3 w-3" /> Regularized
          </div>
        )}
      </div>
    </div>
  );
}

function DetailRow({ label, value, warn }: { label: string; value: string; warn?: boolean }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-surface-500 dark:text-white/40">{label}</span>
      <span className={cn('text-sm font-medium', warn ? 'text-orange-600 dark:text-orange-400' : 'text-surface-900 dark:text-white')}>{value}</span>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  List View                                                          */
/* ------------------------------------------------------------------ */

function ListView({ records, adminRecords = [], onRowClick }: {
  records: AttendanceRecordAPI[];
  adminRecords?: AdminAttendanceRecord[];
  onRowClick?: (record: AttendanceRecordAPI) => void;
}) {
  const adminMap = useMemo(() => {
    const m: Record<string, AdminAttendanceRecord> = {};
    for (const r of adminRecords) m[r.id] = r;
    return m;
  }, [adminRecords]);
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-surface-200 text-left text-xs text-surface-500 dark:border-white/5 dark:text-white/40">
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">#</th>
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">Date</th>
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">Day</th>
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">In</th>
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">Out</th>
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">Shift</th>
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">Eff. Hours</th>
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">Late</th>
            <th className="whitespace-nowrap pb-3 pr-4 font-medium">OT</th>
            <th className="whitespace-nowrap pb-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-100 dark:divide-white/5">
          {records.map((r, idx) => {
            const sc = getStatusConfig(r.status);
            const isEdited = adminMap[r.id]?.is_admin_edited ?? false;
            return (
              <tr
                key={r.id}
                className={cn('hover:bg-surface-50 dark:hover:bg-white/[0.02]', onRowClick && 'cursor-pointer')}
                onClick={() => onRowClick?.(r)}
              >
                <td className="py-2.5 pr-4 text-surface-400 dark:text-white/30">{idx + 1}</td>
                <td className="whitespace-nowrap py-2.5 pr-4 font-medium text-surface-900 dark:text-white">
                  {new Date(r.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
                </td>
                <td className="py-2.5 pr-4 text-surface-600 dark:text-white/60">
                  {new Date(r.date).toLocaleDateString('en-IN', { weekday: 'short' })}
                </td>
                <td className="py-2.5 pr-4 text-surface-600 dark:text-white/60">{formatTime(r.first_in)}</td>
                <td className="py-2.5 pr-4 text-surface-600 dark:text-white/60">{formatTime(r.last_out)}</td>
                <td className="py-2.5 pr-4 text-surface-600 dark:text-white/60">{r.shift_name || '—'}</td>
                <td className="py-2.5 pr-4 font-medium text-surface-900 dark:text-white">{formatDuration(r.effective_hours)}</td>
                <td className="py-2.5 pr-4">
                  {r.late_mins > 0 ? (
                    <span className="text-orange-600 dark:text-orange-400">{r.late_mins}m</span>
                  ) : (
                    <span className="text-surface-300 dark:text-white/20">0</span>
                  )}
                </td>
                <td className="py-2.5 pr-4">
                  {r.overtime_mins > 0 ? (
                    <span className="text-teal-600 dark:text-teal-400">{r.overtime_mins}m</span>
                  ) : (
                    <span className="text-surface-300 dark:text-white/20">0</span>
                  )}
                </td>
                <td className="py-2.5">
                  <span className="flex items-center gap-1">
                    <span className={cn('inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold', sc.bg, sc.color)}>
                      {sc.short}
                    </span>
                    {isEdited && <Edit3 className="h-3 w-3 text-orange-500" />}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Holidays Sidebar                                                   */
/* ------------------------------------------------------------------ */

function HolidaysList({ holidays }: { holidays: HolidayAPI[] }) {
  if (holidays.length === 0) return null;
  return (
    <div className="surface-card rounded-xl border border-surface-100 p-4 dark:border-white/5">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-white/40">
        Upcoming Holidays
      </h3>
      <div className="space-y-2.5">
        {holidays.map((h) => (
          <div key={h.id} className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-purple-50 dark:bg-purple-500/10">
              <Palmtree className="h-3.5 w-3.5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-surface-900 dark:text-white">{h.name}</p>
              <p className="text-2xs text-surface-500 dark:text-white/40">
                {new Date(h.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', weekday: 'short' })}
                {' · '}{h.holiday_type}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Skeleton                                                           */
/* ------------------------------------------------------------------ */

function AttendanceSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="grid grid-cols-4 gap-3 lg:grid-cols-8">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="h-16 rounded-xl bg-surface-200 dark:bg-white/10" />
        ))}
      </div>
      <div className="h-96 rounded-xl bg-surface-200 dark:bg-white/10" />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main: Attendance Panel                                             */
/* ------------------------------------------------------------------ */

export function AttendancePanel() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [view, setView] = useState<'calendar' | 'list'>('calendar');
  const [selectedRecord, setSelectedRecord] = useState<AdminAttendanceRecord | null>(null);

  const activeModule = useUIStore((state) => state.activeModule);
  const portal = useUIStore((state) => state.portal);
  const rawModuleView = useUIStore((state) => state.moduleViews[activeModule] ?? 'admin');
  const moduleView = portal === 'ess' ? 'employee' : rawModuleView;
  const isAdmin = moduleView === 'admin';

  const { data: records = [], isLoading } = useAttendanceRecords(month, year);
  const { data: holidays = [] } = useUpcomingHolidays();
  const { data: adminRecords = [] } = useAdminAttendanceRecords(
    isAdmin ? {} : { _skip: 'true' }
  );

  const goPrev = () => {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else setMonth(month - 1);
  };
  const goNext = () => {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else setMonth(month + 1);
  };

  const tabItems = [
    {
      label: 'Attendance Info',
      value: 'info',
      content: (
        <div className="space-y-4 p-4">
          {/* Month nav + view toggle */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <button type="button" onClick={goPrev} className="rounded-lg border border-surface-200 p-1.5 hover:bg-surface-100 dark:border-white/10 dark:hover:bg-white/5">
                <ChevronLeft className="h-4 w-4" />
              </button>
              <h2 className="min-w-[140px] text-center text-base font-semibold text-surface-900 dark:text-white">
                {MONTH_NAMES[month - 1]} {year}
              </h2>
              <button type="button" onClick={goNext} className="rounded-lg border border-surface-200 p-1.5 hover:bg-surface-100 dark:border-white/10 dark:hover:bg-white/5">
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>

            <div className="flex items-center gap-1 rounded-lg border border-surface-200 p-0.5 dark:border-white/10">
              <button
                type="button"
                onClick={() => setView('calendar')}
                className={cn('rounded-md p-1.5 transition-colors', view === 'calendar' ? 'bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400' : 'text-surface-400 hover:text-surface-600 dark:text-white/30')}
                title="Calendar view"
              >
                <Grid3X3 className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={() => setView('list')}
                className={cn('rounded-md p-1.5 transition-colors', view === 'list' ? 'bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400' : 'text-surface-400 hover:text-surface-600 dark:text-white/30')}
                title="List view"
              >
                <List className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Summary */}
          <SummaryStats records={records} />

          {/* Main view */}
          {isLoading ? (
            <AttendanceSkeleton />
          ) : view === 'calendar' ? (
            <CalendarView records={records} month={month} year={year} />
          ) : (
            <ListView
              records={records}
              adminRecords={isAdmin ? adminRecords : []}
              onRowClick={isAdmin ? (row) => {
                const adminRec = adminRecords.find((r) => r.id === row.id) ?? {
                  ...(row as unknown as AdminAttendanceRecord),
                  is_admin_edited: false,
                  admin_edit_reason: '',
                  admin_edited_at: null,
                  original_first_in: null,
                  original_last_out: null,
                  original_status: '',
                  last_changed_by_source: 'BIOMETRIC',
                  regularization_ref: null,
                  employee_code: '',
                  employee_name: '',
                };
                setSelectedRecord(adminRec);
              } : undefined}
            />
          )}
        </div>
      ),
    },
    {
      label: 'Holidays',
      value: 'holidays',
      content: (
        <div className="p-4">
          <HolidaysList holidays={holidays} />
          {holidays.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Palmtree className="h-10 w-10 text-surface-300 dark:text-white/20" />
              <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No upcoming holidays.</p>
            </div>
          )}
        </div>
      ),
    },
  ];

  return (
    <>
      <Tabs items={tabItems} />
      {selectedRecord && (
        <AttendanceDetailSheet
          record={selectedRecord}
          onClose={() => setSelectedRecord(null)}
        />
      )}
    </>
  );
}
