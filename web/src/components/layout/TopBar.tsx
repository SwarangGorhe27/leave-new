import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { ChevronDown, LogOut, Moon, Settings, Sun, User as UserIcon } from 'lucide-react';
import { Avatar, Badge } from '@components/ui';
import { useUIStore } from '@store/uiStore';
import { useAuthStore } from '@store/authStore';
import { cn } from '@utils/utils';
import { getResolvedTheme } from '@hooks/useTheme';

export function TopBar() {
  const user = useAuthStore((state) => state.user);
  const portal = useUIStore((state) => state.portal);
  const { theme, setTheme } = useUIStore((state) => ({
    theme: state.theme,
    setTheme: state.setTheme,
  }));
  const isAdmin = user?.role === 'ADMIN';
  const resolvedTheme = getResolvedTheme(theme);

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <header
      className="glass sticky top-0 z-40"
      style={{ boxShadow: 'var(--topbar-shadow)' }}
    >
      <div className="mx-auto flex h-[60px] max-w-[1680px] items-center justify-between px-5 sm:px-7">
        {/* ── Left: Logo + App Name ──────────── */}
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={() => useUIStore.getState().navigateTo(isAdmin ? 'admin-dashboard' : 'dashboard')}
            className="group flex items-center gap-3 outline-none transition-opacity hover:opacity-80"
          >
            {/* Logo mark */}
            <div
              className={cn(
                'relative flex h-9 w-9 items-center justify-center rounded-2xl text-sm font-bold text-white shadow-md transition-transform group-hover:scale-105',
                !isAdmin
                  ? 'bg-gradient-to-br from-emerald-400 to-emerald-600'
                  : 'bg-gradient-to-br from-brand-500 to-brand-700',
              )}
            >
              {!isAdmin ? 'E' : 'HR'}
            </div>

            {/* Brand text */}
            <div className="hidden text-left sm:block">
              <p
                className="text-base font-bold text-surface-900 dark:text-white"
                style={{ fontFamily: '"Plus Jakarta Sans", Inter, sans-serif', letterSpacing: '-0.02em' }}
              >
                {!isAdmin ? 'Employee Portal' : 'HRMS Admin'}
              </p>
              <p className="text-[10px] font-bold uppercase tracking-widest text-surface-400 dark:text-white/40">
                Ampcus Tech
              </p>
            </div>
          </button>
        </div>

        {/* ── Right: Theme Toggle + User Profile ──────────── */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={toggleTheme}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-surface-200/50 bg-white/50 text-surface-500 outline-none backdrop-blur-sm transition-all hover:border-surface-300 hover:bg-white hover:text-brand-500 dark:border-white/10 dark:bg-surface-900/50 dark:text-white/60 dark:hover:border-white/20 dark:hover:bg-surface-800 dark:hover:text-brand-400"
            title={resolvedTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {resolvedTheme === 'dark' ? (
              <Sun className="h-4.5 w-4.5 transition-transform duration-300 hover:-translate-y-0.5" />
            ) : (
              <Moon className="h-4.5 w-4.5 transition-transform duration-300 hover:-translate-y-0.5" />
            )}
          </button>

          <DropdownMenu.Root>
            <DropdownMenu.Trigger className="group flex items-center gap-2.5 rounded-full border border-surface-200/50 bg-white/50 p-1 pr-3 outline-none backdrop-blur-sm transition-all hover:border-surface-300 hover:bg-white hover:shadow-sm dark:border-white/10 dark:bg-surface-900/50 dark:hover:border-white/20 dark:hover:bg-surface-800">
              <Avatar name={user?.name || ''} src={user?.avatar} size="md" className="ring-2 ring-surface-0 dark:ring-surface-900" />
              <div className="hidden text-left sm:block">
                <p className="text-sm font-bold text-surface-900 dark:text-white">
                  {user?.name}
                </p>
              </div>
              <ChevronDown className="h-4 w-4 text-surface-400 transition-transform group-data-[state=open]:rotate-180 dark:text-white/40" />
            </DropdownMenu.Trigger>

            <DropdownMenu.Portal>
              <DropdownMenu.Content
                align="end"
                sideOffset={12}
                className="z-50 min-w-[240px] overflow-hidden rounded-3xl border border-surface-200 bg-white/80 p-2 backdrop-blur-xl dark:border-white/10 dark:bg-surface-900/80"
                style={{ boxShadow: '0 10px 40px -10px rgba(0,0,0,0.15)' }}
              >
                {/* User header */}
                <div className="mb-2 flex items-center gap-3 rounded-2xl bg-surface-50 px-4 py-3 dark:bg-white/5">
                  <Avatar name={user?.name || ''} src={user?.avatar} size="md" />
                  <div className="min-w-0">
                    <p
                      className="text-sm font-bold text-surface-900 dark:text-white"
                      style={{ fontFamily: '"Plus Jakarta Sans", sans-serif' }}
                    >
                      {user?.name}
                    </p>
                    <p className="truncate text-xs text-surface-500 dark:text-white/40">{user?.title}</p>
                  </div>
                </div>

                <div className="px-1 py-1">
                  <DropdownMenu.Item
                    className="flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-surface-700 outline-none transition-colors hover:bg-brand-50 hover:text-brand-700 focus:bg-brand-50 focus:text-brand-700 dark:text-white/80 dark:hover:bg-brand-500/10 dark:hover:text-brand-400 dark:focus:bg-brand-500/10 dark:focus:text-brand-400"
                    onSelect={() => useUIStore.getState().navigateTo('my-profile')}
                  >
                    <UserIcon className="h-4 w-4" />
                    My Profile
                  </DropdownMenu.Item>

                  {(['Preferences', 'Settings'] as const).map((label) => (
                    <DropdownMenu.Item
                      key={label}
                      className="flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-surface-700 outline-none transition-colors hover:bg-surface-100 focus:bg-surface-100 dark:text-white/80 dark:hover:bg-white/10 dark:focus:bg-white/10"
                    >
                      <Settings className="h-4 w-4 opacity-50" />
                      {label}
                    </DropdownMenu.Item>
                  ))}
                </div>

                <div className="my-1 h-px bg-surface-100 dark:bg-white/10" />

                <div className="px-1 py-1">
                  <DropdownMenu.Item
                    className="flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-rose-600 outline-none transition-colors hover:bg-rose-50 focus:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-500/10 dark:focus:bg-rose-500/10"
                    onSelect={() => useAuthStore.getState().logout()}
                  >
                    <LogOut className="h-4 w-4" />
                    Sign Out
                  </DropdownMenu.Item>
                </div>

                <div className="px-4 pb-2 pt-1">
                  <Badge variant="brand" size="sm" className="w-full justify-center">{user.company}</Badge>
                </div>
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        </div>
      </div>
    </header>
  );
}

