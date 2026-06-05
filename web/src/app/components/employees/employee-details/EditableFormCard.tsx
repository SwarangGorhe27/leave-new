import { Trash2 } from "lucide-react";
import { cn } from "../../ui/utils";

interface EditableFormCardProps {
  children: React.ReactNode;
  /** Show delete when editing */
  showDelete?: boolean;
  onDelete?: () => void;
  className?: string;
}

export function EditableFormCard({ children, showDelete, onDelete, className }: EditableFormCardProps) {
  return (
    <div className={cn("rounded-xl border border-border bg-background p-4 sm:p-5 relative", className)}>
      {showDelete && onDelete ? (
        <button
          type="button"
          onClick={onDelete}
          className="absolute top-3 right-3 p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
          aria-label="Delete entry"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      ) : null}
      <div className={showDelete ? "pr-10" : undefined}>{children}</div>
    </div>
  );
}
