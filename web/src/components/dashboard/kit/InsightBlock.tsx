import { cn } from '@utils/utils';

interface InsightBlockProps {
  icon?: React.ReactNode;
  label?: string;
  insight: string;
  rightSlot?: React.ReactNode;
  className?: string;
}

export function InsightBlock({ icon, label, insight, rightSlot, className }: InsightBlockProps) {
  return (
    <div
      className={cn(
        'flex items-start justify-between gap-3 rounded-xl border border-surface-100 bg-surface-50 px-4 py-3',
        'dark:border-white/5 dark:bg-white/2.5',
        className,
      )}
    >
      <div className="flex min-w-0 items-start gap-3">
        {icon ? (
          <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-surface-200 text-surface-600 dark:bg-white/10 dark:text-white/60">
            {icon}
          </div>
        ) : null}
        <div className="min-w-0">
          {label ? (
            <p className="text-2xs font-medium text-surface-500 dark:text-white/50">{label}</p>
          ) : null}
          <p className="mt-0.5 text-xs font-medium text-surface-700 dark:text-white/70">
            {insight}
          </p>
        </div>
      </div>
      {rightSlot ? <div className="shrink-0">{rightSlot}</div> : null}
    </div>
  );
}

