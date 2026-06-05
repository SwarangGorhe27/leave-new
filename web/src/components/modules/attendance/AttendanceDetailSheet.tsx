import { useState } from 'react';
import {
  Clock,
  Edit3,
  FileText,
  History,
  Shield,
  X,
  LogIn,
  LogOut,
  Timer,
  AlertTriangle,
  TrendingUp,
  Hourglass,
  CheckCircle2,
} from 'lucide-react';
import { useAttendanceAuditLog, useAttendanceOverride } from '@hooks/useAdminAttendance';
import type { AdminAttendanceRecord, AttendanceEditLogEntry } from '@hooks/useAdminAttendance';
import { useUIStore } from '@store/uiStore';
import { cn } from '@utils/utils';

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function fmtTime(dt: string | null): string {
  if (!dt) return '—';
  return new Date(dt).toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

function fmtDate(d: string): string {
  return new Date(d).toLocaleDateString('en-IN', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });
}

function fmtDuration(iso: string | null): string {
  if (!iso) return '—';
  const parts = iso.split(':');
  if (parts.length >= 2) {
    const h = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10);
    if (h === 0 && m === 0) return '—';
    return `${h}h ${m}m`;
  }
  return iso;
}

function fmtMins(mins: number): string {
  if (!mins || mins <= 0) return '—';
  if (mins < 60) return `${mins}m`;
  return `${Math.floor(mins / 60)}h ${mins % 60}m`;
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0] ?? '')
    .join('')
    .toUpperCase();
}

const SOURCE_LABELS: Record<string, string> = {
  BIOMETRIC: 'Biometric',
  REGULARIZATION: 'Regularization',
  ADMIN_OVERRIDE: 'Admin Override',
  SYSTEM: 'System',
};

/* ------------------------------------------------------------------ */
/*  Status Config                                                       */
/* ------------------------------------------------------------------ */

const STATUS_CFG: Record<
  string,
  { label: string; badgeCls: string; dot: string }
> = {
  PRESENT: {
    label: 'Present',
    badgeCls:
      'bg-emerald-50 text-emerald-700 ring-emerald-200/70 dark:bg-emerald-500/10 dark:text-emerald-400 dark:ring-emerald-500/20',
    dot: 'bg-emerald-500',
  },
  ABSENT: {
    label: 'Absent',
    badgeCls:
      'bg-rose-50 text-rose-600 ring-rose-200/70 dark:bg-rose-500/10 dark:text-rose-400 dark:ring-rose-500/20',
    dot: 'bg-rose-500',
  },
  HALF_DAY: {
    label: 'Half Day',
    badgeCls:
      'bg-amber-50 text-amber-700 ring-amber-200/70 dark:bg-amber-500/10 dark:text-amber-400 dark:ring-amber-500/20',
    dot: 'bg-amber-500',
  },
  LEAVE: {
    label: 'On Leave',
    badgeCls:
      'bg-sky-50 text-sky-700 ring-sky-200/70 dark:bg-sky-500/10 dark:text-sky-400 dark:ring-sky-500/20',
    dot: 'bg-sky-500',
  },
  HOLIDAY: {
    label: 'Holiday',
    badgeCls:
      'bg-violet-50 text-violet-700 ring-violet-200/70 dark:bg-violet-500/10 dark:text-violet-400 dark:ring-violet-500/20',
    dot: 'bg-violet-500',
  },
  WEEK_OFF: {
    label: 'Week Off',
    badgeCls:
      'bg-slate-50 text-slate-500 ring-slate-200/70 dark:bg-white/5 dark:text-white/40 dark:ring-white/10',
    dot: 'bg-slate-400',
  },
  ON_DUTY: {
    label: 'On Duty',
    badgeCls:
      'bg-teal-50 text-teal-700 ring-teal-200/70 dark:bg-teal-500/10 dark:text-teal-400 dark:ring-teal-500/20',
    dot: 'bg-teal-500',
  },
};

