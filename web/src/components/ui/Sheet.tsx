import * as Dialog from '@radix-ui/react-dialog';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import type { ReactNode } from 'react';
import { Button } from './Button';

interface SheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function Sheet({ open, onOpenChange, title, subtitle, children, footer }: SheetProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open ? (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[90] bg-surface-900/30 backdrop-blur-sm" />
            </Dialog.Overlay>
            <Dialog.Content asChild>
              <motion.div initial={{ x: '100%', opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: '100%', opacity: 0 }} transition={{ type: 'spring', stiffness: 320, damping: 32 }} className="fixed right-0 top-0 z-[100] flex h-full w-full max-w-[480px] flex-col border-l border-white/10 bg-white/80 shadow-xl backdrop-blur-2xl dark:bg-surface-0/92 sm:max-w-[480px]">
                <div className="flex items-start justify-between border-b border-surface-300/60 px-6 py-5 dark:border-white/10">
                  <div>
                    <Dialog.Title className="text-xl font-semibold text-surface-900 dark:text-white">{title}</Dialog.Title>
                    {subtitle ? <Dialog.Description className="mt-1 text-sm text-surface-600 dark:text-white/55">{subtitle}</Dialog.Description> : null}
                  </div>
                  <Dialog.Close asChild>
                    <Button variant="ghost" size="sm" iconOnly aria-label="Close panel">
                      <X className="h-4 w-4" />
                    </Button>
                  </Dialog.Close>
                </div>
                <div className="flex-1 overflow-y-auto px-6 py-5">{children}</div>
                {footer ? <div className="sticky bottom-0 flex justify-end gap-2 border-t border-surface-300/60 bg-white/80 px-6 py-4 backdrop-blur-xl dark:border-white/10 dark:bg-surface-0/92">{footer}</div> : null}
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        ) : null}
      </AnimatePresence>
    </Dialog.Root>
  );
}
