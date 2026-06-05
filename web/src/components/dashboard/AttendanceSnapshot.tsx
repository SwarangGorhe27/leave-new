import { TrendingUp, TrendingDown, Minus, Clock } from 'lucide-react';
import { InsightBlock } from './kit/InsightBlock';
import { SkeletonBlock } from './kit/SkeletonLoader';

interface AttendanceTrend {
  date: string;
  present: number;
  absent?: number;
  late?: number;
}

interface AttendanceSnapshotProps {
  presentToday: number;
  absentToday: number;
  lateToday: number;
  attendanceRate: number;
  dailyTrend?: AttendanceTrend[];
  isLoading?: boolean;
}

/* ─── Vertical bar SVG chart ─────────────────────────────────────── */
interface BarDef {
  label: string;
  value: number;
  colorFill: string;      // SVG fill
  colorText: string;      // label text class (Tailwind)
}

function AttendanceBars({
  present,
  absent,
  late,
}: {
  present: number;
  absent: number;
  late: number;
}) {
  const bars: BarDef[] = [
    { label: 'Present', value: present, colorFill: '#10B981', colorText: 'text-emerald-600 dark:text-emerald-400' },
    { label: 'Absent',  value: absent,  colorFill: '#EF4444', colorText: 'text-red-600    dark:text-red-400'     },
    { label: 'Late',    value: late,    colorFill: '#F59E0B', colorText: 'text-amber-600  dark:text-amber-400'   },
  ];

  const max = Math.max(present, absent, late, 1);
  const chartH = 80;   // max bar pixel height
  const barW   = 36;
  const gapX   = 22;
  const svgW   = bars.length * barW + (bars.length - 1) * gapX + 2;  // +2 padding

  return (
    <div className="flex flex-col items-center">
      <svg
        width={svgW}
        height={chartH + 28}
        viewBox={`0 0 ${svgW} ${chartH + 28}`}
        overflow="visible"
        className="w-full max-w-[240px]"
      >
        {bars.map((bar, i) => {
          const barH    = Math.max((bar.value / max) * chartH, bar.value > 0 ? 6 : 2);
          const x       = i * (barW + gapX);
          const y       = chartH - barH;

          return (
            <g key={bar.label}>
              {/* Bar track (background) */}
              <rect
                x={x} y={0}
                width={barW} height={chartH}
                rx={6}
                opacity={0.08}
                fill={bar.colorFill}
              />
              {/* Bar fill */}
              <rect
                x={x} y={y}
                width={barW} height={barH}
                rx={6}
                fill={bar.colorFill}
                style={{ transition: 'height 0.6s cubic-bezier(.4,0,.2,1), y 0.6s cubic-bezier(.4,0,.2,1)' }}
              />
              {/* Value on top */}
              <text
                x={x + barW / 2}
                y={y - 5}
                textAnchor="middle"
                fontSize="11"
                fontWeight="700"
                fontFamily="Inter, system-ui, sans-serif"
                fill={bar.colorFill}
              >
                {bar.value}
              </text>
              {/* Label below */}
              <text
                x={x + barW / 2}
                y={chartH + 16}
                textAnchor="middle"
                fontSize="10"
                fontWeight="500"
                fontFamily="Inter, system-ui, sans-serif"
                fill="#9CA3AF"
              >
                {bar.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/* ─── Sparkline ──────────────────────────────────────────────────── */
function buildSparkPath(points: number[]): string {
  if (points.length < 2) return '';
  const min   = Math.min(...points);
  const max   = Math.max(...points);
  const range = Math.max(1, max - min);
  const w = 88, h = 22;
  return points
    .map((v, i) => {
      const x = (i / (points.length - 1)) * w;
      const y = h - ((v - min) / range) * h;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');
}

export function AttendanceSnapshot({
  presentToday,
  absentToday,
  lateToday,
  attendanceRate,
  dailyTrend = [],
  isLoading,
}: AttendanceSnapshotProps) {
  const presentTrend  = dailyTrend.slice(-7).map(d => d.present).filter(Number.isFinite);
  const lateTrend     = dailyTrend.slice(-7).map(d => d.late ?? 0);
  const lastWeekLateAvg = lateTrend.length > 0
    ? lateTrend.reduce((a, b) => a + b, 0) / lateTrend.length : 0;
  const lateDeltaPct = lastWeekLateAvg > 0
    ? Math.round(((lateToday - lastWeekLateAvg) / lastWeekLateAvg) * 100) : 0;

  const lateInsight =
    lastWeekLateAvg <= 0
      ? lateToday > 0 ? 'Late arrivals detected today' : 'No late arrivals today'
      : lateDeltaPct >= 0
        ? `Late arrivals up ${lateDeltaPct}% vs last week`
        : `Late arrivals down ${Math.abs(lateDeltaPct)}% vs last week`;

  const spark = buildSparkPath(presentTrend);
  const rateGood = attendanceRate >= 90;

  // Trend icon + delta
  const TrendIcon = lateDeltaPct > 0 ? TrendingUp : lateDeltaPct < 0 ? TrendingDown : Minus;

  return (
    <div className="surface-card rounded-2xl px-6 py-6">
      {/* ── Header ────────────────────────────────── */}
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-surface-900 dark:text-white">
            Attendance Snapshot
          </h3>
          <p className="mt-0.5 text-xs text-surface-500 dark:text-white/45">
            Today's headcount at a glance
          </p>
        </div>

        {/* Rate pill */}
        <div className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold ${
          rateGood
            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'
            : 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'
        }`}>
          <span className={`h-1.5 w-1.5 rounded-full ${rateGood ? 'bg-emerald-500' : 'bg-amber-500'}`} />
          {attendanceRate.toFixed(1)}% rate
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          <div className="flex items-end justify-center gap-5">
            {[80, 28, 48].map((h, i) => (
              <div key={i} className="flex flex-col items-center gap-1.5">
                <SkeletonBlock className={`w-9 rounded-md`} style={{ height: h }} />
                <SkeletonBlock className="h-2.5 w-12 rounded" />
              </div>
            ))}
          </div>
          <SkeletonBlock className="h-10 w-full rounded-xl" />
        </div>
      ) : (
        <>
          {/* ── Bar chart ──────────────────────────── */}
          <div className="mb-5 flex justify-center">
            <AttendanceBars present={presentToday} absent={absentToday} late={lateToday} />
          </div>

          {/* ── Insight block ──────────────────────── */}
          <InsightBlock
            icon={<TrendIcon className="h-4 w-4" />}
            label="Late arrival trend"
            insight={lateInsight}
            rightSlot={
              spark ? (
                <svg width="92" height="28" viewBox="0 0 88 22" className="mt-0.5 text-brand-500/80 dark:text-brand-400/80">
                  <polyline
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinejoin="round"
                    strokeLinecap="round"
                    points={spark}
                  />
                </svg>
              ) : (
                <div className="flex items-center gap-1 text-xs font-medium text-surface-400 dark:text-white/35">
                  <Clock className="h-3.5 w-3.5" />
                  <span>7d</span>
                </div>
              )
            }
          />
        </>
      )}
    </div>
  );
}
