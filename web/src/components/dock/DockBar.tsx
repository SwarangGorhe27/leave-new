import { motion, useMotionValue } from 'framer-motion';
import React, { useEffect, useMemo, useState, useRef } from 'react';
import { useDockStore } from '@store/dockStore';
import { useAuthStore } from '@store/authStore';
import { useUIStore, ESS_MODULES } from '@store/uiStore';
import { usePermissions } from '@hooks/usePermissions';
import { DockMotionContext } from './DockContext';
import { DockIcon } from './DockIcon';
import { cn } from '@utils/utils';

export function DockBar() {
  const mouseX = useMotionValue(-1000);
  const modules = useDockStore((state) => state.modules);
  const { activeModule, panelOpen, currentPage } = useUIStore((state) => ({
    activeModule: state.activeModule,
    panelOpen: state.panelOpen,
    currentPage: state.currentPage,
  }));
  const userPermissions = useAuthStore((state) => state.user.permissions);
  const portal = useUIStore((state) => state.portal);
  const { can } = usePermissions();
  const [scrolled, setScrolled] = useState(false);
  const [isScrolling, setIsScrolling] = useState(false);
  const scrollTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 20);
      setIsScrolling(true);
      if (scrollTimerRef.current) clearTimeout(scrollTimerRef.current);
      scrollTimerRef.current = setTimeout(() => setIsScrolling(false), 600);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      if (scrollTimerRef.current) clearTimeout(scrollTimerRef.current);
    };
  }, []);

  const visibleModules = useMemo(() => {
    const portalFiltered = portal === 'ess'
      ? modules.filter((m) => ESS_MODULES.includes(m.key))
      : modules;
    return portalFiltered.filter(
      (module) => module.locked || module.key === 'dashboard' || can('view', module.key) || userPermissions.includes(module.permission),
    );
  }, [can, modules, userPermissions, portal]);

  return (
    <DockMotionContext.Provider value={{ mouseX }}>
      <motion.div
        className="fixed inset-x-0 bottom-4 z-50 flex justify-center px-4"
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{
          type: 'spring',
          stiffness: 260,
          damping: 20,
          delay: 0.1
        }}
      >
        <motion.div
          onMouseMove={(event) => {
            if (window.innerWidth > 768) {
              mouseX.set(event.clientX);
            }
          }}
          onMouseLeave={() => mouseX.set(-1000)}
          className={cn(
            "flex items-end rounded-[24px] px-2 py-2",
            "bg-[#2B1555] shadow-[0_20px_60px_-10px_rgba(0,0,0,0.5)] ring-1 ring-white/20",
            "dark:bg-[#2B1555] dark:ring-white/20",
            "transition-all duration-500 ease-out"
          )}
        >
          {visibleModules.map((module, index) => (
            <React.Fragment key={module.key}>
              {/* Divider before secondary modules like in macOS */}
              {(module.key === 'ai' || module.key === 'settings') && (
                <div className="mx-1.5 mb-2.5 h-8 w-[1px] bg-white/25 self-end" />
              )}
              <DockIcon
                module={{
                  ...module,
                  label: (portal === 'ess' && module.key === 'payroll') ? 'Salary' : module.label
                }}
                active={
                  module.key === 'dashboard'
                    ? (!panelOpen && currentPage === 'dashboard')
                    : module.key === 'profile'
                    ? (!panelOpen && currentPage === 'my-profile')
                    : (panelOpen && activeModule === module.key)
                }
              />
            </React.Fragment>
          ))}
        </motion.div>
      </motion.div>
    </DockMotionContext.Provider>
  );
}
