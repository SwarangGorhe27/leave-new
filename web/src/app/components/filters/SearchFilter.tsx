"use client";

import { Search, X } from "lucide-react";
import { Input } from "../ui/input";
import { cn } from "../ui/utils";

interface SearchFilterProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  placeholder?: string;
}

export function SearchFilter({ value, onChange, onClear, placeholder = "Search employee, code, leave type…" }: SearchFilterProps) {
  return (
    <div className="relative w-full">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500 dark:text-neutral-400" />
      <Input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className={cn(
          "bg-neutral-950 dark:bg-neutral-900 border border-white/10 dark:border-white/10 text-white dark:text-white placeholder:text-neutral-500 dark:placeholder:text-neutral-400 rounded-xl pl-12 pr-11 py-3 shadow-sm",
          "focus-visible:border-white/20 focus-visible:ring-white/10",
        )}
        aria-label="Search leave requests"
      />
      {value ? (
        <button
          type="button"
          onClick={onClear}
          className="absolute right-3 top-1/2 inline-flex h-8 w-8 items-center justify-center rounded-full bg-white/5 text-neutral-300 transition hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/20 -translate-y-1/2"
          aria-label="Clear search"
        >
          <X className="h-4 w-4" />
        </button>
      ) : null}
    </div>
  );
}
