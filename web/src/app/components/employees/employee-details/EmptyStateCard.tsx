import { LucideIcon } from "lucide-react";

interface EmptyStateCardProps {
  icon: LucideIcon;
  title: string;
  description?: string;
}

export function EmptyStateCard({ icon: Icon, title, description }: EmptyStateCardProps) {
  return (
    <div className="rounded-xl border border-dashed border-border bg-secondary/10 py-12 px-6 text-center">
      <Icon className="w-10 h-10 text-muted-foreground/40 mx-auto mb-3" />
      <p className="text-sm font-semibold text-foreground">{title}</p>
      {description ? <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">{description}</p> : null}
    </div>
  );
}
