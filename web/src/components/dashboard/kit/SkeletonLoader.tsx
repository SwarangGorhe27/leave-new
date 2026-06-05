import { cn } from '@utils/utils';

export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded bg-surface-200 dark:bg-white/10', className)} />;
}

export function SkeletonList({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          // eslint-disable-next-line react/no-array-index-key
          key={i}
          className="flex items-start gap-4 rounded-xl border border-surface-200 bg-surface-50 px-4 py-3 dark:border-white/5 dark:bg-white/2.5"
        >
          <SkeletonBlock className="h-9 w-9 shrink-0 rounded-lg" />
          <div className="min-w-0 flex-1 space-y-2">
            <SkeletonBlock className="h-3 w-44" />
            <SkeletonBlock className="h-2 w-28" />
          </div>
          <SkeletonBlock className="h-6 w-8 rounded-full" />
        </div>
      ))}
    </div>
  );
}

