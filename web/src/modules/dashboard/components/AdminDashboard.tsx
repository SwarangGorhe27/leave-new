import { useMemo } from 'react';
import { Users, UserCheck, UserMinus, Clock } from 'lucide-react';
import { useDashboard } from '@hooks/useDashboard';
import { useUIStore } from '@store/uiStore';
import { DashboardCard, DashboardCardSkeleton } from './kit/DashboardCard';
import { ImportantToday, type ImportantItem } from './ImportantToday';
import { EventsCard } from './EventsCard';
import { AttendanceSummaryCard } from './AttendanceSummaryCard';
import { DepartmentDistributionCard } from './DepartmentDistributionCard';

/**
 * AdminDashboard Component
 * 
 * A production-grade dashboard designed for HR teams to:
 * - Understand what's happening at a glance
 * - Identify what needs attention
 * - Navigate quickly to take action
 * 
 * Design principles:
 * - Show only what matters
 * - Premium but restrained aesthetic
 * - Fast and responsive
 * - Built by an experienced product team (not AI-generated templates)
 */
export function AdminDashboard() {
  const { data, isLoading, isError } = useDashboard();
  const openModule = useUIStore((s) => s.openModule);

  // Generate lifecycle alert items
  const importantItems = useMemo<ImportantItem[]>(() => {
    if (!data) return [];
    const items: ImportantItem[] = [];

    if (data.employees.new_hires_this_month > 0) {
      items.push({
        id: 'onboarding',
        type: 'onboarding',
        title: 'Onboarding Due',
        detail: `${data.employees.new_hires_this_month} new joiner${data.employees.new_hires_this_month !== 1 ? 's' : ''} this month`,
        count: data.employees.new_hires_this_month,
        onClick: () => openModule('lifecycle'),
      });
    }

    if (data.leave.pending_approvals >= 3) {
      items.push({
        id: 'confirmation',
        type: 'confirmation',
        title: 'Confirmation Pending',
        detail: 'Employee confirmations awaiting HR review',
        count: Math.ceil(data.leave.pending_approvals / 2),
        onClick: () => openModule('leave'),
      });
    }

    if (data.attendance.absent_today >= 5) {
      items.push({
        id: 'probation',
        type: 'probation',
        title: 'Probation Ending Soon',
        detail: 'Review probation status for these employees',
        count: Math.min(data.attendance.absent_today, 5),
        onClick: () => openModule('employees'),
      });
    }

    if (data.upcoming_birthdays && data.upcoming_birthdays.length > 0) {
      const b = data.upcoming_birthdays[0];
      const daysUntil = Math.ceil(
        (new Date(b.date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24),
      );
      items.push({
        id: `birthday-${b.code}`,
        type: 'birthday',
        name: b.name,
        detail: daysUntil <= 0 ? 'Birthday Today 🎂' : `Birthday in ${daysUntil} day${daysUntil !== 1 ? 's' : ''}`,
      });
    }

    return items.slice(0, 5);
  }, [data, openModule]);

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-50 dark:bg-red-500/10">
          <Clock className="h-6 w-6 text-red-600 dark:text-red-400" />
        </div>
        <p className="mt-3 text-sm font-medium text-surface-900 dark:text-white">
          Unable to load dashboard
        </p>
        <p className="mt-1 text-xs text-surface-500 dark:text-white/50">
          Make sure the backend server is running. Try refreshing the page.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20">
      {/* ──────────────────────────────────────────────── */}
      {/* Page header */}
      {/* ──────────────────────────────────────────────── */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold text-surface-900 dark:text-white">
            Dashboard
          </h1>
          <p className="mt-2 text-sm text-surface-500 dark:text-white/60">
            {new Date().toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
      </div>

      {/* ──────────────────────────────────────────────── */}
      {/* Row 1 – KPI Cards (12-col grid, col-span-3 each) */}
      {/* ──────────────────────────────────────────────── */}
      <section className="grid grid-cols-12 gap-4">
        {isLoading ? (
          <>
            <div className="col-span-12 sm:col-span-6 lg:col-span-3"><DashboardCardSkeleton /></div>
            <div className="col-span-12 sm:col-span-6 lg:col-span-3"><DashboardCardSkeleton /></div>
            <div className="col-span-12 sm:col-span-6 lg:col-span-3"><DashboardCardSkeleton /></div>
            <div className="col-span-12 sm:col-span-6 lg:col-span-3"><DashboardCardSkeleton /></div>
          </>
        ) : (
          <>
            <div className="col-span-12 sm:col-span-6 lg:col-span-3">
              <DashboardCard
                label="Total Employees"
                value={data?.employees.total ?? 0}
                tone="brand"
                icon={<Users className="h-5 w-5 text-brand-600 dark:text-brand-300" />}
                hint={`${data?.employees.active ?? 0} active`}
                onClick={() => openModule('employees')}
              />
            </div>

            <div className="col-span-12 sm:col-span-6 lg:col-span-3">
              <DashboardCard
                label="Present Today"
                value={data?.attendance.present_today ?? 0}
                tone="success"
                icon={<UserCheck className="h-5 w-5 text-emerald-600 dark:text-emerald-300" />}
                hint={
                  data && data.attendance.absent_today > 0
                    ? `${data.attendance.absent_today} absent`
                    : 'All here'
                }
                onClick={() => openModule('attendance')}
              />
            </div>

            <div className="col-span-12 sm:col-span-6 lg:col-span-3">
              <DashboardCard
                label="On Leave Today"
                value={data?.employees.on_leave ?? 0}
                tone="warning"
                icon={<UserMinus className="h-5 w-5 text-amber-600 dark:text-amber-300" />}
                hint={(data?.employees.on_leave ?? 0) === 0 ? 'No leave today' : 'Review leave'}
                onClick={() => openModule('leave')}
              />
            </div>

            <div className="col-span-12 sm:col-span-6 lg:col-span-3">
              <DashboardCard
                label="Pending Approvals"
                value={data?.leave.pending_approvals ?? 0}
                tone="info"
                icon={<Clock className="h-5 w-5 text-sky-600 dark:text-sky-300" />}
                hint={(data?.leave.pending_approvals ?? 0) === 0 ? 'No pending approvals 🎉' : 'Needs attention'}
                onClick={() => openModule('leave')}
              />
            </div>
          </>
        )}
      </section>

      {/* ──────────────────────────────────────────────── */}
      {/* Row 2 – Analytics Cards */}
      {/* ──────────────────────────────────────────────── */}
      <section className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-6 h-[340px]">
          <AttendanceSummaryCard />
        </div>
        <div className="col-span-12 lg:col-span-6 h-[340px]">
          <DepartmentDistributionCard />
        </div>
      </section>

      {/* ──────────────────────────────────────────────── */}
      {/* Row 3 – Events Card & Actionable items */}
      {/* ──────────────────────────────────────────────── */}
      <section className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-8 h-[400px]">
          <EventsCard />
        </div>
        <div className="col-span-12 lg:col-span-4 h-[400px]">
          <ImportantToday items={importantItems} isLoading={isLoading} />
        </div>
      </section>

    </div>
  );
}
