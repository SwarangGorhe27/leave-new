import { Activity, AlarmClock, CalendarCheck2, CalendarX2, Clock3, LucideIcon, Plane } from "lucide-react";
import { motion } from "motion/react";
import { KPI_ICON_TONES, type KpiTone } from "@/components/design-system";
import { AttendanceMetrics } from "./utils";

interface SummaryCardsProps {
  metrics: AttendanceMetrics;
}

export function SummaryCards({ metrics }: SummaryCardsProps) {
  const d = metrics.deltas;
  
  const toneMap: Record<number, KpiTone> = {
    0: "purple",
    1: "green",
    2: "red",
    3: "orange",
    4: "gray",
  };

  const cards: Array<{
    label: string;
    value: string;
    icon: LucideIcon;
    trend: string;
    sub?: string;
  }> = [
    {
      label: "Avg Work Hours",
      value: metrics.avgWorkHours.toFixed(1) + "h",
      icon: Clock3,
      trend: d?.avgWorkHours ?? "+0%",
      sub: "Track your hours",
    },
    { 
      label: "Present Days", 
      value: String(metrics.presentDays), 
      icon: CalendarCheck2, 
      trend: d?.presentDays ?? "Stable",
      sub: "Days checked in",
    },
    { 
      label: "Absent Days", 
      value: String(metrics.absentDays), 
      icon: CalendarX2, 
      trend: d?.absentDays ?? "0",
      sub: "Days marked absent",
    },
    { 
      label: "Leave Taken", 
      value: String(metrics.leaveTaken), 
      icon: Plane, 
      trend: d?.leaveTaken ?? "0",
      sub: "Total leaves used",
    },
    { 
      label: "Late In", 
      value: String(metrics.lateInCount), 
      icon: AlarmClock, 
      trend: d?.lateIn ?? "0",
      sub: "Late arrivals",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {cards.map((card, idx) => {
        const tone = toneMap[idx] || "purple";
        const iconTone = KPI_ICON_TONES[tone];

        return (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.08 }}
            whileHover={{ y: -4, scale: 1.015 }}
            className="flat-card flat-card-hover bg-card p-5 flex items-start gap-4 relative overflow-hidden"
          >
            <div
              className="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 text-white [&_svg]:stroke-white"
              style={{
                background: iconTone.background,
                boxShadow: iconTone.boxShadow,
                color: "#FFFFFF",
              }}
            >
              <card.icon className="w-5 h-5" />
            </div>
            
            <div className="min-w-0 flex-1">
              <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">{card.label}</p>
              <p className="text-2xl font-bold text-foreground mt-0.5">{card.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{card.sub}</p>
              {card.trend && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground mt-2 inline-block">
                  {card.trend}
                </span>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
