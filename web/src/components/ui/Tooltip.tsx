import * as RadixTooltip from '@radix-ui/react-tooltip';
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';
import { cn } from '@utils/utils';

interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  delayDuration?: number;
  side?: 'top' | 'right' | 'bottom' | 'left';
}

export function Tooltip({ content, children, delayDuration = 300, side = 'top' }: TooltipProps) {
  return (
    <RadixTooltip.Provider delayDuration={delayDuration} skipDelayDuration={100}>
      <RadixTooltip.Root>
        <RadixTooltip.Trigger asChild>{children}</RadixTooltip.Trigger>
        <RadixTooltip.Portal>
          <RadixTooltip.Content side={side} sideOffset={10} asChild>
            <motion.div
              initial={{ opacity: 0, y: 4, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 4, scale: 0.98 }}
              className={cn(
                'z-50 max-w-[220px] rounded-lg border border-surface-300/70 bg-surface-900 px-2.5 py-1.5 text-xs text-white shadow-lg',
                'dark:border-white/10 dark:bg-surface-0/96'
              )}
            >
              {content}
              <RadixTooltip.Arrow className="fill-surface-900 dark:fill-[rgba(15,17,23,0.96)]" />
            </motion.div>
          </RadixTooltip.Content>
        </RadixTooltip.Portal>
      </RadixTooltip.Root>
    </RadixTooltip.Provider>
  );
}
