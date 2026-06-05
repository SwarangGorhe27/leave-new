import { useState } from 'react';
import { Eye, EyeOff, ArrowRight } from 'lucide-react';
import { useAuthStore } from '@store/authStore';
import { cn } from '@utils/utils';

interface SharedLoginLayoutProps {
  initialRole: 'admin' | 'employee';
}

const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg">
    <path fill="#4285F4" d="M21.35 11.1h-9.18v2.97h5.24c-.23 1.25-.92 2.3-1.96 3.01v2.5h3.17c1.85-1.71 2.92-4.21 2.92-7.2 0-.63-.06-1.24-.17-1.83z" />
    <path fill="#34A853" d="M12.17 21.5c2.64 0 4.86-.87 6.49-2.36l-3.17-2.5c-.88.6-2.01.95-3.32.95-2.55 0-4.72-1.72-5.49-4.02H3.11v2.52c1.63 3.19 4.92 5.41 9.06 5.41z" />
    <path fill="#FBBC05" d="M6.68 13.57c-.2-.6-.32-1.23-.32-1.88 0-.65.12-1.28.32-1.88V7.29H3.11a9.96 9.96 0 0 0 0 6.18l3.57-0.9z" />
    <path fill="#EA4335" d="M12.17 4.5c1.44 0 2.74.5 3.77 1.48l2.82-2.83C16.99 1.57 14.77.5 12.17.5 7.03.5 3.11 2.72 1.49 6.16l3.57 2.52c.77-2.3 2.94-4.02 5.11-4.02z" />
  </svg>
);

const MicrosoftIcon = () => (
  <svg viewBox="0 0 21 21" width="20" height="20" xmlns="http://www.w3.org/2000/svg">
    <rect x="1" y="1" width="9" height="9" fill="#F35325" />
    <rect x="1" y="11" width="9" height="9" fill="#81BC06" />
    <rect x="11" y="1" width="9" height="9" fill="#05A6F0" />
    <rect x="11" y="11" width="9" height="9" fill="#FFBA00" />
  </svg>
);

