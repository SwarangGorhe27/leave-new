
​import { useState, useMemo } from 'react';
import {
  CalendarDays,
  CheckCircle2,
  Clock,
  FileText,
  Palmtree,
  PieChart,
  Send,
  ShieldCheck,
  UserCheck,
  XCircle,
} from 'lucide-react';
import { Badge, Tabs } from '@components/ui';
import {
  useMyLeaveBalances,
  useMyLeaveApplications,
  useUpcomingHolidays,
  useLeaveTypes,
  useApplyLeave,
} from '@hooks/useLeave';
import {
  useAllLeaveApplications,
  useApproveLeave,
  useRejectLeave,
} from '../../../app/modules/leaves/useLeaves';
import type {
  LeaveBalanceAPI,
  LeaveApplicationAPI,
  HolidayAPI,
} from '@hooks/useLeave';
import type {
  LeaveApplicationAPI as AdminLeaveApplicationAPI,
} from '../../../app/modules/leaves/types';
import { useUIStore } from '@store/uiStore';
import { cn } from '@utils/utils';

/* ------------------------------------------------------------------ */
/*  Status badges                                                      */
/* ------------------------------------------------------------------ */

const STATUS_VARIANT: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
  APPROVED: 'success',
  SUBMITTED: 'warning',
  DRAFT: 'neutral',
  REJECTED: 'danger',
  CANCELLED: 'neutral',
  REVOKED: 'danger',
};

const LEAVE_COLORS: Record<string, string> = {
  CL: 'from-blue-500 to-blue-600',
  EL: 'from-emerald-500 to-emerald-600',
  SL: 'from-amber-500 to-amber-600',
  LOP: 'from-red-500 to-red-600',
  ML: 'from-pink-500 to-pink-600',
  PL: 'from-violet-500 to-violet-600',
};

function getLeaveColor(code: string) {
  return LEAVE_COLORS[code] ?? 'from-surface-500 to-surface-600';
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatShortDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
}

function getLeaveCode(detail?: { code?: string | null; name?: string | null }, rawName?: string | null) {
  const c = detail?.code?.trim();
  if (c) return c.toUpperCase();
  const n = detail?.name?.trim() || rawName?.trim();
  if (n) return n.split(' ').map((s) => s[0]).join('').slice(0, 2).toUpperCase();
  return 'L';
}

function getLeaveName(detail?: { name?: string | null }) {
  return detail?.name ?? 'Leave';
}

/* ------------------------------------------------------------------ */
/*  Balance Cards                                                      */
/* ------------------------------------------------------------------ */

