import { ChevronRight, UserCheck, Clock, UserX, LogOut, AlertCircle, Bell, CheckCircle2 } from 'lucide-react';
import { cn } from '@utils/utils';
import { SkeletonBlock } from './kit/SkeletonLoader';

/* ─── Types ──────────────────────────────────────────────────────── */
export type LifecycleAlertType =
  | 'onboarding'
  | 'probation'
  | 'confirmation'
  | 'offboarding'
  | 'exit'
  | 'birthday'; // kept for backward compat

export interface ImportantItem {
  id: string;
  type: LifecycleAlertType | 'joiner' | 'announcement';
  name?: string;
  title?: string;
  detail?: string;
  date?: string;
  count?: number;
  icon?: React.ReactNode;
  onClick?: () => void;
}

/* ─── Config per type ────────────────────────────────────────────── */
interface AlertConfig {
  label: string;
  cardHover: string;
  iconBg: string;
  iconColor: string;
  icon: React.ReactNode;
  countBg: string;
  countColor: string;
  isCritical?: boolean;
}

function getConfig(type: ImportantItem['type']): AlertConfig {
  switch (type) {
    case 'onboarding':
      return {
        label: 'Onboarding Due',
        cardHover: 'hover:border-sky-300 dark:hover:border-sky-500/50 hover:shadow-sky-500/10 hover:shadow-lg',
        iconBg: 'bg-sky-100/80       dark:bg-sky-500/15',
        iconColor: 'text-sky-600        dark:text-sky-400',
        icon: <UserCheck className="h-4 w-4" />,
        countBg: 'bg-sky-50 border border-sky-200/50 dark:bg-sky-500/15 dark:border-sky-500/20',
        countColor: 'text-sky-700        dark:text-sky-300',
        isCritical: true,
      };
    case 'probation':
      return {
        label: 'Probation Ending',
        cardHover: 'hover:border-amber-300 dark:hover:border-amber-500/50 hover:shadow-amber-500/10 hover:shadow-lg',
        iconBg: 'bg-amber-100/80     dark:bg-amber-500/15',
        iconColor: 'text-amber-600      dark:text-amber-400',
        icon: <Clock className="h-4 w-4" />,
        countBg: 'bg-amber-50 border border-amber-200/50 dark:bg-amber-500/15 dark:border-amber-500/20',
        countColor: 'text-amber-700      dark:text-amber-300',
      };
    case 'confirmation':
      return {
        label: 'Confirmation Pending',
        cardHover: 'hover:border-violet-300 dark:hover:border-violet-500/50 hover:shadow-violet-500/10 hover:shadow-lg',
        iconBg: 'bg-violet-100/80    dark:bg-violet-500/15',
        iconColor: 'text-violet-600     dark:text-violet-400',
        icon: <AlertCircle className="h-4 w-4" />,
        countBg: 'bg-violet-50 border border-violet-200/50 dark:bg-violet-500/15 dark:border-violet-500/20',
        countColor: 'text-violet-700     dark:text-violet-300',
      };
    case 'offboarding':
      return {
        label: 'Offboarding In Progress',
        cardHover: 'hover:border-orange-300 dark:hover:border-orange-500/50 hover:shadow-orange-500/10 hover:shadow-lg',
        iconBg: 'bg-orange-100/80    dark:bg-orange-500/15',
        iconColor: 'text-orange-600     dark:text-orange-400',
        icon: <UserX className="h-4 w-4" />,
        countBg: 'bg-orange-50 border border-orange-200/50 dark:bg-orange-500/15 dark:border-orange-500/20',
        countColor: 'text-orange-700     dark:text-orange-300',
        isCritical: true,
      };
    case 'exit':
      return {
        label: 'Exit Scheduled',
        cardHover: 'hover:border-red-300 dark:hover:border-red-500/50 hover:shadow-red-500/10 hover:shadow-lg',
        iconBg: 'bg-red-100/80       dark:bg-red-500/15',
        iconColor: 'text-red-600        dark:text-red-400',
        icon: <LogOut className="h-4 w-4" />,
        countBg: 'bg-red-50 border border-red-200/50 dark:bg-red-500/15 dark:border-red-500/20',
        countColor: 'text-red-700        dark:text-red-300',
        isCritical: true,
      };
    default:
      return {
        label: type === 'birthday' ? 'Birthday Today' : type === 'joiner' ? 'Joining Today' : 'Update',
        cardHover: 'hover:border-surface-300 dark:hover:border-surface-600 hover:shadow-surface-500/5 hover:shadow-lg',
        iconBg: 'bg-surface-100      dark:bg-white/5',
        iconColor: 'text-surface-600    dark:text-white/50',
        icon: <Bell className="h-4 w-4" />,
        countBg: 'bg-surface-50 border border-surface-200/50 dark:bg-white/5 dark:border-white/10',
        countColor: 'text-surface-700    dark:text-white/60',
      };
  }
}

