import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { UserCheck, UserMinus, UserX, Clock } from 'lucide-react';
import { cn } from '@utils/utils';

const ATTENDANCE_DATA = [
  { name: 'Logged In', value: 145, color: '#10B981' }, // success (green)
  { name: 'On Leave', value: 12, color: '#F59E0B' },   // warning (amber)
  { name: 'Not Logged In', value: 8, color: '#3B5BDB' },// brand (blue)
  { name: 'Half Day', value: 3, color: '#3B82F6' },    // info (sky blue)
];

const TOTAL_EMPLOYEES = ATTENDANCE_DATA.reduce((acc, curr) => acc + curr.value, 0);

interface StatProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  colorClass: string;
}

function StatRow({ label, value, icon, colorClass }: StatProps) {
  return (
    <div className="flex h-full min-h-[84px] items-center justify-between rounded-xl border border-surface-100 bg-surface-50 p-3 dark:border-white/5 dark:bg-white/5">
      <div className="flex items-center gap-3">
        <div className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl', colorClass)}>
          {icon}
        </div>
        <span className="text-sm font-medium text-surface-700 dark:text-white/80">{label}</span>
      </div>
      <span className="text-base font-bold text-surface-900 dark:text-white">{value}</span>
    </div>
  );
}

export function AttendanceSummaryCard() {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-[24px] border border-surface-200/60 bg-surface-0 shadow-sm dark:border-white/10 dark:bg-surface-900/40">
      {/* Header */}
      <div className="border-b border-surface-200/60 p-5 dark:border-white/10">
        <h2 className="text-lg font-bold text-surface-900 dark:text-white">
          Login & Attendance Summary
        </h2>
        <p className="mt-0.5 text-xs text-surface-500 dark:text-white/50">
          Today's real-time attendance overview
        </p>
      </div>

      <div className="grid flex-1 gap-6 p-5 md:grid-cols-[220px_minmax(0,1fr)] md:items-center">
        {/* Chart Area */}
        <div className="relative mx-auto w-full max-w-[260px] md:mx-0 md:max-w-none">
          <div className="relative h-[220px] w-full min-w-[220px] sm:h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={ATTENDANCE_DATA}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {ATTENDANCE_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
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
              </PieChart>
            </ResponsiveContainer>

            {/* Inner Total */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none px-4 text-center">
              <span className="text-3xl font-black text-surface-900 dark:text-white">{TOTAL_EMPLOYEES}</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-surface-400 dark:text-white/40">Total</span>
            </div>
          </div>
        </div>

        {/* Legend / Stats */}
        <div className="grid flex-1 gap-3 sm:grid-cols-2">
          <StatRow
            label="Logged In"
            value={ATTENDANCE_DATA[0].value}
            icon={<UserCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />}
            colorClass="bg-emerald-100 dark:bg-emerald-500/20"
          />
          <StatRow
            label="On Leave"
            value={ATTENDANCE_DATA[1].value}
            icon={<UserMinus className="h-4 w-4 text-amber-600 dark:text-amber-400" />}
            colorClass="bg-amber-100 dark:bg-amber-500/20"
          />
          <StatRow
            label="Not Logged In"
            value={ATTENDANCE_DATA[2].value}
            icon={<UserX className="h-4 w-4 text-rose-600 dark:text-rose-400" />}
            colorClass="bg-rose-100 dark:bg-rose-500/20"
          />
          <StatRow
            label="Half Day"
            value={ATTENDANCE_DATA[3].value}
            icon={<Clock className="h-4 w-4 text-blue-600 dark:text-blue-400" />}
            colorClass="bg-blue-100 dark:bg-blue-500/20"
          />
        </div>
      </div>
    </div>
  );
}
