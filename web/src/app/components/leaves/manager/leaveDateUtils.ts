export function formatLeaveDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

export function formatLeaveShortDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-IN", { day: "2-digit", month: "short" });
}
