import { Clock } from 'lucide-react';
import { EmptyState } from './kit/EmptyState';

interface LeaveSnapshotProps {
  pendingApprovals: number;
  onLeaveToday: number;
  isLoading?: boolean;
}

export function LeaveSnapshot({ pendingApprovals, onLeaveToday, isLoading }: LeaveSnapshotProps) {
  return (
    <div className="surface-card rounded-2xl px-6 py-6">
      {/* Header */}
      <div className="mb-5">
        <h3 className="text-sm font-semibold text-surface-900 dark:text-white">Leave Snapshot</h3>
        <p className="mt-1 text-xs text-surface-500 dark:text-white/50">Approvals + today’s leave</p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <div key={i} className="space-y-2">
              <div className="h-3 w-20 animate-pulse rounded bg-surface-200 dark:bg-white/10" />
              <div className="h-6 w-12 animate-pulse rounded bg-surface-200 dark:bg-white/10" />
            </div>
          ))}
        </div>
      ) : pendingApprovals === 0 && onLeaveToday === 0 ? (
        <EmptyState
          title="No leave today"
          description="No approvals pending, and nobody is on leave today."
          icon={<Clock className="h-9 w-9 text-surface-400/50 dark:text-white/25" />}
        />
      ) : (
        <div className="space-y-4">
          {/* Pending approvals */}
          <div className="rounded-lg border border-surface-100 bg-surface-50 px-4 py-3 dark:border-white/5 dark:bg-white/2.5">
            <div className="flex items-center justify-between">
              <p className="text-xs font-medium text-surface-600 dark:text-white/70">
                Pending Approvals
              </p>
              {pendingApprovals > 0 && (
                <div className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-red-100 dark:bg-red-500/20">
                  <span className="text-xs font-semibold text-red-700 dark:text-red-300">
                    {pendingApprovals}
                  </span>
                </div>
              )}
            </div>
            <p className="mt-2 text-lg font-semibold text-surface-900 dark:text-white">
              {pendingApprovals}
              {pendingApprovals === 1 ? (
                <span className="text-sm font-normal text-surface-500 dark:text-white/50 ml-1">
                  application
                </span>
              ) : (
                <span className="text-sm font-normal text-surface-500 dark:text-white/50 ml-1">
                  applications
                </span>
              )}
            </p>
          </div>

          {/* On leave today */}
          <div className="rounded-lg border border-surface-100 bg-surface-50 px-4 py-3 dark:border-white/5 dark:bg-white/2.5">
            <p className="text-xs font-medium text-surface-600 dark:text-white/70">
              On Leave Today
            </p>
            <p className="mt-2 text-lg font-semibold text-surface-900 dark:text-white">
              {onLeaveToday}
              <span className="text-sm font-normal text-surface-500 dark:text-white/50 ml-1">
                {onLeaveToday === 1 ? 'employee' : 'employees'}
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
