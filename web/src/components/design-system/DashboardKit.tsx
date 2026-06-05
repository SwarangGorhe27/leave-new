import { useState, type ElementType, type ReactNode } from "react";
import { Eye, EyeOff } from "lucide-react";

export type KpiTone = "purple" | "green" | "orange" | "red" | "gray";

export const KPI_ICON_TONES: Record<KpiTone, { background: string; boxShadow: string }> = {
  purple: {
    background: "linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%)",
    boxShadow: "0 10px 20px rgba(124, 58, 237, 0.28)",
  },
  orange: {
    background: "linear-gradient(135deg, #2f4b96 0%, #2f4b96 100%)",
    boxShadow: "0 10px 20px rgba(249, 115, 22, 0.28)",
  },
  red: {
    background: "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)",
    boxShadow: "0 10px 20px rgba(239, 68, 68, 0.28)",
  },
  gray: {
    background: "linear-gradient(135deg, #6B7280 0%, #4B5563 100%)",
    boxShadow: "0 10px 20px rgba(75, 85, 99, 0.24)",
  },
  green: {
    background: "linear-gradient(135deg, #10B981 0%, #059669 100%)",
    boxShadow: "0 10px 20px rgba(16, 185, 129, 0.28)",
  },
};

/** Standard page shell — matches Admin Dashboard spacing */
export function PortalPage({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`portal-page admin-dashboard ${className}`.trim()}>{children}</div>;
}

export function SectionLabel({ label }: { label: string }) {
  return <p className="dashboard-section-label">{label}</p>;
}

export function KpiCard({
  icon: Icon,
  label,
  value,
  sub,
  tone,
}: {
  icon: ElementType;
  label: string;
  value: number | string;
  sub?: string;
  tone: KpiTone;
}) {
  const iconTone = KPI_ICON_TONES[tone];

  return (
    <div className="flat-card flat-card-hover bg-card p-5 flex items-start gap-4">
      <div
        className="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 text-white [&_svg]:stroke-white"
        style={{
          background: iconTone.background,
          boxShadow: iconTone.boxShadow,
          color: "#FFFFFF",
        }}
      >
        <Icon className="w-5 h-5" />
      </div>
      <div className="min-w-0">
        <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-bold text-foreground mt-0.5">{value}</p>
        {sub ? <p className="text-xs text-muted-foreground mt-1">{sub}</p> : null}
      </div>
    </div>
  );
}

export function MaskableKpiCard({
  icon: Icon,
  label,
  value,
  sub,
  tone,
  maskedDisplay = "₹ ••••••",
  defaultVisible = false,
}: {
  icon: ElementType;
  label: string;
  value: number | string;
  sub?: string;
  tone: KpiTone;
  maskedDisplay?: string;
  defaultVisible?: boolean;
}) {
  const [visible, setVisible] = useState(defaultVisible);
  const iconTone = KPI_ICON_TONES[tone];

  return (
    <div className="flat-card flat-card-hover bg-card p-5 flex items-start gap-4">
      <div
        className="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0 text-white [&_svg]:stroke-white"
        style={{
          background: iconTone.background,
          boxShadow: iconTone.boxShadow,
          color: "#FFFFFF",
        }}
      >
        <Icon className="w-5 h-5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">{label}</p>
          <button
            type="button"
            onClick={() => setVisible((v) => !v)}
            className="app-icon-button flex items-center justify-center flex-shrink-0 !w-7 !h-7"
            aria-label={visible ? "Hide amount" : "Show amount"}
            title={visible ? "Hide salary" : "Show salary"}
          >
            {visible ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
          </button>
        </div>
        <p className="text-2xl font-bold text-foreground mt-0.5 tabular-nums tracking-tight">
          {visible ? value : maskedDisplay}
        </p>
        {sub ? <p className="text-xs text-muted-foreground mt-1">{sub}</p> : null}
      </div>
    </div>
  );
}

export function WidgetHeader({
  icon: Icon,
  title,
  subtitle,
  tone,
}: {
  icon: ElementType;
  title: string;
  subtitle?: string;
  tone: KpiTone;
}) {
  const iconTone = KPI_ICON_TONES[tone];
  return (
    <div className="dashboard-widget-header">
      <div
        className="dashboard-widget-icon"
        style={{
          background: iconTone.background,
          boxShadow: iconTone.boxShadow,
        }}
      >
        <Icon className="w-4 h-4" />
      </div>
      <div className="min-w-0">
        <h2 className="dashboard-widget-title">{title}</h2>
        {subtitle ? <p className="dashboard-widget-subtitle">{subtitle}</p> : null}
      </div>
    </div>
  );
}

export function ChartTooltip({
  active,
  payload,
  label,
  valueSuffix = "",
}: {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
  valueSuffix?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border border-border bg-card px-2.5 py-1.5 text-[11px] shadow-md">
      <p className="text-muted-foreground mb-0.5">{label}</p>
      <p className="font-semibold text-foreground">
        {payload[0].value}
        {valueSuffix}
      </p>
    </div>
  );
}

export const STATUS_BADGE_CLASS: Record<string, string> = {
  Present: "dashboard-badge-today",
  Leave: "dashboard-badge-soon",
  Absent: "dashboard-badge-later",
};
