"use client";

import { useEffect, useMemo, useState } from "react";
import { ChevronDown, Search } from "lucide-react";
import { Input } from "../ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { cn } from "../ui/utils";
import { STATUS_BADGE_STYLES } from "./constants";
import type { FilterOption } from "./constants";

interface StatusFilterProps {
  value: string;
  options: FilterOption[];
  onChange: (value: string) => void;
}

export function StatusFilter({ value, options, onChange }: StatusFilterProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  const selectedOption = options.find((option) => option.value === value) ?? options[0];
  const filtered = useMemo(
    () => options.filter((option) => option.label.toLowerCase().includes(search.toLowerCase())),
    [options, search],
  );

  useEffect(() => {
    setActiveIndex((index) => Math.min(index, Math.max(filtered.length - 1, 0)));
  }, [filtered]);

  const selectActive = () => {
    if (!filtered.length) return;
    onChange(filtered[activeIndex].value);
    setOpen(false);
    setSearch("");
  };

  return (
    <Popover open={open} onOpenChange={(state) => setOpen(state)}>
      <PopoverTrigger asChild>
        <button
          type="button"
          className="flex min-w-[170px] items-center gap-2 rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-left text-sm text-white outline-none transition hover:border-white/20 hover:bg-neutral-900"
          aria-label="Select status"
        >
          <span className="min-w-0 truncate text-sm font-medium">{selectedOption.label}</span>
          <ChevronDown className="h-4 w-4 text-neutral-400" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-[260px] bg-neutral-900 border border-white/10 p-3 shadow-lg">
        <div className="space-y-3">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" />
            <Input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search status"
              className="bg-neutral-950 border border-white/10 text-white placeholder:text-neutral-500 rounded-xl pl-10 pr-3 py-2"
              onKeyDown={(event) => {
                if (event.key === "ArrowDown") {
                  event.preventDefault();
                  setActiveIndex((index) => Math.min(index + 1, filtered.length - 1));
                } else if (event.key === "ArrowUp") {
                  event.preventDefault();
                  setActiveIndex((index) => Math.max(index - 1, 0));
                } else if (event.key === "Enter") {
                  event.preventDefault();
                  selectActive();
                }
              }}
            />
          </div>
          <div className="max-h-60 overflow-y-auto rounded-xl border border-white/10 bg-neutral-950 p-1 text-sm">
            {filtered.map((option, index) => (
              <button
                key={option.value}
                type="button"
                onClick={() => {
                  onChange(option.value);
                  setOpen(false);
                  setSearch("");
                }}
                onMouseEnter={() => setActiveIndex(index)}
                className={cn(
                  "w-full rounded-xl px-3 py-2 text-left transition",
                  index === activeIndex ? "bg-white/10 text-white" : "text-neutral-300 hover:bg-white/5 hover:text-white",
                )}
              >
                <span className={cn("inline-flex items-center gap-2 rounded-full px-2 py-1", STATUS_BADGE_STYLES[option.value] ?? "text-neutral-300 bg-white/5")}>{option.label}</span>
              </button>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
