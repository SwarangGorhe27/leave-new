import { BriefcaseBusiness, CalendarClock, CircleDashed, TrendingUp } from 'lucide-react';
import { Avatar, Badge, Button } from '@components/ui';
import type { Employee } from '@/types/employee';

interface EmployeeOverviewProps {
  employee: Employee;
}

const icons = [CalendarClock, CircleDashed, BriefcaseBusiness, TrendingUp];

export function EmployeeOverview({ employee }: EmployeeOverviewProps) {
  return (
    <div className="space-y-5">
      <section className="surface-card grid gap-6 p-5 lg:grid-cols-[1.4fr_0.6fr]">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start">
          <Avatar name={employee.name} size="2xl" status="online" />
          <div className="space-y-3">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-2xl font-semibold text-surface-900 dark:text-white">{employee.name}</h2>
                <Badge variant="brand">{employee.code}</Badge>
                <Badge variant={employee.status === 'Active' ? 'success' : employee.status === 'On Leave' ? 'warning' : 'info'} dot>
                  {employee.status}
                </Badge>
              </div>
              <p className="mt-1 text-sm text-surface-600 dark:text-white/55">{employee.designation} · {employee.department}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button size="sm">Promote</Button>
              <Button size="sm" variant="secondary">Update documents</Button>
              <Button size="sm" variant="ghost">View lifecycle</Button>
            </div>
          </div>
        </div>
        <div className="surface-card flex flex-col justify-between bg-surface-50/70 p-4 dark:bg-white/[0.03]">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-surface-500 dark:text-white/35">Reporting chain</p>
            <div className="mt-4 flex items-center gap-3 overflow-x-auto pb-1">
              {employee.reportingChain.map((person) => (
                <div key={person.name} className="flex min-w-[150px] items-center gap-2 rounded-2xl border border-surface-300/60 bg-surface-0 px-3 py-2 dark:border-white/10 dark:bg-white/5">
                  <Avatar name={person.name} size="sm" />
                  <div>
                    <p className="text-xs font-medium text-surface-800 dark:text-white/80">{person.name}</p>
                    <p className="text-2xs text-surface-500 dark:text-white/45">{person.title}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {employee.stats.map((stat, index) => {
          const Icon = icons[index] ?? CalendarClock;
          return (
            <article key={stat.label} className="surface-card p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-200">
                <Icon className="h-5 w-5" />
              </div>
              <p className="mt-5 text-2xl font-semibold text-surface-900 dark:text-white">{stat.value}</p>
              <p className="mt-1 text-sm text-surface-600 dark:text-white/55">{stat.label}</p>
              {stat.delta ? <p className="mt-3 text-xs text-surface-500 dark:text-white/35">{stat.delta}</p> : null}
            </article>
          );
        })}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1fr_0.8fr]">
        <article className="surface-card p-5">
          <h3 className="text-sm font-semibold text-surface-900 dark:text-white">Recent activity</h3>
          <div className="mt-4 space-y-3">
            {employee.recentActivity.map((activity, index) => (
              <div key={activity} className="flex items-start gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-brand-500" />
                <div>
                  <p className="text-sm text-surface-800 dark:text-white/80">{activity}</p>
                  <p className="text-xs text-surface-500 dark:text-white/35">Event {index + 1}</p>
                </div>
              </div>
            ))}
          </div>
        </article>
        <article className="surface-card p-5">
          <h3 className="text-sm font-semibold text-surface-900 dark:text-white">Employment summary</h3>
          <dl className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-surface-500 dark:text-white/40">Location</dt>
              <dd className="mt-1 font-medium text-surface-800 dark:text-white/80">{employee.location}</dd>
            </div>
            <div>
              <dt className="text-surface-500 dark:text-white/40">Joined</dt>
              <dd className="mt-1 font-medium text-surface-800 dark:text-white/80">{employee.joinedAt}</dd>
            </div>
            <div>
              <dt className="text-surface-500 dark:text-white/40">Email</dt>
              <dd className="mt-1 font-medium text-surface-800 dark:text-white/80">{employee.email}</dd>
            </div>
            <div>
              <dt className="text-surface-500 dark:text-white/40">Leave balance</dt>
              <dd className="mt-1 font-medium text-surface-800 dark:text-white/80">{employee.leaveBalance} days</dd>
            </div>
          </dl>
        </article>
      </section>
    </div>
  );
}
