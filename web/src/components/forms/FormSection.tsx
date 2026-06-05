import { motion } from 'framer-motion';
import { ChevronDown, PencilLine } from 'lucide-react';
import { useState, type ReactNode } from 'react';
import { Button } from '@components/ui';
import { cn } from '@utils/utils';

interface FormSectionProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  defaultOpen?: boolean;
  actions?: ReactNode;
}

export function FormSection({ title, subtitle, children, defaultOpen = true, actions }: FormSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section className="surface-card overflow-hidden">
      <button type="button" className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left" onClick={() => setOpen((current) => !current)}>
        <div>
          <h3 className="text-sm font-semibold text-surface-900 dark:text-white">{title}</h3>
          {subtitle ? <p className="mt-1 text-xs text-surface-600 dark:text-white/50">{subtitle}</p> : null}
        </div>
        <div className="flex items-center gap-2">
          {actions ?? <Button variant="ghost" size="xs" iconLeft={<PencilLine className="h-3.5 w-3.5" />}>Edit</Button>}
          <ChevronDown className={cn('h-4 w-4 text-surface-500 transition-transform dark:text-white/45', open && 'rotate-180')} />
        </div>
      </button>
      {open ? (
        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="border-t border-surface-300/60 px-5 py-5 dark:border-white/10">
          {children}
        </motion.div>
      ) : null}
    </section>
  );
}
