import * as Dialog from '@radix-ui/react-dialog';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import type { ReactNode } from 'react';
import { Button } from './Button';

interface DrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function Drawer({ open, onOpenChange, title, subtitle, children, footer }: DrawerProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open ? (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[90] bg-surface-900/35 backdrop-blur-sm" />
            </Dialog.Overlay>
            <Dialog.Content asChild>
              <motion.div initial={{ y: '100%', opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: '100%', opacity: 0 }} transition={{ type: 'spring', stiffness: 320, damping: 32 }} className="fixed bottom-0 left-0 right-0 z-[100] flex max-h-[90vh] flex-col rounded-t-[24px] border border-white/10 bg-white/80 shadow-xl backdrop-blur-2xl dark:bg-surface-0/95 sm:hidden">
                <div className="flex items-start justify-between border-b border-surface-300/60 px-5 py-4 dark:border-white/10">
                  <div>
                    <Dialog.Title className="text-lg font-semibold text-surface-900 dark:text-white">{title}</Dialog.Title>
                    {subtitle ? <Dialog.Description className="mt-1 text-sm text-surface-600 dark:text-white/55">{subtitle}</Dialog.Description> : null}
                  </div>
                  <Dialog.Close asChild>
                    <Button variant="ghost" size="sm" iconOnly aria-label="Close drawer">
                      <X className="h-4 w-4" />
                    </Button>
                  </Dialog.Close>
                </div>
                <div className="flex-1 overflow-y-auto px-5 py-4">{children}</div>
                {footer ? <div className="flex justify-end gap-2 border-t border-surface-300/60 px-5 py-4 dark:border-white/10">{footer}</div> : null}
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        ) : null}
      </AnimatePresence>
    </Dialog.Root>
  );
}
