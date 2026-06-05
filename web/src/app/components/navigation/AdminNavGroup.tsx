import { ChevronDown } from "lucide-react";
import { cn } from "../ui/utils";

export function AdminNavGroup({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1">
      <button
        type="button"
        onClick={onToggle}
        className="w-full h-7 px-2 text-[10px] tracking-wider uppercase font-semibold text-neutral-500 hover:text-neutral-300 flex items-center justify-between rounded-md transition-colors duration-150"
      >
        {title}
        <ChevronDown className={cn("w-3.5 h-3.5 transition-transform duration-150", open ? "rotate-0" : "-rotate-90")} />
      </button>
      <div
        className={cn(
          "grid transition-all duration-200 ease-out",
          open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0",
        )}
      >
        <div className="overflow-hidden">
          <div className="space-y-1">{children}</div>
        </div>
      </div>
    </div>
  );
}

