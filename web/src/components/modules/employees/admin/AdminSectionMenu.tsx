import React, { useState } from 'react';
import { ChevronRight, AlertCircle } from 'lucide-react';
import { ADMIN_MENU_ITEMS } from './constants';

interface AdminSectionMenuProps {
  onSelectItem: (itemId: string, route: string) => void;
  selectedItem?: string;
}

export function AdminSectionMenu({ onSelectItem, selectedItem }: AdminSectionMenuProps) {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  return (
    <div className="space-y-3">
      <div className="px-1 py-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-text-tertiary mb-3">
          Admin Tools
        </h3>
      </div>

      <div className="space-y-1">
        {ADMIN_MENU_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => !item.disabled && onSelectItem(item.id, item.route)}
            disabled={item.disabled}
            className={`w-full px-3 py-2.5 rounded-lg transition-all text-sm font-medium flex items-center justify-between group ${
              selectedItem === item.id
                ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/20 dark:text-brand-300'
                : item.disabled
                  ? 'text-text-tertiary cursor-not-allowed opacity-50'
                  : 'text-text-secondary hover:bg-surface-100 dark:hover:bg-white/5'
            }`}
            onMouseEnter={() => !item.disabled && setHoveredItem(item.id)}
            onMouseLeave={() => setHoveredItem(null)}
            title={item.disabled ? 'Coming Soon' : item.description}
          >
            <div className="flex items-center gap-2">
              <item.icon className="h-4 w-4" />
              <span>{item.label}</span>
            </div>
            <div className="flex items-center gap-1">
              {item.disabled && <AlertCircle className="h-3 w-3 opacity-50" />}
              {!item.disabled && hoveredItem === item.id && (
                <ChevronRight className="h-4 w-4 opacity-60" />
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Info box for disabled items */}
      <div className="mt-4 p-3 rounded-lg bg-surface-50 dark:bg-white/3 border border-surface-200 dark:border-white/8">
        <p className="text-xs text-text-tertiary">
          <span className="font-semibold">💡 Tip:</span> Some features are currently being developed. Check back soon for updates.
        </p>
      </div>
    </div>
  );
}
