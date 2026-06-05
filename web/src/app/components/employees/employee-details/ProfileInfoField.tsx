import { cn } from "../../ui/utils";

interface ProfileInfoFieldProps {
  label: string;
  value: string;
  editing?: boolean;
  onChange?: (v: string) => void;
  type?: "text" | "date" | "email" | "tel" | "number" | "textarea" | "select";
  options?: Array<{ value: string; label: string; disabled?: boolean }>;
  readOnly?: boolean;
  placeholder?: string;
  className?: string;
  error?: string | null;
  min?: string;
  max?: string;
}

export function ProfileInfoField({
  label,
  value,
  editing,
  onChange,
  type = "text",
  options,
  readOnly = false,
  placeholder,
  className,
  error,
  min,
  max,
}: ProfileInfoFieldProps) {
  const selectOptions = options?.length
    ? options.some((option) => option.value === value) || !value
      ? options
      : [{ value, label: value }, ...options]
    : undefined;

  const display = value === "" ? "—" : value;
  return (
    <div className={cn("space-y-1.5", className)}>
      <span className="block text-[11px] font-semibold text-muted-foreground tracking-wide">{label}</span>
      {editing && !readOnly ? (
        <>
          {selectOptions?.length ? (
            <select
              value={value}
              onChange={(e) => onChange?.(e.target.value)}
              className="w-full rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              <option value="">{placeholder ?? `Select ${label}`}</option>
              {selectOptions.map((option) => (
                <option key={option.value} value={option.value} disabled={(option as any).disabled}>
                  {option.label}
                </option>
              ))}
            </select>
          ) : type === "textarea" ? (
            <textarea
              value={value}
              onChange={(e) => onChange?.(e.target.value)}
              placeholder={placeholder}
              rows={3}
              className="w-full rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          ) : (
            <input
              type={type}
              value={value}
              min={type === "date" ? min : undefined}
              max={type === "date" ? max : undefined}
              onChange={(e) => onChange?.(e.target.value)}
              placeholder={placeholder}
              className="w-full rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          )}
          {error ? <p className="text-xs text-destructive">{error}</p> : null}
        </>
      ) : (
        <div className="w-full rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm font-semibold text-foreground min-h-10 flex items-center shadow-sm">
          {display}
        </div>
      )}
    </div>
  );
}
