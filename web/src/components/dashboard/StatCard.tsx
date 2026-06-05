import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { cn } from "@utils/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: string;
    positive: boolean;
  };
  color?: string;
}

export function StatCard({ label, value, icon, trend }: StatCardProps) {
  return (
    <div className="flat-card flat-card-hover bg-card p-5">
      <div className="flex items-start gap-4">
        <div className="w-11 h-11 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0 text-foreground">
          {icon}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">{label}</p>
          <p className="text-2xl font-bold text-foreground mt-0.5">{value}</p>
          {trend && (
            <div
              className={cn(
                "mt-2 inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-semibold border",
                trend.positive
                  ? "bg-secondary text-foreground border-border"
                  : "dashboard-badge-later"
              )}
            >
              {trend.positive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
              {trend.value}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="flat-card bg-card p-5">
      <div className="animate-pulse space-y-2">
        <div className="h-11 w-11 rounded-lg bg-secondary" />
        <div className="h-3 w-20 rounded bg-secondary" />
        <div className="h-6 w-16 rounded bg-secondary" />
      </div>
    </div>
  );
}
