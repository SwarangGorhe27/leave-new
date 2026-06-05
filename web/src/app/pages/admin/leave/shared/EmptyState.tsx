import { cn } from "../../../../components/ui/utils";

export function EmptyState({
  icon: Icon,
  title,
  subtitle,
  action,
  className,
}: {
  icon: React.ElementType;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-14 text-center", className)}>
      <div className="w-12 h-12 rounded-xl bg-secondary border border-border flex items-center justify-center">
        <Icon className="w-6 h-6 text-muted-foreground" />
      </div>
      <p className="mt-3 text-sm font-semibold text-foreground">{title}</p>
      {subtitle && <p className="mt-1 text-xs text-muted-foreground max-w-[520px]">{subtitle}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

