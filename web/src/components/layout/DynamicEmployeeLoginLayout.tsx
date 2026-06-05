import { useState } from 'react';
import { Eye, EyeOff, ArrowRight, MapPin, Building2, BriefcaseBusiness, Users, Calendar, Zap, AlertCircle, CheckCircle2, ChevronRight } from 'lucide-react';
import { useAuthStore } from '@store/authStore';
import { cn } from '@utils/utils';

interface DynamicEmployeeLoginLayoutProps {
  initialRole?: 'employee';
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

// Employee data fetching (using store data)
function getEmployeeData() {
  const users = useAuthStore((state) => state.user);
  const employees = useAuthStore((state) => state.employees);
  
  if (!users || users.role !== 'EMPLOYEE') return null;
  const employee = employees[1]; // Aarav Mehta
  
  return {
    name: employee?.name || users.name,
    title: employee?.designation || users.title,
    company: employee?.company || users.company,
    email: users.email,
    location: employee?.location || 'Pune',
    department: employee?.department || 'Experience Design',
    leaveBalance: employee?.leaveBalance || 14,
    presentDays: employee?.presentDays || 19,
    tenure: employee?.tenure || '4y 10m',
    nextIncrement: employee?.nextIncrement || '2026-07-01',
    manager: employee?.reportingChain?.[1]?.name || 'Neha Kapoor',
    stats: employee?.stats || [],
    recentActivity: employee?.recentActivity || [],
    personalAlert: undefined // Can be set dynamically based on conditions
  };
}

// Stat Card Component
function StatCard({ 
  label, 
  value, 
  delta, 
  icon: Icon,
  trend = 'neutral',
  color = 'brand'
}: { 
  label: string; 
  value: string | number; 
  delta?: string;
  icon?: any;
  trend?: 'positive' | 'negative' | 'neutral';
  color?: 'brand' | 'success' | 'warning' | 'danger';
}) {
  const colorMap = {
    brand: 'bg-brand-50 text-brand-600 border-brand-200',
    success: 'bg-success-50 text-success-600 border-success-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    danger: 'bg-danger-50 text-danger-600 border-danger-200'
  };

  const trendColorMap = {
    positive: 'text-success-600',
    negative: 'text-danger-600',
    neutral: 'text-slate-500'
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md dark:border-white/10 dark:bg-surface-100">
      <div className="flex items-start justify-between mb-3">
        {Icon && (
          <div className={cn('rounded-xl p-2 border', colorMap[color])}>
            <Icon className="h-4 w-4" />
          </div>
        )}
        <span className={cn('text-xs font-medium', trendColorMap[trend])}>
          {delta}
        </span>
      </div>
      <p className="text-sm text-slate-600 dark:text-surface-400 mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
    </div>
  );
}

// Activity Item Component
function ActivityItem({
  title,
  description,
  date,
  icon: Icon,
  type = 'default',
  isLatest = false
}: {
  title: string;
  description?: string;
  date: string;
  icon?: any;
  type?: 'achievement' | 'alert' | 'update' | 'default';
  isLatest?: boolean;
}) {
  const typeMap = {
    achievement: 'bg-success-50 text-success-700 border-success-200',
    alert: 'bg-warning-50 text-warning-700 border-warning-200',
    update: 'bg-brand-50 text-brand-700 border-brand-200',
    default: 'bg-slate-50 text-slate-700 border-slate-200'
  };

  return (
    <div className={cn(
      'relative flex gap-3 rounded-xl border p-3 transition',
      typeMap[type],
      isLatest && 'ring-2 ring-offset-2 ring-brand-400'
    )}>
      <div className="flex-shrink-0 mt-0.5">
        {Icon ? (
          <Icon className="h-5 w-5" />
        ) : (
          <div className="h-2 w-2 rounded-full bg-current mt-2" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold">{title}</p>
        {description && <p className="text-xs opacity-75 mt-1">{description}</p>}
        <p className="text-xs opacity-60 mt-2">{date}</p>
      </div>
    </div>
  );
}

// Alert Banner Component
function AlertBanner({
  title,
  description,
  type = 'info',
  action
}: {
  title: string;
  description?: string;
  type?: 'success' | 'warning' | 'alert' | 'info';
  action?: { label: string; onClick: () => void };
}) {
  const typeMap = {
    success: 'bg-success-50 border-success-200 text-success-700',
    warning: 'bg-warning-50 border-warning-200 text-warning-700',
    alert: 'bg-danger-50 border-danger-200 text-danger-700',
    info: 'bg-brand-50 border-brand-200 text-brand-700'
  };

  const iconMap = {
    success: CheckCircle2,
    warning: AlertCircle,
    alert: AlertCircle,
    info: AlertCircle
  };

  const Icon = iconMap[type];

  return (
    <div className={cn('rounded-xl border p-4 flex items-start gap-3', typeMap[type])}>
      <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="font-semibold text-sm">{title}</p>
        {description && <p className="text-xs opacity-75 mt-1">{description}</p>}
      </div>
      {action && (
        <button
          onClick={action.onClick}
          className="text-xs font-semibold whitespace-nowrap hover:opacity-75 transition"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

export function DynamicEmployeeLoginLayout({ initialRole = 'employee' }: DynamicEmployeeLoginLayoutProps) {
  const [email, setEmail] = useState('employee@ampcus.example');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);

  const employeeData = getEmployeeData();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 800));
      await login(email, 'EMPLOYEE');
    } finally {
      setLoading(false);
    }
  };

  // Current hour for greeting
  const hour = new Date().getHours();
  const getGreeting = () => {
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  // Check leave balance status
  const getLeaveStatus = (balance: number) => {
    if (balance > 10) return { type: 'success' as const, label: 'Sufficient balance' };
    if (balance > 5) return { type: 'warning' as const, label: 'Plan ahead' };
    return { type: 'alert' as const, label: 'Low balance' };
  };

  const leaveStatus = employeeData ? getLeaveStatus(employeeData.leaveBalance) : { type: 'neutral' as const, label: 'N/A' };

  return (
    <div className="relative overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white min-h-screen">
      {/* Decorative Backgrounds */}
      <div className="pointer-events-none absolute left-[-2rem] top-64 h-72 w-72 rounded-full bg-[#31C48D]/15 blur-3xl dark:bg-success-500/10" />
      <div className="pointer-events-none absolute right-[-4rem] bottom-32 h-96 w-96 rounded-full bg-[#3B82F6]/10 blur-3xl dark:bg-brand-500/5" />

      <div className="relative mx-auto flex min-h-screen max-w-[1840px] flex-col gap-8 px-4 py-8 sm:px-6 lg:flex-row lg:gap-12 lg:px-14 lg:py-12">
        {/* Left Side - Employee Information & Personalized Content */}
        <div className="w-full flex-1 lg:pr-12">
          {/* Header Badge */}
          <div className="mb-8 inline-flex items-center gap-3 rounded-full bg-white/90 px-4 py-3 shadow-xl shadow-slate-200/60 backdrop-blur-xl sm:px-5 sm:py-3.5 dark:bg-surface-100/90 dark:shadow-black/20">
            <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-gradient-to-br from-brand-500 to-brand-600 text-lg font-bold text-white shadow-lg shadow-slate-300/50 dark:shadow-black/30">
              HR
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">HRMS Portal</p>
              <p className="text-xs text-slate-500 dark:text-surface-400">Employee Self-Service</p>
            </div>
          </div>

          {/* Personalized Welcome */}
          <div className="mb-8">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight tracking-tight text-slate-950 dark:text-white mb-2">
              {getGreeting()},<br />{employeeData?.name.split(' ')[0] || 'Employee'}
            </h1>
            <p className="text-lg text-slate-600 dark:text-surface-300 max-w-2xl">
              Welcome to your personalized workplace hub. Stay updated on attendance, leaves, payroll, and everything you need.
            </p>
          </div>

          {/* Employee Profile Card - Condensed */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lg shadow-slate-200/40 dark:border-white/10 dark:bg-surface-100 dark:shadow-black/20 mb-6">
            <div className="flex items-start justify-between mb-6 pb-6 border-b border-slate-200 dark:border-white/10">
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{employeeData?.name}</h3>
                <p className="text-sm text-brand-600 dark:text-brand-400 font-medium">{employeeData?.title}</p>
              </div>
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-600 text-2xl font-bold text-white shadow-lg">
                {employeeData?.name.charAt(0)}
              </div>
            </div>

            {/* Quick Info Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Department</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-brand-500" />
                  {employeeData?.department}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Location</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-success-500" />
                  {employeeData?.location}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Manager</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                  <Users className="h-4 w-4 text-warning-500" />
                  {employeeData?.manager}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Tenure</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-purple-500" />
                  {employeeData?.tenure}
                </p>
              </div>
            </div>
          </div>

          {/* Alert Banners */}
          <div className="space-y-3 mb-6">
            <AlertBanner
              title="Leave Balance Alert"
              description={`You have ${employeeData?.leaveBalance || 0} days remaining. Plan your leaves wisely.`}
              type={leaveStatus.type}
            />
            <AlertBanner
              title="Attendance Check"
              description={`You're marked present for ${employeeData?.presentDays || 0} days this month.`}
              type="info"
            />
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 mb-8 sm:grid-cols-4">
            <StatCard
              label="Leave Balance"
              value={`${employeeData?.leaveBalance || 0} days`}
              delta={leaveStatus.label}
              icon={Calendar}
              trend={leaveStatus.type === 'alert' ? 'negative' : leaveStatus.type === 'warning' ? 'neutral' : 'positive'}
              color={leaveStatus.type}
            />
            <StatCard
              label="Days Present"
              value={employeeData?.presentDays || 0}
              delta="+2 vs last month"
              icon={CheckCircle2}
              trend="positive"
              color="success"
            />
            <StatCard
              label="Tenure"
              value={employeeData?.tenure || 'N/A'}
              delta="Last increment pending"
              icon={Zap}
              color="warning"
            />
            <StatCard
              label="Next Increment"
              value={employeeData?.nextIncrement ? new Date(employeeData.nextIncrement).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'N/A'}
              delta={employeeData?.nextIncrement ? `${Math.ceil((new Date(employeeData.nextIncrement).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days away` : 'N/A'}
              icon={BriefcaseBusiness}
              color="brand"
            />
          </div>

          {/* Recent Activity Section */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lg shadow-slate-200/40 dark:border-white/10 dark:bg-surface-100 dark:shadow-black/20">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Recent Activity</h3>
              <a href="#" className="text-sm text-brand-600 hover:text-brand-700 font-semibold flex items-center gap-1">
                View All <ChevronRight className="h-4 w-4" />
              </a>
            </div>
            <div className="space-y-3">
              {employeeData?.recentActivity?.slice(0, 3).map((activity, idx) => (
                <ActivityItem
                  key={idx}
                  title={activity}
                  date={['2 days ago', '1 week ago', '2 weeks ago'][idx]}
                  icon={idx === 0 ? CheckCircle2 : undefined}
                  type={idx === 0 ? 'achievement' : 'update'}
                  isLatest={idx === 0}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full flex-1 flex items-start justify-center lg:sticky lg:top-8 lg:max-h-[calc(100vh-4rem)]">
          <div className="w-full max-w-md rounded-3xl border border-slate-200/75 bg-white/95 p-6 shadow-2xl shadow-slate-300/40 backdrop-blur-xl sm:p-8 dark:border-white/10 dark:bg-surface-100/95 dark:shadow-black/50">
            {/* Sign In Header */}
            <div className="mb-8">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-surface-400">Sign in</p>
              <h2 className="mt-4 text-2xl font-bold tracking-tight text-slate-950 dark:text-white">Welcome back</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-surface-300">Enter your credentials to access your dashboard.</p>
            </div>

            {/* Employee Role Badge */}
            <div className="mb-6 rounded-2xl bg-gradient-to-r from-brand-50 to-success-50 p-3 border border-brand-200 dark:from-surface-200 dark:to-surface-200 dark:border-white/10">
              <p className="text-xs font-semibold text-brand-700 dark:text-brand-400 flex items-center gap-2">
                <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-brand-500 text-white text-xs font-bold">E</span>
                Signing in as Employee
              </p>
            </div>

            {/* Login Form */}
            <form onSubmit={handleLogin} className="space-y-5">
              <label className="block text-sm font-semibold text-slate-800 dark:text-white">
                Email address
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition-all duration-150 focus:border-brand-400 focus:ring-2 focus:ring-brand-400/20 dark:border-white/10 dark:bg-surface-200 dark:text-white dark:focus:border-brand-400"
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
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-sm text-slate-900 outline-none transition-all duration-150 focus:border-brand-400 focus:ring-2 focus:ring-brand-400/20 dark:border-white/10 dark:bg-surface-200 dark:text-white dark:focus:border-brand-400"
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
                    className="h-4 w-4 rounded border-slate-300 text-brand-500 focus:ring-brand-400 dark:border-white/20 dark:bg-surface-200"
                  />
                  Remember me
                </label>
                <a href="#" className="font-semibold text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300">
                  Forgot password?
                </a>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-brand-600 to-brand-700 px-5 py-3 text-sm font-semibold text-white shadow-xl shadow-brand-500/30 transition duration-150 hover:from-brand-700 hover:to-brand-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span>{loading ? 'Signing in...' : 'Sign in'}</span>
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

            {/* Footer */}
            <p className="mt-8 text-center text-xs text-slate-500 dark:text-surface-500">
              Having issues? <a href="#" className="text-brand-600 hover:text-brand-700 font-semibold dark:text-brand-400">Contact support</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
