import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { cn } from '@utils/utils';
import { EmptyState } from './EmptyState';
import { SkeletonBlock } from './SkeletonLoader';
import { DonutChart } from '../../ui/donut-chart';

import type { DepartmentData } from '../WorkforceDistribution';



interface DonutSegment {
  priority: string;
  count: number;
  color: string;            // stroke colour class (Tailwind → inline)
  colorHex: string;         // actual hex for SVG
  label: string;
  badgeClass: string;
  dotClass: string;
}

const deptHexColors: Record<string, string> = {
  Engineering: '#0ea5e9', // sky-500
  'Human Resources': '#10b981', // emerald-500
  Finance: '#f59e0b', // amber-500
  Operations: '#8b5cf6', // violet-500
  'Sales & Marketing': '#ec4899', // pink-500
  Administration: '#6366f1', // indigo-500
  Product: '#06b6d4', // cyan-500
  'Quality Assurance': '#14b8a6', // teal-500
};

function getTeamsForDepartment(name: string, totalCount: number) {
  // Mock logic to split department count into realistic teams
  if (name === 'Engineering') {
    return [
      { name: 'AI/ML', count: Math.ceil(totalCount * 0.35) },
      { name: 'Frontend', count: Math.ceil(totalCount * 0.35) },
      { name: 'Backend', count: totalCount - Math.ceil(totalCount * 0.35) * 2 }
    ].filter(t => t.count > 0);
  }
  if (name === 'Human Resources') {
    return [
      { name: 'Talent Acquisition', count: Math.ceil(totalCount * 0.6) },
      { name: 'Employee Relations', count: totalCount - Math.ceil(totalCount * 0.6) }
    ].filter(t => t.count > 0);
  }
  if (name === 'Finance') {
    return [
      { name: 'Accounting', count: Math.ceil(totalCount * 0.5) },
      { name: 'Payroll', count: totalCount - Math.ceil(totalCount * 0.5) }
    ].filter(t => t.count > 0);
  }
  if (name === 'Operations') {
    return [
      { name: 'Logistics', count: Math.ceil(totalCount * 0.6) },
      { name: 'Support', count: totalCount - Math.ceil(totalCount * 0.6) }
    ].filter(t => t.count > 0);
  }
  // Generic fallback if no specific teams
  return [
    { name: 'Core Team', count: Math.ceil(totalCount * 0.7) },
    { name: 'Support', count: totalCount - Math.ceil(totalCount * 0.7) }
  ].filter(t => t.count > 0);
}

function buildDepartmentSegments(departments?: DepartmentData[]): DonutSegment[] {
  if (!departments || departments.length === 0) return [];
  const total = departments.reduce((sum, d) => sum + d.count, 0) || 1;

  // Show top 3 or 4 departments for clarity
  return departments.slice(0, 4).map(dept => {
    const colorHex = deptHexColors[dept.name] || '#94a3b8';
    return {
      priority: dept.name as any,
      count: dept.count,
      colorHex,
      color: colorHex,
      label: dept.name,
      badgeClass: 'bg-surface-50 text-surface-900 border border-surface-200 dark:bg-white/5 dark:border-white/10 dark:text-white',
      dotClass: '', // Using inline style
      total,
      teams: getTeamsForDepartment(dept.name, dept.count),
    };
  });
}

/* ─── Donut Chart removed, using external DonutChart instead ─── */

/* ─── Legend row (clickable) ─────────────────────────────────────── */
function LegendRow({
  seg,
}: {
  seg: DonutSegment;
}) {


  return (
    <div
      className={cn(
        'flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left',
        seg.count === 0 && 'opacity-40'
      )}
    >
      {/* Colour dot */}
      <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: seg.colorHex }} />

      {/* Label */}
      <span className="flex-1 text-sm font-medium text-surface-700 dark:text-white/70">
        {seg.label}
      </span>

      {/* Count badge */}
      <span className={cn(
        'flex h-6 min-w-[28px] items-center justify-center rounded-full px-2 text-xs font-bold tabular-nums',
        seg.badgeClass,
      )}>
        {seg.count}
      </span>
    </div>
  );
}

/* ─── Skeleton donut ─────────────────────────────────────────────── */
function DonutSkeleton() {
  return (
    <div className="flex items-center gap-6">
      {/* Circle placeholder */}
      <div className="relative h-[140px] w-[140px] shrink-0">
        <svg width="140" height="140" viewBox="0 0 140 140">
          <circle cx={70} cy={70} r={54} fill="none" strokeWidth={13}
            stroke="currentColor" className="animate-pulse text-surface-100 dark:text-white/8" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <SkeletonBlock className="h-5 w-8 rounded" />
        </div>
      </div>
      {/* Legend placeholders */}
      <div className="flex-1 space-y-2.5">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex items-center gap-3">
            <SkeletonBlock className="h-2.5 w-2.5 rounded-full" />
            <SkeletonBlock className="h-3 w-20 rounded" />
            <SkeletonBlock className="ml-auto h-5 w-8 rounded-full" />
          </div>
        ))}
      </div>
    </div>
  );
}



/* ─── Public list component ──────────────────────────────────────── */
interface ActionListProps {
  departments?: DepartmentData[];
  isLoading?: boolean;
}

export function ActionList({ departments, isLoading }: ActionListProps) {
  if (isLoading) return <DonutSkeleton />;

  if (!departments || departments.length === 0) {
    return (
      <EmptyState
        title="No pending actions"
        description="You're all caught up. Nothing needs attention right now."
        icon={<CheckCircle2 className="h-10 w-10 text-success-500/40 dark:text-success-500/30" />}
      />
    );
  }

  const segs = buildDepartmentSegments(departments);

  return (
    <div className="space-y-5 px-4 pt-2 pb-6">
      {/* Donut + legend */}
      <div className="flex flex-col sm:flex-row items-center gap-10 sm:gap-16">
        <div className="shrink-0">
          <DonutChart 
            data={segs.map((seg) => ({
              label: seg.label,
              value: seg.count,
              color: seg.colorHex,
              teams: (seg as any).teams,
            }))}
            size={220}
            strokeWidth={36}
          centerContent={
            <div className="flex flex-col items-center justify-center">
              <span className="text-2xl font-bold text-surface-900 dark:text-white -mb-1">
                {departments ? departments.reduce((s,d) => s + d.count, 0) : 0}
              </span>
              <span className="text-[10px] font-medium text-surface-500">employees</span>
            </div>
          }
        />
        </div>

        {/* Legend */}
        <div className="flex w-full flex-1 flex-col space-y-2">
          {segs.map(seg => (
            <LegendRow key={seg.priority} seg={seg} />
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─── Urgency chip ───────────────────────────────────────────────── */
export function ActionUrgencyChip({
  highCount,
  mediumCount,
}: {
  highCount: number;
  mediumCount: number;
}) {
  const total = highCount + mediumCount;
  if (total === 0) return null;
  return (
    <div className="flex items-center gap-2 rounded-xl border border-surface-200 bg-surface-50 px-3 py-1.5 text-xs dark:border-white/10 dark:bg-white/5">
      <AlertCircle className="h-3.5 w-3.5 text-red-500 dark:text-red-400" />
      <span className="font-semibold text-red-600 dark:text-red-400">{highCount} high</span>
      <span className="text-surface-300 dark:text-white/20">·</span>
      <span className="font-medium text-surface-600 dark:text-white/60">{mediumCount} medium</span>
    </div>
  );
}
