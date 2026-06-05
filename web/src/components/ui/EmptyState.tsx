import type { LucideIcon } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  ctaLabel?: string;
  onCta?: () => void;
}

export function EmptyState({ icon: Icon, title, description, ctaLabel, onCta }: EmptyStateProps) {
  return (
    <div className="flex min-h-[240px] flex-col items-center justify-center gap-4 px-6 py-10 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-100 text-surface-500 dark:bg-white/5 dark:text-white/40">
        <Icon className="h-8 w-8" />
      </div>
      <div className="space-y-1">
        <h3 className="text-lg font-semibold text-surface-900 dark:text-white">{title}</h3>
        <p className="mx-auto max-w-md text-sm text-surface-600 dark:text-white/60">{description}</p>
      </div>
      {ctaLabel && onCta ? <Button onClick={onCta}>{ctaLabel}</Button> : null}
    </div>
  );
}
