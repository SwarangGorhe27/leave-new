import { Loader2 } from 'lucide-react';
import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { cn } from '@utils/utils';
import { Tooltip } from './Tooltip';

const variants = {
  primary:
    'bg-brand-500 text-white hover:bg-brand-600 active:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600',
  secondary:
    'border border-surface-200 bg-surface-0 text-surface-700 hover:bg-surface-50 hover:border-surface-300 dark:border-white/10 dark:bg-white/5 dark:text-white/75 dark:hover:bg-white/10 dark:hover:border-white/15',
  ghost:
    'bg-transparent text-surface-600 hover:bg-surface-100 hover:text-surface-800 dark:text-white/60 dark:hover:bg-white/6 dark:hover:text-white/85',
  danger:
    'bg-danger-500 text-white hover:bg-danger-700 dark:bg-danger-500/90 dark:hover:bg-danger-600',
  link:
    'bg-transparent px-0 text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300 underline-offset-4 hover:underline',
} as const;

const sizes = {
  xs: 'h-7 px-2.5 text-xs rounded-lg gap-1',
  sm: 'h-9 px-3 text-sm rounded-xl gap-1.5',
  md: 'h-10 px-3.5 text-sm rounded-xl gap-1.5',
  lg: 'h-11 px-5 text-base rounded-xl gap-2',
} as const;

const shadowMap = {
  primary: '0 1px 3px rgba(59,91,219,0.25), inset 0 1px 0 rgba(255,255,255,0.1)',
  secondary: '0 1px 2px rgba(0,0,0,0.04)',
  ghost: 'none',
  danger: '0 1px 3px rgba(239,68,68,0.25)',
  link: 'none',
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
  loading?: boolean;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
  fullWidth?: boolean;
  iconOnly?: boolean;
  tooltip?: ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    className,
    children,
    variant = 'primary',
    size = 'md',
    loading,
    disabled,
    iconLeft,
    iconRight,
    fullWidth,
    iconOnly,
    tooltip,
    style,
    ...props
  },
  ref,
) {
  const button = (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center font-semibold transition-all duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400/50 focus-visible:ring-offset-1',
        'disabled:pointer-events-none disabled:opacity-45',
        'active:scale-[0.97]',
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        iconOnly && 'aspect-square px-0',
        className,
      )}
      style={{ boxShadow: shadowMap[variant], ...style }}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : iconLeft}
      {loading ? 'Loading…' : children}
      {!loading ? iconRight : null}
    </button>
  );

  if (tooltip && iconOnly) {
    return <Tooltip content={tooltip}>{button}</Tooltip>;
  }

  return button;
});
