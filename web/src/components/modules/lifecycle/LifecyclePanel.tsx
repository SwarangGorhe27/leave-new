import { useState } from 'react';
import { Users, CalendarDays, ChevronDown, ArrowRight } from 'lucide-react';
import { cn } from '@utils/utils';
import { useEmployeeLifecycle, type LifecycleEvent } from '@hooks/useLifecycle';
import { useEmployeeList } from '@hooks/useEmployees';

const EVENT_CONFIG: Record<string, { label: string; color: string }> = {
  ONBOARDING:   { label: 'Onboarding',      color: 'bg-emerald-500' },
  PROMOTION:    { label: 'Promotion',        color: 'bg-brand-500' },
  DEMOTION:     { label: 'Demotion',         color: 'bg-orange-500' },
  TRANSFER:     { label: 'Transfer',         color: 'bg-violet-500' },
  RESIGNATION:  { label: 'Resignation',      color: 'bg-red-500' },
  TERMINATION:  { label: 'Termination',      color: 'bg-red-700' },
  DEPARTMENT_CHANGE: { label: 'Dept Change', color: 'bg-amber-500' },
  DESIGNATION_CHANGE: { label: 'Role Change', color: 'bg-sky-500' },
  SALARY_REVISION: { label: 'Salary Change', color: 'bg-teal-500' },
  CONFIRMATION: { label: 'Confirmed',        color: 'bg-indigo-500' },
  PROBATION:    { label: 'Probation',        color: 'bg-yellow-500' },
  SUSPENSION:   { label: 'Suspension',       color: 'bg-rose-500' },
  REJOINING:    { label: 'Rejoined',         color: 'bg-lime-500' },
};

function getConfig(type: string) {
  return EVENT_CONFIG[type] ?? { label: type.replace(/_/g, ' '), color: 'bg-surface-400' };
}

