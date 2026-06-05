import { useState } from 'react';
import { CheckCircle2, Eye, EyeOff, KeyRound, Lock, ShieldCheck } from 'lucide-react';
import api from '@api/client';
import { cn } from '@utils/utils';

export function SetupPasswordPage() {
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const passwordValid = password.length >= 8;
  const passwordsMatch = password === confirmPassword && confirmPassword.length > 0;

  const strength =
    password.length === 0 ? 0
    : password.length < 6 ? 1
    : password.length < 8 ? 2
    : password.length < 12 ? 3
    : 4;

  const strengthConfig = [
    null,
    { label: 'Weak',      color: '#EF4444', bar: 'bg-red-500' },
    { label: 'Fair',      color: '#F59E0B', bar: 'bg-amber-500' },
    { label: 'Good',      color: '#3B82F6', bar: 'bg-blue-500' },
    { label: 'Strong',    color: '#10B981', bar: 'bg-emerald-500' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordValid || !passwordsMatch || !token) return;
    setStatus('loading');
    setErrorMsg('');
    try {
      await api.post('/auth/setup-password/', { token, password });
      setStatus('success');
    } catch (err: unknown) {
      setStatus('error');
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setErrorMsg(axiosErr?.response?.data?.detail || 'Failed to set password. The link may have expired.');
    }
  };

  /* ── Invalid token ─────────────────────────────────────── */
  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface-50 p-4 dark:bg-[var(--surface-0)]">
        <div className="max-w-sm text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-red-50 dark:bg-red-500/10">
            <Lock className="h-7 w-7 text-red-500" />
          </div>
          <h1
            className="mt-4 text-xl font-bold text-surface-900 dark:text-white"
            style={{ fontFamily: '"Plus Jakarta Sans", sans-serif' }}
          >
            Invalid Link
          </h1>
          <p className="mt-2 text-sm text-surface-500 dark:text-white/40">
            This invitation link is invalid or has expired. Please contact your HR administrator.
          </p>
        </div>
      </div>
    );
  }

  /* ── Success state ─────────────────────────────────────── */
  if (status === 'success') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface-50 p-4 dark:bg-[var(--surface-0)]">
        <div className="max-w-sm text-center">
          <div
            className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-50 dark:bg-emerald-500/10"
            style={{ boxShadow: '0 0 0 6px rgba(16,185,129,0.08)' }}
          >
            <CheckCircle2 className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h1
            className="mt-5 text-xl font-bold text-surface-900 dark:text-white"
            style={{ fontFamily: '"Plus Jakarta Sans", sans-serif' }}
          >
            Password Set Successfully!
          </h1>
          <p className="mt-2 text-sm text-surface-500 dark:text-white/40">
            Your account is ready. You can now sign in with your work email and the password you just created.
          </p>
          <a
            href="/"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-brand-500 px-7 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-600 active:scale-[0.97]"
            style={{ boxShadow: '0 2px 8px rgba(59,91,219,0.30)' }}
          >
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  /* ── Form ──────────────────────────────────────────────── */
  const inputClass =
    'w-full rounded-xl border border-surface-200 bg-surface-0 px-3.5 py-2.5 text-sm text-surface-900 outline-none transition-all placeholder:text-surface-400 hover:border-surface-300 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/15 dark:border-white/10 dark:bg-surface-100 dark:text-white dark:placeholder:text-white/25 dark:focus:border-brand-400';

  return (
    <div
      className="flex min-h-screen items-center justify-center p-4"
      style={{
        background: 'radial-gradient(ellipse 80% 50% at 20% -5%, rgba(59,91,219,0.06) 0%, transparent 55%), #F7F8FC',
      }}
    >
      <div className="w-full max-w-md">

        {/* Branding */}
        <div className="mb-8 text-center">
          <div
            className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 text-xl font-bold text-white"
            style={{ boxShadow: '0 4px 16px rgba(59,91,219,0.35)' }}
          >
            HR
          </div>
          <h1
            className="mt-4 text-2xl font-bold text-surface-900"
            style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', letterSpacing: '-0.03em' }}
          >
            Set Up Your Password
          </h1>
          <p className="mt-1.5 text-sm text-surface-500">
            Welcome to HRMS · Create a secure password to get started
          </p>
        </div>

        {/* Card */}
        <div
          className="rounded-2xl border border-surface-200/70 bg-surface-0 p-7"
          style={{ boxShadow: '0 1px 2px rgba(0,0,0,0.04), 0 8px 32px -8px rgba(0,0,0,0.10)' }}
        >
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* New Password */}
            <div>
              <label className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-surface-600">
                <KeyRound className="h-3 w-3" />
                New Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={inputClass}
                  placeholder="Minimum 8 characters"
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-1 text-surface-400 transition-colors hover:text-surface-600 dark:text-white/25 dark:hover:text-white/50"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>

              {/* Strength meter */}
              {password.length > 0 && (
                <div className="mt-2.5">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className={cn(
                          'h-1 flex-1 rounded-full transition-all duration-300',
                          strength >= i
                            ? (strengthConfig[strength]?.bar ?? 'bg-surface-200')
                            : 'bg-surface-100 dark:bg-white/8',
                        )}
                      />
                    ))}
                  </div>
                  <p className="mt-1 text-xs font-medium" style={{ color: strengthConfig[strength]?.color ?? '#ADB5BD' }}>
                    {strengthConfig[strength]?.label ?? ''}
                  </p>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-surface-600">
                <Lock className="h-3 w-3" />
                Confirm Password
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={cn(
                  inputClass,
                  confirmPassword && !passwordsMatch && 'border-red-400 focus:border-red-500 focus:ring-red-500/15',
                  confirmPassword && passwordsMatch && 'border-emerald-400 focus:border-emerald-500 focus:ring-emerald-500/15',
                )}
                placeholder="Re-enter your password"
                required
              />
              {confirmPassword && !passwordsMatch && (
                <p className="mt-1 text-xs font-medium text-red-500">Passwords do not match.</p>
              )}
              {confirmPassword && passwordsMatch && (
                <p className="mt-1 flex items-center gap-1 text-xs font-medium text-emerald-600">
                  <ShieldCheck className="h-3.5 w-3.5" /> Passwords match
                </p>
              )}
            </div>

            {/* Error */}
            {status === 'error' && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-500/20 dark:bg-red-500/10 dark:text-red-400">
                {errorMsg}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={status === 'loading' || !passwordValid || !passwordsMatch}
              className="w-full rounded-xl bg-brand-500 py-2.5 text-sm font-bold text-white transition-all hover:bg-brand-600 active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-45"
              style={{ boxShadow: '0 2px 8px rgba(59,91,219,0.25)' }}
            >
              {status === 'loading' ? 'Setting password…' : 'Set Password & Continue'}
            </button>
          </form>
        </div>

        <p className="mt-5 text-center text-xs text-surface-400">
          Need help? Contact your HR administrator.
        </p>
      </div>
    </div>
  );
}