export function SharedLoginLayout({ initialRole }: SharedLoginLayoutProps) {
  const [role, setRole] = useState<'admin' | 'employee'>(initialRole);
  const [email, setEmail] = useState(role === 'admin' ? 'admin@ampcus.example' : 'employee@ampcus.example');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const login = useAuthStore((state) => state.login);

  const handleRoleSwitch = (newRole: 'admin' | 'employee') => {
    setRole(newRole);
    setEmail(newRole === 'admin' ? 'admin@ampcus.example' : 'employee@ampcus.example');
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 800));

      await login(email, role === 'admin' ? 'ADMIN' : 'EMPLOYEE');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white">
      <div className="pointer-events-none absolute left-[-2rem] top-64 h-72 w-72 rounded-full bg-[#31C48D]/15 blur-3xl dark:bg-success-500/10" />

      <div className="relative mx-auto flex min-h-screen max-w-[1640px] flex-col items-center justify-center gap-10 px-4 py-8 sm:px-6 md:gap-12 lg:flex-row lg:items-start lg:px-14">
        <div className="mb-10 w-full max-w-[760px] flex-1 lg:mb-0 lg:pr-10">
          <div className="mb-8 inline-flex items-center gap-3 rounded-full bg-white/90 px-4 py-3 shadow-xl shadow-slate-200/60 backdrop-blur-xl sm:px-5 sm:py-3.5 dark:bg-surface-100/90 dark:shadow-black/20">
            <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-[#3B5BDB] text-lg font-bold text-white shadow-lg shadow-slate-300/50 dark:shadow-black/30">
              HR
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">HRMS Portal</p>
              <p className="text-xs text-slate-500 dark:text-surface-400">Modern team login experience</p>
            </div>
          </div>

          <h1 className="max-w-2xl text-center text-4xl font-semibold leading-tight tracking-[-0.035em] text-slate-950 sm:text-5xl md:text-6xl lg:text-left dark:text-white">
            Login to your workplace in one streamlined portal.
          </h1>
          <p className="mt-6 max-w-xl text-center text-base leading-7 text-slate-600 sm:text-left sm:text-lg dark:text-surface-300">
            Fast access to attendance, documents, payroll and approvals with a beautifully crafted HRMS login experience.
          </p>

          <div className="relative mt-10 overflow-hidden rounded-[42px] border border-slate-200/70 bg-white/95 p-6 shadow-[0_40px_90px_-40px_rgba(15,23,42,0.18)] sm:p-8 dark:border-white/10 dark:bg-surface-100/95 dark:shadow-[0_40px_90px_-40px_rgba(0,0,0,0.3)]">
            <div className="absolute -left-6 top-5 h-20 w-20 rounded-full bg-[#3B82F6]/10 blur-3xl dark:bg-brand-500/10" />
            <div className="absolute -right-6 bottom-6 h-28 w-28 rounded-full bg-[#10B981]/10 blur-3xl dark:bg-success-500/10" />

            <div className="mb-8 rounded-[32px] bg-gradient-to-br from-[#EBF3FF] to-[#F8FBFF] p-5 shadow-sm shadow-slate-200/50 dark:from-surface-200 dark:to-surface-100 dark:shadow-black/10">
              <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-surface-300">
                  <span className="inline-flex h-2.5 w-2.5 rounded-full bg-[#3B82F6] dark:bg-brand-400" />
                  Product overview
                </div>
                <div className="flex gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#EF4444] dark:bg-danger-400" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[#F59E0B] dark:bg-warning-400" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[#10B981] dark:bg-success-400" />
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-[28px] bg-white p-5 shadow-[0_18px_30px_-20px_rgba(15,23,42,0.18)] dark:bg-surface-100 dark:shadow-[0_18px_30px_-20px_rgba(0,0,0,0.3)]">
                  <div className="mb-4 flex items-center gap-3">
                    <div className="h-12 w-12 rounded-3xl bg-slate-100" />
                    <div>
                      <p className="text-sm font-semibold text-slate-900 dark:text-white">Payroll</p>
                      <p className="text-xs text-slate-500 dark:text-surface-400">Weekly summary</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="h-3 w-24 rounded-full bg-slate-200" />
                    <div className="h-3 w-20 rounded-full bg-slate-200" />
                    <div className="h-3 w-16 rounded-full bg-slate-200" />
                  </div>
                </div>
                <div className="rounded-[28px] bg-white p-5 shadow-[0_18px_30px_-20px_rgba(15,23,42,0.18)] dark:bg-surface-100 dark:shadow-[0_18px_30px_-20px_rgba(0,0,0,0.3)]">
                  <div className="mb-4 flex items-center gap-3">
                    <div className="h-12 w-12 rounded-3xl bg-slate-100" />
                    <div>
                      <p className="text-sm font-semibold text-slate-900 dark:text-white">Tasks</p>
                      <p className="text-xs text-slate-500 dark:text-surface-400">Pending actions</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <span className="h-2.5 w-2.5 rounded-full bg-brand-500" />
                      <span>Review timesheets</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <span className="h-2.5 w-2.5 rounded-full bg-slate-300 dark:bg-surface-400" />
                      <span>Approve leave requests</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-[32px] bg-slate-950 p-6 text-white shadow-[0_30px_60px_-30px_rgba(15,23,42,0.35)] dark:shadow-[0_30px_60px_-30px_rgba(0,0,0,0.5)]">
                <div className="mb-5 flex items-center justify-between rounded-3xl bg-white/10 p-3 text-xs text-slate-300">
                  <span>Today</span>
                  <span>09:34 AM</span>
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-semibold text-white">Attendance check-in</p>
                    <p className="text-xs text-slate-400 dark:text-surface-400">8:45 AM</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Payroll review</p>
                    <p className="text-xs text-slate-400 dark:text-surface-400">Due today</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Document approvals</p>
                    <p className="text-xs text-slate-400 dark:text-surface-400">2 items pending</p>
                  </div>
                </div>
              </div>

              <div className="grid gap-4">
                <div className="rounded-[32px] bg-slate-950 p-5 text-white shadow-[0_20px_45px_-30px_rgba(15,23,42,0.35)] dark:shadow-[0_20px_45px_-30px_rgba(0,0,0,0.5)]">
                  <div className="mb-4 flex items-center gap-3 text-sm font-semibold text-white/75 dark:text-surface-300">
                    <span className="inline-flex h-10 w-10 items-center justify-center rounded-3xl bg-white/10 dark:bg-surface-200/20">HR</span>
                    People
                  </div>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-semibold text-white">New hires</p>
                      <p className="text-xs text-slate-400 dark:text-surface-400">3 onboarding tasks</p>
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">Team feedback</p>
                      <p className="text-xs text-slate-400">2 notes</p>
                    </div>
                  </div>
                </div>
                <div className="rounded-[32px] bg-slate-950 p-5 text-white shadow-[0_20px_45px_-30px_rgba(15,23,42,0.35)] dark:shadow-[0_20px_45px_-30px_rgba(0,0,0,0.5)]">
                  <div className="mb-4 flex items-center gap-3 text-sm font-semibold text-white/75">
                    <span className="inline-flex h-10 w-10 items-center justify-center rounded-3xl bg-white/10 dark:bg-surface-200/20">UI</span>
                    Design
                  </div>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-semibold text-white">Prototype review</p>
                      <p className="text-xs text-slate-400 dark:text-surface-400">In progress</p>
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">Brand update</p>
                      <p className="text-xs text-slate-400 dark:text-surface-400">Ready to launch</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1">
          <div className="mx-auto w-full max-w-md rounded-[40px] border border-slate-200/75 bg-white/95 p-6 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.25)] backdrop-blur-xl sm:p-8 md:max-w-lg md:p-10 dark:border-white/10 dark:bg-surface-100/95 dark:shadow-[0_45px_90px_-45px_rgba(0,0,0,0.4)]">
            <div className="mb-8 text-center lg:text-left dark:text-white">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Sign in</p>
              <h2 className="mt-4 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">Welcome back</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600">Enter your credentials to access HR and ESS tools securely.</p>
            </div>

            <div className="mb-6 grid gap-3 rounded-3xl bg-slate-100 p-1 sm:grid-cols-2">
              {(['admin', 'employee'] as const).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => handleRoleSwitch(r)}
                  className={cn(
                    'w-full rounded-3xl px-4 py-3 text-sm font-semibold transition-all duration-150',
                    role === r
                      ? 'bg-slate-950 text-white shadow-lg shadow-slate-900/10'
                      : 'text-slate-600 hover:bg-white'
                  )}
                >
                  {r === 'admin' ? 'Admin' : 'Employee'}
                </button>
              ))}
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              <label className="block text-sm font-semibold text-slate-800">
                Email address
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="mt-2 w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition-all duration-150 focus:border-brand-400 focus:ring-2 focus:ring-brand-400/20"
                />
              </label>

              <label className="block text-sm font-semibold text-slate-800">
                Password
                <div className="relative mt-2">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-sm text-slate-900 outline-none transition-all duration-150 focus:border-brand-400 focus:ring-2 focus:ring-brand-400/20"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-slate-700"
                  >
                    {showPassword ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                  </button>
                </div>
              </label>

              <div className="flex items-center justify-between text-sm text-slate-600">
                <label className="inline-flex items-center gap-2">
                  <input type="checkbox" className="h-4 w-4 rounded border-slate-300 text-brand-500 focus:ring-brand-400" />
                  Remember me
                </label>
                <a href="#" className="font-semibold text-brand-600 hover:text-brand-700">Forgot password?</a>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex w-full items-center justify-center gap-2 rounded-3xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_15px_40px_-15px_rgba(15,23,42,0.35)] transition duration-150 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span>{loading ? 'Signing in...' : 'Sign in'}</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </form>

            <div className="mt-8 flex items-center gap-3 text-xs text-slate-400">
              <span className="h-px flex-1 bg-slate-200" />
              <span>Or continue with</span>
              <span className="h-px flex-1 bg-slate-200" />
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <button type="button" className="inline-flex items-center justify-center gap-2 rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
                <GoogleIcon /> Google
              </button>
              <button type="button" className="inline-flex items-center justify-center gap-2 rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
                <MicrosoftIcon /> Microsoft
              </button>
            </div>

            <p className="mt-8 text-center text-sm text-slate-500">
              New here? Contact your administrator to get started.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
