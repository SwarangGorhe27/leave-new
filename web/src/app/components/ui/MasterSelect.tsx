import React from 'react';
import { useMasterList } from '@/app/modules/masters/hooks';
import { SearchableSelect } from './SearchableSelect';
import { Loader2 } from 'lucide-react';

interface MasterSelectProps {
  masterName: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchable?: boolean;
  enabled?: boolean;
}

export function MasterSelect({
  masterName,
  value,
  onChange,
  placeholder,
  searchable = true,
  enabled = true,
}: MasterSelectProps) {
  const { data, isLoading } = useMasterList(masterName, { is_active: 'true' }, enabled);

  const options = React.useMemo(() => {
    if (!data?.results) return [];
    return data.results.map((item: any) => ({
      value: String(item.id),
      label: item.label || item.name || item.code || String(item.id),
    }));
  }, [data]);

  if (isLoading) {
    return (
      <div className="w-full flex items-center justify-between px-3 h-11 text-sm bg-slate-50/50 border border-border/40 rounded-xl animate-pulse">
        <span className="text-muted-foreground italic">Loading {masterName}...</span>
        <Loader2 size={14} className="animate-spin text-muted-foreground/40" />
      </div>
    );
  }

  return (
    <SearchableSelect
      value={value}
      onChange={onChange}
      options={options}
      placeholder={placeholder || `Select ${masterName}...`}
      searchable={searchable}
    />
  );
}
