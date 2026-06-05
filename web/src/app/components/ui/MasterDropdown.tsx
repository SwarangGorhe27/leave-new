import React from 'react';
import { MasterSelect } from './MasterSelect';
import { SearchableSelect } from './SearchableSelect';
import { useMasterDropdownOptions } from '@/app/hooks/useMasterDropdownOptions';

/**
 * Production-ready Master Dropdown Component
 * Unified interface for all master data dropdowns
 * 
 * Usage:
 * <MasterDropdown masterName="Gender" value={gender} onChange={setGender} />
 */
interface MasterDropdownProps {
  masterName: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchable?: boolean;
  isActive?: boolean;
  required?: boolean;
  disabled?: boolean;
  error?: string;
}

export function MasterDropdown({
  masterName,
  value,
  onChange,
  placeholder = `Select ${masterName}...`,
  searchable = true,
  isActive = true,
  required = false,
  disabled = false,
  error,
}: MasterDropdownProps) {
  // Use the same component as MasterSelect (which is already optimized)
  return (
    <MasterSelect
      masterName={masterName}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      searchable={searchable}
      enabled={!disabled && isActive}
    />
  );
}

/**
 * Production-ready Multi-Select Master Dropdown
 * For fields like "Weekly Off Days", "Permissions", etc.
 */
interface MasterMultiSelectProps {
  masterName: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  isActive?: boolean;
}

export function MasterMultiDropdown({
  masterName,
  values,
  onChange,
  placeholder = `Select ${masterName}...`,
  isActive = true,
}: MasterMultiSelectProps) {
  const options = useMasterDropdownOptions(masterName, isActive);

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <label
            key={option.value}
            className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border hover:bg-secondary/50 cursor-pointer transition-colors"
          >
            <input
              type="checkbox"
              checked={values.includes(option.value)}
              onChange={(e) => {
                if (e.target.checked) {
                  onChange([...values, option.value]);
                } else {
                  onChange(values.filter((v) => v !== option.value));
                }
              }}
              className="w-4 h-4 cursor-pointer accent-primary"
            />
            <span className="text-sm font-medium">{option.label}</span>
          </label>
        ))}
      </div>
      {options.length === 0 && (
        <div className="text-xs text-muted-foreground italic py-2">
          No options available
        </div>
      )}
    </div>
  );
}

/**
 * Searchable Master Dropdown
 * For long lists with many options
 */
interface MasterSearchableDropdownProps {
  masterName: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  isActive?: boolean;
}

export function MasterSearchableDropdown({
  masterName,
  value,
  onChange,
  placeholder = `Search ${masterName}...`,
  isActive = true,
}: MasterSearchableDropdownProps) {
  const options = useMasterDropdownOptions(masterName, isActive);

  return (
    <SearchableSelect
      value={value}
      onChange={onChange}
      options={options}
      placeholder={placeholder}
      searchable={true}
    />
  );
}
