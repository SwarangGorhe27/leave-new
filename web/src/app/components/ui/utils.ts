import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function safeFormatDate(dateInput: string | Date | null | undefined, formatStr = "dd MMM yyyy") {
  if (!dateInput) return "N/A";
  const date = typeof dateInput === "string" ? new Date(dateInput) : dateInput;
  if (!(date instanceof Date) || isNaN(date.getTime())) return "Invalid Date";
  try {
    return format(date, formatStr);
  } catch {
    return "Invalid Date";
  }
}
