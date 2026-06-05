import { cn } from "../../ui/utils";

export function LeavePageSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("animate-pulse space-y-4", className)}>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 rounded-xl border border-border bg-secondary/80" />
        ))}
      </div>
      <div className="h-48 rounded-xl border border-border bg-secondary/60" />
      <div className="h-64 rounded-xl border border-border bg-secondary/60" />
    </div>
  );
}

export function TableSkeletonRows({ rows = 6 }: { rows?: number }) {
  return (
    <div className="animate-pulse divide-y divide-border">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 px-4 py-3">
          <div className="h-4 w-24 rounded bg-secondary" />
          <div className="h-4 flex-1 rounded bg-secondary" />
          <div className="h-4 w-16 rounded bg-secondary" />
        </div>
      ))}
    </div>
  );
}