import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { Users } from 'lucide-react';
import { cn } from '@utils/utils';

const DEPARTMENT_DATA = [
  { name: 'Engineering', employees: 68 },
  { name: 'Sales', employees: 42 },
  { name: 'Marketing', employees: 24 },
  { name: 'HR', employees: 12 },
  { name: 'Finance', employees: 18 },
  { name: 'Support', employees: 34 },
];

const COLORS = ['#3B5BDB', '#10B981', '#F59E0B', '#3B82F6', '#8B5CF6', '#EF4444'];

export function DepartmentDistributionCard() {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-[24px] border border-surface-200/60 bg-surface-0 shadow-sm dark:border-white/10 dark:bg-surface-900/40">
      {/* Header */}
      <div className="border-b border-surface-200/60 p-5 dark:border-white/10">
        <h2 className="flex items-center gap-2 text-lg font-bold text-surface-900 dark:text-white">
          <Users className="h-5 w-5 text-brand-500" />
          Employees by Department
        </h2>
        <p className="mt-0.5 text-xs text-surface-500 dark:text-white/50">
          Current active workforce distribution
        </p>
      </div>

      <div className="flex-1 p-5">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={DEPARTMENT_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" opacity={0.5} />
            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: 'var(--text-secondary)' }}
              dy={10}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: 'var(--text-secondary)' }}
            />
            <Tooltip
              cursor={{ fill: 'var(--surface-100)', opacity: 0.5 }}
              contentStyle={{
                borderRadius: '12px',
                border: 'none',
                boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                backgroundColor: 'var(--surface-0)',
                color: 'var(--text-primary)',
                fontSize: '12px'
              }}
              itemStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
              labelStyle={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '4px' }}
            />
            <Bar dataKey="employees" radius={[6, 6, 0, 0]} maxBarSize={40}>
              {DEPARTMENT_DATA.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
