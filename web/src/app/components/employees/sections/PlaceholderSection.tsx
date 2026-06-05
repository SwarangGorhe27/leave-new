import { FileText, Plus } from "lucide-react";

interface Props {
  title: string;
  description: string;
  icon?: React.ComponentType<{ className?: string }>;
}

export function PlaceholderSection({ title, description, icon: Icon = FileText }: Props) {
  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-bold text-foreground">{title}</h2>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>

      <div className="flat-card bg-card overflow-hidden">
        <div className="bg-background border-b border-dashed border-border p-16 text-center">
          <div className="w-16 h-16 rounded-lg bg-secondary border border-border flex items-center justify-center mx-auto mb-5">
            <Icon className="w-7 h-7 text-muted-foreground" />
          </div>
          <h3 className="text-sm font-bold text-foreground">No {title} Added Yet</h3>
          <p className="text-sm text-muted-foreground mt-1.5 max-w-xs mx-auto">
            {description}. Click below to add details.
          </p>
          <button className="mt-7 inline-flex items-center gap-2 px-6 py-2.5 bg-foreground text-primary-foreground text-sm font-semibold rounded-lg hover:bg-accent transition-colors">
            <Plus className="w-4 h-4" />
            Add {title}
          </button>
        </div>
      </div>
    </div>
  );
}
