import React from "react";
import { MoreVertical, LucideIcon } from "lucide-react";
import { Button } from "./button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuPortal
} from "./dropdown-menu";
import { cn } from "./utils";

export interface KebabMenuItem {
  label: string;
  icon?: LucideIcon;
  onClick: () => void;
  variant?: "default" | "destructive" | "warning";
  disabled?: boolean;
  separator?: boolean;
}

interface KebabMenuProps {
  items: KebabMenuItem[];
  align?: "start" | "center" | "end";
  className?: string;
  triggerClassName?: string;
  size?: "sm" | "md" | "lg";
}

export function KebabMenu({ 
  items, 
  align = "end", 
  className, 
  triggerClassName,
  size = "md"
}: KebabMenuProps) {
  const iconSize = size === "sm" ? 14 : size === "lg" ? 20 : 16;
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size="icon" 
          className={cn(
            "rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors",
            size === "sm" ? "h-8 w-8" : size === "lg" ? "h-11 w-11" : "h-9 w-9",
            triggerClassName
          )}
        >
          <MoreVertical size={iconSize} className="text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuPortal>
        <DropdownMenuContent 
          align={align} 
          className={cn("w-56 p-1 rounded-2xl shadow-2xl border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 z-[100]", className)}
        >
          {items.map((item, index) => (
            <React.Fragment key={index}>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  item.onClick();
                }}
                disabled={item.disabled}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest cursor-pointer transition-all",
                  item.variant === "destructive" 
                    ? "text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 focus:bg-rose-50 dark:focus:bg-rose-500/10" 
                    : item.variant === "warning"
                    ? "text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-500/10 focus:bg-amber-50 dark:focus:bg-amber-500/10"
                    : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 focus:bg-slate-50 dark:focus:bg-slate-800",
                  item.disabled && "opacity-50 cursor-not-allowed grayscale"
                )}
              >
                {item.icon && <item.icon size={iconSize} className={cn("shrink-0", !item.variant && "text-slate-400")} />}
                {item.label}
              </DropdownMenuItem>
              {item.separator && <DropdownMenuSeparator className="my-1 bg-slate-100 dark:bg-slate-800" />}
            </React.Fragment>
          ))}
        </DropdownMenuContent>
      </DropdownMenuPortal>
    </DropdownMenu>
  );
}
