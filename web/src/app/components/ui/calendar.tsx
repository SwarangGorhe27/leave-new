"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { DayPicker } from "react-day-picker";

import { cn } from "./utils";
import { buttonVariants } from "./button";

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: React.ComponentProps<typeof DayPicker>) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-4 rounded-xl border border-border bg-card shadow-sm", className)}
      classNames={{
        months: "flex flex-col sm:flex-row gap-4",
        month: "flex flex-col gap-4",
        caption: "flex justify-center pt-2 relative items-center w-full mb-3",
        caption_label: "text-sm font-semibold text-foreground",
        nav: "flex items-center gap-2",
        nav_button: cn(
          buttonVariants({ variant: "outline" }),
          "size-8 bg-card hover:bg-secondary/60 border-border hover:border-border/80 p-0 opacity-70 hover:opacity-100 transition-all duration-200 rounded-lg",
        ),
        nav_button_previous: "absolute left-0",
        nav_button_next: "absolute right-0",
        table: "w-full border-collapse space-x-0",
        head_row: "flex",
        head_cell:
          "text-muted-foreground rounded-lg w-9 font-semibold text-[0.75rem] uppercase tracking-wider py-2",
        row: "flex w-full mt-2 gap-0.5",
        cell: cn(
          "relative p-0 text-center text-sm focus-within:relative focus-within:z-20 [&:has([aria-selected])]:bg-transparent",
          props.mode === "range"
            ? "[&:has(>.day-range-end)]:rounded-r-lg [&:has(>.day-range-start)]:rounded-l-lg first:[&:has([aria-selected])]:rounded-l-lg last:[&:has([aria-selected])]:rounded-r-lg"
            : "[&:has([aria-selected])]:rounded-lg",
        ),
        day: cn(
          buttonVariants({ variant: "ghost" }),
          "size-9 p-0 font-medium aria-selected:opacity-100 rounded-lg transition-all duration-200 hover:bg-secondary/50",
        ),
        day_range_start:
          "day-range-start aria-selected:bg-primary aria-selected:text-primary-foreground aria-selected:font-semibold",
        day_range_end:
          "day-range-end aria-selected:bg-primary aria-selected:text-primary-foreground aria-selected:font-semibold",
        day_selected:
          "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground font-semibold shadow-md",
        day_today: "bg-secondary/60 text-foreground font-semibold border-2 border-primary/30",
        day_outside:
          "day-outside text-muted-foreground/50 aria-selected:text-muted-foreground/50",
        day_disabled: "text-muted-foreground opacity-30 cursor-not-allowed",
        day_range_middle:
          "aria-selected:bg-primary/15 aria-selected:text-foreground",
        day_hidden: "invisible",
        ...classNames,
      }}
      components={{
        IconLeft: ({ className, ...props }) => (
          <ChevronLeft className={cn("size-4 transition-transform", className)} {...props} />
        ),
        IconRight: ({ className, ...props }) => (
          <ChevronRight className={cn("size-4 transition-transform", className)} {...props} />
        ),
      }}
      {...props}
    />
  );
}

export { Calendar };
