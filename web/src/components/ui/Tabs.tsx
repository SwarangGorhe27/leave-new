import * as RadixTabs from '@radix-ui/react-tabs';
import { AnimatePresence, motion } from 'framer-motion';
import { useState, type ReactNode } from 'react';
import { cn } from '@utils/utils';

export interface TabItem {
  label: string;
  value: string;
  content: ReactNode;
}

interface TabsProps {
  items: TabItem[];
  defaultValue?: string;
  value?: string;
  onChange?: (value: string) => void;
  variant?: 'underline' | 'pills' | 'boxed';
  className?: string;
}

const listVariants = {
  underline: 'border-b border-surface-200 dark:border-white/10',
  pills: 'rounded-xl bg-surface-100/50 p-1 dark:bg-white/5',
  boxed: 'rounded-xl border border-surface-200 p-1 dark:border-white/10 bg-surface-50/50 dark:bg-white/5'
} as const;

const triggerVariants = {
  underline: 'relative rounded-none px-2 pb-3.5 pt-2 text-sm font-semibold text-surface-500 hover:text-surface-700 data-[state=active]:text-brand-600 dark:text-white/40 dark:hover:text-white/70 dark:data-[state=active]:text-brand-400 transition-colors',
  pills: 'relative rounded-lg px-3 py-2 text-sm font-medium text-surface-600 hover:text-surface-900 data-[state=active]:text-surface-900 dark:text-white/50 dark:hover:text-white/80 dark:data-[state=active]:text-white transition-colors',
  boxed: 'relative rounded-lg px-3 py-2 text-sm font-medium text-surface-600 hover:text-surface-900 data-[state=active]:text-surface-900 dark:text-white/50 dark:hover:text-white/80 dark:data-[state=active]:text-white transition-colors'
} as const;

export function Tabs({ items, defaultValue, value: controlledValue, onChange, variant = 'underline', className }: TabsProps) {
  const initialValue = defaultValue ?? items[0]?.value;
  const [internalValue, setInternalValue] = useState(initialValue);
  const value = controlledValue ?? internalValue;
  const [mounted, setMounted] = useState<string[]>(initialValue ? [initialValue] : []);

  return (
    <RadixTabs.Root
      value={value}
      onValueChange={(nextValue) => {
        setInternalValue(nextValue);
        onChange?.(nextValue);
        setMounted((current) => (current.includes(nextValue) ? current : [...current, nextValue]));
      }}
      className={className}
    >
      <RadixTabs.List className={cn('flex gap-2', listVariants[variant])}>
        {items.map((item) => (
          <RadixTabs.Trigger key={item.value} value={item.value} className={cn('outline-none', triggerVariants[variant])}>
            {value === item.value ? (
              <motion.span
                layoutId={`tab-indicator-${variant}`}
                className={cn(
                  'absolute z-0',
                  variant === 'underline' ? '-bottom-[1px] inset-x-0 h-0.5 bg-brand-500 dark:bg-brand-400 rounded-t-full' : 'inset-0 bg-white dark:bg-surface-200 rounded-lg shadow-sm border border-surface-200/50 dark:border-white/10'
                )}
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
              />
            ) : null}
            <span className="relative z-10">{item.label}</span>
          </RadixTabs.Trigger>
        ))}
      </RadixTabs.List>
      {items.map((item) => (
        <RadixTabs.Content key={item.value} value={item.value} className="pt-5 outline-none">
          <AnimatePresence mode="wait">
            {mounted.includes(item.value) && value === item.value ? (
              <motion.div key={item.value} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.2, ease: "easeOut" }}>
                {item.content}
              </motion.div>
            ) : null}
          </AnimatePresence>
        </RadixTabs.Content>
      ))}
    </RadixTabs.Root>
  );
}
