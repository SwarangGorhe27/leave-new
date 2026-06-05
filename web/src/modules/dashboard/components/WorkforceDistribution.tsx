import { Users } from 'lucide-react';
import { cn } from '@utils/utils';

export interface DepartmentData {
  name: string;
  count: number;
  color?: string;
}

interface WorkforceDistributionProps {
  departments: DepartmentData[];
  totalEmployees: number;
  isLoading?: boolean;
}

const departmentColors: Record<string, string> = {
  Engineering: 'bg-sky-500 dark:bg-sky-400',
  'Human Resources': 'bg-emerald-500 dark:bg-emerald-400',
  Finance: 'bg-amber-500 dark:bg-amber-400',
  Operations: 'bg-violet-500 dark:bg-violet-400',
  'Sales & Marketing': 'bg-pink-500 dark:bg-pink-400',
  Administration: 'bg-indigo-500 dark:bg-indigo-400',
  Product: 'bg-cyan-500 dark:bg-cyan-400',
  'Quality Assurance': 'bg-teal-500 dark:bg-teal-400',
};

export function WorkforceDistribution({
  departments,
  totalEmployees,
  isLoading,
}: WorkforceDistributionProps) {
  const sortedDepts = [...departments].sort((a, b) => b.count - a.count);
  const displayDepts = sortedDepts.slice(0, 6);

  return (
    <div className="surface-card rounded-2xl px-6 py-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-surface-900 dark:text-white">
            Employees by Department
          </h3>
          <p className="mt-1 text-xs text-surface-500 dark:text-white/50">
            Workforce distribution (top departments)
          </p>
        </div>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-100 dark:bg-white/10">
          <Users className="h-4 w-4 text-surface-500 dark:text-white/50" />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="h-3 w-24 animate-pulse rounded bg-surface-200 dark:bg-white/10" />
                <div className="h-3 w-8 animate-pulse rounded bg-surface-200 dark:bg-white/10" />
              </div>
              <div className="h-2 w-full animate-pulse rounded bg-surface-200 dark:bg-white/10" />
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {displayDepts.map((dept) => {
            const percentage = totalEmployees > 0 ? (dept.count / totalEmployees) * 100 : 0;
            const colorClass = departmentColors[dept.name] || departmentColors.Administration;

            return (
              <div key={dept.name}>
                {/* Label and count */}
                <div className="mb-1.5 flex items-center justify-between">
                  <span className="text-xs font-medium text-surface-600 dark:text-white/70">
                    {dept.name}
                  </span>
                  <span className="text-xs font-semibold text-surface-900 dark:text-white">
                    {dept.count}
                  </span>
                </div>

                {/* Bar */}
                <div className="h-2 overflow-hidden rounded-full bg-surface-100 dark:bg-white/5">
                  <div
                    className={cn('h-full rounded-full transition-all', colorClass)}
                    style={{ width: `${Math.max(percentage, 4)}%` }}
                  />
                </div>

                {/* Percentage */}
                <p className="mt-0.5 text-2xs text-surface-400 dark:text-white/40">
                  {percentage.toFixed(0)}% of total
                </p>
              </div>
            );
          })}

        </div>
      )}
    </div>
  );
}
