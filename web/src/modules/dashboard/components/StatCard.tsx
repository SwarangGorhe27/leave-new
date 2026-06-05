import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { cn } from '@utils/utils';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: string;
    positive: boolean;
  };
  color: string;
}

export function StatCard({ label, value, icon, trend, color }: StatCardProps) {
  return (
    <div className="surface-card group overflow-hidden border border-transparent dark:hover:border-white/10">
      <div className="relative px-5 py-5">
        {/* Background gradient on hover */}
        <div className="absolute inset-0 opacity-0 transition-opacity group-hover:opacity-100 bg-gradient-to-br from-surface-50 to-transparent dark:from-white/5 dark:to-transparent" />

        <div className="relative">
          {/* Icon container */}
          <div
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-lg mb-3',
              color
            )}
          >
            {icon}
          </div>

          {/* Label */}
          <p className="text-xs font-medium text-surface-500 dark:text-white/60">
            {label}
          </p>

          {/* Value */}
          <p className="mt-2 text-2xl font-bold text-surface-900 dark:text-white">
            {value}
          </p>

          {/* Trend */}
          {trend && (
            <div
              className={cn(
                'mt-3 inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium',
                trend.positive
                  ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400'
                  : 'bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400'
              )}
            >
              {trend.positive ? (
                <ArrowUpRight className="h-3 w-3" />
              ) : (
                <ArrowDownRight className="h-3 w-3" />
              )}
              {trend.value}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="surface-card rounded-xl px-5 py-5">
      <div className="animate-pulse space-y-2">
        <div className="h-10 w-10 rounded-lg bg-surface-200 dark:bg-white/10" />
        <div className="h-3 w-20 rounded bg-surface-200 dark:bg-white/10" />
        <div className="h-6 w-16 rounded bg-surface-200 dark:bg-white/10" />
      </div>
    </div>
  );
}