function BalanceCards({ balances }: { balances: LeaveBalanceAPI[] }) {
  if (balances.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <PieChart className="h-10 w-10 text-surface-300 dark:text-white/20" />
        <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No leave balances found.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {balances.map((b) => {
        const name = getLeaveName(b.leave_type_detail) ?? (b.leave_type as string | undefined);
        const code = getLeaveCode(b.leave_type_detail, b.leave_type as string | undefined);
        const total = Number(b.total_allocated) || 0;
        const used = Number(b.used) || 0;
        const available = Number(b.available) || 0;
        const pending = Number(b.pending_approval) || 0;
        const pct = total > 0 ? Math.min((used / total) * 100, 100) : 0;

        return (
          <div key={b.id} className="surface-card overflow-hidden rounded-xl border border-surface-100 dark:border-white/5">
            {/* Color header */}
            <div className={cn('flex items-center gap-3 bg-gradient-to-r px-4 py-3 text-white', getLeaveColor(code))}>
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/20 text-sm font-bold">
                {code}
              </div>
              <div>
                <p className="text-sm font-semibold">{name}</p>
                <p className="text-2xs opacity-80">
                  {b.leave_type_detail?.is_paid ? 'Paid' : 'Unpaid'}
                </p>
              </div>
            </div>

            {/* Numbers */}
            <div className="p-4">
              <div className="mb-3 grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="text-lg font-bold text-surface-900 dark:text-white">{total}</p>
                  <p className="text-2xs text-surface-500 dark:text-white/40">Allocated</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-amber-600 dark:text-amber-400">{used}</p>
                  <p className="text-2xs text-surface-500 dark:text-white/40">Used</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">{available}</p>
                  <p className="text-2xs text-surface-500 dark:text-white/40">Available</p>
                </div>
              </div>

              {/* Progress bar */}
              <div className="mb-2 h-2 overflow-hidden rounded-full bg-surface-100 dark:bg-white/10">
                <div
                  className={cn('h-full rounded-full bg-gradient-to-r transition-all', getLeaveColor(code))}
                  style={{ width: `${pct}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-2xs text-surface-500 dark:text-white/40">
                <span>{pct.toFixed(0)}% used</span>
                {pending > 0 && (
                  <span className="text-amber-600 dark:text-amber-400">{pending} pending</span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Applications Table                                                 */
/* ------------------------------------------------------------------ */

function ApplicationsTable({ applications }: { applications: LeaveApplicationAPI[] }) {
  if (applications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <FileText className="h-10 w-10 text-surface-300 dark:text-white/20" />
        <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No leave applications found.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-surface-200 text-left text-xs text-surface-500 dark:border-white/5 dark:text-white/40">
            <th className="pb-3 pr-4 font-medium">Leave Type</th>
            <th className="pb-3 pr-4 font-medium">From</th>
            <th className="pb-3 pr-4 font-medium">To</th>
            <th className="pb-3 pr-4 font-medium">Days</th>
            <th className="pb-3 pr-4 font-medium">Reason</th>
            <th className="pb-3 pr-4 font-medium">Applied On</th>
            <th className="pb-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-100 dark:divide-white/5">
          {applications.map((app) => {
            const code = getLeaveCode(app.leave_type_detail, app.leave_type as string | undefined);
            return (
              <tr key={app.id} className="hover:bg-surface-50 dark:hover:bg-white/[0.02]">
                <td className="py-3 pr-4">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'inline-flex h-6 w-6 items-center justify-center rounded-md bg-gradient-to-br text-2xs font-bold text-white',
                      getLeaveColor(code),
                    )}>
                      {code}
                    </span>
                    <span className="font-medium text-surface-900 dark:text-white">{getLeaveName(app.leave_type_detail)}</span>
                  </div>
                </td>
                <td className="whitespace-nowrap py-3 pr-4 text-surface-600 dark:text-white/60">{formatShortDate(app.from_date)}</td>
                <td className="whitespace-nowrap py-3 pr-4 text-surface-600 dark:text-white/60">{formatShortDate(app.to_date)}</td>
                <td className="py-3 pr-4 font-medium text-surface-900 dark:text-white">{app.total_days}</td>
                <td className="max-w-[200px] truncate py-3 pr-4 text-surface-600 dark:text-white/60">{app.reason}</td>
                <td className="whitespace-nowrap py-3 pr-4 text-surface-500 dark:text-white/40">{formatDate(app.applied_on)}</td>
                <td className="py-3">
                  <Badge variant={STATUS_VARIANT[app.status] ?? 'neutral'} size="sm" dot>
                    {app.status}
                  </Badge>
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
/*  Holidays List                                                      */
/* ------------------------------------------------------------------ */

function HolidaysList({ holidays }: { holidays: HolidayAPI[] }) {
  if (holidays.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Palmtree className="h-10 w-10 text-surface-300 dark:text-white/20" />
        <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No upcoming holidays.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {holidays.map((h) => {
        const d = new Date(h.date);
        const isPast = d < new Date();
        return (
          <div
            key={h.id}
            className={cn(
              'flex items-center gap-4 rounded-xl border border-surface-100 p-3 dark:border-white/5',
              isPast && 'opacity-50',
            )}
          >
            <div className="flex h-12 w-12 shrink-0 flex-col items-center justify-center rounded-xl bg-purple-50 dark:bg-purple-500/10">
              <span className="text-xs font-bold text-purple-700 dark:text-purple-300">
                {d.toLocaleDateString('en-IN', { month: 'short' })}
              </span>
              <span className="text-lg font-bold leading-none text-purple-800 dark:text-purple-200">
                {d.getDate()}
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-medium text-surface-900 dark:text-white">{h.name}</p>
              <p className="text-xs text-surface-500 dark:text-white/40">
                {d.toLocaleDateString('en-IN', { weekday: 'long' })} · {h.holiday_type}
              </p>
            </div>
            {h.is_optional && (
              <Badge variant="warning" size="sm">Optional</Badge>
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Apply Leave Form                                                   */
/* ------------------------------------------------------------------ */

function ApplyLeaveForm({ onSuccess }: { onSuccess: () => void }) {
  const { data: leaveTypes = [] } = useLeaveTypes();
  const { data: balances = [] } = useMyLeaveBalances();
  const applyLeave = useApplyLeave();

  const [leaveType, setLeaveType] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [fromHalf, setFromHalf] = useState<'FULL' | 'AM' | 'PM'>('FULL');
  const [toHalf, setToHalf] = useState<'FULL' | 'AM' | 'PM'>('FULL');
  const [reason, setReason] = useState('');
  const [contactDuringLeave, setContactDuringLeave] = useState('');
  const [documentUrl, setDocumentUrl] = useState('');

  // Calculate total days (simple)
  const totalDays = useMemo(() => {
    if (!fromDate || !toDate) return 0;
    const from = new Date(fromDate);
    const to = new Date(toDate);
    if (to < from) return 0;
    let days = Math.ceil((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    if (fromHalf !== 'FULL') days -= 0.5;
    if (toHalf !== 'FULL' && fromDate !== toDate) days -= 0.5;
    return Math.max(days, 0.5);
  }, [fromDate, toDate, fromHalf, toHalf]);

  // Get available balance for selected type
  const selectedBalance = useMemo(() => {
    if (!leaveType) return null;
    return balances.find((b) => b.leave_type === leaveType) ?? null;
  }, [leaveType, balances]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!leaveType || !fromDate || !toDate || !reason.trim()) return;
    applyLeave.mutate(
      {
        leave_type_id: leaveType,
        from_date: fromDate,
        to_date: toDate,
        from_session: fromHalf === 'AM' ? 'first_half' : fromHalf === 'PM' ? 'second_half' : 'first_half',
        to_session: toHalf === 'AM' ? 'first_half' : toHalf === 'PM' ? 'second_half' : 'first_half',
        reason: reason.trim(),
        contact_during_leave: contactDuringLeave.trim() || '',
      },
      {
        onSuccess: () => {
          setLeaveType('');
          setFromDate('');
          setToDate('');
          setFromHalf('FULL');
          setToHalf('FULL');
          setReason('');
          setContactDuringLeave('');
          setDocumentUrl('');
          onSuccess();
        },
      },
    );
  };

  const inputClass = 'w-full rounded-lg border border-surface-200 bg-surface-0 px-3 py-2 text-sm text-surface-900 outline-none transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-white/10 dark:bg-surface-100 dark:text-white dark:focus:border-brand-400';
  const labelClass = 'mb-1.5 block text-xs font-medium text-surface-600 dark:text-white/50';

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-xl space-y-5 p-4">
      <div className="surface-card rounded-xl border border-surface-100 p-5 dark:border-white/5">
        {/* <h3 className="mb-4 flex items-center gap-2 text-base font-semibold text-surface-900 dark:text-white">
          <Plus className="h-4 w-4 text-brand-500" /> Apply for Leave
        </h3> */}

        {/* Leave Type */}
        <div className="mb-4">
          <label className={labelClass}>Leave Type *</label>
          <select value={leaveType} onChange={(e) => setLeaveType(e.target.value)} className={inputClass} required>
            <option value="">Select leave type</option>
            {leaveTypes.map((lt) => (
              <option key={lt.leave_type_id} value={lt.leave_type_id}>{lt.name} ({lt.code})</option>
            ))}
          </select>
          {selectedBalance && (
            <p className="mt-1.5 text-xs text-surface-500 dark:text-white/40">
              Available: <span className="font-semibold text-emerald-600 dark:text-emerald-400">{Number(selectedBalance.available)}</span> days
              {' · '}Used: <span className="font-semibold text-amber-600 dark:text-amber-400">{Number(selectedBalance.used)}</span> days
            </p>
          )}
        </div>

        {/* Date range */}
        <div className="mb-4 grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>From Date *</label>
            <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} className={inputClass} required />
          </div>
          <div>
            <label className={labelClass}>To Date *</label>
            <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} min={fromDate} className={inputClass} required />
          </div>
        </div>

        {/* Half day options */}
        <div className="mb-4 grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>From Session</label>
            <select value={fromHalf} onChange={(e) => setFromHalf(e.target.value as 'FULL' | 'AM' | 'PM')} className={inputClass}>
              <option value="FULL">Full Day</option>
              <option value="AM">First Half</option>
              <option value="PM">Second Half</option>
            </select>
          </div>
          <div>
            <label className={labelClass}>To Session</label>
            <select value={toHalf} onChange={(e) => setToHalf(e.target.value as 'FULL' | 'AM' | 'PM')} className={inputClass}>
              <option value="FULL">Full Day</option>
              <option value="AM">First Half</option>
              <option value="PM">Second Half</option>
            </select>
          </div>
        </div>

        {/* Total days display */}
        {totalDays > 0 && (
          <div className="mb-4 rounded-lg bg-brand-50 px-3 py-2 text-sm dark:bg-brand-500/10">
            <span className="text-surface-600 dark:text-white/50">Total Days: </span>
            <span className="font-bold text-brand-700 dark:text-brand-300">{totalDays}</span>
          </div>
        )}

        {/* Reason */}
        <div className="mb-5">
          <label className={labelClass}>Reason *</label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            className={inputClass}
            placeholder="Enter reason for leave..."
            required
          />
        </div>

        <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className={labelClass}>Contact During Leave</label>
            <input
              type="text"
              value={contactDuringLeave}
              onChange={(e) => setContactDuringLeave(e.target.value)}
              className={inputClass}
              placeholder="Phone or alternate contact"
            />
          </div>
          <div>
            <label className={labelClass}>Document URL</label>
            <input
              type="url"
              value={documentUrl}
              onChange={(e) => setDocumentUrl(e.target.value)}
              className={inputClass}
              placeholder="Medical certificate link (if any)"
            />
          </div>
        </div>

        {/* Error */}
        {applyLeave.isError && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-500/20 dark:bg-red-500/10 dark:text-red-400">
            {(applyLeave.error as Error)?.message || 'Failed to submit leave application.'}
          </div>
        )}

        {/* Success */}
        {applyLeave.isSuccess && (
          <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-400">
            Leave application submitted successfully!
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={applyLeave.isPending || !leaveType || !fromDate || !toDate || !reason.trim()}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-brand-500 dark:hover:bg-brand-600"
        >
          <Send className="h-4 w-4" />
          {applyLeave.isPending ? 'Submitting...' : 'Submit Application'}
        </button>
      </div>
    </form>
  );
}

/* ------------------------------------------------------------------ */
/*  Admin Leave Approval View                                          */
/* ------------------------------------------------------------------ */

function AdminLeaveApprovalView() {
  const { data: applications = [], isLoading } = useAllLeaveApplications();
  const approveMut = useApproveLeave();
  const rejectMut = useRejectLeave();
  const [rejectId, setRejectId] = useState<string | null>(null);
  const [rejectRemarks, setRejectRemarks] = useState('');

  const pending = useMemo(() => applications.filter((a: AdminLeaveApplicationAPI) => a.status === 'SUBMITTED'), [applications]);
  const resolved = useMemo(() => applications.filter((a: AdminLeaveApplicationAPI) => a.status !== 'SUBMITTED' && a.status !== 'DRAFT'), [applications]);

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-3 p-4">
        {[1, 2, 3].map((i) => <div key={i} className="h-20 rounded-xl bg-surface-200 dark:bg-white/10" />)}
      </div>
    );
  }

  const AppRow = ({ app }: { app: AdminLeaveApplicationAPI }) => {
    const isPending = app.status === 'SUBMITTED';
    return (
      <div className="flex flex-wrap items-center gap-3 rounded-xl border border-surface-100 bg-surface-0 p-3 dark:border-white/5 dark:bg-white/[0.03]">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-600 text-xs font-bold text-white">
          {getLeaveCode(app.leave_type_detail, app.leave_type as string | undefined)}
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-surface-900 dark:text-white">{app.employee_name}</p>
          <p className="text-xs text-surface-500 dark:text-white/40">
            {getLeaveName(app.leave_type_detail)} · {new Date(app.from_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
            {' — '}{new Date(app.to_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
            {' · '}{Number(app.total_days)} day{Number(app.total_days) > 1 ? 's' : ''}
          </p>
          {app.reason && <p className="mt-0.5 truncate text-xs italic text-surface-400 dark:text-white/30">"{app.reason}"</p>}
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={(STATUS_VARIANT[app.status as keyof typeof STATUS_VARIANT] ?? 'neutral') as any} size="sm" dot>{app.status}</Badge>
          {isPending && (
            <>
              <button
                type="button"
                disabled={approveMut.isPending}
                onClick={() => approveMut.mutate(app.id)}
                className="flex items-center gap-1 rounded-lg bg-emerald-600 px-2.5 py-1 text-xs font-semibold text-white transition-colors hover:bg-emerald-700 disabled:opacity-50"
              >
                <UserCheck className="h-3.5 w-3.5" /> Approve
              </button>
              <button
                type="button"
                disabled={rejectMut.isPending}
                onClick={() => { setRejectId(app.id); setRejectRemarks(''); }}
                className="flex items-center gap-1 rounded-lg bg-red-100 px-2.5 py-1 text-xs font-semibold text-red-700 transition-colors hover:bg-red-200 dark:bg-red-500/10 dark:text-red-400 dark:hover:bg-red-500/20"
              >
                <XCircle className="h-3.5 w-3.5" /> Reject
              </button>
            </>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-5 p-4">
      {/* Reject dialog */}
      {rejectId && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-500/20 dark:bg-red-500/10">
          <p className="mb-2 text-sm font-semibold text-red-700 dark:text-red-400">Rejection Remarks (optional)</p>
          <textarea
            value={rejectRemarks}
            onChange={(e) => setRejectRemarks(e.target.value)}
            rows={2}
            className="mb-3 w-full rounded-lg border border-red-200 bg-white px-3 py-2 text-sm text-surface-900 outline-none focus:border-red-400 dark:border-red-500/30 dark:bg-surface-100 dark:text-white"
            placeholder="Reason for rejection..."
          />
          <div className="flex gap-2">
            <button
              type="button"
              disabled={rejectMut.isPending}
              onClick={() => {
                rejectMut.mutate({ id: rejectId, remarks: rejectRemarks.trim() || undefined });
                setRejectId(null);
              }}
              className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-50"
            >
              Confirm Reject
            </button>
            <button type="button" onClick={() => setRejectId(null)} className="rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-semibold text-surface-600 hover:bg-surface-100 dark:border-white/10 dark:text-white/50">
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Pending queue */}
      <div>
        <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-surface-700 dark:text-white/80">
          <Clock className="h-4 w-4 text-amber-500" />
          Pending Approval
          {pending.length > 0 && (
            <span className="ml-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700 dark:bg-amber-500/15 dark:text-amber-400">
              {pending.length}
            </span>
          )}
        </h2>
        {pending.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-surface-200 py-12 text-center dark:border-white/10">
            <ShieldCheck className="h-8 w-8 text-emerald-400" />
            <p className="mt-2 text-sm text-surface-500 dark:text-white/40">All caught up — no pending requests</p>
          </div>
        ) : (
          <div className="space-y-2">
            {pending.map((app: AdminLeaveApplicationAPI) => <AppRow key={app.id} app={app} />)}
          </div>
        )}
      </div>

      {/* Recent resolved */}
      {resolved.length > 0 && (
        <div>
          <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-surface-700 dark:text-white/80">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" /> Recent Decisions ({resolved.length})
          </h2>
          <div className="space-y-2">
            {resolved.slice(0, 10).map((app: AdminLeaveApplicationAPI) => <AppRow key={app.id} app={app} />)}
          </div>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Skeleton                                                           */
/* ------------------------------------------------------------------ */

function LeaveSkeleton() {
  return (
    <div className="animate-pulse space-y-4 p-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-44 rounded-xl bg-surface-200 dark:bg-white/10" />
        ))}
      </div>
      <div className="h-48 rounded-xl bg-surface-200 dark:bg-white/10" />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main: Leave Panel                                                  */
/* ------------------------------------------------------------------ */

export function LeavePanel() {
  const { data: balances = [], isLoading: loadingBalances } = useMyLeaveBalances();
  const { data: applications = [], isLoading: loadingApps } = useMyLeaveApplications();
  const { data: holidays = [] } = useUpcomingHolidays();
  const [activeTab, setActiveTab] = useState('dashboard');

  const portal = useUIStore((s) => s.portal);
  const activeModule = useUIStore((s) => s.activeModule);
  const rawModuleView = useUIStore((s) => s.moduleViews[activeModule] ?? 'employee');
  const isAdminView = portal === 'hrms' && rawModuleView === 'admin';

  const isLoading = loadingBalances || loadingApps;

  // Split pending vs history
  const pendingApps = useMemo(() => applications.filter((a) => a.status === 'SUBMITTED' || a.status === 'DRAFT'), [applications]);

  const tabItems = [
    {
      label: 'Dashboard',
      value: 'dashboard',
      content: isLoading ? (
        <LeaveSkeleton />
      ) : (
        <div className="space-y-6 p-4">
          {/* Balance cards */}
          <div>
            <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-surface-700 dark:text-white/80">
              <PieChart className="h-4 w-4" /> Leave Balances
            </h2>
            <BalanceCards balances={balances} />
          </div>

          {/* Pending approvals */}
          {pendingApps.length > 0 && (
            <div>
              <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-surface-700 dark:text-white/80">
                <Clock className="h-4 w-4 text-amber-500" /> Pending Approval ({pendingApps.length})
              </h2>
              <div className="surface-card rounded-xl border border-amber-200 p-4 dark:border-amber-500/20">
                {pendingApps.map((app) => (
                  <div key={app.id} className="flex items-center gap-4 py-2">
                    <span className={cn(
                      'inline-flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br text-2xs font-bold text-white',
                      getLeaveColor(getLeaveCode(app.leave_type_detail, app.leave_type as string | undefined)),
                    )}>
                      {getLeaveCode(app.leave_type_detail, app.leave_type as string | undefined)}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-surface-900 dark:text-white">{getLeaveName(app.leave_type_detail)}</p>
                      <p className="text-xs text-surface-500 dark:text-white/40">
                        {formatShortDate(app.from_date)} — {formatShortDate(app.to_date)} · {app.total_days} day{app.total_days > 1 ? 's' : ''}
                      </p>
                    </div>
                    <Badge variant="warning" size="sm" dot>Pending</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick stats row */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <QuickStat
              icon={CalendarDays}
              label="Total Allocated"
              value={balances.reduce((s, b) => s + Number(b.total_allocated || 0), 0).toString()}
              color="text-brand-600 dark:text-brand-400"
            />
            <QuickStat
              icon={CheckCircle2}
              label="Total Used"
              value={balances.reduce((s, b) => s + Number(b.used || 0), 0).toString()}
              color="text-amber-600 dark:text-amber-400"
            />
            <QuickStat
              icon={Send}
              label="Applications"
              value={applications.length.toString()}
              color="text-violet-600 dark:text-violet-400"
            />
            <QuickStat
              icon={Palmtree}
              label="Upcoming Holidays"
              value={holidays.length.toString()}
              color="text-purple-600 dark:text-purple-400"
            />
          </div>
        </div>
      ),
    },
    {
      label: 'My Applications',
      value: 'applications',
      content: (
        <div className="p-4">
          <ApplicationsTable applications={applications} />
        </div>
      ),
    },
    {
      label: 'Holiday Calendar',
      value: 'holidays',
      content: (
        <div className="p-4">
          <HolidaysList holidays={holidays} />
        </div>
      ),
    },
    {
      label: 'Apply Leave',
      value: 'apply',
      content: <ApplyLeaveForm onSuccess={() => setActiveTab('applications')} />,
    },
    ...(isAdminView ? [{
      label: 'Approvals',
      value: 'approvals',
      content: <AdminLeaveApprovalView />,
    }] : []),
  ];

  return <Tabs items={tabItems} value={activeTab} onChange={setActiveTab} />;
}

/* ------------------------------------------------------------------ */
/*  Quick Stat                                                         */
/* ------------------------------------------------------------------ */

function QuickStat({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: string; color: string }) {
  return (
    <div className="surface-card flex items-center gap-3 rounded-xl border border-surface-100 p-3 dark:border-white/5">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-surface-100 dark:bg-white/5">
        <Icon className={cn('h-4 w-4', color)} />
      </div>
      <div>
        <p className={cn('text-lg font-bold', color)}>{value}</p>
        <p className="text-2xs text-surface-500 dark:text-white/40">{label}</p>
      </div>
    </div>
  );
}
