import { cn } from '@utils/utils';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function EmptyState({ title, description, icon, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-xl border border-surface-200 bg-surface-50 px-6 py-10 text-center',
        'dark:border-white/5 dark:bg-white/2.5',
        className,
      )}
    >
      {icon ? <div className="text-surface-400/60 dark:text-white/30">{icon}</div> : null}
      <p className="mt-3 text-sm font-medium text-surface-700 dark:text-white/70">{title}</p>
      {description ? (
        <p className="mt-1 text-xs text-surface-500 dark:text-white/45">{description}</p>
      ) : null}
    </div>
  );
}

