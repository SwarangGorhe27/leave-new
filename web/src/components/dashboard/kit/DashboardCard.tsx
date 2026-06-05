import { cn } from '@utils/utils';

type DashboardCardTone = 'brand' | 'success' | 'warning' | 'info';

const toneStyles: Record<DashboardCardTone, { chip: string; ring: string }> = {
  brand: { chip: 'bg-brand-50 dark:bg-brand-500/10', ring: 'focus-visible:ring-brand-400/40' },
  success: { chip: 'bg-[#EEF4FF] dark:bg-[#8B5CF6]/10', ring: 'focus-visible:ring-indigo-400/35' },
  warning: { chip: 'bg-[#EEF4FF] dark:bg-[#6366F1]/10', ring: 'focus-visible:ring-violet-400/35' },
  info: { chip: 'bg-[#EEF4FF] dark:bg-[#3B82F6]/10', ring: 'focus-visible:ring-blue-400/30' },
};

interface DashboardCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  tone: DashboardCardTone;
  hint?: string;
  onClick?: () => void;
}

export function DashboardCard({ label, value, icon, tone, hint, onClick }: DashboardCardProps) {
  const styles = toneStyles[tone];
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'surface-card group relative w-full overflow-hidden text-left',
        'focus-visible:outline-none focus-visible:ring-2',
        styles.ring,
        'hover:drop-shadow-[0_0_18px_rgba(99,102,241,0.18)]',
      )}
    >
      <div className="absolute inset-0 opacity-0 transition-opacity duration-200 group-hover:opacity-100 bg-gradient-to-br from-surface-50 to-transparent dark:from-white/5 dark:to-transparent" />
      <div className="relative px-5 py-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-medium text-surface-500 dark:text-white/60">{label}</p>
            <p className="mt-2 text-2xl font-bold text-surface-900 dark:text-white">{value}</p>
            {hint ? (
              <p className="mt-2 text-2xs font-medium text-surface-500 dark:text-white/45">{hint}</p>
            ) : null}
          </div>
          <div
            className={cn(
              'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-110',
              styles.chip,
              'ring-1 ring-white/30 dark:ring-white/10',
            )}
          >
            {icon}
          </div>
        </div>
      </div>
    </button>
  );
}

export function DashboardCardSkeleton() {
  return (
    <div className="surface-card rounded-2xl px-5 py-5">
      <div className="animate-pulse space-y-2">
        <div className="h-3 w-24 rounded bg-surface-200 dark:bg-white/10" />
        <div className="h-7 w-16 rounded bg-surface-200 dark:bg-white/10" />
        <div className="h-3 w-28 rounded bg-surface-200 dark:bg-white/10" />
      </div>
    </div>
  );
}

