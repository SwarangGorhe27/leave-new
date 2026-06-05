import React, { useState } from 'react';
import { ChevronDown, Search, Check } from 'lucide-react';
import { Input } from './input';

interface SearchableSelectProps {
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  placeholder?: string;
  searchable?: boolean;
}

export function SearchableSelect({
  value,
  onChange,
  options,
  placeholder = 'Select...',
  searchable = true,
}: SearchableSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');

  const filtered = searchable
    ? options.filter((opt) =>
        opt.label.toLowerCase().includes(search.toLowerCase())
      )
    : options;

  const selectedLabel = options.find((opt) => opt.value === value)?.label;

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 h-11 text-sm text-left bg-card border border-border hover:border-border/80 hover:bg-secondary/40 dark:border-border dark:hover:border-border/80 dark:hover:bg-secondary/40 rounded-lg transition-all duration-200 shadow-sm focus:ring-2 focus:ring-ring/50 focus:outline-none"
      >
        <span className={selectedLabel ? 'font-semibold text-foreground dark:text-foreground' : 'text-muted-foreground dark:text-muted-foreground'}>
          {selectedLabel || placeholder}
        </span>
        <ChevronDown size={16} className={`transition-transform duration-300 text-muted-foreground dark:text-muted-foreground ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute top-full left-0 right-0 mt-2 bg-card dark:bg-card border border-border dark:border-border rounded-xl shadow-lg z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200 backdrop-blur-sm">
            {searchable && (
              <div className="p-3 border-b border-border/60 dark:border-border/60 bg-secondary/30 dark:bg-secondary/30">
                <div className="relative">
                  <Input
                    placeholder="Search..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="h-8 text-xs pl-10 bg-card dark:bg-card border-border dark:border-border rounded-lg focus:ring-2 focus:ring-ring/50"
                    autoFocus
                  />
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground dark:text-muted-foreground" />
                </div>
              </div>
            )}
            <div className="max-h-64 overflow-y-auto p-1.5">
              {filtered.length > 0 ? (
                filtered.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => {
                      onChange(opt.value);
                      setOpen(false);
                      setSearch('');
                    }}
                    className={`w-full text-left px-3 py-2.5 text-sm rounded-lg transition-all duration-200 flex items-center justify-between font-medium ${
                      value === opt.value 
                        ? 'bg-primary dark:bg-primary text-primary-foreground dark:text-primary-foreground font-semibold shadow-md' 
                        : 'hover:bg-secondary/60 dark:hover:bg-secondary/60 text-foreground dark:text-foreground hover:translate-x-1'
                    }`}
                  >
                    {opt.label}
                    {value === opt.value && <Check size={16} />}
                  </button>
                ))
              ) : (
                <div className="px-3 py-8 text-center text-xs text-muted-foreground dark:text-muted-foreground font-medium">
                  No options found
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
