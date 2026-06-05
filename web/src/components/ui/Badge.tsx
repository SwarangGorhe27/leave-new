import type { ReactNode } from 'react';
import { cn } from '@utils/utils';

const variants = {
  success: 'bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-emerald-300',
  warning: 'bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-amber-300',
  danger: 'bg-danger-50 text-danger-700 dark:bg-danger-500/15 dark:text-rose-300',
  info: 'bg-info-50 text-info-700 dark:bg-info-500/15 dark:text-sky-300',
  neutral: 'bg-surface-100 text-surface-700 dark:bg-white/5 dark:text-white/70',
  brand: 'bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-200',
  ghost: 'bg-transparent text-surface-600 dark:text-white/55'
} as const;

const sizes = {
  sm: 'h-5 px-1.5 text-2xs',
  md: 'h-6 px-2 text-xs'
} as const;

interface BadgeProps {
  children: ReactNode;
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
  dot?: boolean;
  icon?: ReactNode;
  className?: string;
}

export function Badge({ children, variant = 'neutral', size = 'md', dot, icon, className }: BadgeProps) {
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-md font-medium', variants[variant], sizes[size], className)}>
      {dot ? <span className="h-1.5 w-1.5 rounded-full bg-current opacity-70" aria-hidden="true" /> : null}
      {icon ? <span className="flex h-2.5 w-2.5 items-center justify-center [&_svg]:h-2.5 [&_svg]:w-2.5">{icon}</span> : null}
      {children}
    </span>
  );
}
