import * as Dialog from '@radix-ui/react-dialog';
import * as VisuallyHidden from '@radix-ui/react-visually-hidden';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight, BrainCircuit, Clock3, HelpCircle, Search, Settings2 } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Avatar } from './Avatar';
import { useAuthStore } from '@store/authStore';
import { useDockStore } from '@store/dockStore';
import { useUIStore } from '@store/uiStore';

interface PaletteItem {
  id: string;
  group: 'Recent' | 'Employees' | 'Module actions' | 'Settings' | 'Help';
  title: string;
  subtitle?: string;
  meta?: string;
  icon?: React.ReactNode;
  onSelect: () => void;
  keywords: string[];
}

const recentKey = 'hrms-command-recent';

function rankResult(query: string, candidate: string, boost = 0) {
  const normalizedCandidate = candidate.toLowerCase();
  const normalizedQuery = query.toLowerCase();
  if (!normalizedQuery) {
    return 100 + boost;
  }
  if (normalizedCandidate === normalizedQuery) {
    return 1000 + boost;
  }
  if (normalizedCandidate.startsWith(normalizedQuery)) {
    return 700 + boost;
  }
  if (normalizedCandidate.includes(normalizedQuery)) {
    return 400 + boost;
  }
  return 0;
}

export function CommandPalette() {
  const open = useUIStore((state) => state.commandPaletteOpen);
  const setOpen = useUIStore((state) => state.setCommandPaletteOpen);
  const openModule = useUIStore((state) => state.openModule);
  const employees = useAuthStore((state) => state.employees);
  const modules = useDockStore((state) => state.modules);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    const timeout = window.setTimeout(() => setDebouncedQuery(query), 120);
    return () => window.clearTimeout(timeout);
  }, [query]);

  useEffect(() => {
    if (open) {
      window.setTimeout(() => inputRef.current?.focus(), 30);
    }
  }, [open]);

  const items = useMemo<PaletteItem[]>(() => {
    const recent = (() => {
      try {
        return JSON.parse(localStorage.getItem(recentKey) ?? '[]') as Array<{ title: string; module: string }>;
      } catch {
        return [];
      }
    })();

    const recentItems: PaletteItem[] = recent.slice(0, 5).map((item, index) => ({
      id: `recent-${index}`,
      group: 'Recent',
      title: item.title,
      subtitle: 'Recently accessed',
      meta: 'Recent',
      icon: <Clock3 className="h-4 w-4" />,
      onSelect: () => {
        openModule(item.module as never);
        setOpen(false);
      },
      keywords: [item.title, item.module]
    }));

    const employeeItems: PaletteItem[] = employees.map((employee) => ({
      id: employee.id,
      group: 'Employees',
      title: employee.name,
      subtitle: employee.designation,
      meta: employee.code,
      icon: <Avatar name={employee.name} size="sm" />,
      onSelect: () => {
        openModule('employees');
        persistRecent(employee.name, 'employees');
        setOpen(false);
      },
      keywords: [employee.name, employee.designation, employee.code, employee.department]
    }));

    const actionItems: PaletteItem[] = [
      { id: 'apply-leave', group: 'Module actions', title: 'Apply leave', subtitle: 'Leave module', meta: 'L', icon: <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-emerald-500 text-white">L</span>, onSelect: () => selectModule('leave', 'Apply leave'), keywords: ['apply leave', 'leave'] },
      { id: 'view-attendance', group: 'Module actions', title: 'View attendance', subtitle: 'Attendance dashboard', meta: 'A', icon: <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-sky-500 text-white">A</span>, onSelect: () => selectModule('attendance', 'View attendance'), keywords: ['attendance', 'timesheet'] },
      { id: 'run-payroll', group: 'Module actions', title: 'Run payroll', subtitle: 'Payroll workspace', meta: 'P', icon: <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-amber-500 text-white">P</span>, onSelect: () => selectModule('payroll', 'Run payroll'), keywords: ['payroll'] }
    ];

    const settingsItems: PaletteItem[] = [
      { id: 'preferences', group: 'Settings', title: 'Preferences', subtitle: 'Theme and density', meta: 'Settings', icon: <Settings2 className="h-4 w-4" />, onSelect: () => selectModule('settings', 'Preferences'), keywords: ['preferences', 'settings', 'theme'] }
    ];

    const helpItems: PaletteItem[] = [
      { id: 'help', group: 'Help', title: 'Ask AI assistant', subtitle: 'Get help with HR workflows', meta: 'AI', icon: <BrainCircuit className="h-4 w-4" />, onSelect: () => selectModule('ai', 'Ask AI assistant'), keywords: ['help', 'assistant', 'ai'] },
      { id: 'docs', group: 'Help', title: 'Platform help center', subtitle: 'Policies and guides', meta: 'Docs', icon: <HelpCircle className="h-4 w-4" />, onSelect: () => selectModule('documents', 'Platform help center'), keywords: ['help center', 'documentation'] }
    ];

    return [...recentItems, ...employeeItems, ...actionItems, ...settingsItems, ...helpItems];

    function selectModule(module: typeof modules[number]['key'], title: string) {
      openModule(module);
      persistRecent(title, module);
      setOpen(false);
    }

    function persistRecent(title: string, module: string) {
      const current = (() => {
        try {
          return JSON.parse(localStorage.getItem(recentKey) ?? '[]') as Array<{ title: string; module: string }>;
        } catch {
          return [];
        }
      })();
      const next = [{ title, module }, ...current.filter((item) => item.title !== title)].slice(0, 5);
      localStorage.setItem(recentKey, JSON.stringify(next));
    }
  }, [employees, modules, openModule, setOpen]);

  const filteredItems = useMemo(() => {
    return items
      .map((item) => ({
        item,
        score: Math.max(...item.keywords.map((keyword) => rankResult(debouncedQuery, keyword, item.group === 'Recent' ? 100 : 0)))
      }))
      .filter((entry) => entry.score > 0 || !debouncedQuery)
      .sort((left, right) => right.score - left.score)
      .map((entry) => entry.item);
  }, [debouncedQuery, items]);

  const grouped = useMemo(() => {
    const order: PaletteItem['group'][] = ['Recent', 'Employees', 'Module actions', 'Settings', 'Help'];
    return order
      .map((group) => ({ group, items: filteredItems.filter((item) => item.group === group) }))
      .filter((entry) => entry.items.length > 0);
  }, [filteredItems]);

  const flatItems = grouped.flatMap((group) => group.items);

  useEffect(() => {
    setSelectedIndex(0);
  }, [debouncedQuery, open]);

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setSelectedIndex((current) => Math.min(current + 1, Math.max(flatItems.length - 1, 0)));
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setSelectedIndex((current) => Math.max(current - 1, 0));
    }
    if (event.key === 'Enter') {
      event.preventDefault();
      flatItems[selectedIndex]?.onSelect();
    }
    if (event.key === 'Tab') {
      event.preventDefault();
      const currentGroup = grouped.findIndex((group) => group.items.includes(flatItems[selectedIndex]));
      const nextGroup = grouped[(currentGroup + 1) % Math.max(grouped.length, 1)];
      if (nextGroup) {
        const nextIndex = flatItems.findIndex((item) => item.id === nextGroup.items[0]?.id);
        setSelectedIndex(Math.max(nextIndex, 0));
      }
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <AnimatePresence>
        {open ? (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 0.5 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[95] bg-surface-900" />
            </Dialog.Overlay>
            <Dialog.Content asChild>
              <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.96 }} transition={{ type: 'spring', stiffness: 360, damping: 28 }} className="fixed left-1/2 top-[14vh] z-[100] w-[min(560px,calc(100vw-2rem))] -translate-x-1/2 overflow-hidden rounded-[24px] border border-white/40 bg-white/85 shadow-xl backdrop-blur-2xl dark:border-white/10 dark:bg-surface-0/92">
                <VisuallyHidden.Root asChild><Dialog.Title>Command Palette</Dialog.Title></VisuallyHidden.Root>
                <VisuallyHidden.Root asChild><Dialog.Description>Search employees, actions, and modules</Dialog.Description></VisuallyHidden.Root>
                <div className="flex items-center gap-3 border-b border-surface-300/70 px-4 py-3 dark:border-white/10">
                  <Search className="h-4 w-4 text-surface-500 dark:text-white/40" />
                  <input
                    ref={inputRef}
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Search employees, actions, modules..."
                    className="h-11 flex-1 bg-transparent text-sm text-surface-900 outline-none placeholder:text-surface-500 dark:text-white dark:placeholder:text-white/35"
                  />
                </div>
                <div className="max-h-[480px] overflow-y-auto p-2">
                  {grouped.map((group) => (
                    <div key={group.group} className="pt-2">
                      <p className="px-2 pb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-surface-500 dark:text-white/35">{group.group}</p>
                      <div className="space-y-1">
                        {group.items.map((item) => {
                          const itemIndex = flatItems.findIndex((candidate) => candidate.id === item.id);
                          const selected = itemIndex === selectedIndex;
                          return (
                            <button
                              key={item.id}
                              type="button"
                              onMouseEnter={() => setSelectedIndex(itemIndex)}
                              onClick={item.onSelect}
                              className={`flex h-10 w-full items-center gap-3 rounded-xl border-l-2 px-3 text-left transition ${selected ? 'border-brand-500 bg-brand-50 text-brand-900 dark:bg-brand-500/12 dark:text-white' : 'border-transparent text-surface-700 hover:bg-surface-100 dark:text-white/75 dark:hover:bg-white/5'}`}
                            >
                              <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-surface-100 text-surface-700 dark:bg-white/5 dark:text-white/70">{item.icon ?? <Search className="h-4 w-4" />}</span>
                              <span className="min-w-0 flex-1">
                                <span className="block truncate text-sm font-medium">{item.title}</span>
                                {item.subtitle ? <span className="block truncate text-xs opacity-60">{item.subtitle}</span> : null}
                              </span>
                              <span className="flex items-center gap-2 text-xs opacity-60">
                                {item.meta ? <kbd className="rounded-md border border-current/10 px-1.5 py-0.5 font-mono">{item.meta}</kbd> : null}
                                <ArrowRight className="h-3.5 w-3.5" />
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        ) : null}
      </AnimatePresence>
    </Dialog.Root>
  );
}
