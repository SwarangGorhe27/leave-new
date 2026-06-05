import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle2, AlertTriangle, Info, Loader2, XCircle } from 'lucide-react';
import { create } from 'zustand';
import { Button } from './Button';

export type ToastType = 'success' | 'error' | 'warning' | 'info' | 'loading';

interface ToastItem {
  id: string;
  title: string;
  description?: string;
  type: ToastType;
  duration: number;
}

interface ToastStore {
  items: ToastItem[];
  push: (item: Omit<ToastItem, 'id'>) => string;
  dismiss: (id: string) => void;
}

const toneMap: Record<ToastType, { icon: typeof CheckCircle2; tone: string }> = {
  success: { icon: CheckCircle2, tone: 'border-emerald-200 bg-emerald-50/90 text-emerald-900 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-100' },
  error: { icon: XCircle, tone: 'border-rose-200 bg-rose-50/90 text-rose-900 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-rose-100' },
  warning: { icon: AlertTriangle, tone: 'border-amber-200 bg-amber-50/90 text-amber-900 dark:border-amber-500/20 dark:bg-amber-500/10 dark:text-amber-100' },
  info: { icon: Info, tone: 'border-sky-200 bg-sky-50/90 text-sky-900 dark:border-sky-500/20 dark:bg-sky-500/10 dark:text-sky-100' },
  loading: { icon: Loader2, tone: 'border-brand-200 bg-brand-50/90 text-brand-900 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-100' }
};

const useToastStore = create<ToastStore>((set, get) => ({
  items: [],
  push: (item) => {
    const id = crypto.randomUUID();
    set((state) => ({ items: [item.type === 'loading' ? { ...item, duration: 1000000, id } : { ...item, id }, ...state.items].slice(0, 3) }));
    if (item.type !== 'loading') {
      window.setTimeout(() => {
        get().dismiss(id);
      }, item.duration);
    }
    return id;
  },
  dismiss: (id) => set((state) => ({ items: state.items.filter((item) => item.id !== id) }))
}));

export const toast = {
  success: (title: string, description?: string) => useToastStore.getState().push({ title, description, type: 'success', duration: 4000 }),
  error: (title: string, description?: string) => useToastStore.getState().push({ title, description, type: 'error', duration: 5000 }),
  warning: (title: string, description?: string) => useToastStore.getState().push({ title, description, type: 'warning', duration: 4500 }),
  info: (title: string, description?: string) => useToastStore.getState().push({ title, description, type: 'info', duration: 4000 }),
  loading: (title: string, description?: string) => useToastStore.getState().push({ title, description, type: 'loading', duration: 1000000 }),
  dismiss: (id: string) => useToastStore.getState().dismiss(id),
  promise: async <T,>(operation: Promise<T>, messages: { loading: string; success: string; error: string }) => {
    const id = toast.loading(messages.loading);
    try {
      const result = await operation;
      toast.dismiss(id);
      toast.success(messages.success);
      return result;
    } catch (error) {
      toast.dismiss(id);
      toast.error(messages.error);
      throw error;
    }
  }
};

export function ToastViewport() {
  const items = useToastStore((state) => state.items);
  const dismiss = useToastStore((state) => state.dismiss);

  return (
    <div className="pointer-events-none fixed right-4 top-4 z-[120] flex w-[360px] max-w-[calc(100vw-2rem)] flex-col gap-2">
      <AnimatePresence initial={false}>
        {items.map((item, index) => {
          const config = toneMap[item.type];
          const Icon = config.icon;
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: 24, scale: 0.98 }}
              animate={{ opacity: 1, x: 0, scale: 1, y: index * 4 }}
              exit={{ opacity: 0, x: 24, scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 340, damping: 28 }}
              className={`pointer-events-auto overflow-hidden rounded-2xl border shadow-lg backdrop-blur-xl ${config.tone}`}
            >
              <div className="flex items-start gap-3 px-4 py-3">
                <span className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-xl bg-white/65 dark:bg-white/10">
                  <Icon className={item.type === 'loading' ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold">{item.title}</p>
                  {item.description ? <p className="mt-0.5 text-xs opacity-75">{item.description}</p> : null}
                </div>
                <Button variant="ghost" size="xs" iconOnly aria-label="Dismiss notification" onClick={() => dismiss(item.id)}>
                  <span className="text-sm">x</span>
                </Button>
              </div>
              {item.type !== 'loading' ? (
                <motion.div className="h-1 origin-left bg-current/25" initial={{ scaleX: 1 }} animate={{ scaleX: 0 }} transition={{ duration: item.duration / 1000, ease: 'linear' }} />
              ) : null}
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
