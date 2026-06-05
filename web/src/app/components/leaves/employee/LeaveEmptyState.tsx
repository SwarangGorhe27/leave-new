import type { ElementType } from "react";
import { cn } from "../../ui/utils";

export function LeaveEmptyState({
  icon: Icon,
  title,
  description,
  className,
}: {
  icon: ElementType;
  title: string;
  description: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card/60 px-6 py-14 text-center",
        className,
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-secondary">
        <Icon className="h-6 w-6 text-muted-foreground" aria-hidden />
      </div>
      <p className="mt-3 text-sm font-semibold text-foreground">{title}</p>
      <p className="mt-1 max-w-sm text-xs text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}