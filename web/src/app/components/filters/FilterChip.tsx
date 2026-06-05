import { cn } from "../ui/utils";

interface FilterChipProps {
  label: string;
  onRemove?: () => void;
}

export function FilterChip({ label, onRemove }: FilterChipProps) {
  return (
    <div className={cn("inline-flex items-center gap-2 rounded-full border border-white/10 bg-neutral-950 px-3 py-1 text-xs font-medium text-white")}>
      <span>{label}</span>
      {onRemove ? (
        <button type="button" onClick={onRemove} className="rounded-full p-1 text-neutral-400 hover:bg-white/5 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-white/20">
          ×
        </button>
      ) : null}
    </div>
  );
}
