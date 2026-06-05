import type { ReactNode } from 'react';

interface FormFieldProps {
  label: string;
  description?: string;
  required?: boolean;
  children: ReactNode;
  className?: string;
  error?: string;
  hint?: string;
}

export function FormField({ label, description, required, children, className, error, hint }: FormFieldProps) {
  return (
    <div className={`space-y-2 ${className || ''}`}>
      <div className="space-y-0.5">
        <div className="flex items-center gap-1 text-sm font-medium text-foreground">
          <span>{label}</span>
          {required ? (
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-destructive" aria-label="required" />
          ) : null}
        </div>
        {description ? (
          <p className="text-xs text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {children}
      {error ? (
        <p className="text-xs font-medium text-destructive mt-1">{error}</p>
      ) : hint ? (
        <p className="text-xs text-muted-foreground mt-1">{hint}</p>
      ) : null}
    </div>
  );
}
