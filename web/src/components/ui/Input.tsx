import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';
import { cn } from '@utils/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  helperText?: string;
  error?: string;
  required?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, helperText, error, required, leftIcon, rightIcon, className, id, ...props },
  ref
) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-');

  return (
    <label htmlFor={inputId} className="flex w-full flex-col gap-1.5 text-sm">
      <span className="flex items-center gap-1 font-medium text-text-secondary dark:text-text-primary/90">
        {label}
        {required ? <span className="h-1.5 w-1.5 rounded-full bg-danger-500" aria-hidden="true" /> : null}
      </span>
      <span className="relative flex items-center">
        {leftIcon ? <span className="pointer-events-none absolute left-3 text-text-tertiary dark:text-text-tertiary">{leftIcon}</span> : null}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'input-base',
            leftIcon && 'pl-12',
            rightIcon && 'pr-10',
            error && 'border-danger-500 dark:border-danger-500 focus:border-danger-500 dark:focus:border-danger-500 focus:ring-danger-500/15 dark:focus:ring-danger-500/15',
            className
          )}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-help` : undefined}
          {...props}
        />
        {rightIcon ? <span className="pointer-events-none absolute right-3 text-text-tertiary dark:text-text-tertiary">{rightIcon}</span> : null}
      </span>
      {error ? <span id={`${inputId}-error`} className="text-xs text-danger-700 dark:text-rose-300">{error}</span> : null}
      {!error && helperText ? <span id={`${inputId}-help`} className="text-xs text-text-tertiary dark:text-text-tertiary">{helperText}</span> : null}
    </label>
  );
});
