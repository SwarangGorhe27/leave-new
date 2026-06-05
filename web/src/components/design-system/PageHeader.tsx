import { ChevronRight } from "lucide-react";
import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  subtitle,
  crumbs,
  right,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  crumbs?: string[];
  right?: ReactNode;
}) {
  return (
    <div className="dashboard-widget">
      {crumbs?.length ? (
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">
          {crumbs.map((c, i) => (
            <span key={`${c}-${i}`} className="inline-flex items-center gap-1.5">
              <span>{c}</span>
              {i < crumbs.length - 1 && <ChevronRight className="w-3 h-3" />}
            </span>
          ))}
        </div>
      ) : eyebrow ? (
        <p className="dashboard-section-label mb-0">{eyebrow}</p>
      ) : null}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-[15px] font-semibold text-foreground leading-tight">{title}</h1>
          {subtitle ? <p className="text-[11px] text-muted-foreground mt-1">{subtitle}</p> : null}
        </div>
        {right ? <div className="flex flex-wrap items-center gap-2 flex-shrink-0">{right}</div> : null}
      </div>
    </div>
  );
}
