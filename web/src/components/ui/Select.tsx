import * as RadixSelect from '@radix-ui/react-select';
import { Check, ChevronDown } from 'lucide-react';
import type { ReactNode } from 'react';
import { cn } from '@utils/utils';

export interface SelectOption {
  label: string;
  value: string;
  description?: string;
}

interface SelectProps {
  label: string;
  value?: string;
  onValueChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  helperText?: string;
  error?: string;
  required?: boolean;
  leftIcon?: ReactNode;
}

export function Select({ label, value, onValueChange, options, placeholder = 'Select', helperText, error, required, leftIcon }: SelectProps) {
  const inputId = label.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="flex w-full flex-col gap-1.5 text-sm">
      <label htmlFor={inputId} className="flex items-center gap-1 font-medium text-text-secondary dark:text-text-primary/90">
        {label}
        {required ? <span className="h-1.5 w-1.5 rounded-full bg-danger-500" aria-hidden="true" /> : null}
      </label>
      <RadixSelect.Root value={value} onValueChange={onValueChange}>
        <RadixSelect.Trigger
          id={inputId}
          className={cn(
            'input-base flex items-center justify-between gap-2 text-left',
            leftIcon && 'pl-10',
            error && 'border-danger-500 focus:ring-danger-500/15'
          )}
          aria-invalid={Boolean(error)}
        >
          {leftIcon ? <span className="pointer-events-none absolute ml-3 text-text-tertiary">{leftIcon}</span> : null}
          <RadixSelect.Value placeholder={placeholder} />
          <RadixSelect.Icon>
            <ChevronDown className="h-4 w-4 text-text-tertiary" />
          </RadixSelect.Icon>
        </RadixSelect.Trigger>
        <RadixSelect.Portal>
          <RadixSelect.Content position="popper" sideOffset={8} className="z-50 min-w-[240px] overflow-hidden rounded-xl border border-surface-200 bg-surface-0 p-1 shadow-lg dark:border-white/10 dark:bg-surface-100/95 backdrop-blur-xl">
            <RadixSelect.Viewport>
              {options.map((option) => (
                <RadixSelect.Item key={option.value} value={option.value} className="flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-sm text-text-secondary outline-none focus:bg-surface-50 dark:focus:bg-white/5 data-[state=checked]:text-text-primary">
                  <div>
                    <RadixSelect.ItemText className="font-medium">{option.label}</RadixSelect.ItemText>
                    {option.description ? <p className="text-xs text-text-tertiary mt-0.5">{option.description}</p> : null}
                  </div>
                  <RadixSelect.ItemIndicator>
                    <Check className="h-4 w-4 text-brand-500" />
                  </RadixSelect.ItemIndicator>
                </RadixSelect.Item>
              ))}
            </RadixSelect.Viewport>
          </RadixSelect.Content>
        </RadixSelect.Portal>
      </RadixSelect.Root>
      {error ? <span className="text-xs text-danger-700 dark:text-rose-300">{error}</span> : null}
      {!error && helperText ? <span className="text-xs text-text-tertiary">{helperText}</span> : null}
    </div>
  );
}
