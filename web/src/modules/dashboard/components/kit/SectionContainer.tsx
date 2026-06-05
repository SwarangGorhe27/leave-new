import { cn } from '@utils/utils';

interface SectionContainerProps {
  title: string;
  description?: string;
  rightSlot?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}

export function SectionContainer({
  title,
  description,
  rightSlot,
  className,
  children,
}: SectionContainerProps) {
  return (
    <section className={cn('surface-card rounded-2xl px-6 py-6', className)}>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">{title}</h2>
          {description ? (
            <p className="mt-1 text-xs text-surface-500 dark:text-white/50">{description}</p>
          ) : null}
        </div>
        {rightSlot ? <div className="shrink-0">{rightSlot}</div> : null}
      </div>
      {children}
    </section>
  );
}

