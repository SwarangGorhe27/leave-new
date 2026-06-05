export function formatLeaveDate(dateStr: string): string {
  const date = new Date(dateStr).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
  return date;
}

export function formatLeaveShortDate(dateStr: string): string {
  const date = new Date(dateStr).toLocaleDateString("en-IN", { day: "2-digit", month: "short" });
  return date;
}