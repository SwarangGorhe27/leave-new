import { cn } from "../../../../components/ui/utils";

type Tone = "success" | "warning" | "danger" | "info" | "neutral";

const TONE_CLASS: Record<Tone, string> = {
  success: "bg-emerald-100 text-emerald-800 dark:bg-emerald-500/15 dark:text-emerald-300",
  warning: "bg-amber-100 text-amber-800 dark:bg-amber-500/15 dark:text-amber-300",
  danger: "bg-rose-100 text-rose-800 dark:bg-rose-500/15 dark:text-rose-300",
  info: "bg-sky-100 text-sky-800 dark:bg-sky-500/15 dark:text-sky-300",
  neutral: "bg-secondary text-foreground border border-border",
};

export function StatusBadge({
  tone,
  label,
  className,
}: {
  tone: Tone;
  label: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-md font-semibold",
        TONE_CLASS[tone],
        className,
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
      {label}
    </span>
  );
}

