import { forwardRef, type ReactNode, type TextareaHTMLAttributes } from 'react';
import { cn } from '@utils/utils';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  helperText?: string;
  error?: string;
  required?: boolean;
  rightAddon?: ReactNode;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { label, helperText, error, required, className, id, maxLength, value, rightAddon, ...props },
  ref
) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-');
  const count = typeof value === 'string' ? value.length : 0;

  return (
    <label htmlFor={inputId} className="flex w-full flex-col gap-1.5 text-sm">
      <span className="flex items-center gap-1 font-medium text-surface-800 dark:text-white/85">
        {label}
        {required ? <span className="h-1.5 w-1.5 rounded-full bg-danger-500" aria-hidden="true" /> : null}
      </span>
      <div className="relative">
        <textarea
          ref={ref}
          id={inputId}
          maxLength={maxLength}
          value={value}
          className={cn(
            'input-base min-h-[112px] resize-y pr-12',
            error && 'border-danger-500 focus:border-danger-500 focus:ring-danger-500/15',
            className
          )}
          aria-invalid={Boolean(error)}
          {...props}
        />
        {rightAddon ? <span className="absolute right-3 top-3 text-surface-500 dark:text-white/45">{rightAddon}</span> : null}
      </div>
      <div className="flex items-center justify-between gap-3 text-xs">
        {error ? <span className="text-danger-700 dark:text-rose-300">{error}</span> : <span className="text-surface-600 dark:text-white/50">{helperText}</span>}
        {maxLength ? <span className="text-surface-500 dark:text-white/40">{count}/{maxLength}</span> : null}
      </div>
    </label>
  );
});
