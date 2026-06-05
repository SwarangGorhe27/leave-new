import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { UserCheck, UserMinus, Clock, Plane, Briefcase } from "lucide-react";

interface TodayAttendanceOverviewProps {
  stats: {
    present: { count: number; percentage: number };
    onLeave: { count: number; percentage: number };
    absent: { count: number; percentage: number };
    late: { count: number; percentage: number };
    wfh: { count: number; percentage: number };
  };
}

export function TodayAttendanceOverview({ stats }: TodayAttendanceOverviewProps) {
  const cards = [
    { label: "Present Today", value: stats.present.count, percentage: stats.present.percentage, icon: UserCheck, color: "text-emerald-500", bg: "bg-emerald-500/10" },
    { label: "On Leave", value: stats.onLeave.count, percentage: stats.onLeave.percentage, icon: Plane, color: "text-blue-500", bg: "bg-blue-500/10" },
    { label: "Absent", value: stats.absent.count, percentage: stats.absent.percentage, icon: UserMinus, color: "text-red-500", bg: "bg-red-500/10" },
    { label: "Late Arrivals", value: stats.late.count, percentage: stats.late.percentage, icon: Clock, color: "text-amber-500", bg: "bg-amber-500/10" },
    { label: "Work From Home", value: stats.wfh.count, percentage: stats.wfh.percentage, icon: Briefcase, color: "text-indigo-500", bg: "bg-indigo-500/10" },
  ];

  return (
    <Card className="shadow-sm border-border h-full flex flex-col">
      <CardHeader className="pb-3 border-b border-border/50 p-4">
        <CardTitle className="text-sm font-black text-foreground uppercase tracking-wider">
          Today's Attendance Overview
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 p-4 space-y-2 flex-1 overflow-auto">
        {cards.map((card) => (
          <div key={card.label} className="flex items-center justify-between p-2.5 rounded-xl border border-border/50 bg-secondary/5 group hover:bg-secondary/10 transition-all">
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-lg ${card.bg} flex items-center justify-center transition-transform group-hover:scale-110`}>
                <card.icon className={`w-4 h-4 ${card.color}`} />
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] font-black text-foreground uppercase tracking-wider">{card.label}</span>
                <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">{card.percentage}% of total</span>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xl font-black text-foreground block leading-none tracking-tighter">{card.value}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
