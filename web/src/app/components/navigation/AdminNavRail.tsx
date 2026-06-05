import { ChevronDown, Menu, Search, X } from "lucide-react";
import { useEffect, useRef, useMemo, useState } from "react";
import { Sheet, SheetContent, SheetTrigger } from "../ui/sheet";
import { cn } from "../ui/utils";
import type { AdminNavMenuItem } from "./AdminFloatingMenu";

export type AdminNavGroupSchema<T extends string> = {
  id: string;
  label: string;
  items: Array<AdminNavMenuItem<T>>;
};

function TopNavDropdown<T extends string>({
  group,
  active,
  onSelect,
}: {
  group: AdminNavGroupSchema<T>;
  active: T;
  onSelect: (id: T) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const isGroupActive = group.items.some((i) => i.id === active);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative z-50">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 whitespace-nowrap",
          isGroupActive
            ? "bg-secondary text-foreground shadow-sm"
            : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
        )}
      >
        {group.label}
        <ChevronDown
          className={cn(
            "w-3.5 h-3.5 transition-transform duration-200",
            open && "rotate-180"
          )}
        />
      </button>

      {open && (
        <div className="absolute top-full left-0 mt-2 z-[999] min-w-[220px] rounded-lg border border-border bg-card shadow-xl py-2">
          {group.items.map((item) => {
            const Icon = item.icon;
            const isActive = active === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  onSelect(item.id);
                  setOpen(false);
                }}
                className={cn(
                  "w-full flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors duration-100",
                  isActive
                    ? "bg-secondary text-foreground font-medium"
                    : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
                )}
              >
                <Icon
                  className={cn(
                    "w-4 h-4 shrink-0",
                    isActive ? "text-foreground" : "text-muted-foreground"
                  )}
                />
                <span>{item.label}</span>
                {isActive && (
                  <span className="ml-auto h-1.5 w-1.5 rounded-full bg-foreground" />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function SearchBar({
  value,
  onChange,
  onClose,
}: {
  value: string;
  onChange: (v: string) => void;
  onClose: () => void;
}) {
  const ref = useRef<HTMLInputElement>(null);
  useEffect(() => ref.current?.focus(), []);
  return (
    <div className="flex items-center gap-2 border border-border rounded-lg px-3 py-1.5 bg-background shadow-sm">
      <Search className="w-3.5 h-3.5 text-slate-400 shrink-0" />
      <input
        ref={ref}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search navigation..."
        className="text-sm text-foreground placeholder:text-muted-foreground bg-transparent outline-none w-44"
      />
      <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600">
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

export function AdminNavRail<T extends string>({
  groups,
  active,
  onSelect,
}: {
  groups: Array<AdminNavGroupSchema<T>>;
  active: T;
  onSelect: (id: T) => void;
}) {
  const [query, setQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);

  const filteredGroups = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return groups;
    return groups
      .map((g) => ({
        ...g,
        items: g.items.filter((item) => item.label.toLowerCase().includes(q)),
      }))
      .filter((g) => g.items.length > 0);
  }, [groups, query]);

  // Mobile: flat list of all items
  const allItems = useMemo(() => groups.flatMap((g) => g.items), [groups]);

  const topNav = (
    <nav className="rounded-xl border border-border bg-card shadow-sm px-3 py-2">
      <div className="flex items-center gap-1 flex-wrap">
        {/* Search toggle */}
        {searchOpen ? (
          <SearchBar
            value={query}
            onChange={setQuery}
            onClose={() => {
              setSearchOpen(false);
              setQuery("");
            }}
          />
        ) : (
          <button
            type="button"
            onClick={() => setSearchOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors duration-150"
            title="Search navigation"
          >
            <Search className="w-3.5 h-3.5" />
          </button>
        )}

        <div className="h-5 w-px bg-border mx-1" />

        {/* Group dropdowns */}
        {filteredGroups.map((group) => (
          <TopNavDropdown
            key={group.id}
            group={group}
            active={active}
            onSelect={onSelect}
          />
        ))}
      </div>
    </nav>
  );

  // Mobile: sheet with vertical list
  const mobileNav = (
    <div className="lg:hidden">
      <Sheet>
        <SheetTrigger asChild>
          <button
            type="button"
            className="h-9 px-3 rounded-lg border border-slate-200 bg-white text-slate-700 text-xs font-medium inline-flex items-center gap-2 shadow-sm"
          >
            <Menu className="w-4 h-4" />
            Navigation
          </button>
        </SheetTrigger>
        <SheetContent side="left" className="bg-white border-slate-200 p-4 w-72">
          <div className="mb-4">
            <div className="flex items-center gap-2 border border-slate-200 rounded-lg px-3 py-2">
              <Search className="w-4 h-4 text-slate-400" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search..."
                className="text-sm text-slate-700 placeholder:text-slate-400 bg-transparent outline-none flex-1"
              />
            </div>
          </div>
          <div className="space-y-4">
            {filteredGroups.map((group) => (
              <div key={group.id}>
                <p className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold px-1 mb-1.5">
                  {group.label}
                </p>
                <div className="space-y-0.5">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => onSelect(item.id)}
                        className={cn(
                          "w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors duration-100",
                          active === item.id
                            ? "bg-[#0f2744] text-white font-medium"
                            : "text-slate-600 hover:bg-slate-100"
                        )}
                      >
                        <Icon className="w-4 h-4 shrink-0" />
                        {item.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );

  return (
    <>
      <div className="hidden lg:block w-full">{topNav}</div>
      {mobileNav}
    </>
  );
}