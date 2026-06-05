import { cn } from "../../ui/utils";

export function LeaveTypePill({ code, className }: { code: string; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex h-7 min-w-[1.75rem] px-1.5 items-center justify-center rounded-lg",
        "bg-secondary border border-border text-[10px] font-bold text-foreground flex-shrink-0",
        className,
      )}
      title={code}
    >
      {code}
    </span>
  );
}
