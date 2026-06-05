import { Search } from "lucide-react";
import { Input } from "../ui/input";

export function AdminSearchNavigation({
  value,
  onChange,
  placeholder = "Search navigation...",
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <div className="relative">
      <Search className="w-3.5 h-3.5 text-neutral-500 dark:text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2" />
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="h-8 pl-8 pr-2 text-xs bg-neutral-950 border-white/10 text-neutral-200 placeholder:text-neutral-500"
      />
    </div>
  );
}