/* ─── Single alert row ───────────────────────────────────────────── */
function AlertRow({ item }: { item: ImportantItem }) {
  const cfg = getConfig(item.type);
  const displayLabel = item.title ?? item.name ?? cfg.label;
  const displaySub = item.detail ?? cfg.label;
  const count = item.count;

  return (
    <button
      type="button"
      onClick={item.onClick}
      className={cn(
        'group relative flex w-full items-center gap-4 rounded-[14px] border border-surface-200/50 bg-surface-50/50 px-4 py-3.5',
        'text-left transition-all duration-300 ease-out',
        'hover:-translate-y-[2px] dark:border-white/5 dark:bg-surface-800/40',
        cfg.cardHover
      )}
    >
      {/* Icon with optional pulse for critical items */}
      <div className="relative">
        <div className={cn('relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-110', cfg.iconBg, cfg.iconColor)}>
          {item.icon ?? cfg.icon}
        </div>
        {cfg.isCritical && (
          <span className="absolute -right-1 -top-1 flex h-3. w-3">
            <span className={cn("absolute inline-flex h-full w-full animate-ping rounded-full opacity-75", cfg.iconColor.replace('text-', 'bg-'))} />
            <span className={cn("relative inline-flex h-3 w-3 rounded-full", cfg.iconColor.replace('text-', 'bg-'))} />
          </span>
        )}
      </div>

      {/* Labels */}
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-surface-900 group-hover:text-surface-950 dark:text-white/90 dark:group-hover:text-white transition-colors duration-200">
          {displayLabel}
        </p>
        <p className="mt-0.5 text-xs text-surface-500 dark:text-white/45">
          {displaySub}
        </p>
      </div>

      {/* Premium OS-like badge */}
      {count !== undefined && count > 0 && (
        <span className={cn(
          'flex h-6 min-w-[28px] items-center justify-center rounded-full px-2.5 text-xs font-bold tabular-nums shadow-sm',
          cfg.countBg, cfg.countColor,
        )}>
          {count}
        </span>
      )}

      {/* Action Chevron */}
      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-surface-100 opacity-0 transition-all duration-300 group-hover:opacity-100 group-hover:bg-surface-200 dark:bg-white/5 dark:group-hover:bg-white/10 mr-1 group-hover:mr-0">
        <ChevronRight className="h-4 w-4 text-surface-500 dark:text-white/50 transition-transform group-hover:translate-x-0.5" />
      </div>
    </button>
  );
}

/* ─── Skeleton ───────────────────────────────────────────────────── */
function AlertRowSkeleton() {
  return (
    <div className="flex w-full items-center gap-4 rounded-[14px] border border-surface-200/50 bg-surface-50/50 px-4 py-3.5 dark:border-white/5 dark:bg-surface-800/40 animate-pulse">
      <SkeletonBlock className="h-10 w-10 rounded-xl shrink-0" />
      <div className="flex-1 space-y-2">
        <SkeletonBlock className="h-4 w-40 rounded" />
        <SkeletonBlock className="h-3 w-28 rounded" />
      </div>
      <SkeletonBlock className="h-6 w-8 rounded-full" />
    </div>
  );
}

/* ─── Public component ───────────────────────────────────────────── */
interface LifecycleAlertsProps {
  items: ImportantItem[];
  isLoading?: boolean;
}

/** Renamed from ImportantToday — shows HR lifecycle events (onboarding, probation, etc.) */
export function ImportantToday({ items, isLoading }: LifecycleAlertsProps) {
  return (
    <div className="surface-card flex h-full flex-col rounded-[20px] px-0 py-0 pb-2 overflow-hidden shadow-sm">
      {/* Gradient Header Component */}
      <div className="relative mb-6 px-6 pt-6 pb-4 border-b border-surface-200/50 dark:border-white/5 bg-gradient-to-b from-surface-50 to-surface-0 dark:from-white/[0.02] dark:to-transparent">
        <div className="absolute inset-0 bg-noise opacity-[0.02] mix-blend-overlay" />
        <h2 className="relative flex items-center gap-2 text-[17px] font-semibold tracking-tight text-surface-900 dark:text-white">
          <div className="h-4 w-1 rounded-full bg-brand-500" />
          Lifecycle Alerts
        </h2>
        <p className="relative pl-3 mt-1 text-[13px] font-medium text-surface-500 dark:text-white/45">
          Priority events requiring immediate action
        </p>
      </div>

      {/* Content Stream */}
      <div className="flex-1 space-y-2.5 px-5 overflow-y-auto custom-scrollbar pb-4">
        {isLoading ? (
          <>
            <AlertRowSkeleton />
            <AlertRowSkeleton />
            <AlertRowSkeleton />
          </>
        ) : items.length === 0 ? (
          <div className="flex h-[240px] flex-col items-center justify-center rounded-[18px] border border-surface-200/60 bg-surface-50/50 px-4 text-center dark:border-white/5 dark:bg-surface-800/30">
            <div className="relative mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-success-100 to-emerald-50 shadow-sm ring-1 ring-inset ring-white dark:from-success-500/20 dark:to-emerald-500/5 dark:ring-white/10">
              <UserCheck className="h-6 w-6 text-success-600 dark:text-success-400" />
              <span className="absolute -right-1 -top-1 flex h-4 w-4">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success-400 opacity-40" />
                <span className="relative inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 border-white bg-success-500 dark:border-surface-800">
                  <CheckCircle2 className="h-2.5 w-2.5 text-white" />
                </span>
              </span>
            </div>
            <p className="text-base font-semibold text-surface-900 dark:text-white/90">
              Inbox Zero
            </p>
            <p className="mt-1 text-[13px] font-medium text-surface-500 dark:text-white/50">
              No lifecycle events pending your action
            </p>
          </div>
        ) : (
          items.map((item, index) => (
            <div
              key={item.id}
              className="animate-in fade-in slide-in-from-bottom-2 fill-mode-both"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <AlertRow item={item} />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