function StatusBadge({ status, size = 'md' }: { status: string; size?: 'sm' | 'md' }) {
  const cfg = STATUS_CFG[status] ?? STATUS_CFG['WEEK_OFF'];
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-semibold ring-1 ring-inset',
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm',
        cfg.badgeCls,
      )}
    >
      <span className={cn('rounded-full', size === 'sm' ? 'h-1.5 w-1.5' : 'h-2 w-2', cfg.dot)} />
      {cfg.label}
    </span>
  );
}

/* ------------------------------------------------------------------ */
/*  Stat Card                                                          */
/* ------------------------------------------------------------------ */

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  value: string;
  /** Extra class applied to the value text */
  valueCls?: string;
  sub?: string;
}

function StatCard({ icon: Icon, label, value, valueCls, sub }: StatCardProps) {
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-surface-100 bg-surface-50/60 p-4 dark:border-white/5 dark:bg-white/[0.03]">
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white shadow-sm dark:bg-white/10 dark:shadow-none">
        <Icon className="h-4.5 w-4.5 text-surface-500 dark:text-white/40" />
      </div>
      <div>
        <p className={cn('text-xl font-bold tracking-tight text-surface-900 dark:text-white', valueCls)}>
          {value}
        </p>
        {sub && <p className="mt-0.5 text-xs text-surface-400 dark:text-white/30">{sub}</p>}
        <p className="mt-1 text-xs font-medium text-surface-500 dark:text-white/40">{label}</p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Section Title                                                      */
/* ------------------------------------------------------------------ */

function SectionTitle({ icon: Icon, title }: { icon: React.ElementType; title: string }) {
  return (
    <div className="flex items-center gap-2 border-b border-surface-100 pb-3 dark:border-white/5">
      <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-surface-100 dark:bg-white/10">
        <Icon className="h-3.5 w-3.5 text-surface-500 dark:text-white/40" />
      </div>
      <h4 className="text-sm font-semibold text-surface-700 dark:text-white/70">{title}</h4>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Info Row                                                           */
/* ------------------------------------------------------------------ */

function InfoRow({ label, value, valueCls }: { label: string; value: React.ReactNode; valueCls?: string }) {
  return (
    <div className="flex items-center justify-between gap-4 py-2.5 border-b border-surface-50 last:border-0 dark:border-white/[0.04]">
      <span className="text-sm text-surface-500 dark:text-white/40 shrink-0">{label}</span>
      <span className={cn('text-sm font-medium text-right text-surface-800 dark:text-white/80', valueCls)}>
        {value}
      </span>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Audit Trail                                                        */
/* ------------------------------------------------------------------ */

function AuditTrail({ logs }: { logs: AttendanceEditLogEntry[] }) {
  if (logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-surface-200 py-8 dark:border-white/10">
        <History className="h-6 w-6 text-surface-300 dark:text-white/20" />
        <p className="mt-2 text-sm text-surface-400 dark:text-white/30">No edit history yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {logs.map((log, idx) => (
        <div key={log.id} className="flex gap-3">
          <div className="flex flex-col items-center pt-1">
            <span className="h-2 w-2 rounded-full bg-brand-400 ring-2 ring-brand-100 dark:ring-brand-500/20 shrink-0" />
            {idx < logs.length - 1 && (
              <span className="mt-1 w-px flex-1 bg-surface-100 dark:bg-white/5" />
            )}
          </div>
          <div className={cn('pb-5 min-w-0', idx === logs.length - 1 && 'pb-0')}>
            <p className="text-sm font-medium text-surface-800 dark:text-white/80">
              {SOURCE_LABELS[log.change_source] ?? log.change_source}
            </p>
            <p className="mt-0.5 text-xs text-surface-500 dark:text-white/40">
              <span className="font-medium">{log.field_changed}</span>:{' '}
              <span className="line-through opacity-60">{log.old_value || '—'}</span>
              {' → '}
              <span className="font-semibold text-surface-700 dark:text-white/70">
                {log.new_value || '—'}
              </span>
            </p>
            <p className="mt-0.5 text-xs text-surface-400 dark:text-white/30">
              by {log.changed_by_name} ·{' '}
              {new Date(log.created_at).toLocaleString('en-IN', {
                day: '2-digit',
                month: 'short',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Override Form                                                      */
/* ------------------------------------------------------------------ */

function OverrideForm({
  record,
  onSuccess,
  onCancel,
}: {
  record: AdminAttendanceRecord;
  onSuccess: () => void;
  onCancel: () => void;
}) {
  const override = useAttendanceOverride();
  const [status, setStatus] = useState(record.status);
  const [reason, setReason] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (reason.length < 10) return;
    override.mutate(
      {
        recordId: record.id,
        payload: {
          status: status !== record.status ? status : undefined,
          reason,
        },
      },
      { onSuccess },
    );
  };

  const inputCls =
    'w-full rounded-xl border border-surface-200 bg-white px-4 py-2.5 text-sm text-surface-900 outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-400/20 dark:border-white/10 dark:bg-white/5 dark:text-white dark:focus:border-brand-400';

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="mb-1.5 block text-xs font-semibold text-surface-600 dark:text-white/50">
          New Status
        </label>
        <select value={status} onChange={(e) => setStatus(e.target.value)} className={inputCls}>
          <option value="PRESENT">Present</option>
          <option value="ABSENT">Absent</option>
          <option value="HALF_DAY">Half Day</option>
          <option value="LEAVE">Leave</option>
          <option value="ON_DUTY">On Duty</option>
        </select>
      </div>
      <div>
        <label className="mb-1.5 block text-xs font-semibold text-surface-600 dark:text-white/50">
          Reason{' '}
          <span className="font-normal text-surface-400 dark:text-white/25">
            (min 10 characters)
          </span>
        </label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          className={cn(inputCls, 'min-h-[88px] resize-none')}
          placeholder="Describe why this record is being changed…"
          required
          minLength={10}
        />
        {reason.length > 0 && reason.length < 10 && (
          <p className="mt-1 text-xs text-rose-500">
            {10 - reason.length} more character{10 - reason.length !== 1 ? 's' : ''} needed
          </p>
        )}
      </div>
      <div className="flex gap-2.5">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-xl border border-surface-200 px-4 py-2.5 text-sm font-medium text-surface-600 transition hover:bg-surface-50 dark:border-white/10 dark:text-white/50 dark:hover:bg-white/5"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={override.isPending || reason.length < 10}
          className="flex-1 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-brand-500 dark:hover:bg-brand-600"
        >
          {override.isPending ? 'Saving…' : 'Save Override'}
        </button>
      </div>
      {override.isError && (
        <div className="flex items-center gap-2 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:bg-rose-500/10 dark:text-rose-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {(override.error as Error)?.message || 'Failed to save override.'}
        </div>
      )}
    </form>
  );
}

/* ------------------------------------------------------------------ */
/*  Main: AttendanceDetailSheet                                        */
/* ------------------------------------------------------------------ */

interface Props {
  record: AdminAttendanceRecord;
  onClose: () => void;
}

export function AttendanceDetailSheet({ record, onClose }: Props) {
  const { data: auditLogs = [], refetch } = useAttendanceAuditLog(record.id);
  const [showOverride, setShowOverride] = useState(false);

  const initials = getInitials(record.employee_name || 'UN');

  /* Stat values */
  const lateVal = fmtMins(record.late_mins);
  const earlyVal = fmtMins(record.early_leave_mins);
  const otVal = fmtMins(record.overtime_mins);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/25 backdrop-blur-[3px] dark:bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative flex min-h-full items-start justify-center px-4 py-8">
        <div className="relative w-full max-w-5xl rounded-3xl bg-white shadow-2xl ring-1 ring-surface-200/60 dark:bg-[#111318] dark:ring-white/5">

          {/* ── Header ────────────────────────────────────── */}
          <div className="flex flex-col gap-5 px-6 pb-5 pt-6 sm:flex-row sm:items-start sm:gap-6 sm:px-8 sm:pt-8">
            {/* Avatar */}
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-100 to-brand-200/80 text-xl font-bold text-brand-700 shadow-sm dark:from-brand-500/25 dark:to-brand-600/15 dark:text-brand-300">
              {initials}
            </div>

            {/* Name block */}
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-xl font-bold text-surface-900 dark:text-white truncate">
                  {record.employee_name}
                </h2>
                <StatusBadge status={record.status} />
                {record.is_admin_edited && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-orange-50 px-2.5 py-0.5 text-xs font-medium text-orange-600 ring-1 ring-orange-200/70 dark:bg-orange-500/10 dark:text-orange-400 dark:ring-orange-500/20">
                    <Edit3 className="h-3 w-3" />
                    Edited
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-surface-500 dark:text-white/40">
                {record.employee_code}
                {record.shift_name && (
                  <span className="before:mx-2 before:content-['·']">{record.shift_name}</span>
                )}
              </p>
              <p className="mt-0.5 text-xs text-surface-400 dark:text-white/30">
                {fmtDate(record.date)}
              </p>
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={onClose}
                className="rounded-xl p-2 text-surface-400 transition hover:bg-surface-100 dark:text-white/30 dark:hover:bg-white/5"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* ── Divider ───────────────────────────────────── */}
          <div className="mx-6 border-t border-surface-100 dark:border-white/5 sm:mx-8" />

          {/* ── Body ──────────────────────────────────────── */}
          <div className="px-6 py-6 sm:px-8 sm:py-8">

            {/* 6-Stat grid */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
              <StatCard
                icon={LogIn}
                label="Punch In"
                value={fmtTime(record.first_in)}
              />
              <StatCard
                icon={LogOut}
                label="Punch Out"
                value={fmtTime(record.last_out)}
              />
              <StatCard
                icon={Timer}
                label="Working Hours"
                value={fmtDuration(record.effective_hours)}
              />
              <StatCard
                icon={Clock}
                label="Late By"
                value={lateVal === '—' ? 'On Time' : lateVal}
                valueCls={record.late_mins > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}
                sub={record.late_mins > 0 ? 'Arrived late' : undefined}
              />
              <StatCard
                icon={Hourglass}
                label="Early Out"
                value={earlyVal === '—' ? 'None' : earlyVal}
                valueCls={record.early_leave_mins > 0 ? 'text-amber-600 dark:text-amber-400' : undefined}
              />
              <StatCard
                icon={TrendingUp}
                label="Overtime"
                value={otVal === '—' ? 'None' : otVal}
                valueCls={record.overtime_mins > 0 ? 'text-teal-600 dark:text-teal-400' : undefined}
              />
            </div>

            {/* ── Two-column main body ───────────────────── */}
            <div className="mt-6 grid gap-6 lg:grid-cols-[3fr_2fr]">

              {/* LEFT COLUMN */}
              <div className="space-y-6">

                {/* Record Details */}
                <div className="rounded-2xl border border-surface-100 bg-white p-5 dark:border-white/5 dark:bg-white/[0.02]">
                  <SectionTitle icon={Clock} title="Record Details" />
                  <div className="mt-3">
                    <InfoRow label="Shift" value={record.shift_name || '—'} />
                    <InfoRow
                      label="Source"
                      value={SOURCE_LABELS[record.last_changed_by_source] ?? record.last_changed_by_source}
                    />
                    {record.remarks && (
                      <InfoRow label="Remarks" value={record.remarks} />
                    )}
                    <InfoRow
                      label="Regularized"
                      value={
                        record.is_regularized ? (
                          <span className="flex items-center gap-1.5 justify-end text-emerald-600 dark:text-emerald-400">
                            <CheckCircle2 className="h-3.5 w-3.5" /> Yes
                          </span>
                        ) : (
                          'No'
                        )
                      }
                    />
                    {record.admin_edit_reason && (
                      <InfoRow label="Override Reason" value={record.admin_edit_reason} />
                    )}
                    {record.admin_edited_at && (
                      <InfoRow
                        label="Edited At"
                        value={new Date(record.admin_edited_at).toLocaleString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      />
                    )}
                  </div>
                </div>

                {/* Original Biometric Record */}
                {record.original_status && (
                  <div className="rounded-2xl border border-surface-100 bg-white p-5 dark:border-white/5 dark:bg-white/[0.02]">
                    <SectionTitle icon={History} title="Original Biometric Record" />
                    <div className="mt-4 grid grid-cols-3 gap-3">
                      {[
                        { label: 'Punch In', value: fmtTime(record.original_first_in) },
                        { label: 'Punch Out', value: fmtTime(record.original_last_out) },
                      ].map((item) => (
                        <div
                          key={item.label}
                          className="rounded-xl bg-surface-50 p-3 dark:bg-white/[0.03]"
                        >
                          <p className="text-xs text-surface-400 dark:text-white/30">{item.label}</p>
                          <p className="mt-1 text-sm font-semibold text-surface-800 dark:text-white/80">
                            {item.value}
                          </p>
                        </div>
                      ))}
                      <div className="rounded-xl bg-surface-50 p-3 dark:bg-white/[0.03]">
                        <p className="text-xs text-surface-400 dark:text-white/30">Status</p>
                        <div className="mt-1">
                          <StatusBadge status={record.original_status} size="sm" />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* RIGHT COLUMN */}
              <div className="space-y-6">

                {/* Admin Override */}
                <div className="rounded-2xl border border-surface-100 bg-white p-5 dark:border-white/5 dark:bg-white/[0.02]">
                  <SectionTitle icon={Shield} title="Admin Override" />
                  <div className="mt-4">
                    {showOverride ? (
                      <OverrideForm
                        record={record}
                        onSuccess={() => {
                          setShowOverride(false);
                          refetch();
                        }}
                        onCancel={() => setShowOverride(false)}
                      />
                    ) : (
                      <button
                        type="button"
                        onClick={() => setShowOverride(true)}
                        className="group w-full rounded-xl border-2 border-dashed border-surface-200 py-5 text-sm font-medium text-surface-400 transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700 dark:border-white/10 dark:text-white/30 dark:hover:border-brand-400/30 dark:hover:bg-brand-500/5 dark:hover:text-brand-400"
                      >
                        <Edit3 className="mr-2 inline h-4 w-4 transition-transform group-hover:scale-110" />
                        Override this record
                      </button>
                    )}
                  </div>
                </div>

                {/* Audit Trail */}
                <div className="rounded-2xl border border-surface-100 bg-white p-5 dark:border-white/5 dark:bg-white/[0.02]">
                  <SectionTitle icon={History} title="Audit Trail" />
                  <div className="mt-4">
                    <AuditTrail logs={auditLogs} />
                  </div>
                </div>

                {/* Regularization note */}
                {record.is_regularized && (
                  <div className="flex items-start gap-3 rounded-2xl bg-emerald-50 p-4 ring-1 ring-emerald-200/60 dark:bg-emerald-500/5 dark:ring-emerald-500/15">
                    <FileText className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
                    <div>
                      <p className="text-sm font-medium text-emerald-800 dark:text-emerald-300">
                        Regularization Applied
                      </p>
                      <p className="mt-0.5 text-xs text-emerald-600/80 dark:text-emerald-400/70">
                        This record has been updated through a regularization request.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
