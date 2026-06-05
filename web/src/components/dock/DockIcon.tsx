import { AnimatePresence, motion } from 'framer-motion';
import { Lock } from 'lucide-react';
import { useRef, useState } from 'react';
import React from 'react';
import { Tooltip } from '@components/ui/Tooltip';
import { useUIStore } from '@store/uiStore';
import type { DockModule } from '@store/dockStore';
import { cn } from '@utils/utils';
import { useDockMotionContext } from './DockContext';
import { useMagnification } from './useMagnification';

interface DockIconProps {
  module: DockModule;
  active: boolean;
}

export function DockIcon({ module, active }: DockIconProps) {
  const { openModule, navigateTo } = useUIStore((state) => ({
    openModule: state.openModule,
    navigateTo: state.navigateTo,
  }));
  const { mouseX } = useDockMotionContext();
  const ref = useRef<HTMLButtonElement>(null);
  const { scale, y, width } = useMagnification(ref, mouseX);
  const [hovered, setHovered] = useState(false);
  const Icon = module.icon as React.ComponentType<{ className?: string }>;

  function handleClick() {
    if (module.locked) return;
    if (module.key === 'dashboard') {
      navigateTo('dashboard');
    } else if (module.key === 'profile') {
      navigateTo('my-profile');
    } else {
      openModule(module.key);
    }
  }

  return (
    <Tooltip content={module.locked ? 'Upgrade plan' : module.label} delayDuration={600}>
      <motion.button
        ref={ref}
        type="button"
        style={{ width }}
        className="relative flex flex-col items-center justify-end gap-1.5 pb-1 outline-none"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        onClick={handleClick}
      >
        <motion.div
          style={{ scale, y }}
          whileTap={{
            scale: 0.8,
            transition: { type: 'spring', stiffness: 400, damping: 10 }
          }}
          className="relative"
        >
          <div
            className={cn(
              'relative flex h-[48px] w-[48px] items-center justify-center rounded-[12px] bg-gradient-to-br text-white shadow-lg transition-all duration-300 ring-1 ring-white/10 inset',
              module.colorClass,
              module.locked && 'grayscale opacity-60',
              active && 'ring-2 ring-white/30 ring-offset-2 ring-offset-transparent'
            )}
            style={{
              boxShadow: hovered && !module.locked
                ? `0 12px 24px -6px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.2)`
                : '0 4px 10px -4px rgba(0,0,0,0.3)',
            }}
          >
            <Icon className="h-[26px] w-[26px] drop-shadow-md" />
            {module.locked ? (
              <span className="absolute inset-0 flex items-center justify-center rounded-[12px] bg-black/20">
                <Lock className="h-3 w-3" />
              </span>
            ) : null}
            {/* Subtle gloss effect */}
            <div className="absolute inset-x-0 top-0 h-[40%] rounded-t-[12px] bg-gradient-to-b from-white/20 to-transparent" />
          </div>
        </motion.div>

        {/* Active dot indicator - tiny and centered as per macOS */}
        <div className="h-[2px] mt-1 flex items-center justify-center">
          <AnimatePresence>
            {active && (
              <motion.span
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                className="h-[3px] w-[3px] rounded-full bg-white/80"
              />
            )}
          </AnimatePresence>
        </div>
      </motion.button>
    </Tooltip>
  );
}
