import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { HelpCircle, TrendingUp } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";
import { cn } from "../ui/utils";

interface AttendanceHealthSnapshotProps {
  score: number;
  breakdown: {
    present: number;
    late: number;
    absent: number;
    leave: number;
  };
}

export function AttendanceHealthSnapshot({ score, breakdown }: AttendanceHealthSnapshotProps) {
  const getScoreColor = (s: number) => {
    if (s >= 90) return "text-slate-700 stroke-slate-700";
    if (s >= 75) return "text-amber-500 stroke-amber-500";
    return "text-red-500 stroke-red-500";
  };

  const getScoreText = (s: number) => {
    if (s >= 90) return "Excellent attendance today";
    if (s >= 75) return "Attendance is good";
    return "Attendance needs attention";
  };

  const getScoreBg = (s: number) => {
    if (s >= 90) return "bg-secondary/10 text-foreground";
    if (s >= 75) return "bg-amber-500/10 text-amber-600";
    return "bg-red-500/10 text-red-600";
  };

  // SVG Circle calculations
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <Card className="shadow-sm border-border h-full flex flex-col">
      <CardHeader className="pb-4 border-b border-border/50">
        <CardTitle className="text-base font-black text-foreground uppercase tracking-wider flex items-center gap-2">
          Attendance Health Snapshot
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <HelpCircle className="w-3.5 h-3.5 text-muted-foreground cursor-help" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="text-[10px] font-bold">Overall attendance score for the selected date.</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-8 flex-1 flex flex-col items-center justify-center space-y-8">
        {/* Large Circular Progress */}
        <div className="relative flex items-center justify-center">
          <svg className="w-48 h-48 transform -rotate-90">
            <circle
              cx="96"
              cy="96"
              r={radius}
              stroke="currentColor"
              strokeWidth="12"
              fill="transparent"
              className="text-secondary/30"
            />
            <circle
              cx="96"
              cy="96"
              r={radius}
              stroke="currentColor"
              strokeWidth="12"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className={cn("transition-all duration-1000 ease-in-out", getScoreColor(score))}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn("text-5xl font-black", getScoreColor(score).split(' ')[0])}>{score}</span>
            <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mt-1">Score</span>
          </div>
        </div>

        {/* Status Text */}
        <div className="text-center space-y-2">
           <div className={cn("px-4 py-1.5 rounded-full text-[11px] font-black uppercase tracking-widest inline-block", getScoreBg(score))}>
            {getScoreText(score)}
          </div>
           <div className="flex items-center justify-center gap-1.5 text-[10px] font-bold text-muted-foreground">
             <TrendingUp className="w-3 h-3 text-muted-foreground" /> +2% from yesterday
           </div>
        </div>

        {/* Breakdown Chips */}
        <div className="grid grid-cols-2 gap-3 w-full">
           <div className="p-3 rounded-2xl bg-secondary/20 border border-border/50 flex flex-col">
              <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1">Present</span>
              <span className="text-base font-black text-foreground">{breakdown.present}%</span>
           </div>
           <div className="p-3 rounded-2xl bg-secondary/20 border border-border/50 flex flex-col">
              <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1">Late</span>
              <span className="text-base font-black text-amber-600">{breakdown.late}%</span>
           </div>
           <div className="p-3 rounded-2xl bg-secondary/20 border border-border/50 flex flex-col">
              <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1">Absent</span>
              <span className="text-base font-black text-red-600">{breakdown.absent}%</span>
           </div>
           <div className="p-3 rounded-2xl bg-secondary/20 border border-border/50 flex flex-col">
              <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1">Leave</span>
              <span className="text-base font-black text-blue-600">{breakdown.leave}%</span>
           </div>
        </div>
      </CardContent>
    </Card>
  );
}
