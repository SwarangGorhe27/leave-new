import { useState } from 'react';
import { Eye, EyeOff, ArrowRight, Users, AlertCircle, TrendingUp, Clock, CheckCircle2, XCircle, ChevronRight } from 'lucide-react';
import { useAuthStore } from '@store/authStore';
import { cn } from '@utils/utils';

interface DynamicAdminLoginLayoutProps {
  initialRole?: 'admin';
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

// Admin Stats Card
function AdminStatCard({
  label,
  value,
  status,
  icon: Icon,
  trend,
  color = 'brand'
}: {
  label: string;
  value: string | number;
  status?: string;
  icon?: any;
  trend?: string;
  color?: 'brand' | 'success' | 'warning' | 'danger' | 'info';
}) {
  const colorMap = {
    brand: 'bg-brand-50 text-brand-600 border-brand-200',
    success: 'bg-success-50 text-success-600 border-success-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    danger: 'bg-danger-50 text-danger-600 border-danger-200',
    info: 'bg-blue-50 text-blue-600 border-blue-200'
  };

  const trendColorMap = {
    'up': 'text-success-600',
    'down': 'text-danger-600',
    'neutral': 'text-slate-500'
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md dark:border-white/10 dark:bg-surface-100">
      <div className="flex items-start justify-between mb-4">
        {Icon && (
          <div className={cn('rounded-xl p-2.5 border', colorMap[color])}>
            <Icon className="h-5 w-5" />
          </div>
        )}
        {trend && (
          <span className={cn('text-xs font-bold', trendColorMap[trend as keyof typeof trendColorMap] || 'text-slate-500')}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trend}
          </span>
        )}
      </div>
      <p className="text-sm text-slate-600 dark:text-surface-400 mb-1">{label}</p>
      <p className="text-3xl font-bold text-slate-900 dark:text-white">{value}</p>
      {status && <p className="text-xs text-slate-500 dark:text-surface-400 mt-2">{status}</p>}
    </div>
  );
}

// Priority Alert Card
function PriorityAlert({
  title,
  description,
  count,
  priority = 'medium',
  icon: Icon,
  action
}: {
  title: string;
  description?: string;
  count?: number;
  priority?: 'high' | 'medium' | 'low';
  icon?: any;
  action?: string;
}) {
  const priorityMap = {
    high: 'bg-danger-50 border-danger-200 text-danger-700',
    medium: 'bg-warning-50 border-warning-200 text-warning-700',
    low: 'bg-info-50 border-info-200 text-info-700'
  };

  const priorityBadge = {
    high: 'bg-danger-100 text-danger-700',
    medium: 'bg-warning-100 text-warning-700',
    low: 'bg-info-100 text-info-700'
  };

  return (
    <div className={cn('rounded-xl border p-4 flex items-start gap-3 transition', priorityMap[priority])}>
      {Icon && <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />}
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <p className="font-semibold text-sm">{title}</p>
          {count && (
            <span className={cn('text-xs font-bold px-2.5 py-1 rounded-full', priorityBadge[priority])}>
              {count}
            </span>
          )}
        </div>
        {description && <p className="text-xs opacity-75">{description}</p>}
      </div>
      {action && (
        <button className="text-xs font-semibold whitespace-nowrap hover:opacity-75 transition">
          {action}
        </button>
      )}
    </div>
  );
}

// Team Health Component
function TeamHealthMetrics() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lg shadow-slate-200/40 dark:border-white/10 dark:bg-surface-100 dark:shadow-black/20">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">Team Health</h3>
        <a href="#" className="text-sm text-brand-600 hover:text-brand-700 font-semibold flex items-center gap-1">
          Details <ChevronRight className="h-4 w-4" />
        </a>
      </div>

      <div className="space-y-4">
        {/* Health Items */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">Attendance Rate</p>
            <p className="text-xs text-slate-500 dark:text-surface-400">Last 30 days</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-success-600">94.2%</p>
            <p className="text-xs text-success-600">+1.2% vs month</p>
          </div>
        </div>

        <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden dark:bg-surface-300">
          <div className="h-full bg-gradient-to-r from-success-400 to-success-500" style={{ width: '94.2%' }} />
        </div>

        <div className="pt-4 border-t border-slate-200 dark:border-white/10 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">Leave Approvals</p>
            <p className="text-xs text-slate-500 dark:text-surface-400">Pending review</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-warning-600">12</p>
            <p className="text-xs text-warning-600">Action needed</p>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-200 dark:border-white/10 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">New Joiners</p>
            <p className="text-xs text-slate-500 dark:text-surface-400">This month</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-brand-600">3</p>
            <p className="text-xs text-brand-600">Onboarding in progress</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Quick Actions Component
function QuickActions() {
  const actions = [
    { icon: Users, label: 'Manage Employees', count: '230 total', color: 'text-brand-600' },
    { icon: CheckCircle2, label: 'Approve Documents', count: '18 pending', color: 'text-success-600' },
    { icon: AlertCircle, label: 'Review Requests', count: '7 alerts', color: 'text-warning-600' },
    { icon: TrendingUp, label: 'View Reports', count: 'Updated today', color: 'text-purple-600' }
  ];

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lg shadow-slate-200/40 dark:border-white/10 dark:bg-surface-100 dark:shadow-black/20">
      <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Quick Actions</h3>
      <div className="space-y-3">
        {actions.map((action, idx) => (
          <button
            key={idx}
            className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-surface-200 transition group"
          >
            <div className="flex items-center gap-3">
              <action.icon className={cn('h-5 w-5', action.color)} />
              <div className="text-left">
                <p className="text-sm font-semibold text-slate-900 dark:text-white">{action.label}</p>
                <p className="text-xs text-slate-500 dark:text-surface-400">{action.count}</p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-surface-300 transition" />
          </button>
        ))}
      </div>
    </div>
  );
}