function TimelineEvent({ event }: { event: LifecycleEvent }) {
  const cfg = getConfig(event.event_type);
  const [open, setOpen] = useState(false);

  return (
    <div className="flex gap-4">
      {/* Dot + line */}
      <div className="flex flex-col items-center">
        <div className={cn('mt-1 h-3 w-3 shrink-0 rounded-full ring-2 ring-surface-0 dark:ring-surface-900', cfg.color)} />
        <div className="mt-1 flex-1 w-px bg-surface-100 dark:bg-white/10" />
      </div>

      {/* Content */}
      <div className="flex-1 pb-4">
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className={cn('inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium text-white', cfg.color)}>
              {cfg.label}
            </span>
            <p className="mt-1 text-xs text-surface-400 dark:text-white/30">
              {new Date(event.event_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
              {event.effective_date && event.effective_date !== event.event_date && (
                <span> · effective {new Date(event.effective_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
              )}
            </p>
          </div>
          {(event.previous_value || event.new_value) && (
            <button onClick={() => setOpen(!open)} className="flex items-center gap-1 text-xs text-surface-400 hover:text-brand-600 dark:text-white/30 dark:hover:text-brand-400">
              Details <ChevronDown className={cn('h-3 w-3 transition-transform', open && 'rotate-180')} />
            </button>
          )}
        </div>

        {/* Value change */}
        {(event.previous_value || event.new_value) && (
          <div className="mt-1.5 flex items-center gap-2 text-xs">
            {event.previous_value && (
              <span className="rounded-lg bg-surface-100 px-2 py-0.5 text-surface-600 line-through dark:bg-white/10 dark:text-white/40">
                {event.previous_value}
              </span>
            )}
            {event.previous_value && event.new_value && <ArrowRight className="h-3 w-3 text-surface-400 dark:text-white/20" />}
            {event.new_value && (
              <span className="rounded-lg bg-brand-50 px-2 py-0.5 font-medium text-brand-700 dark:bg-brand-900/20 dark:text-brand-400">
                {event.new_value}
              </span>
            )}
          </div>
        )}

        {/* Expanded details */}
        {open && (
          <div className="mt-2 space-y-1 rounded-xl border border-surface-100 bg-surface-50 p-3 text-xs dark:border-white/5 dark:bg-white/5">
            {event.remarks && (
              <div>
                <span className="font-medium text-surface-600 dark:text-white/50">Remarks: </span>
                <span className="text-surface-700 dark:text-white/60">{event.remarks}</span>
              </div>
            )}
            {event.approved_by && (
              <div>
                <span className="font-medium text-surface-600 dark:text-white/50">Approved by: </span>
                <span className="text-surface-700 dark:text-white/60">{event.approved_by}</span>
              </div>
            )}
            <div>
              <span className="font-medium text-surface-600 dark:text-white/50">Recorded: </span>
              <span className="text-surface-400 dark:text-white/30">{new Date(event.created_at).toLocaleString('en-IN')}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function EmployeeTimeline({ employeeId }: { employeeId: string }) {
  const { data: events = [], isLoading } = useEmployeeLifecycle(employeeId);

  if (isLoading) {
    return (
      <div className="space-y-4 p-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-4">
            <div className="flex flex-col items-center gap-1">
              <div className="h-3 w-3 animate-pulse rounded-full bg-surface-200 dark:bg-white/10" />
              <div className="h-14 w-px bg-surface-100 dark:bg-white/10" />
            </div>
            <div className="flex-1 space-y-1.5">
              <div className="h-5 w-24 animate-pulse rounded-full bg-surface-200 dark:bg-white/10" />
              <div className="h-3 w-40 animate-pulse rounded-lg bg-surface-100 dark:bg-white/5" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!events.length) {
    return (
      <div className="flex flex-col items-center py-14 text-center">
        <CalendarDays className="h-10 w-10 text-surface-300 dark:text-white/20" />
        <p className="mt-3 text-sm font-medium text-surface-700 dark:text-white/60">No lifecycle events</p>
        <p className="mt-1 text-xs text-surface-400 dark:text-white/30">No events recorded for this employee yet.</p>
      </div>
    );
  }

  const sorted = [...events].sort(
    (a, b) => new Date(b.event_date).getTime() - new Date(a.event_date).getTime(),
  );

  return (
    <div className="p-4">
      {sorted.map((ev) => <TimelineEvent key={ev.id} event={ev} />)}
    </div>
  );
}

export function LifecyclePanel() {
  const { data: employees = [], isLoading: empLoading } = useEmployeeList();
  const [selectedId, setSelectedId] = useState('');

  const selectedEmployee = employees.find((e) => e.id === selectedId);

  return (
    <div className="space-y-4 p-1">
      {/* Header */}
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-100 dark:bg-brand-900/30">
          <Users className="h-4 w-4 text-brand-600 dark:text-brand-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-surface-900 dark:text-white">Employee Lifecycle</h3>
          <p className="text-xs text-surface-400 dark:text-white/30">View promotions, transfers, and other life events</p>
        </div>
      </div>

      {/* Employee selector */}
      <div className="relative">
        <select
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          disabled={empLoading}
          className="w-full appearance-none rounded-xl border border-surface-200 bg-surface-0 px-3 py-2.5 pr-8 text-sm text-surface-900 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white disabled:opacity-50"
        >
          <option value="">{empLoading ? 'Loading employees…' : 'Select an employee…'}</option>
          {employees.map((e) => (
            <option key={e.id} value={e.id}>
              {e.full_name} ({e.employee_code})
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-surface-400 dark:text-white/30" />
      </div>

      {/* Timeline */}
      {selectedId ? (
        <div className="rounded-2xl border border-surface-200/70 bg-surface-0 shadow-xs dark:border-white/10 dark:bg-white/5">
          {selectedEmployee && (
            <div className="border-b border-surface-100 px-4 py-3 dark:border-white/5">
              <p className="text-sm font-semibold text-surface-900 dark:text-white">
                {selectedEmployee.full_name}
              </p>
              <p className="text-xs text-surface-400 dark:text-white/30">
                {selectedEmployee.employee_code}
                {selectedEmployee.department && ` · ${selectedEmployee.department}`}
              </p>
            </div>
          )}
          <EmployeeTimeline employeeId={selectedId} />
        </div>
      ) : (
        <div className="flex flex-col items-center rounded-2xl border border-surface-200/70 border-dashed py-16 text-center dark:border-white/10">
          <CalendarDays className="h-10 w-10 text-surface-300 dark:text-white/20" />
          <p className="mt-3 text-sm text-surface-500 dark:text-white/40">Select an employee to view their timeline</p>
        </div>
      )}
    </div>
  );
}
