import type { ElementType } from "react";
import { AdminNavItem } from "./AdminNavItem";

export type AdminNavMenuItem<T extends string> = {
  id: T;
  label: string;
  icon: ElementType;
};

export function AdminFloatingMenu<T extends string>({
  items,
  active,
  onSelect,
}: {
  items: Array<AdminNavMenuItem<T>>;
  active: T;
  onSelect: (id: T) => void;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/90 backdrop-blur-sm shadow-2xl p-2 min-w-[220px]">
      <div className="space-y-1">
        {items.map((item) => (
          <AdminNavItem
            key={item.id}
            label={item.label}
            icon={item.icon}
            active={active === item.id}
            onClick={() => onSelect(item.id)}
          />
        ))}
      </div>
    </div>
  );
}

