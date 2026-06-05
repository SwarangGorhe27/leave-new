import * as Dialog from '@radix-ui/react-dialog';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import type { ReactNode } from 'react';
import { Button } from './Button';
import { cn } from '@utils/utils';

interface ModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
}

export function Modal({ open, onOpenChange, title, subtitle, children, footer, className }: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open ? (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[90] bg-surface-900/35 backdrop-blur-sm" />
            </Dialog.Overlay>
            <Dialog.Content asChild>
              <motion.div
                initial={{ opacity: 0, scale: 0.96, y: 18 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.96, y: 18 }}
                transition={{ type: 'spring', stiffness: 320, damping: 28 }}
                className={cn('fixed left-1/2 top-1/2 z-[100] w-[min(640px,calc(100vw-2rem))] -translate-x-1/2 -translate-y-1/2 overflow-hidden rounded-3xl border border-white/30 bg-white/80 shadow-xl backdrop-blur-2xl dark:border-white/10 dark:bg-surface-0/92', className)}
              >
                <div className="flex items-start justify-between border-b border-surface-300/60 px-6 py-5 dark:border-white/10">
                  <div>
                    <Dialog.Title className="text-xl font-semibold text-surface-900 dark:text-white">{title}</Dialog.Title>
                    {subtitle ? <Dialog.Description className="mt-1 text-sm text-surface-600 dark:text-white/55">{subtitle}</Dialog.Description> : null}
                  </div>
                  <Dialog.Close asChild>
                    <Button variant="ghost" size="sm" iconOnly aria-label="Close modal">
                      <X className="h-4 w-4" />
                    </Button>
                  </Dialog.Close>
                </div>
                <div className="max-h-[70vh] overflow-y-auto px-6 py-5">{children}</div>
                {footer ? <div className="sticky bottom-0 flex justify-end gap-2 border-t border-surface-300/60 bg-white/80 px-6 py-4 backdrop-blur-xl dark:border-white/10 dark:bg-surface-0/92">{footer}</div> : null}
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        ) : null}
      </AnimatePresence>
    </Dialog.Root>
  );
}
