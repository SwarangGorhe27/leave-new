import type { ElementType } from "react";
import { useEffect, useRef, useState } from "react";
import { cn } from "../../ui/utils";

function useAnimatedNumber(target: number, ms = 420) {
  const [n, setN] = useState(target);
  const currentRef = useRef(n);
  currentRef.current = n;

  useEffect(() => {
    const startVal = currentRef.current;
    const t0 = performance.now();
    let id = 0;
    const step = (now: number) => {
      const p = Math.min(1, (now - t0) / ms);
      const eased = 1 - (1 - p) ** 3;
      setN(Math.round(startVal + (target - startVal) * eased));
      if (p < 1) id = requestAnimationFrame(step);
    };
    id = requestAnimationFrame(step);
    return () => cancelAnimationFrame(id);
  }, [target, ms]);

  return n;
}

export function LeaveStatCard({
  icon: Icon,
  label,
  value,
  sub,
  hint,
  className,
}: {
  icon: ElementType;
  label: string;
  value: number;
  sub: string;
  hint?: string;
  className?: string;
}) {
  const animated = useAnimatedNumber(value);

  return (
    <div
      className={cn(
        "flat-card flat-card-hover bg-card p-4 sm:p-5 flex gap-3 sm:gap-4 transition-shadow duration-200",
        className,
      )}
      title={hint}
    >
      <div className="flex h-10 w-10 sm:h-11 sm:w-11 flex-shrink-0 items-center justify-center rounded-xl border border-border bg-secondary">
        <Icon className="h-[18px] w-[18px] sm:h-5 sm:w-5 text-foreground" aria-hidden />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>
        <p className="mt-0.5 text-xl sm:text-2xl font-bold tabular-nums tracking-tight text-foreground">{animated}</p>
        <p className="mt-1 text-[11px] sm:text-xs text-muted-foreground leading-snug">{sub}</p>
      </div>
    </div>
  );
}