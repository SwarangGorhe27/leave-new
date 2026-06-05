import type { ElementType } from "react";
import { cn } from "../ui/utils";

export function AdminNavItem({
  label,
  icon: Icon,
  active,
  compact = false,
  onClick,
}: {
  label: string;
  icon: ElementType;
  active: boolean;
  compact?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "group w-full relative flex items-center gap-2.5 rounded-lg border border-transparent transition-all duration-150",
        compact ? "justify-center h-9 px-0" : "h-9 px-2.5",
        active
          ? "bg-neutral-900 text-neutral-100 border-white/10"
          : "text-neutral-400 hover:text-neutral-100 hover:bg-neutral-900/70",
      )}
      title={label}
    >
      {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-0.5 rounded-r bg-white/80" />}
      <Icon className={cn("w-4 h-4 flex-shrink-0", active ? "text-white" : "text-neutral-500 group-hover:text-neutral-200")} />
      {!compact && <span className="truncate text-xs font-medium">{label}</span>}
      {active && !compact && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-white/80" />}
    </button>
  );
}