export function DynamicAdminLoginLayout({ initialRole = 'admin' }: DynamicAdminLoginLayoutProps) {
  const [email, setEmail] = useState('admin@ampcus.example');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 800));
      await login(email, 'ADMIN');
    } finally {
      setLoading(false);
    }
  };

  const hour = new Date().getHours();
  const getGreeting = () => {
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="relative overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white min-h-screen">
      {/* Decorative Backgrounds */}
      <div className="pointer-events-none absolute left-[-2rem] top-64 h-72 w-72 rounded-full bg-[#FF6B6B]/10 blur-3xl dark:bg-danger-500/5" />
      <div className="pointer-events-none absolute right-[-4rem] bottom-32 h-96 w-96 rounded-full bg-[#4F46E5]/15 blur-3xl dark:bg-indigo-500/10" />

      <div className="relative mx-auto flex min-h-screen max-w-[1840px] flex-col gap-8 px-4 py-8 sm:px-6 lg:flex-row lg:gap-12 lg:px-14 lg:py-12">
        {/* Left Side - Admin Dashboard Overview */}
        <div className="w-full flex-1 lg:pr-12">
          {/* Header Badge */}
          <div className="mb-8 inline-flex items-center gap-3 rounded-full bg-white/90 px-4 py-3 shadow-xl shadow-slate-200/60 backdrop-blur-xl sm:px-5 sm:py-3.5 dark:bg-surface-100/90 dark:shadow-black/20">
            <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-gradient-to-br from-red-500 to-red-600 text-lg font-bold text-white shadow-lg shadow-slate-300/50 dark:shadow-black/30">
              HR
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">Admin Dashboard</p>
              <p className="text-xs text-slate-500 dark:text-surface-400">HR Management System</p>
            </div>
          </div>

          {/* Personalized Welcome */}
          <div className="mb-8">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight tracking-tight text-slate-950 dark:text-white mb-2">
              {getGreeting()},<br />HR Administrator
            </h1>
            <p className="text-lg text-slate-600 dark:text-surface-300 max-w-2xl">
              Monitor team health, manage approvals, and oversee all HR operations from your command center.
            </p>
          </div>

          {/* Admin Profile Card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lg shadow-slate-200/40 dark:border-white/10 dark:bg-surface-100 dark:shadow-black/20 mb-6">
            <div className="flex items-start justify-between mb-6 pb-6 border-b border-slate-200 dark:border-white/10">
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">Sakshi Deshpande</h3>
                <p className="text-sm text-red-600 dark:text-red-400 font-medium">HR Operations Head</p>
              </div>
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-red-500 to-red-600 text-2xl font-bold text-white shadow-lg">
                S
              </div>
            </div>

            {/* Admin Info Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Admin Level</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-white">Super Admin</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Team Size</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-white">230 Employees</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Department</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-white">HR & Admin</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Access</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-white">Full System</p>
              </div>
            </div>
          </div>

          {/* Priority Alerts */}
          <div className="space-y-3 mb-6">
            <PriorityAlert
              title="Leave Approvals Pending"
              description="12 leave requests awaiting your approval"
              count={12}
              priority="high"
              icon={AlertCircle}
              action="Review"
            />
            <PriorityAlert
              title="Document Verifications"
              description="18 documents need compliance review"
              count={18}
              priority="medium"
              icon={CheckCircle2}
              action="Process"
            />
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 mb-8 sm:grid-cols-4">
            <AdminStatCard
              label="Total Employees"
              value="230"
              status="3 new this month"
              icon={Users}
              trend="up"
              color="brand"
            />
            <AdminStatCard
              label="Attendance Rate"
              value="94.2%"
              status="↑ 1.2% vs month"
              icon={CheckCircle2}
              trend="up"
              color="success"
            />
            <AdminStatCard
              label="Pending Leaves"
              value="12"
              status="Action needed"
              icon={Clock}
              trend="neutral"
              color="warning"
            />
            <AdminStatCard
              label="Open Requisitions"
              value="5"
              status="In hiring stage"
              icon={TrendingUp}
              trend="down"
              color="info"
            />
          </div>

          {/* Team Health & Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TeamHealthMetrics />
            <QuickActions />
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full flex-1 flex items-start justify-center lg:sticky lg:top-8 lg:max-h-[calc(100vh-4rem)]">
          <div className="w-full max-w-md rounded-3xl border border-slate-200/75 bg-white/95 p-6 shadow-2xl shadow-slate-300/40 backdrop-blur-xl sm:p-8 dark:border-white/10 dark:bg-surface-100/95 dark:shadow-black/50">
            {/* Sign In Header */}
            <div className="mb-8">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-surface-400">Admin Sign in</p>
              <h2 className="mt-4 text-2xl font-bold tracking-tight text-slate-950 dark:text-white">Management Portal</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-surface-300">Access comprehensive HR management tools and analytics.</p>
            </div>

            {/* Admin Role Badge */}
            <div className="mb-6 rounded-2xl bg-gradient-to-r from-red-50 to-orange-50 p-3 border border-red-200 dark:from-surface-200 dark:to-surface-200 dark:border-white/10">
              <p className="text-xs font-semibold text-red-700 dark:text-red-400 flex items-center gap-2">
                <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-white text-xs font-bold">A</span>
                Signing in as Administrator
              </p>
            </div>

            {/* Login Form */}
            <form onSubmit={handleLogin} className="space-y-5">
              <label className="block text-sm font-semibold text-slate-800 dark:text-white">
                Admin Email
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@company.com"
                  className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition-all duration-150 focus:border-red-400 focus:ring-2 focus:ring-red-400/20 dark:border-white/10 dark:bg-surface-200 dark:text-white dark:focus:border-red-400"
                />
              </label>

              <label className="block text-sm font-semibold text-slate-800 dark:text-white">
                Password
                <div className="relative mt-2">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-sm text-slate-900 outline-none transition-all duration-150 focus:border-red-400 focus:ring-2 focus:ring-red-400/20 dark:border-white/10 dark:bg-surface-200 dark:text-white dark:focus:border-red-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-slate-700 dark:text-surface-400 dark:hover:text-white"
                  >
                    {showPassword ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                  </button>
                </div>
              </label>

              <div className="flex items-center justify-between text-sm text-slate-600 dark:text-surface-400">
                <label className="inline-flex items-center gap-2">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-red-500 focus:ring-red-400 dark:border-white/20 dark:bg-surface-200"
                  />
                  Remember me
                </label>
                <a href="#" className="font-semibold text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300">
                  Forgot password?
                </a>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-red-600 to-red-700 px-5 py-3 text-sm font-semibold text-white shadow-xl shadow-red-500/30 transition duration-150 hover:from-red-700 hover:to-red-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span>{loading ? 'Signing in...' : 'Sign in as Admin'}</span>
                {!loading && <ArrowRight className="h-4 w-4" />}
              </button>
            </form>

            {/* Divider */}
            <div className="mt-8 flex items-center gap-3 text-xs text-slate-400 dark:text-surface-500">
              <span className="h-px flex-1 bg-slate-200 dark:bg-white/10" />
              <span>Or continue with</span>
              <span className="h-px flex-1 bg-slate-200 dark:bg-white/10" />
            </div>

            {/* OAuth Buttons */}
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-white/10 dark:bg-surface-200 dark:text-white dark:hover:bg-surface-300"
              >
                <GoogleIcon /> Google
              </button>
              <button
                type="button"
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-white/10 dark:bg-surface-200 dark:text-white dark:hover:bg-surface-300"
              >
                <MicrosoftIcon /> Microsoft
              </button>
            </div>

            {/* Security Notice */}
            <div className="mt-8 p-3 rounded-xl bg-slate-50 dark:bg-surface-200 border border-slate-200 dark:border-white/10">
              <p className="text-xs text-slate-600 dark:text-surface-400">
                <span className="font-semibold">Security:</span> Ensure you're on a secure network. Never share your admin credentials.
              </p>
            </div>

            {/* Footer */}
            <p className="mt-6 text-center text-xs text-slate-500 dark:text-surface-500">
              Need help? <a href="#" className="text-red-600 hover:text-red-700 font-semibold dark:text-red-400">Contact IT Support</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
